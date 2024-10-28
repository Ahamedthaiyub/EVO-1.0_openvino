

# EVO_1.0+ Health Care System

![EVO_1.0+ Logo](https://github.com/Ahamedthaiyub/EVO-1.0_openvino/blob/main/Green%20and%20Orange%20Simple%20Medical%20Logo(1).png)

---

## Overview

EVO_1.0+ is an AI-powered healthcare monitoring system designed to track and analyze patient vitals, including BPM (Beats per Minute) and oxygen levels, along with emotional data through camera-based analysis. This system automates interactions between patients and doctors, ensuring timely interventions and prioritizing patient well-being.

---

## System Flowchart

![image](https://github.com/user-attachments/assets/0e5dbe14-426e-4e81-bd6e-c4cf3b6e6b03)


The above flowchart illustrates the data flow within EVO_1.0+, showing how patient data is processed and analyzed to generate reports and recommendations.

---

## Key Features

- **Emotion and Vitals Monitoring**: Capture emotional states via a camera and retrieve BPM and oxygen levels from connected devices.
- **Automated Reporting**: Generates daily reports for doctors and patients, summarizing vital data and emotional trends.
- **AI-Based Recommendations**: Analyzes patient data and provides medication suggestions or alerts doctors for further action if needed.
- **Doctor-Patient Interaction**: Allows patients to view reports, describe symptoms, and book appointments with specialists.

---

## System Performance

**CPU vs. NPU Comparison**  
![CPU Performance](https://github.com/Ahamedthaiyub/EVO-1.0_openvino/blob/main/WhatsApp%20Image%202024-10-27%20at%2022.25.46.jpeg)
![ NPU Performance](https://github.com/Ahamedthaiyub/EVO-1.0_openvino/blob/main/WhatsApp%20Image%202024-10-27%20at%2022.31.02.jpeg)


The switch from CPU to NPU for specific tasks has significantly improved processing speeds and overall system efficiency, enabling EVO_1.0+ to deliver real-time insights more effectively.

---

## Tech Stack

- **AI Model Deployment**: OpenVINO
- **Deep Learning Frameworks**: Torch, Transformers
- **Data Processing**: BERT Tokenizer, Faiss-CPU, PyPDF
- **Web Frameworks**: Streamlit, Chainlit
- **Additional Libraries**: Langchain, Accelerate, BitsAndBytes, CTransformers, Huggingface-hub

---

## Installation

Due to the large size of the project (5GB+), GitHub does not support direct download or hosting of the entire codebase. Instead, you can download the necessary files from the following Google Drive links:

- **Chatbot Backend**: [Download here](https://drive.google.com/drive/folders/1zYYp1ZbeRzo1zfxk4TU5pyD1pXKqJnBT?usp=sharing)
- **Main Application Files**: [Download here](https://drive.google.com/drive/folders/1whe8bFdKN5dNOIB_PYTTPqM8_JTxeQEX?usp=sharing)

After downloading, navigate to the project directories as instructed below.

1. **Install the required packages**:
   ```bash
   pip install -r requirements.txt
   ```
   
   > **Note:** Given the large number of dependencies, please manually install any additional packages as they are requested by the application.

2. **Ensure OpenVINO is installed** for model inference:
   - [Install OpenVINO](https://docs.openvino.ai/latest/openvino_docs_install_guides_installing_openvino.html)

---

## Running the Project

### 1. Backend (Chatbot)

After downloading the backend files from Google Drive, navigate to the directory and start the chatbot backend by running:

```bash
chainlit run model.py -w
```

### 2. Main Application

Navigate to the health folder from the downloaded main application files and run:

```bash
cd health
python app.py
```

---

## Usage

- Once the application is running, EVO_1.0+ will capture real-time data from connected devices (e.g., watch and camera).
- Data is processed, analyzed, and stored in the patient database.
- Daily reports, medication suggestions, and alerts are automatically generated for doctors and patients.

---

## System Flow and Architecture

Here’s a high-level view of the system architecture and data flow:

![image](https://github.com/user-attachments/assets/6ac0fb8f-dd6e-4d5f-b2b0-9c8d0d878f16)


---

## Contribution

We welcome contributions! However, due to the large file size, please coordinate on specific changes and test smaller parts of the system. Standard GitHub practices like forking, branching, and pull requests apply.

---

## Downloads

- **Chatbot Backend**: [Download here](https://drive.google.com/drive/folders/1zYYp1ZbeRzo1zfxk4TU5pyD1pXKqJnBT?usp=sharing)
- **Main Application Files**: [Download here](https://drive.google.com/drive/folders/1whe8bFdKN5dNOIB_PYTTPqM8_JTxeQEX?usp=sharing)

---

## Contributors

- **AHAMED THAIYUB A** – Lead Developer
- **JEYASUNDAR R**
- **ADITYA RS**

---


---

## Contact

For inquiries, please reach out to [Your Email](ahamedthaiyub27@gmail.com).

---

Replace any placeholder links or paths as needed. This README.md includes specific guidance about the limitations of GitHub for large files and directs users to Google Drive for downloads.
