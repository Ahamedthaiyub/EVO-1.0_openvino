<!DOCTYPE html>
<html>
<body>
    <h1>EVO_1.0+ Health Care System</h1>
    <!-- Logo Section -->
    <h2>Logo</h2>
    
![Green and Orange Simple Medical Logo](https://github.com/user-attachments/assets/260c2d81-0c16-4d33-ad60-faf3682ac6e6)
    
<h2>Overview</h2>
    <p>
        EVO_1.0+ is an AI-powered healthcare monitoring system designed to track patients' vitals like BPM (Beats per Minute) 
        and oxygen levels, analyze emotional data through cameras, and suggest appropriate treatments. 
        The system is fully automated, providing seamless interaction between patients and doctors, 
        with a focus on timely interventions and patient well-being.
    </p>
    <!-- Flowchart Section -->
    <h2>System Flowchart</h2>

![Picture1](https://github.com/user-attachments/assets/1d44e3e8-e3bf-4ef6-8be1-375f73004578)
<h2> Compilation of <B>openVINO model</B></h2>

![image](https://github.com/user-attachments/assets/dbe48a72-a692-4367-8e0b-6a61f6061aa7)
    <h2>Intel Ultra Processor Series 2(Intel AI Pc)</h2>
    ![image](https://github.com/user-attachments/assets/95078fad-c8bd-452a-aad4-ac4a285a0e8f)
    <h3>CPU vs NPU Performance Comparison<h3>
    ![WhatsApp Image 2024-10-27 at 22 31 24_06d87ff4](https://github.com/user-attachments/assets/4cab4674-9f03-4b1d-bda2-6a6c411dcec6)
    ![WhatsApp Image 2024-10-27 at 22 25 48_96a49ec9](https://github.com/user-attachments/assets/e5c863e8-6ce9-4d66-a6a3-ce5dc0731da4)
    <p>The switch from CPU to NPU has increased performance significantly.</p>
    <h2>Features</h2>
    <ul>
        <li><strong>Emotion and Vitals Monitoring:</strong> Capture emotional data via camera and retrieve BPM and oxygen levels from a connected watch.</li>
        <li><strong>Automated Reporting:</strong> Data is stored and analyzed to generate daily reports for doctors and patients.</li>
        <li><strong>AI-based Recommendations:</strong> The system analyzes patient inputs and generates medication suggestions when required.</li>
        <li><strong>Doctor-Patient Interaction:</strong> Patients can view reports, describe illnesses, and book appointments with specialists via the platform.</li>
    </ul>
    <h2>Tech Stack</h2>
    <ul>
        <li>OpenVINO</li>
        <li>Torch</li>
        <li>BERT Tokenizer</li>
        <li>Langchain</li>
        <li>PyPDF</li>
        <li>Accelerate</li>
        <li>BitsAndBytes</li>
        <li>CTransformers</li>
        <li>Faiss-CPU</li>
        <li>Huggingface-hub</li>
        <li>Transformers</li>
        <li>Chainlit</li>
        <li>Streamlit</li>
    </ul>
    <h2>Installation</h2>
    <ol>
        <li>Install the required packages:
            <pre><code>pip install -r requirements.txt</code></pre>
        </li>
        <li>Ensure that you have installed OpenVINO for model inference:
            <ul>
                <li><a href="https://docs.openvino.ai/" target="_blank">Install OpenVINO</a></li>
            </ul>
        </li>
    </ol>
    <h2>Running the Project</h2>
    <ol>
        <li>Run the main application:
            <pre><code>python app.py</code></pre>
        </li>
        <li>The system will initialize, retrieve data from patient devices, and start monitoring vitals.</li>
    </ol>
    <h2>Usage</h2>
    <ul>
        <li>After running the application, the system will capture real-time data from connected devices (watch and camera).</li>
        <li>Data will be processed and stored in the patient database.</li>
        <li>The system will generate report doctors, suggesting potential medications or alerting the doctor for further analysis.</li>
    </ul>
    <h2>Contributions</h2>
    <p>
    about team.
    my name Aditya Krishna RS
    </p>

</body>
</html>
