import os
import math
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import pandas as pd
import numpy as np


class DataService:
    """Service to safely read and normalize AI/data outputs for EnergiQ backend."""

    # Default Constants for Calculations
    DEFAULT_TARIFF_PER_KWH: float = 8.0
    DEFAULT_CO2_PER_KWH: float = 0.5  # kg CO2 per kWh

    def __init__(self, ai_dir: Optional[Path] = None):
        if ai_dir:
            self.ai_dir = ai_dir
        else:
            # Determine project root (EnergiQ) from backend/services/data_service.py
            file_path = Path(__file__).resolve()
            project_root = file_path.parent.parent.parent
            self.ai_dir = project_root / "ai"

    def _get_file_path(self, filename: str) -> Path:
        """Returns full path to an AI CSV file."""
        return self.ai_dir / filename

    def _read_csv(self, filename: str) -> pd.DataFrame:
        """Helper to read CSV with validation."""
        path = self._get_file_path(filename)
        if not path.exists():
            raise FileNotFoundError(f"Data file '{filename}' not found at path: {path}")

        if path.stat().st_size == 0:
            raise ValueError(f"Data file '{filename}' at path {path} is empty.")

        try:
            df = pd.read_csv(path)
            if df.empty:
                raise ValueError(f"Data file '{filename}' contains no rows.")
            return df
        except Exception as e:
            if isinstance(e, (FileNotFoundError, ValueError)):
                raise e
            raise ValueError(f"Error reading CSV file '{filename}': {str(e)}")

    def _sanitize_value(self, val: Any) -> Any:
        """Convert Numpy / Pandas specific types to JSON-compatible Python types."""
        if val is None or pd.isna(val):
            return None
        if isinstance(val, (float, np.floating)):
            if math.isnan(val) or math.isinf(val):
                return None
            return float(val)
        if isinstance(val, (int, np.integer)):
            return int(val)
        if isinstance(val, (pd.Timestamp, np.datetime64)):
            return str(val)
        return str(val) if not isinstance(val, (str, bool, dict, list)) else val

    def _sanitize_records(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sanitize a list of dictionary records for clean JSON output."""
        sanitized = []
        for rec in records:
            clean_rec = {col: self._sanitize_value(val) for col, val in rec.items()}
            sanitized.append(clean_rec)
        return sanitized

    def get_consumption_data(
        self,
        building: Optional[str] = None,
        room: Optional[str] = None,
        equipment: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Reads consumption dataset (cleaned_data.csv or input.csv) with optional filters."""
        # Try cleaned_data.csv first, fallback to input.csv
        try:
            df = self._read_csv("cleaned_data.csv")
        except FileNotFoundError:
            df = self._read_csv("input.csv")

        # Column normalization
        col_map = {}
        for col in df.columns:
            low = col.strip().lower()
            if low in ["location", "building_name"]:
                col_map[col] = "building"
            elif low in ["room_name"]:
                col_map[col] = "room"
            elif low in ["device", "appliance"]:
                col_map[col] = "equipment"
            elif low in ["power", "power_kw", "kw"]:
                col_map[col] = "power_kw"
            elif low in ["energy", "energy_kwh", "kwh"]:
                col_map[col] = "energy_kwh"
            elif low in ["time", "datetime", "timestamp"]:
                col_map[col] = "timestamp"

        if col_map:
            df = df.rename(columns=col_map)

        # Ensure required columns exist with defaults if missing
        if "energy_kwh" not in df.columns and "power_kw" in df.columns:
            df["energy_kwh"] = df["power_kw"]

        # Apply filters
        if building:
            df = df[df["building"].astype(str).str.lower() == building.strip().lower()]
        if room:
            df = df[df["room"].astype(str).str.lower() == room.strip().lower()]
        if equipment:
            df = df[df["equipment"].astype(str).str.lower() == equipment.strip().lower()]

        records = df.to_dict(orient="records")
        return self._sanitize_records(records)

    def get_anomaly_data(
        self,
        building: Optional[str] = None,
        room: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Reads anomaly output (anomaly_output.csv)."""
        df = self._read_csv("anomaly_output.csv")

        # Column normalization
        col_map = {}
        for col in df.columns:
            low = col.strip().lower()
            if low in ["location", "building_name"]:
                col_map[col] = "building"
            elif low in ["room_name"]:
                col_map[col] = "room"
            elif low in ["power_kw", "actual_power", "actual_power_kw"]:
                col_map[col] = "actual_power_kw"
            elif low in ["normal_power", "normal_power_kw", "expected_power_kw"]:
                col_map[col] = "normal_power_kw"
            elif low in ["is_anomaly", "anomaly_flag"]:
                col_map[col] = "status"
            elif low in ["score"]:
                col_map[col] = "anomaly_score"

        if col_map:
            df = df.rename(columns=col_map)

        # Normalize status representation if numeric (e.g. -1 for anomaly)
        if "status" in df.columns:
            df["status"] = df["status"].apply(
                lambda s: "ANOMALY" if str(s).strip().upper() in ["ANOMALY", "-1", "TRUE", "1"] else "NORMAL"
            )

        if building:
            df = df[df["building"].astype(str).str.lower() == building.strip().lower()]
        if room:
            df = df[df["room"].astype(str).str.lower() == room.strip().lower()]

        records = df.to_dict(orient="records")
        return self._sanitize_records(records)

    def get_prediction_data(
        self,
        building: Optional[str] = None,
        room: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Reads prediction output (prediction_output.csv)."""
        df = self._read_csv("prediction_output.csv")

        col_map = {}
        for col in df.columns:
            low = col.strip().lower()
            if low in ["building", "building_name"]:
                col_map[col] = "location"
            elif low in ["timestamp", "datetime"]:
                col_map[col] = "date"
            elif low in ["predicted_kwh", "forecast_kwh", "predicted_energy"]:
                col_map[col] = "predicted_energy_kwh"

        if col_map:
            df = df.rename(columns=col_map)

        if building:
            df = df[df["location"].astype(str).str.lower() == building.strip().lower()]
        if room:
            df = df[df["room"].astype(str).str.lower() == room.strip().lower()]

        records = df.to_dict(orient="records")
        return self._sanitize_records(records)

    def get_room_hierarchy(self) -> Dict[str, Any]:
        """Generates dynamic hierarchical building -> room -> equipment dictionary."""
        try:
            records = self.get_consumption_data()
        except (FileNotFoundError, ValueError):
            records = []

        buildings_dict: Dict[str, Dict[str, set]] = {}

        for rec in records:
            b_name = rec.get("building") or "Default Building"
            r_name = rec.get("room") or "Default Room"
            eq_name = rec.get("equipment")

            if b_name not in buildings_dict:
                buildings_dict[b_name] = {}
            if r_name not in buildings_dict[b_name]:
                buildings_dict[b_name][r_name] = set()

            if eq_name:
                buildings_dict[b_name][r_name].add(eq_name)

        result_buildings = []
        for b_name, rooms_data in sorted(buildings_dict.items()):
            rooms_list = []
            for r_name, equipment_set in sorted(rooms_data.items()):
                rooms_list.append({
                    "name": r_name,
                    "equipment": sorted(list(equipment_set))
                })
            result_buildings.append({
                "name": b_name,
                "rooms": rooms_list
            })

        return {"buildings": result_buildings}

    def get_summary_metrics(
        self,
        tariff_per_kwh: float = DEFAULT_TARIFF_PER_KWH,
        co2_per_kwh: float = DEFAULT_CO2_PER_KWH,
    ) -> Dict[str, Any]:
        """Computes summary KPIs required by frontend."""
        # 1. Total Energy kWh
        try:
            consumption = self.get_consumption_data()
            total_energy = sum(
                float(rec.get("energy_kwh") or rec.get("power_kw") or 0.0)
                for rec in consumption
            )
        except Exception:
            total_energy = 0.0

        # 2. Estimated Cost
        estimated_cost = round(total_energy * tariff_per_kwh, 2)

        # 3. Active Anomalies
        try:
            anomalies = self.get_anomaly_data()
            active_anomalies = len([
                a for a in anomalies if str(a.get("status", "")).upper() == "ANOMALY"
            ])
        except Exception:
            active_anomalies = 0

        # 4. Predicted Next Day kWh
        try:
            predictions = self.get_prediction_data()
            predicted_next_day = sum(
                float(p.get("predicted_energy_kwh", 0.0)) for p in predictions
            )
        except Exception:
            predicted_next_day = 0.0

        # 5. Estimated CO2 kg
        estimated_co2 = round(total_energy * co2_per_kwh, 2)

        return {
            "total_energy_kwh": round(total_energy, 2),
            "estimated_cost": estimated_cost,
            "active_anomalies": active_anomalies,
            "predicted_next_day_kwh": round(predicted_next_day, 2),
            "estimated_co2_kg": estimated_co2,
            "tariff_rate_kwh": tariff_per_kwh,
            "co2_factor_kg_per_kwh": co2_per_kwh,
        }
