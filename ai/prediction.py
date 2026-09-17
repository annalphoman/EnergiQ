"""
Energy Consumption Prediction Module for EnergiQ Energy Monitoring System.

Trains a Random Forest Regressor on daily aggregated energy consumption to forecast
next-day energy needs per building and room location.
"""

import os
from datetime import datetime, timedelta
import joblib
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


def run_pred(
    data_file: str = None,
    output_file: str = None,
    model_file: str = None
) -> pd.DataFrame:
    """
    Trains daily energy prediction model and forecasts next day kWh usage.

    Args:
        data_file: Path to cleaned dataset CSV.
        output_file: Path to save prediction output CSV.
        model_file: Path to save trained RandomForestRegressor pkl.

    Returns:
        pd.DataFrame containing location-wise next-day energy forecasts.
    """
    base_dir = os.path.dirname(os.path.abspath(__file__))

    if data_file is None:
        default_data = os.path.join(base_dir, "data", "cleaned_data.csv")
        fallback_data = os.path.join(base_dir, "cleaned_data.csv")
        data_file = default_data if os.path.exists(default_data) else fallback_data

    if output_file is None:
        outputs_dir = os.path.join(base_dir, "outputs")
        os.makedirs(outputs_dir, exist_ok=True)
        output_file = os.path.join(outputs_dir, "prediction_output.csv")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)

    if model_file is None:
        models_dir = os.path.join(base_dir, "models")
        os.makedirs(models_dir, exist_ok=True)
        model_file = os.path.join(models_dir, "prediction_model.pkl")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(model_file)), exist_ok=True)

    if not os.path.exists(data_file):
        raise FileNotFoundError(f"Cleaned data file not found at: {data_file}")

    df = pd.read_csv(data_file)
    df["date"] = pd.to_datetime(df["timestamp"]).dt.date

    # Aggregate hourly energy consumption into daily total per building & room
    daily = df.groupby(["building", "room", "date"])["energy_kwh"].sum().reset_index()
    daily["date"] = pd.to_datetime(daily["date"])
    daily["day_of_week"] = daily["date"].dt.dayofweek
    daily["is_weekend"] = daily["day_of_week"].apply(lambda x: 1 if x >= 5 else 0)
    daily["prev_day_kwh"] = daily.groupby("room")["energy_kwh"].shift(1)

    clean = daily.dropna()

    feature_cols = ["day_of_week", "is_weekend", "prev_day_kwh"]
    model = RandomForestRegressor(n_estimators=50, random_state=42)
    model.fit(clean[feature_cols], clean["energy_kwh"])

    joblib.dump(model, model_file)

    next_day_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    next_day_dow = (datetime.now() + timedelta(days=1)).weekday()
    next_day_is_weekend = 1 if next_day_dow >= 5 else 0

    preds = []
    locations = daily[["building", "room"]].drop_duplicates()

    for _, row in locations.iterrows():
        room_daily = daily[(daily["building"] == row["building"]) & (daily["room"] == row["room"])]
        last_kwh = room_daily.iloc[-1]["energy_kwh"]

        X_pred = pd.DataFrame([{
            "day_of_week": next_day_dow,
            "is_weekend": next_day_is_weekend,
            "prev_day_kwh": last_kwh
        }])

        predicted_kwh = model.predict(X_pred)[0]

        preds.append({
            "location": f"{row['building']} - {row['room']}",
            "prediction_date": next_day_date,
            "predicted_next_day_kwh": round(predicted_kwh, 2),
            "historical_last_day_kwh": round(last_kwh, 2)
        })

    pred_df = pd.DataFrame(preds)
    pred_df.to_csv(output_file, index=False)
    print(f"✓ Energy prediction completed: {output_file} ({len(pred_df)} locations predicted, model saved to {model_file})")
    return pred_df


if __name__ == "__main__":
    run_pred()
