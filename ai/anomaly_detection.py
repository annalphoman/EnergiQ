"""
Anomaly Detection Module for EnergiQ Energy Monitoring System.

Uses Isolation Forest unsupervised learning to detect abnormal energy consumption patterns
and flags suspicious usage spikes per room and equipment type.
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


def run_anomaly(
    data_file: str = None,
    output_file: str = None,
    model_file: str = None,
    contamination: float = 0.03
) -> pd.DataFrame:
    """
    Trains Isolation Forest anomaly detector and saves detected anomalies.

    Args:
        data_file: Path to cleaned CSV dataset.
        output_file: Path to save anomaly detection output CSV.
        model_file: Path to save trained IsolationForest model pkl.
        contamination: Proportion of expected outliers in dataset.

    Returns:
        pd.DataFrame containing flagged anomalous records.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if data_file is None:
        default_data = os.path.join(base_dir, "data", "cleaned_data.csv")
        fallback_data = os.path.join(base_dir, "cleaned_data.csv")
        data_file = default_data if os.path.exists(default_data) else fallback_data

    if output_file is None:
        outputs_dir = os.path.join(base_dir, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        output_file = os.path.join(outputs_dir, "anomaly_output.csv")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

    if model_file is None:
        models_dir = os.path.join(base_dir, "models")
        os.makedirs(models_dir, exist_ok=True)
        model_file = os.path.join(models_dir, "anomaly_model.pkl")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(model_file)), exist_ok=True)

    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Cleaned data file not found at: {data_file}")

    df = pd.read_csv(data_file)

    # Compute room & equipment level baselines
    baseline = df.groupby(["room", "equipment"])["power_kw"].median().reset_index()
    baseline.rename(columns={"power_kw": "expected_power_kw"}, inplace=True)

    df = pd.merge(df, baseline, on=["room", "equipment"], how="left")

    feature_cols = ["power_kw", "hour", "is_weekend"]
    X = df[feature_cols]

    model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42)
    model.fit(X)

    joblib.dump(model, model_file)

    df["anomaly_status"] = np.where(model.predict(X) == -1, "ANOMALY", "NORMAL")
    df["anomaly_score"] = np.round(model.score_samples(X), 4)

    anomalies = df[df["anomaly_status"] == "ANOMALY"][
        ["timestamp", "building", "room", "equipment", "power_kw", "expected_power_kw", "anomaly_status", "anomaly_score"]
    ]
    out = anomalies.rename(columns={"power_kw": "actual_power_kw"})

    out.to_csv(output_file, index=False)
    print(f"✓ Anomaly detection completed: {output_file} ({len(out)} anomalies detected, model saved to {model_file})")
    return out


if __name__ == "__main__":
    run_anomaly()
