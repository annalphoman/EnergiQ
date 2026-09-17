"""
EnergiQ AI Pipeline Master Runner.

Executes the complete machine learning workflow end-to-end:
1. Synthetic Data Generation -> ai/data/input.csv
2. Preprocessing & Feature Engineering -> ai/data/cleaned_data.csv
3. Anomaly Detection (Isolation Forest) -> ai/outputs/anomaly_output.csv & ai/models/anomaly_model.pkl
4. Energy Forecasting (Random Forest) -> ai/outputs/prediction_output.csv & ai/models/prediction_model.pkl
"""

import sys
import os

# Ensure local ai package modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from generate_data import generate_synthetic_data
from preprocess import preprocess_data
from anomaly_detection import run_anomaly
from prediction import run_pred


def run_pipeline():
    """Executes all AI pipeline stages sequentially."""
    print("=" * 60)
    print("⚡ Starting EnergiQ AI Pipeline Execution")
    print("=" * 60)

    print("\n[Stage 1/4] Generating Synthetic Data...")
    generate_synthetic_data()

    print("\n[Stage 2/4] Preprocessing Data & Engineering Features...")
    preprocess_data()

    print("\n[Stage 3/4] Running Anomaly Detection (Isolation Forest)...")
    run_anomaly()

    print("\n[Stage 4/4] Forecasting Next-Day Energy Consumption (Random Forest)...")
    run_pred()

    print("\n" + "=" * 60)
    print("🎉 EnergiQ AI Pipeline Executed Successfully!")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
