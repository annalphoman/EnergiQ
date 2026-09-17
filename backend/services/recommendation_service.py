from typing import List, Dict, Any
from backend.services.data_service import DataService


class RecommendationService:
    """Generates rule-based energy-saving recommendations."""

    def __init__(self, data_service: DataService):
        self.data_service = data_service

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        recommendations = []
        seen_keys = set()

        # 1. Evaluate Anomalies
        try:
            anomalies = self.data_service.get_anomaly_data()
            for item in anomalies:
                status = str(item.get("status", "")).upper()
                if status == "ANOMALY":
                    building = item.get("building", "Unknown Building")
                    room = item.get("room", "Unknown Room")
                    equipment = item.get("equipment", "Equipment")
                    actual = item.get("actual_power_kw")
                    normal = item.get("normal_power_kw")

                    key = f"anomaly_{building}_{room}_{equipment}"
                    if key not in seen_keys:
                        seen_keys.add(key)
                        msg = f"{equipment} consumption is significantly above normal."
                        if actual and normal:
                            msg += f" (Actual: {actual} kW, Expected: {normal} kW)."
                        msg += " Inspect operation and check settings."

                        recommendations.append({
                            "building": building,
                            "room": room,
                            "equipment": equipment,
                            "priority": "HIGH",
                            "message": msg
                        })
        except Exception:
            pass

        # 2. Evaluate Off-Hours Usage from Consumption Data
        try:
            consumption = self.data_service.get_consumption_data()
            for rec in consumption:
                ts = str(rec.get("timestamp", ""))
                power = float(rec.get("power_kw") or rec.get("energy_kwh") or 0.0)
                building = rec.get("building", "Unknown Building")
                room = rec.get("room", "Unknown Room")
                equipment = rec.get("equipment", "Equipment")

                # Extract hour if timestamp format matches 'YYYY-MM-DD HH:MM'
                hour = None
                if " " in ts:
                    time_part = ts.split(" ")[1]
                    if ":" in time_part:
                        try:
                            hour = int(time_part.split(":")[0])
                        except ValueError:
                            pass

                if hour is not None and (hour >= 21 or hour <= 5) and power > 1.0:
                    key = f"offhours_{building}_{room}_{equipment}"
                    if key not in seen_keys:
                        seen_keys.add(key)
                        recommendations.append({
                            "building": building,
                            "room": room,
                            "equipment": equipment,
                            "priority": "HIGH",
                            "message": f"Possible energy wastage detected after operating hours ({ts}). Check if equipment was left ON."
                        })

                # 3. AC Specific High Power Check
                if str(equipment).upper() == "AC" and power >= 4.0:
                    key = f"ac_{building}_{room}"
                    if key not in seen_keys:
                        seen_keys.add(key)
                        recommendations.append({
                            "building": building,
                            "room": room,
                            "equipment": "AC",
                            "priority": "MEDIUM",
                            "message": f"High AC power usage ({power} kW) detected in {room}. Inspect AC temperature setpoints and room insulation."
                        })
        except Exception:
            pass

        # 4. Evaluate Future Predictions
        try:
            predictions = self.data_service.get_prediction_data()
            for pred in predictions:
                kwh = float(pred.get("predicted_energy_kwh", 0.0))
                location = pred.get("location", "Unknown Building")
                room = pred.get("room", "All Rooms")

                if kwh >= 150.0:
                    key = f"prediction_{location}_{room}"
                    if key not in seen_keys:
                        seen_keys.add(key)
                        recommendations.append({
                            "building": location,
                            "room": room,
                            "equipment": "All Heavy Equipment",
                            "priority": "MEDIUM",
                            "message": f"High energy demand ({kwh} kWh) predicted for {location} ({room}). Consider scheduling non-essential loads during off-peak hours."
                        })
        except Exception:
            pass

        # Fallback if no specific rule triggered
        if not recommendations:
            recommendations.append({
                "building": "All Buildings",
                "room": "All Rooms",
                "equipment": "General",
                "priority": "LOW",
                "message": "All energy metrics operating within normal baseline limits."
            })

        return recommendations
