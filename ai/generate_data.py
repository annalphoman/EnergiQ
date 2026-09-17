"""
Synthetic Data Generator for EnergiQ Energy Monitoring System.

Generates realistic hourly energy consumption data across multiple buildings,
floors, rooms, and equipment types with random peak spikes/anomalies.
"""

import os
import random
from datetime import datetime, timedelta
import numpy as np
import pandas as pd


def generate_synthetic_data(
    output_filepath: str = None,
    days: int = 14,
    seed: int = 42
) -> pd.DataFrame:
    """
    Generates synthetic hourly power and energy consumption logs.

    Args:
        output_filepath: Path to save the resulting CSV file.
        days: Number of historical days to simulate.
        seed: Random seed for reproducible dataset generation.

    Returns:
        pd.DataFrame containing synthetic energy logs.
    """
    if output_filepath is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        output_filepath = os.path.join(data_dir, "input.csv")
    else:
        os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)

    random.seed(seed)
    np.random.seed(seed)

    buildings = {
        "Main Block": {
            "Ground": ["Lab 101"],
            "First": ["Computer Lab 201"]
        },
        "Research Wing": {
            "Ground": ["AI Research Lab", "Server Room"]
        }
    }

    equipment_profiles = {
        "AC": (2.5, 1.8),
        "Computers": (0.8, 2.5),
        "Lights": (0.2, 1.5),
        "Fans": (0.15, 1.3),
        "Server Units": (4.0, 1.1)
    }

    start_time = datetime.now() - timedelta(days=days)
    records = []
    current_time = start_time
    now = datetime.now()

    while current_time <= now:
        hour = current_time.hour
        for bldg, floors in buildings.items():
            for flr, rooms in floors.items():
                for rm in rooms:
                    for eq, (base, mult) in equipment_profiles.items():
                        is_active_hours = (8 <= hour <= 18) or (eq == "Server Units")
                        if is_active_hours:
                            power_kw = base * mult * random.uniform(0.85, 1.15)
                        else:
                            power_kw = base * 0.1

                        # Inject random power spike anomalies (~2.5% probability)
                        if random.random() < 0.025:
                            power_kw *= 3.0

                        records.append({
                            "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                            "building": bldg,
                            "floor": flr,
                            "room": rm,
                            "equipment": eq,
                            "power_kw": round(power_kw, 3),
                            "energy_kwh": round(power_kw, 3)
                        })
        current_time += timedelta(hours=1)

    df = pd.DataFrame(records)
    df.to_csv(output_filepath, index=False)
    print(f"✓ Synthetic data generated: {output_filepath} ({len(df)} records)")
    return df


if __name__ == "__main__":
    generate_synthetic_data()
