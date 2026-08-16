# 🔍 Fake Job Posting Detector

A machine learning application that detects potentially fraudulent job postings using **TF-IDF text features combined with tabular job-posting features and Logistic Regression**.

The project includes a Streamlit dashboard where users can enter job-posting information and receive a fraud probability, classification, and feature-based explanation.

## 🚀 Features

- Detects whether a job posting is likely **Fraud** or **Not Fraud**
- Produces a **fraud probability score**
- Uses both **text and structured/tabular features**
- TF-IDF based text representation
- Logistic Regression classification
- Handles missing values using missingness indicators
- Supports categorical job-posting fields
- Provides feature-based explanations for predictions
- Streamlit dashboard with a dark UI
- Auto-fill helper for pasted job postings
- Model performance dashboard

## 🧠 Machine Learning Approach

The detector uses a text + tabular feature fusion approach.

### Text Features

The following fields are combined into one text representation:

- Job title
- Company profile
- Job description
- Requirements
- Benefits

The combined text is transformed using a trained **TF-IDF vectorizer**.

### Tabular Features

The model also uses structured features such as:

- Employment type
- Required experience
- Required education
- Industry
- Function
- Department
- Salary range
- Missing-value indicators

Categorical variables are one-hot encoded before being combined with the TF-IDF representation.

### Model

The final feature representation is created by horizontally combining the TF-IDF features and tabular features. A trained **Logistic Regression** model then calculates the probability of fraud.

The prediction rule is:

```text
Fraud probability >= 0.50 → Fraud
Fraud probability < 0.50  → Not Fraud
```

The prediction pipeline and probability calculation are implemented in `predict.py`.

## 📊 Model Performance

The Streamlit dashboard reports the following held-out test-set metrics:

| Metric | Result |
|---|---:|
| PR-AUC | 0.89 |
| Precision (Fraud) | 61% |
| Recall (Fraud) | 90% |

These metrics are displayed directly in the application dashboard.

## 🖥️ Streamlit Dashboard

The project includes an interactive Streamlit interface called **Fake Job Posting Detector**.

Users can enter:

- Job title
- Employment type
- Required experience
- Required education
- Industry
- Department
- Company profile
- Job description

After checking a posting, the dashboard displays:

- Fraud / Not Fraud verdict
- Fraud probability
- Top contributing features
- Model performance indicators

The interface also includes an auto-fill helper that extracts basic fields such as title, employment type, experience level, and education from pasted job-posting text.

## 📁 Project Structure

```text
fake-job-posting-detector/
│
├── data/
│
├── models/
│   ├── logistic_regression_model.pkl
│   ├── tfidf_vectorizer.pkl
│   └── tabular_feature_columns.pkl
│
├── notebook/
│   └── eda.ipynb
│
├── extraction_utils.py
├── predict.py
├── streamlit_app.py
├── fake_job_postings.csv
├── requirements.txt
└── README.md
```

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/fake-job-posting-detector.git
cd fake-job-posting-detector
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it on Windows:

```bash
.venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

## ▶️ Run the Application

The Streamlit application can be started with:

```bash
streamlit run streamlit_app.py
```

The application requires the trained model files inside the `models/` directory.

The application expects these files:

```text
models/
├── logistic_regression_model.pkl
├── tfidf_vectorizer.pkl
└── tabular_feature_columns.pkl
```

If these model files are missing, the application instructs you to run the training notebook first.

## 🔎 Prediction Pipeline

```text
Job Posting
     ↓
Input / Pasted Text
     ↓
Field Extraction
     ↓
Text Preprocessing
     ↓
TF-IDF Features
     +
Tabular Features
     ↓
Feature Fusion
     ↓
Logistic Regression
     ↓
Fraud Probability
     ↓
Fraud / Not Fraud
     ↓
Feature-Based Explanation
```

## 🧩 Main Components

### `extraction_utils.py`

Contains heuristic extraction functions for identifying fields from pasted job-posting text, including employment type, experience level, education, title, and description.

### `predict.py`

Contains the `FraudDetector` class. It loads the trained Logistic Regression model, TF-IDF vectorizer, and tabular feature columns, constructs prediction features, calculates fraud probability, and generates the top contributing features.

### `streamlit_app.py`

Provides the interactive Streamlit dashboard and connects the user interface to the fraud detection model.

### `fake_job_postings.csv`

Dataset used by the project.

### `notebook/eda.ipynb`

Notebook referenced by the application for the model training workflow and generation of the required model files.

## 🛠️ Technologies Used

- Python
- Pandas
- NumPy
- Scikit-learn
- SciPy
- Joblib
- Streamlit
- Jupyter / IPython
- TF-IDF
- Logistic Regression

## 📦 Dependencies

The project requirements include:

```text
pandas
numpy
scikit-learn
scipy
joblib
ipykernel
streamlit
```

## ⚠️ Limitations

This system provides a machine-learning based prediction and should not be treated as definitive proof that a job posting is fraudulent.

The quality of predictions depends on the training data, feature representation, and trained model.

The pasted-text auto-fill functionality is heuristic and should be reviewed before submitting a posting for prediction.

## 🔮 Possible Improvements

- Add additional machine learning models for comparison
- Improve text preprocessing and semantic representation
- Add cross-validation and model comparison
- Add calibration for probability estimates
- Expand explainability with SHAP or similar methods
- Add URL-based job-posting extraction
- Deploy the Streamlit application online
- Add automated model monitoring

## 👨‍💻 Author

**Dipan Majumdar**

B.Sc. Data Science Student

GitHub: https://github.com/MAJUMDARcu
