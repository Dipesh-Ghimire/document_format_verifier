# Document Format Verifier
### **NLP Internship Evaluation Task**

This project implements a **Document Format Verifier**, which analyzes text-based PDFs to extract metadata and verify formatting compliance. The tool leverages a **fine-tuned BERT model** for metadata extraction and **NLP techniques & regex** for format validation. The BERT model has been fine-tuned on a small annotated dataset for metadata extraction, meaning its accuracy may vary when different PDFs are analyzed. If higher accuracy is required, users can provide their own dataset and utilize the modular and pipeline-based ML architecture to fine-tune the model accordingly. A **Streamlit** application is also provided to visualize the results.

---

## **Modular and End-to-End Pipeline-based ML Architecture**
This project follows a **Modular and Pipeline-based ML Architecture**, ensuring efficiency in **Machine Learning workflows**:
- **Scalability**: The architecture allows seamless integration of new ML models, metadata extraction techniques, or formatting rules without affecting existing components.
- **Maintainability**: The structured separation of ML pipelines, including **data ingestion, preprocessing, training, and inference**, ensures that modifications to one stage do not disrupt the entire system.
- **Reusability**: Individual ML components (such as the **BERT-based metadata extraction** and **format verification** models) can be reused across different projects or datasets with minimal modifications.
- **Adaptability for Fine-Tuning**: Since the **BERT model** was fine-tuned on a small annotated dataset, users seeking higher accuracy can provide their own dataset and re-execute the **training pipeline** to optimize performance for their specific use case.
- **Production-Readiness**: Logging, exception handling, and modularized ML components make the system **deployment-ready** for real-world applications, supporting both research and practical use cases.

---

## **Project Structure**
This project follows a **modular and pipeline-based ML architecture**, making it easy to scale and maintain.

```
document_format_verifier/
│── app.py                           # Streamlit Web App for UI interaction
│── artifacts/                        # Stores trained models and datasets
│   ├── fine_tuned_bert_ner/          # Directory for fine-tuned BERT model
│   ├── merged_dataset.json           # Processed dataset used for training
│   ├── tokenized_test_data.pkl       # Tokenized test dataset
│   ├── tokenized_train_data.pkl      # Tokenized training dataset
│── dataset/                          # Contains datasets for training
│   ├── annoted_dataset/              # Labeled dataset for metadata extraction
│   │   ├── academic_report.json
│   │   ├── corporate_report.json
│   │   ├── custom.json
│   │   ├── thesis_report.json
│   ├── pdfs/                         # Sample PDFs for testing
│── LICENSE                           # Project license
│── notebooks/                        # Jupyter Notebooks for experimentation
│   ├── fine_tune_bert.ipynb          # Notebook for fine-tuning BERT
│   ├── l_e.ipynb                     # Additional exploratory notebook
│── README.md                         # Project documentation
│── requirements.txt                   # List of dependencies
│── setup.py                          # Package setup script
│── src/                              # Main source code directory
│   ├── components/                    # Core ML processing components
│   │   ├── data_ingestion.py          # Handles loading PDFs and JSON files
│   │   ├── data_transformation.py     # Prepares data for model training
│   │   ├── extraction/                # Metadata extraction utilities
│   │   ├── model_trainer.py           # Fine-tunes the BERT model
│   ├── exception.py                   # Custom error handling
│   ├── logger.py                      # Logging setup for debugging
│   ├── pipelines/                     # ML pipelines for processing
│   │   ├── format_verifier_pipeline.py  # Runs document format validation
│   │   ├── metadata_extraction_pipeline.py # Extracts metadata from documents
│   │   ├── train_pipeline.py          # Training pipeline for the model
│   │   ├── utils.py                   # Utility functions
│   ├── utils.py                        # General helper functions
```

---

## **Features**
- **Metadata Extraction**: Extracts:
  - **Author Name**
  - **Organization**
  - **Roll Number**
  - **Supervisor Name**
  - **Document Submission Date**
- **Formatting Verification**: Checks for compliance with:
  - **Table of Contents (ToC)**
  - **List of Figures (LoF)**
  - **Abbreviations Section**
  - **Font Type & Size**
  - **Header Fonts**
  - **Margins**
  - **Text Alignment**
  - **Figure/Table Placement**
  - **References Formatting**
- **JSON Output**: The extracted metadata and formatting assessment results are generated in JSON format.
- **Streamlit UI**: A user-friendly interface to upload PDFs and visualize results.

---

## **Installation & Setup**

### **1. Clone GitHub Repository**
```bash
git clone https://github.com/Dipesh-Ghimire/document_format_verifier.git
cd document_format_verifier
```

### **2. Create & Activate Virtual Environment**
#### **Linux/macOS**
```bash
python3.12 -m venv nlp_env
source nlp_env/bin/activate
```
#### **Windows**
```powershell
python3.12 -m venv nlp_env
.\nlp_env\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Download Fine-tuned BERT Model**
#### **Linux/macOS**
```bash
mkdir -p artifacts/fine_tuned_bert_ner
huggingface-cli download djdipesh/bert_metadata_extractor --local-dir artifacts/fine_tuned_bert_ner
```
#### **Windows**
```powershell
mkdir artifacts\fine_tuned_bert_ner
huggingface-cli download djdipesh/bert_metadata_extractor --local-dir artifacts\fine_tuned_bert_ner
```

---

## **Running the Streamlit Web App**
Launch the Streamlit interface:
```bash
streamlit run app.py
```
- The application allows users to upload PDFs and view extracted metadata and formatting analysis.

---

## **Contributions**
Feel free to contribute via pull requests on [GitHub](https://github.com/Dipesh-Ghimire/document_format_verifier).

---

