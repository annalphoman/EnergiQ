# EnergiQ - AI & Machine Learning Module

This directory contains the AI and Machine Learning components of **EnergiQ**, providing synthetic data generation, preprocessing, anomaly detection, and energy forecasting capabilities.

---

## 📁 Directory Structure

```text
ai/
├── main.py                  # Master entry point script to run end-to-end pipeline
├── generate_data.py         # Synthetic data generation module
├── preprocess.py            # Data cleaning and feature engineering module
├── anomaly_detection.py     # Isolation Forest anomaly detection model
├── prediction.py            # Random Forest next-day energy forecasting model
├── README.md                # AI module documentation
├── data/                    # Processed datasets
│   ├── input.csv
│   └── cleaned_data.csv
├── models/                  # Serialized machine learning models (.pkl)
│   ├── anomaly_model.pkl
│   └── prediction_model.pkl
└── outputs/                 # Pipeline inference outputs
    ├── anomaly_output.csv
    └── prediction_output.csv
```

---

## 🚀 Quick Start

### 1. Requirements

Ensure required Python packages are installed:

```bash
pip install pandas numpy scikit-learn joblib
```

### 2. Run Entire AI Pipeline

Run the full automated end-to-end pipeline with one command:

```bash
python3 ai/main.py
```

---

## ⚙️ Running Individual Modules

You can also run any module independently:

- **Generate Data:**
  ```bash
  python3 ai/generate_data.py
  ```
- **Preprocess Data:**
  ```bash
  python3 ai/preprocess.py
  ```
- **Detect Anomalies:**
  ```bash
  python3 ai/anomaly_detection.py
  ```
- **Predict Consumption:**
  ```bash
  python3 ai/prediction.py
  ```

---

## 📊 Outputs Summary

- **`outputs/anomaly_output.csv`**: Contains flagged high consumption spikes with `actual_power_kw`, `expected_power_kw`, and `anomaly_score`.
- **`outputs/prediction_output.csv`**: Contains forecasted next-day kWh consumption per building and room location (`predicted_next_day_kwh` vs `historical_last_day_kwh`).
