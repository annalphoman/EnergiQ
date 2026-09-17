"""
Data Preprocessing Module for EnergiQ Energy Monitoring System.

Cleans input data, imputes missing values, parses timestamps, and engineers
time-based features (hour, day_of_week, is_weekend).
"""

import os
import pandas as pd


def preprocess_data(
    input_file: str = None,
    output_file: str = None
) -> pd.DataFrame:
    """
    Preprocesses raw energy consumption data.

    Args:
        input_file: Path to input CSV file.
        output_file: Path to output cleaned CSV file.

    Returns:
        pd.DataFrame containing cleaned and feature-engineered data.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if input_file is None:
        default_input = os.path.join(base_dir, "data", "input.csv")
        fallback_input = os.path.join(base_dir, "input.csv")
        input_file = default_input if os.path.exists(default_input) else fallback_input

    if output_file is None:
        data_dir = os.path.join(base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        output_file = os.path.join(data_dir, "cleaned_data.csv")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

    if not os.path.exists(input_file):
        raise FileNotFoundError(f"Input file not found at: {input_file}")

    df = pd.read_csv(input_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Missing value imputation
    if df['power_kw'].isnull().any():
        df['power_kw'] = df['power_kw'].fillna(df['power_kw'].median())

    if df['energy_kwh'].isnull().any():
        df['energy_kwh'] = df['energy_kwh'].fillna(df['power_kw'])

    # Feature Engineering
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].apply(lambda x: 1 if x >= 5 else 0)

    df.to_csv(output_file, index=False)
    print(f"✓ Cleaned data saved: {output_file} ({len(df)} records)")
    return df


if __name__ == "__main__":
    preprocess_data()
