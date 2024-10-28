



# EVO_1.0+ Health Care System

![EVO_1.0+ Logo](https://github.com/Ahamedthaiyub/EVO-1.0_openvino/blob/main/Green%20and%20Orange%20Simple%20Medical%20Logo(1).png)

---

## Overview

EVO_1.0+ is a comprehensive AI-powered healthcare monitoring system designed to track and analyze patient vitals such as BPM (Beats per Minute) and oxygen levels, alongside emotional data through camera-based analysis. This solution automates patient-doctor interactions, enabling timely interventions and enhancing patient well-being through accurate, real-time insights.

---

## System Flow

![System Flowchart](https://github.com/user-attachments/assets/0e5dbe14-426e-4e81-bd6e-c4cf3b6e6b03)

The flowchart above illustrates the data flow within EVO_1.0+, demonstrating how patient data is processed and analyzed to generate actionable reports and personalized recommendations.

---

## Key Features

- **Emotion and Vitals Monitoring**: Capture real-time emotional states via camera and retrieve vital data (BPM, oxygen levels) from connected devices.
- **Automated Reporting**: Daily reports generated for doctors and patients, summarizing vital data and emotional insights.
- **AI-Based Recommendations**: Suggests medication or alerts doctors for further action based on patient data.
- **Doctor-Patient Interaction**: Enables patients to view reports, describe symptoms, and book appointments with specialists directly through the platform.

---

## System Performance

### CPU vs. NPU Performance Comparison

**CPU Performance**  
![CPU Performance](https://github.com/Ahamedthaiyub/EVO-1.0_openvino/blob/main/WhatsApp%20Image%202024-10-27%20at%2022.25.46.jpeg)

**NPU Performance**  
![NPU Performance](https://github.com/Ahamedthaiyub/EVO-1.0_openvino/blob/main/WhatsApp%20Image%202024-10-27%20at%2022.31.02.jpeg)


![WhatsApp Image 2024-10-28 at 00 10 26](https://github.com/user-attachments/assets/94a74f3b-2820-4dab-8b99-e89a62419687)

Switching from CPU to NPU for specific tasks significantly improved processing speeds and overall system efficiency, allowing EVO_1.0+ to deliver real-time insights more effectively.

---

## Tech Stack

- **AI Model Deployment**: OpenVINO
- **Deep Learning Frameworks**: Torch, Transformers
- **Data Processing**: BERT Tokenizer, Faiss-CPU, PyPDF
- **Web Frameworks**: Streamlit, Chainlit
- **Additional Libraries**: Langchain, Accelerate, BitsAndBytes, CTransformers, Huggingface-hub

---

## Installation

> Due to the large size of the project (5GB+), GitHub does not support hosting the entire codebase. Instead, download the necessary files from the provided Google Drive links.

- **Main Application Files**: [Download here](https://drive.google.com/drive/folders/1whe8bFdKN5dNOIB_PYTTPqM8_JTxeQEX?usp=sharing)

- **Chatbot Backend**: [Download here](https://drive.google.com/drive/folders/1zYYp1ZbeRzo1zfxk4TU5pyD1pXKqJnBT?usp=sharing)

### Steps to Install

1. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   > **Note:** Given the large number of dependencies, please manually install any additional packages if prompted by the application.

2. **Ensure OpenVINO is installed** for model inference:
   - [Install OpenVINO](https://docs.openvino.ai/latest/openvino_docs_install_guides_installing_openvino.html)

---

## Running the Project

### 1. Backend (Chatbot)

After downloading the backend files from Google Drive, navigate to the backend directory and start the chatbot by running:

```bash
chainlit run model.py -w
```

### 2. Main Application

Navigate to the `health` folder in the main application directory and run:

```bash
cd health
python app.py
```

---

## Usage

- Once the application is running, EVO_1.0+ will capture real-time data from connected devices (e.g., smartwatch and camera).
- Data is processed, analyzed, and securely stored in the patient database.
- Automated daily reports, medication recommendations, and alerts are generated for both doctors and patients.

---

## System Architecture

![System Architecture](https://github.com/user-attachments/assets/6ac0fb8f-dd6e-4d5f-b2b0-9c8d0d878f16)

This diagram provides a high-level overview of the system’s architecture and data flow, showcasing the interaction between various components of the EVO_1.0+ system.

---

## Contribution Guidelines

We welcome contributions to EVO_1.0+! However, due to the large file size, please coordinate on specific changes and test smaller parts of the system before submitting pull requests. Follow standard GitHub practices:



---

## Downloads

- **Chatbot Backend**: [Download here](https://drive.google.com/drive/folders/1whe8bFdKN5dNOIB_PYTTPqM8_JTxeQEX?usp=sharing)
- **Main Application Files**: [Download here](https://drive.google.com/drive/folders/1zYYp1ZbeRzo1zfxk4TU5pyD1pXKqJnBT?usp=sharing)

---

## Contributors

- **Ahamed Thaiyub A** – Lead Developer
- **Jeyasundar R** – Developer
- **Aditya RS** – Developer

---

## Contact

For inquiries, please reach out to [ahamedthaiyub27@gmail.com](mailto:ahamedthaiyub27@gmail.com).

