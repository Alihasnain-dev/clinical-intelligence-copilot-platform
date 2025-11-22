# The AI-Powered Clinical Intelligence Platform

## 📋 Executive Summary
The **Clinical Intelligence Platform** is a hybrid AI system designed to augment clinical decision-making. It unifies **predictive analytics** (for risk scoring and diagnostics) with **generative AI** (for evidence-based reasoning) into a single, coherent operational copilot.

By bridging the gap between structured operational data and unstructured medical knowledge, this platform enables healthcare providers to:
- **Predict Patient Risks:** Forecast appointment no-shows using machine learning on EMR data.
- **Analyze Medical Imaging:** Detect pathologies in X-rays using a fine-tuned ResNet50 computer vision model.
- **Access Clinical Knowledge:** Interact with a RAG (Retrieval-Augmented Generation) system grounded in medical guidelines and research.

---

## 🏗️ Architecture Overview
The solution is built on a modern **Azure Cloud** stack, leveraging containerized microservices and managed AI services.

### **1. Data & Infrastructure Layer (Terraform)**
- **Azure Blob Storage:** Data lake for raw medical images (DICOM/PNG) and PDF knowledge base.
- **Azure PostgreSQL (Flexible Server):** Relational store for structured patient records and appointment logs.
- **Azure AI Search:** Vector database for semantic retrieval of clinical documents.
- **Azure OpenAI:** GPT-4o integration for synthesizing clinical answers with citations.

### **2. Intelligence Layer (Hybrid Brain)**
- **Predictive Brain (Operations):** LightGBM model for no-show risk scoring based on demographics and history.
- **Visual Brain (Diagnostics):** PyTorch-based Computer Vision model (ResNet50) for pathology detection.
- **Generative Brain (Knowledge):** RAG pipeline using LangChain to index and retrieve medical context.

### **3. Application Layer**
- **FastAPI Backend:** Serves AI models via RESTful endpoints.
- **Streamlit Dashboard:** A unified frontend for clinicians to view risks, upload scans, and chat with the AI assistant.

---

## 🚀 Getting Started

### Prerequisites
- **Docker & Docker Compose** (for local orchestration)
- **Python 3.9+** (for local development)
- **Azure Subscription** (with access to OpenAI and Cognitive Services)
- **Terraform** (for infrastructure deployment)

### 1. Environment Configuration
This project uses a secure `.env` file to manage credentials.
1. Copy the example template:
   ```bash
   cp example.env .env
   ```
2. Populate `.env` with your Azure credentials (obtained after Terraform deployment).

### 2. Deployment (Infrastructure)
Navigate to the `terraform/` directory to provision the Azure resources:
```bash
cd terraform
terraform init
terraform apply
```
> **Note:** This will create the Resource Group, Storage Accounts, Database, and AI Services.

### 3. Data Ingestion & Training
Once infrastructure is ready, hydrate the data stores and train the models:
```bash
# Upload data to Azure Blob
python scripts/upload_csv_to_azure.py

# Train the No-Show Prediction Model
jupyter notebook notebooks/01_train_no_show_model.ipynb

# Train/Fine-tune the Vision Model
jupyter notebook notebooks/02_train_vision_model.ipynb
```

### 4. Running the Application
Use Docker Compose to spin up the full stack locally:
```bash
docker-compose up --build
```
- **Frontend (Streamlit):** [http://localhost:8501](http://localhost:8501)
- **Backend API (FastAPI):** [http://localhost:5000/docs](http://localhost:5000/docs)

---

## 🖥️ Usage Guide

### **Scenario 1: Patient Risk Assessment**
1. Navigate to the **"Patient Operations"** sidebar.
2. Input patient demographics (Age, Neighbourhood, Conditions).
3. Click **"Calculate Risk"** to receive a No-Show Probability score.

### **Scenario 2: Diagnostic Imaging**
1. Upload a Chest X-Ray (PNG/JPEG).
2. Click **"Run AI Analysis"**.
3. View predicted pathologies (e.g., Pneumonia, Effusion) with confidence scores.

### **Scenario 3: Clinical Assistant (RAG)**
1. Use the chat interface to ask questions like *"What is the recommended treatment for Pneumonia?"*
2. The system retrieves relevant snippets from your uploaded medical PDF knowledge base and generates an answer using GPT-4.

---

## 🛠️ Tech Stack

| Component | Technology |
| :--- | :--- |
| **Languages** | Python, HCL (Terraform) |
| **Frontend** | Streamlit |
| **Backend** | FastAPI, Uvicorn |
| **ML Frameworks** | PyTorch, Scikit-Learn, LightGBM |
| **LLM Orchestration** | LangChain, Azure OpenAI |
| **Infrastructure** | Azure (Blob, PostgreSQL, AI Search), Docker |

---

## 🔒 Security & Compliance
- **Secrets Management:** No hardcoded keys; all credentials loaded via environment variables.
- **Data Privacy:** Designed with HIPAA compliance in mind (data encryption at rest and in transit).
- **Infrastructure as Code:** reproducible and auditable environments via Terraform.

---

## 🤝 Contributing
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to the branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.

## 📄 License
Distributed under the MIT License. See `LICENSE` for more information.
