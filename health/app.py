import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import subprocess
from flask import Flask, render_template, request, session, redirect, url_for, flash, send_file, abort, send_from_directory, jsonify
from datetime import datetime, timedelta
import os
import pandas as pd
import csv
import io
import pdfkit
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import matplotlib.pyplot as plt
from google_fit_module import GoogleFit, GFitDataType  # Assuming you saved the GoogleFit class in google_fit_module.py
import base64
from io import BytesIO
import secrets 
from werkzeug.utils import secure_filename  # Ensure secure filename import
from datetime import datetime


app = Flask(__name__)

app.secret_key = secrets.token_hex(16)  # Generates a secure random key each time the app starts

# Set paths for file saving
reports_directory = os.path.join(os.getcwd(), 'reports')

blood_test_report_folder = os.path.join(os.getcwd(), 'bloodtestreports')
os.makedirs(reports_directory, exist_ok=True)
os.makedirs(blood_test_report_folder, exist_ok=True)
    
# Allowed file type check
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() == 'pdf'

# Path to save the text file for health form data
txt_file_path = os.path.abspath('medical_data.txt')
txt_file_path2 = os.path.abspath('extracted_info.txt')
# Path to the CSV file for storing appointments
appointments_csv_path = os.path.abspath('appointments.csv')
xcel_file_path = os.path.join(reports_directory, 'reports.xlsx')
# Path to your CSV file for storing user data
csv_path = os.path.abspath('users.csv')

# Path to store the logged-in patient's ID (logpatient_id.txt)
log_patient_id_path = os.path.abspath('logpatient_id.txt')

# Path to store the Excel file
google_fit_excel_path = os.path.abspath('google_fit_week_data.xlsx')
# Google Maps API key
google_maps_api_key = os.getenv('AIzaSyBUseRAD3lPC47TukWCKnnhLHRaqI-ouxY')

# Read the CSV file into a DataFrame
df = pd.read_csv(csv_path)

# Serve the static files (like the logo image) in the assets folder
@app.route('/assets/<path:filename>')
def assets(filename):
    return send_from_directory('assets', filename)

@app.route('/save_responses', methods=['POST'])
def save_responses():
    data = request.json  # Get the JSON data from the POST request
    responses = data.get("responses", [])  # Extract the responses from JSON
    
    # Save responses to a text file
    with open('user_responses.txt', 'w') as f:
        for question, response in responses:
            f.write(f"{question}: {response}\n")
    
    return jsonify({"status": "success", "message": "Responses saved successfully."})

def clean_data(df):
    # Replace non-numeric values with NaN and coerce to numeric
    df['Steps'] = pd.to_numeric(df['Steps'], errors='coerce')
    df['Heart Points'] = pd.to_numeric(df['Heart Points'], errors='coerce')
    df['Distance (km)'] = pd.to_numeric(df['Distance (km)'], errors='coerce')
    df['Energy Expended (cal)'] = pd.to_numeric(df['Energy Expended (cal)'], errors='coerce')

    # You can fill NaN values with 0, or drop rows with NaN
    df = df.fillna(0)  # Or you could use df.dropna()
    return df


# Function to fetch and store Google Fit data in an Excel file
def fetch_google_fit_data():
    client_id = "127051961270-oq0tt2utemkjn3ceegpe2vbtsegj8hmt.apps.googleusercontent.com"
    client_secret = "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"

    fit = GoogleFit(client_id, client_secret)
    fit.authenticate()

    today = datetime.now()
    week_data = []

    # Fetch data for the past 7 days
    for i in range(7):
        day = today - timedelta(days=i)
        steps = fit.average_for_date(GFitDataType.STEPS, day)
        heart_points = fit.average_for_date(GFitDataType.HEART_POINTS, day)
        distance = fit.average_for_date(GFitDataType.DISTANCE, day)
        energy = fit.average_for_date(GFitDataType.ENERGY_EXPENDED, day)

        # Collect data for the day
        week_data.append({
            "Date": day.strftime('%Y-%m-%d'),
            "Steps": steps,
            "Heart Points": heart_points,
            "Distance (km)": distance / 1000 if isinstance(distance, (float, int)) else "No Data",
            "Energy Expended (cal)": energy,
        })

    # Convert to DataFrame for further usage
    return pd.DataFrame(week_data)

# Route to fetch and display Google Fit data
@app.route('/google_fit_data')
def google_fit_data():
    df = fetch_google_fit_data()
    return render_template('google_fit_data.html', tables=[df.to_html()], titles=df.columns.values)

# Route to download Google Fit data as an Excel file
@app.route('/download_google_fit_data')
def download_google_fit_data():
    try:
        return send_file(google_fit_excel_path, as_attachment=True)
    except FileNotFoundError:
        return "No Google Fit data found. Please fetch the data first."

# Route to display graphs for Google Fit data
@app.route('/plot_google_fit/<metric>')
def plot_google_fit(metric):
    df = pd.read_excel(google_fit_excel_path)

    # Check if the metric exists in the data
    if metric not in df.columns:
        return "Invalid metric"

    # Plot the graph and return as an image
    output = plot_graph(df, metric)
    return send_file(io.BytesIO(output.getvalue()), mimetype='image/png')

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Re-read the CSV file to get the latest data for login
        try:
            df = pd.read_csv(csv_path)
        except pd.errors.EmptyDataError:
            return render_template('login.html', error='No accounts found. Please create an account first.')

        username = request.form['username']
        password = request.form['password']

        # Check if user exists in the CSV file with matching username and password
        user_row = df[(df['username'] == username) & (df['password'] == password)]
        
        if not user_row.empty:
            role = user_row.iloc[0]['role']
            user_id = user_row.iloc[0]['id']  # Get user ID from the CSV file
            # Store the logged-in user's ID in logpatient_id.txt
            with open(log_patient_id_path, 'w') as file:
                file.write(str(user_id))

            # Redirect based on role
            if role == 'doctor':
                return redirect(url_for('doctor_page'))
            elif role == 'patient':
                return redirect(url_for('patient_main_page'))
            elif role == 'nurse':
                return redirect(url_for('nurse_dashboard'))  # Redirect to nurse dashboard
        else:
            return render_template('login.html', error='Invalid Credentials')

    return render_template('login.html')

@app.route('/create_doctor_account', methods=['GET', 'POST'])
def create_doctor_account():
    if request.method == 'POST':
        # Read the CSV file or create a new DataFrame if it’s empty
        try:
            df = pd.read_csv(csv_path)
            print("CSV Data Read Successfully:\n", df)  # Debug: Print data to ensure correct loading
        except pd.errors.EmptyDataError:
            # Initialize DataFrame if the CSV file is empty or does not exist
            df = pd.DataFrame(columns=[
                'id', 'username', 'password', 'name', 'dob', 'phone', 'gender', 
                'address', 'city', 'state', 'zip_code', 'hospital_name', 'role'
            ])
            print("CSV is empty or not found. Initialized new DataFrame.")  # Debug message

        # Retrieve form data
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        dob = request.form.get('dob', '')  # Optional handling of 'dob'
        phone = request.form['phone']
        gender = request.form['gender']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zip_code']
        hospital_name = request.form['hospital_name']
        role = 'doctor'

        # Check if the username already exists in the DataFrame
        if not df[df['username'] == username].empty:
            print("Username check triggered - username already exists.")  # Debug message
            return render_template('create_doctor_account.html', error="Username already exists")

        # Generate the next user ID
        if 'id' in df.columns and not df.empty:
            next_id = df['id'].max() + 1
        else:
            next_id = 1

        # Create a new doctor DataFrame row
        new_user = pd.DataFrame([[
            next_id, username, password, name, dob, phone, gender, 
            address, city, state, zip_code, hospital_name, role
        ]], columns=[
            'id', 'username', 'password', 'name', 'dob', 'phone', 'gender', 
            'address', 'city', 'state', 'zip_code', 'hospital_name', 'role'
        ])

        # Append the new doctor to the existing DataFrame and save it to the CSV
        updated_df = pd.concat([df, new_user], ignore_index=True)
        updated_df.to_csv(csv_path, index=False)
        print("New doctor account created and saved successfully.")  # Debug message

        # Redirect to the doctor page after account creation
        return redirect(url_for('login'))

    # Render the doctor account creation form for GET requests
    return render_template('create_doctor_account.html')


# Nurse's page showing all blood test appointments
@app.route('/nurse_dashboard')
def nurse_dashboard():
    blood_test_appointments = []
    search_patient_id = request.args.get('patient_id', '').strip()

    # Read appointments from the CSV file
    try:
        with open(appointments_csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Only show blood test appointments
                if row['appointment_type'] == 'Blood Test':
                    try:
                        # Parse the appointment date and time
                        appointment_datetime = datetime.strptime(
                            f"{row['appointment_date']} {row['appointment_time']}", "%Y-%m-%d %H:%M"
                        )
                        current_datetime = datetime.now()

                        # Determine the status of the appointment
                        if row['status'] != 'Completed':
                            row['status'] = 'New' if appointment_datetime >= current_datetime else 'Expired'

                        # Only add 'mark_as_completed' key if status is 'New'
                        row['mark_as_completed'] = row['status'] == 'New'
                        
                        # Check if a search filter is applied
                        if search_patient_id and row['patient_id'] != search_patient_id:
                            continue  # Skip this row if it doesn't match the search

                        blood_test_appointments.append(row)
                    except ValueError as e:
                        print(f"Error parsing appointment date/time for row {row}: {e}")
    except FileNotFoundError:
        print("Appointments CSV file not found.")

    # Pass the blood test appointments and current search term to the template
    return render_template('nurse_dashboard.html', blood_test_appointments=blood_test_appointments, search_patient_id=search_patient_id)

@app.route('/create_nurse_account', methods=['GET', 'POST'])
def create_nurse_account():
    if request.method == 'POST':
        # Read the CSV file or create a new DataFrame if it’s empty
        try:
            df = pd.read_csv(csv_path)
            print("CSV Data Read Successfully:\n", df)  # Debug: Print data to ensure correct loading
        except pd.errors.EmptyDataError:
            # Initialize DataFrame if the CSV file is empty or does not exist
            df = pd.DataFrame(columns=[
                'id', 'username', 'password', 'name', 'dob', 'phone', 'gender', 
                'address', 'city', 'state', 'zip_code', 'hospital_name', 'role'
            ])
            print("CSV is empty or not found. Initialized new DataFrame.")  # Debug message

        # Retrieve form data
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        dob = request.form.get('dob', '')  # Optional handling of 'dob'
        phone = request.form['phone']
        gender = request.form['gender']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zip_code']
        hospital_name = request.form['hospital_name']
        role = 'nurse'

        # Check if the username already exists in the DataFrame
        if not df[df['username'] == username].empty:
            print("Username check triggered - username already exists.")  # Debug message
            return render_template('create_nurse_account.html', error="Username already exists")

        # Generate the next user ID
        if 'id' in df.columns and not df.empty:
            next_id = df['id'].max() + 1
        else:
            next_id = 1

        # Create a new nurse DataFrame row
        new_user = pd.DataFrame([[
            next_id, username, password, name, dob, phone, gender, 
            address, city, state, zip_code, hospital_name, role
        ]], columns=[
            'id', 'username', 'password', 'name', 'dob', 'phone', 'gender', 
            'address', 'city', 'state', 'zip_code', 'hospital_name', 'role'
        ])

        # Append the new nurse to the existing DataFrame and save it to the CSV
        updated_df = pd.concat([df, new_user], ignore_index=True)
        updated_df.to_csv(csv_path, index=False)
        print("New nurse account created and saved successfully.")  # Debug message

        # Redirect to the nurse dashboard after account creation
        return redirect(url_for('login'))

    # Render the nurse account creation form for GET requests
    return render_template('create_nurse_account.html')

# Doctor's page showing all doctor appointments

@app.route('/doctor')
def doctor_page():
    doctor_appointments = []
    blood_test_report_folder = 'bloodtestreports'
    search_patient_id = request.args.get('patient_id', '').strip()  # Get search parameter from query string

    # Read appointments from the CSV file
    try:
        with open(appointments_csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Only show doctor appointments and filter by patient ID if search is provided
                if row['appointment_type'] == 'Doctor Consultation' and (not search_patient_id or row['patient_id'] == search_patient_id):
                    try:
                        # Parse the appointment date and time
                        appointment_datetime = datetime.strptime(f"{row['appointment_date']} {row['appointment_time']}", "%Y-%m-%d %H:%M")
                        current_datetime = datetime.now()

                        # Update status: If it's 'New' but the date has passed, mark it as 'Expired'
                        if row['status'] == 'New' and appointment_datetime < current_datetime:
                            row['status'] = 'Expired'

                        # Check if a blood test report exists for this patient
                        patient_id = row['patient_id']
                        report_exists = False
                        if os.path.isdir(blood_test_report_folder):
                            report_exists = any(f.startswith(f"{patient_id}_") for f in os.listdir(blood_test_report_folder))

                        # Add the 'has_blood_test_report' key
                        row['has_blood_test_report'] = report_exists

                        # Append updated row to doctor_appointments
                        doctor_appointments.append(row)
                    except ValueError as e:
                        print(f"Error parsing date/time for appointment: {e}")
    except FileNotFoundError:
        print("Appointments CSV file not found.")

    # Pass the appointments and search parameter to the template
    return render_template('doctor_main_page.html', doctor_appointments=doctor_appointments, search_patient_id=search_patient_id)


import re

@app.route('/show_last_blood_test_report')
def show_last_blood_test_report():
    blood_test_report_folder = 'bloodtestreports'

    # Read the patient ID from a text file
    try:
        with open(log_patient_id_path, "r") as file:
            patient_id = file.read().strip()
            print(f"Read Patient ID from file: {patient_id}")  # Debug: Check patient ID from file
    except FileNotFoundError:
        return "Patient ID file not found."
    except Exception as e:
        return f"Error reading patient ID file: {e}"

    if patient_id and os.path.isdir(blood_test_report_folder):
        # Define a regex pattern to match files with the format {patient_id}_YYYY-MM-DD.pdf
        pattern = re.compile(rf"{patient_id}_(\d{{4}}-\d{{2}}-\d{{2}})\.pdf")
        
        # Find all matching reports for this patient
        patient_reports = []
        for filename in os.listdir(blood_test_report_folder):
            print(f"Found file: {filename}")  # Debug: Check all files in the directory
            match = pattern.match(filename)
            if match:
                report_date = match.group(1)
                try:
                    # Parse the date from the filename
                    report_date_obj = datetime.strptime(report_date, "%Y-%m-%d")
                    patient_reports.append((filename, report_date_obj))
                    print(f"Matched report: {filename} with date {report_date}")  # Debug: Matched files
                except ValueError:
                    print(f"Invalid date in filename: {filename}")  # Debug: Invalid date format
                    continue
        
        # If we found any reports, pick the latest by date
        if patient_reports:
            latest_report = max(patient_reports, key=lambda x: x[1])[0]  # Get the filename of the latest report
            report_path = os.path.join(blood_test_report_folder, latest_report)
            print(f"Latest report path: {report_path}")  # Debug: Path of the latest report
            return send_file(report_path, mimetype='application/pdf')  # Serve the PDF to open in the browser

    return "No blood test report found."


@app.route('/show_blood_test_report/<patient_id>')
def show_blood_test_report(patient_id):
    blood_test_report_folder = 'bloodtestreports'

    # Find the latest report for this patient
    reports = [f for f in os.listdir(blood_test_report_folder) if f.startswith(f"{patient_id}_") and f.endswith(".pdf")]
    if not reports:
        abort(404, description="No blood test report found for this patient.")
    
    # Sort reports to get the latest by name (assumes date is part of the filename in YYYY-MM-DD format)
    latest_report = sorted(reports, reverse=True)[0]
    report_path = os.path.join(blood_test_report_folder, latest_report)

    # Send the PDF file as a response to display in the browser
    return send_file(report_path, mimetype='application/pdf')

def get_appointments():
    appointments = []
    with open(appointments_csv_path, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                # Parse the appointment date and time ('dd-mm-yyyy hh.mm' format)
                #appointment_datetime = datetime.strptime(f"{row['appointment_date']} {row['appointment_time']}", "%d-%m-%Y %H.%M")
                appointment_datetime = datetime.strptime(f"{row['appointment_date']} {row['appointment_time']}", "%Y-%m-%d %H:%M")
            except ValueError as e:
                print(f"Error parsing date and time for appointment ID {row['id']}: {e}")
                continue

            current_datetime = datetime.now()

            # Determine the status of the appointment
            if appointment_datetime >= current_datetime:
                row['status'] = 'New'
            else:
                row['status'] = 'Expired'

            appointments.append(row)
    return appointments

# Route to mark an appointment as completed
@app.route('/mark_completed/<appointment_id>')
def mark_completed(appointment_id):
    # Update the appointment status in the CSV file
    updated_appointments = []

    try:
        with open(appointments_csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['id'] == appointment_id:
                    row['status'] = 'Completed'
                updated_appointments.append(row)

        # Write the updated appointments back to the CSV
        with open(appointments_csv_path, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=['id', 'patient_id', 'consultant_name', 'appointment_type', 'appointment_date', 'appointment_time', 'hospital_location', 'status'])
            writer.writeheader()
            writer.writerows(updated_appointments)

    except FileNotFoundError:
        return "Appointments file not found."

    # Redirect back to the doctor's page
    return redirect(url_for('doctor_page'))

@app.route('/patient')
def patient_main_page():
    # Read the data from the existing Google Fit Excel file
    try:
        df = pd.read_excel(google_fit_excel_path, engine='openpyxl') 
        df = clean_data(df)  # Clean the data in case there are any missing values or non-numeric entries
    except FileNotFoundError:
        return "No Google Fit data found. Please update the data first."
    except UnicodeDecodeError as e:
        return f"Error reading Excel file: {e}"

    # Generate graphs in memory and convert to base64
    steps_graph = generate_graph_in_memory(df, 'Steps')
    heart_points_graph = generate_graph_in_memory(df, 'Heart Points')
    distance_graph = generate_graph_in_memory(df, 'Distance (km)')
    energy_expended_graph = generate_graph_in_memory(df, 'Energy Expended (cal)')

    # Fetch the last blood test report for the logged-in patient
    patient_id = session.get('patient_id')  # Assumes patient_id is stored in session after login
    last_blood_test_report = None
    
    blood_test_report_folder = 'bloodtestreports'
    if patient_id and os.path.isdir(blood_test_report_folder):
        # Find files starting with the patient ID and sort by modification time to get the latest report
        patient_reports = [f for f in os.listdir(blood_test_report_folder) if f.startswith(f"{patient_id}_")]
        if patient_reports:
            latest_report = max(patient_reports, key=lambda f: os.path.getmtime(os.path.join(blood_test_report_folder, f)))
            last_blood_test_report = os.path.join(blood_test_report_folder, latest_report)

    # Render the patient dashboard template with the graphs and the last blood test report
    return render_template('patient_main_page.html', 
                           steps_graph=steps_graph, 
                           heart_points_graph=heart_points_graph, 
                           distance_graph=distance_graph, 
                           energy_expended_graph=energy_expended_graph,
                           last_blood_test_report=last_blood_test_report)
import logging

# Enable logging
logging.basicConfig(level=logging.INFO)
@app.route('/update_data')
def update_data():
    # Fetch new data from Google Fit
    logging.info("Fetching new Google Fit data...")
    new_data = fetch_google_fit_data()

    # Check if the Excel file exists and read existing data if available
    if os.path.exists(google_fit_excel_path):
        try:
            existing_data = pd.read_excel(google_fit_excel_path, engine='openpyxl')
            logging.info("Existing data found, merging with new data...")
            
            # Append new data and drop duplicates based on 'Date' to keep unique entries
            combined_data = pd.concat([existing_data, new_data]).drop_duplicates(subset=['Date'], keep='last')
        except Exception as e:
            logging.error(f"Error reading existing data: {e}")
            return f"Error reading existing data: {e}"
    else:
        logging.info("No existing data found, initializing with new data...")
        combined_data = new_data  # No existing data, so use only new data

    # Save the combined data back to the Excel file
    try:
        logging.info(f"Saving updated data to Excel: {google_fit_excel_path}")
        combined_data.to_excel(google_fit_excel_path, index=False, engine='openpyxl')
        logging.info("Data successfully saved without duplicates.")
    except Exception as e:
        logging.error(f"Error saving data to Excel: {e}")
        return f"Error updating Google Fit data: {e}"

    # After updating, redirect back to the patient dashboard
    return redirect(url_for('patient_main_page'))




# Function to generate a graph and return it as base64-encoded image
def generate_graph_in_memory(df, metric):
    # Convert the 'Date' column to datetime format if not already done
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Get the last 7 days, sort them by date in ascending order, and convert to weekday names
    df_last_week = df.tail(7).sort_values(by='Date')
    df_last_week['Day'] = df_last_week['Date'].dt.strftime('%a')  # Display day of the week (e.g., Mon, Tue)
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Plot data with weekday names in ascending order
    ax.plot(df_last_week['Day'], df_last_week[metric], marker='o', label=metric)
    
    # Set title and labels with larger font sizes
    ax.set_title(f"Weekly {metric}", fontsize=18, weight='bold')
    ax.set_xlabel("Day", fontsize=14)
    ax.set_ylabel(metric, fontsize=14)
    
    # Adjust font size for readability
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)

    # Show grid
    ax.grid(True)
    
    # Save the graph to a BytesIO object in memory
    buf = BytesIO()
    plt.savefig(buf, format='png', bbox_inches="tight")  # Adjusts plot area to fit labels
    plt.close()
    buf.seek(0)  # Ensure to seek to the start of the BytesIO object

    # Encode the image to base64
    image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
    
    # Return the base64 string to be embedded in HTML
    return f"data:image/png;base64,{image_base64}"



# Appointments main page route (Shows only logged-in patient's appointments)
@app.route('/appointments')
def appointments_page():
    blood_test_appointments = []
    doctor_appointments = []

    # Read the patient ID from the logpatient_id.txt file
    try:
        with open(log_patient_id_path, 'r') as file:
            patient_id = file.read().strip()  # Get the logged-in patient ID
    except FileNotFoundError:
        return "Patient ID log not found. Please log in again."

    # Read appointments from the CSV file
    try:
        with open(appointments_csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Check if the appointment belongs to the logged-in patient
                if row['patient_id'] == patient_id:
                    # Parse the appointment date and time
                    #appointment_datetime = datetime.strptime(f"{row['appointment_date']} {row['appointment_time']}", "%d-%m-%Y %H.%M")
                    appointment_datetime = datetime.strptime(f"{row['appointment_date']} {row['appointment_time']}", "%Y-%m-%d %H:%M")
                    
                    current_datetime = datetime.now()

                    # If the status is already 'Completed', keep it, otherwise calculate based on the date/time
                    if row['status'] != 'Completed':
                        if appointment_datetime >= current_datetime:
                            row['status'] = 'New'
                        else:
                            row['status'] = 'Expired'

                    # Append to the respective lists
                    if row['appointment_type'] == 'Blood Test':
                        blood_test_appointments.append(row)
                    elif row['appointment_type'] == 'Doctor Consultation':
                        doctor_appointments.append(row)
    except FileNotFoundError:
        pass

    # Pass the filtered appointments to the template
    return render_template('appointment_main_page.html', blood_test_appointments=blood_test_appointments, doctor_appointments=doctor_appointments)

# Define route for uploading blood test report and marking an appointment as completed
@app.route('/upload_blood_test_report/<appointment_id>', methods=['POST'])
def upload_blood_test_report(appointment_id):
    if 'report' not in request.files:
        flash('No file part')
        return redirect(url_for('nurse_dashboard'))

    file = request.files['report']
    if file.filename == '':
        flash('No selected file')
        return redirect(url_for('nurse_dashboard'))

    if file and allowed_file(file.filename):  # Ensure file is a PDF
        patient_id = request.form.get('patient_id')
        appointment_date = request.form.get('appointment_date')

        # Generate secure filename and save file
        filename = secure_filename(f"{patient_id}_{appointment_date}.pdf")
        filepath = os.path.join(blood_test_report_folder, secure_filename(filename))
        file.save(filepath)  # Save file in the specified directory

        # Update the appointment status to 'Completed' in the CSV file
        update_appointment_status(appointment_id, 'Completed')
        flash('Blood test report uploaded and appointment marked as completed.')
    else:
        flash('Invalid file format. Please upload a PDF file.')

    return redirect(url_for('nurse_dashboard'))

# Function to update the status of an appointment in the CSV file
def update_appointment_status(appointment_id, new_status):
    updated_appointments = []
    appointments_csv_path = os.path.abspath('appointments.csv')

    try:
        with open(appointments_csv_path, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['id'] == appointment_id:
                    row['status'] = new_status
                updated_appointments.append(row)

        # Write updated status back to CSV
        with open(appointments_csv_path, 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=updated_appointments[0].keys())
            writer.writeheader()
            writer.writerows(updated_appointments)
    except FileNotFoundError:
        print("Appointments CSV file not found.")


# Patient chatbot page
@app.route('/chatbot')
def chatbot():
    return render_template('chatbot_page.html')



@app.route('/health_form')
def health_form():
    # Get patient ID from logpatient_id.txt
    patient_id = get_patient_id_from_file()
    if not patient_id:
        return "Patient ID not found. Please log in again."

    # Initialize user data with default values
    user_data = {
        "phone": "N/A",
        "address": "N/A",
        "city": "N/A",
        "state": "N/A",
        "zip_code": "N/A",
        "dob": "N/A"
    }

    # Read user data from CSV
    try:
        df = pd.read_csv(csv_path)
        user = df[df['id'] == int(patient_id)]
        if not user.empty:
            user_data["phone"] = user.iloc[0].get('phone', "N/A")
            user_data["address"] = user.iloc[0].get('address', "N/A")
            user_data["city"] = user.iloc[0].get('city', "N/A")
            user_data["state"] = user.iloc[0].get('state', "N/A")
            user_data["zip_code"] = user.iloc[0].get('zip_code', "N/A")
            user_data["dob"] = user.iloc[0].get('dob', "N/A")
    except FileNotFoundError:
        return "User data file not found."

    # Pass user data to the template
    return render_template('health_google_sheets.html', user_data=user_data)

# Add appointment page
@app.route('/add_appointment')
def add_appointment():
    return render_template('add_appointment.html', google_maps_api_key=google_maps_api_key)

# Route to handle appointment submission and save to CSV
@app.route('/submit_appointment', methods=['POST'])
def submit_appointment():
    consultant_name = request.form['consultant_name']
    appointment_date = request.form['appointment_date']
    appointment_time = request.form['appointment_time']  # Capture the appointment time
    appointment_type = request.form['appointment_type']
    hospital_location = request.form['hospital_location']

    # Read the patient ID from logpatient_id.txt
    try:
        with open(log_patient_id_path, 'r') as file:
            patient_id = file.read().strip()  # Get the patient ID
    except FileNotFoundError:
        return "Patient ID log not found. Please log in again."

    # Generate a new appointment ID
    appointment_id = get_next_appointment_id()

    # Prepare the data to be saved
    appointment_data = {
        'id': appointment_id,
        'patient_id': patient_id,  # Use the patient ID from the log file
        'consultant_name': consultant_name,
        'appointment_type': appointment_type,
        'appointment_date': appointment_date,
        'appointment_time': appointment_time,  # Add this to the saved data
        'hospital_location': hospital_location,
        'status': 'New'  # When creating, mark as New by default
    }

    # Save the appointment data to CSV
    save_appointment_to_csv(appointment_data)

    # Redirect to appointments page
    return redirect(url_for('appointments_page'))



@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if request.method == 'POST':
        # Read the CSV file or create a new DataFrame if it’s empty
        try:
            df = pd.read_csv(csv_path)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame(columns=[
                'id', 'username', 'password', 'name', 'dob', 'weight', 'height', 'phone', 'gender', 
                'address', 'city', 'state', 'zip_code', 'insurance', 'role'
            ])

        # Get form data
        username = request.form['username']
        password = request.form['password']
        name = request.form['name']
        dob = request.form['dob']
        weight = request.form['weight']
        height = request.form['height']
        phone = request.form['phone']
        gender = request.form['gender']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        zip_code = request.form['zip_code']
        insurance = request.form['insurance']
        role = 'patient'

        # Check if the username already exists
        if not df[df['username'] == username].empty:
            return render_template('create_account.html', error="Username already exists")

        # Generate the next user ID
        if 'id' in df.columns and not df.empty:
            next_id = df['id'].max() + 1
        else:
            next_id = 1

        # Create new user DataFrame row
        new_user = pd.DataFrame([[
            next_id, username, password, name, dob, weight, height, phone, gender, 
            address, city, state, zip_code, insurance, role
        ]], columns=[
            'id', 'username', 'password', 'name', 'dob', 'weight', 'height', 'phone', 'gender', 
            'address', 'city', 'state', 'zip_code', 'insurance', 'role'
        ])

        # Append new user to existing DataFrame and save to CSV
        updated_df = pd.concat([df, new_user], ignore_index=True)
        updated_df.to_csv(csv_path, index=False)

        # Redirect to login page after account creation
        return redirect(url_for('login'))

    # Render the account creation form for GET requests
    return render_template('create_account.html')



# Function to read and get the next appointment ID
def get_next_appointment_id():
    try:
        with open(appointments_csv_path, 'r') as file:
            reader = csv.DictReader(file)
            appointments = list(reader)
            if appointments:
                last_id = int(appointments[-1]['id'])
                return last_id + 1
    except FileNotFoundError:
        return 1
    return 1

# Function to save appointment data to the CSV file
def save_appointment_to_csv(appointment_data):
    file_exists = os.path.isfile(appointments_csv_path)
    with open(appointments_csv_path, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['id', 'patient_id', 'consultant_name', 'appointment_type', 'appointment_date', 'appointment_time', 'hospital_location', 'status'])
        if not file_exists:
            writer.writeheader()
        writer.writerow(appointment_data)



def get_patient_id_from_file():
    """
    Function to read the patient_id from logpatient_id.txt.
    """
    patient_id_file = 'logpatient_id.txt'
    if os.path.exists(patient_id_file):
        with open(patient_id_file, 'r') as f:
            patient_id = f.read().strip()  # Strip any extra newline or spaces
            return patient_id
    else:
        return None  # Handle case if the file doesn't exist

# Route to download the saved PDF file
@app.route('/download_health_report')
def download_health_report():
    patient_id = get_patient_id_from_file()
    if not patient_id:
        return "Patient ID not found. Please log in again."

    # Check for the latest PDF report by the patient
    current_date = datetime.now().strftime("%Y-%m-%d")
    pdf_filename = f"{patient_id}_{current_date}.pdf"
    pdf_filepath = os.path.join(reports_directory, pdf_filename)

    if os.path.exists(pdf_filepath):
        return send_file(pdf_filepath, as_attachment=True)
    else:
        return "Health report PDF not found."
    

# Route to handle health form submission and store data in a text file

@app.route('/report_health_care', methods=['POST'])
def report_health_care():
    form_data = {
        'consultant': request.form.get('consultant'),
        'phone': request.form.get('phone'),
        'address': request.form.get('address'),
        'city': request.form.get('city'),
        'state': request.form.get('state'),
        'zip_code': request.form.get('zip_code'),
        'dob': request.form.get('dob'),
        'diagnosis': request.form.get('diagnosis'),
        'medicines': request.form.get('medicines'),
        'still_using': request.form.get('still_using')
    }

    # Save form data to a text file
    with open(txt_file_path, 'w') as f:
        for key, value in form_data.items():
            f.write(f'{key}: {value}\n')

    # Run model scripts without waiting for them to complete
    #subprocess.Popen(["streamlit", "run", "chat_pat_1.py"])
    #subprocess.Popen(["chainlit", "run", "model.py"])

    # Redirect to waiting page
    return render_template('chatbot_page.html')

import os

from flask import Flask, render_template, jsonify, redirect, url_for
import asyncio
from model import qa_bot, read_user_response


@app.route('/waiting')
def waiting_page():
    return render_template('waiting_page.html')

@app.route('/generate_report', methods=['POST'])
async def generate_report():
    question = read_user_response()  # Get the question from user responses
    answer = await qa_bot(question)  # Pass the question as an argument to qa_bot
    return jsonify({"success": True, "answer": answer})

form_data_path = 'medical_data.txt'  # Path to form data
user_responses_path = 'user_responses.txt'  # Path to user responses
log_patient_id_path = 'logpatient_id.txt'  # Path to patient ID
model_output_path = 'model_output.txt'  # Path to model output
health_reports_folder = os.path.join(os.getcwd(), 'health_reports')
os.makedirs(health_reports_folder, exist_ok=True)

# Route to display the report preview
@app.route('/preview_report')
def preview_report():
    try:
        # Retrieve patient ID and current date
        patient_id = get_patient_id_from_file()
        if patient_id is None:
            return "Patient ID not found. Please log in again."

        # Load form data
        form_data = {}
        with open(form_data_path, 'r') as f:
            for line in f:
                if ':' in line:
                    key, value = line.split(":", 1)
                    form_data[key.strip()] = value.strip()

        # Load user responses
        user_responses = {}
        with open(user_responses_path, 'r') as f:
            for line in f:
                if ':' in line:
                    question, answer = line.split(":", 1)
                    user_responses[question.strip()] = answer.strip()

        # Pass data to the HTML template
        return render_template(
            'report_health_care.html', 
            form_data=form_data,
            user_responses=user_responses,
            current_date=datetime.now().strftime("%Y-%m-%d"),
            patient_id=patient_id
        )
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Route to save the report as a .txt file
@app.route('/save_report_txt', methods=['POST'])
def save_report_txt():
    try:
        # Retrieve patient ID and create a file name
        patient_id = get_patient_id_from_file()
        if patient_id is None:
            return jsonify({"status": "error", "message": "Patient ID not found. Please log in again."})

        current_date = datetime.now().strftime("%Y-%m-%d")
        filename = f"Report_{patient_id}_{current_date}.txt"
        file_path = os.path.join(health_reports_folder, filename)

        # Generate the report content
        report_content = f"Medical Report\nPatient ID: {patient_id}\nDate: {current_date}\n\n"

        # Add form data
        with open(form_data_path, 'r') as f:
            report_content += "Patient Information\n" + f.read() + "\n"

        # Add user responses
        with open(user_responses_path, 'r') as ur:
            report_content += "User Responses\n" + ur.read() + "\n"

        # Add model output (not displayed on the webpage)
        with open(model_output_path, 'r') as mo:
            report_content += "Model Output\n" + mo.read() + "\n"

        # Write the report content to a .txt file
        with open(file_path, 'w') as file:
            file.write(report_content)

        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

def get_patient_id_from_file():
    try:
        with open(log_patient_id_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return None

def get_latest_report_file(patient_id):
    """
    Retrieve the path of the latest report file for a given patient ID.
    """
    health_reports_folder = os.path.join(os.getcwd(), 'health_reports')
    report_files = [
        f for f in os.listdir(health_reports_folder) 
        if f.startswith(f"Report_{patient_id}_") and f.endswith(".txt")
    ]
    
    if not report_files:
        return None  # No report found for this patient

    latest_report = max(report_files, key=lambda f: os.path.getmtime(os.path.join(health_reports_folder, f)))
    return os.path.join(health_reports_folder, latest_report)

@app.route('/view_patient_report')
def view_patient_report():
    try:
        # Retrieve the patient ID
        patient_id = get_patient_id_from_file()
        if patient_id is None:
            return "Patient ID not found. Please log in again."

        # Get the path to the latest report file
        report_file_path = get_latest_report_file(patient_id)
        if report_file_path is None:
            return "No report found for this patient."

        # Extract report data, excluding the "Model Output" section
        form_data, user_responses, model_output = {}, {}, None
        with open(report_file_path, 'r') as file:
            current_section = None
            for line in file:
                line = line.strip()
                if line.startswith("Model Output"):
                    current_section = "model_output"
                elif line.startswith("Patient Information"):
                    current_section = "form_data"
                elif line.startswith("User Responses"):
                    current_section = "user_responses"
                elif current_section == "form_data" and ':' in line:
                    key, value = line.split(":", 1)
                    form_data[key.strip()] = value.strip()
                elif current_section == "user_responses" and ':' in line:
                    question, answer = line.split(":", 1)
                    user_responses[question.strip()] = answer.strip()

        # Pass the data to the HTML template
        return render_template(
            'report_patient.html',
            form_data=form_data,
            user_responses=user_responses,
            current_date=datetime.now().strftime("%Y-%m-%d"),
            patient_id=patient_id
        )
    except Exception as e:
        return f"An error occurred: {str(e)}"

@app.route('/view_doctor_patient_report/<patient_id>')
def view_doctor_patient_report(patient_id):
    try:
        # Directory where health reports are stored
        health_reports_folder = os.path.join(os.getcwd(), 'health_reports')

        # Fetch all reports for the specific patient and select the latest one
        report_files = [f for f in os.listdir(health_reports_folder) 
                        if f.startswith(f"Report_{patient_id}_") and f.endswith(".txt")]
        if not report_files:
            return f"No report found for patient ID {patient_id}."

        # Sort files by date to get the latest report
        latest_report_file = max(report_files, key=lambda f: datetime.strptime(f.split("_")[-1].replace(".txt", ""), "%Y-%m-%d"))
        latest_report_path = os.path.join(health_reports_folder, latest_report_file)

        # Initialize dictionaries to hold form data and user responses
        form_data, user_responses = {}, {}
        model_output = ""

        # Read the content of the latest report file
        with open(latest_report_path, 'r') as file:
            current_section = None
            for line in file:
                line = line.strip()
                if line.startswith("Model Output"):
                    current_section = "model_output"
                elif line.startswith("Patient Information"):
                    current_section = "form_data"
                elif line.startswith("User Responses"):
                    current_section = "user_responses"
                elif current_section == "form_data" and ':' in line:
                    key, value = line.split(":", 1)
                    form_data[key.strip()] = value.strip()
                elif current_section == "user_responses" and ':' in line:
                    question, answer = line.split(":", 1)
                    user_responses[question.strip()] = answer.strip()
                elif current_section == "model_output":
                    model_output += line + "\n"

        # Render the report template for doctor view
        current_date = datetime.now().strftime("%Y-%m-%d")
        return render_template(
            'report_doctor.html',
            form_data=form_data,
            user_responses=user_responses,
            model_output=model_output,
            current_date=current_date,
            patient_id=patient_id
        )
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"
    
    
    
    
if __name__ == '__main__':
    app.run(debug=False)