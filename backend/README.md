# EnergiQ Backend API (Person 2 Handoff)

AI-Based Energy Consumption Intelligence & Optimization System — FastAPI Backend.

---

## 1. Architecture Overview

```text
Person 1 (AI/ML)
Dataset + Models → Generates CSV outputs in ai/
       ↓
Person 2 (Backend)  <-- THIS SERVICE
FastAPI API → Reads CSVs, normalizes schema, computes KPIs & recommendations
       ↓
Person 3 (Frontend)
Streamlit UI → Consumes JSON APIs
```

---

## 2. Installation & Requirements

### Required Packages
- Python 3.10+
- `fastapi`
- `uvicorn[standard]`
- `pandas`
- `pydantic`

### Installation Command
```bash
pip install -r backend/requirements.txt
```

---

## 3. How to Start the Backend Server

From the root repository directory (`EnergiQ/`):

```bash
uvicorn backend.main:app --reload
```

Server will run at:
- **API Base URL:** `http://127.0.0.1:8000`
- **Interactive Swagger Documentation:** `http://127.0.0.1:8000/docs`
- **ReDoc Documentation:** `http://127.0.0.1:8000/redoc`

---

## 4. Expected Data Files (Person 1 Hand-off)

The backend automatically locates CSV output files relative to the project root in the `ai/` directory:

- `ai/cleaned_data.csv` (or `ai/input.csv`) - Energy consumption logs
- `ai/anomaly_output.csv` - Anomaly detection results
- `ai/prediction_output.csv` - Energy consumption forecasts

> **Note:** If column names differ slightly, the backend automatically normalizes them (e.g. `location` vs `building`, `power_kw` vs `actual_power_kw`).

---

## 5. Available API Endpoints

### 1. `GET /summary`
Returns top-level dashboard KPIs:
- Total Energy (kWh)
- Estimated Cost (Tariff = 8.0 currency units/kWh)
- Active Anomalies count
- Predicted Next-Day Energy (kWh)
- Estimated CO₂ Footprint (0.5 kg CO₂/kWh)

**Example Response:**
```json
{
  "total_energy_kwh": 57.0,
  "estimated_cost": 456.0,
  "active_anomalies": 4,
  "predicted_next_day_kwh": 472.0,
  "estimated_co2_kg": 28.5,
  "tariff_rate_kwh": 8.0,
  "co2_factor_kg_per_kwh": 0.5
}
```

---

### 2. `GET /consumption`
Returns energy consumption logs with optional filters (`building`, `room`, `equipment`).

**Query Parameters:**
- `building` (optional, e.g. `Building A`)
- `room` (optional, e.g. `Lab 1`)
- `equipment` (optional, e.g. `AC`)

**Example Request:**
`GET /consumption?building=Building A&room=Lab 1`

**Example Response:**
```json
{
  "data": [
    {
      "timestamp": "2026-09-17 08:00",
      "building": "Building A",
      "room": "Lab 1",
      "equipment": "AC",
      "power_kw": 2.1,
      "energy_kwh": 2.1
    }
  ]
}
```

---

### 3. `GET /anomalies`
Returns detected abnormal consumption events with optional filters (`building`, `room`).

**Example Response:**
```json
{
  "anomalies": [
    {
      "timestamp": "2026-09-17 09:00",
      "building": "Building A",
      "room": "Lab 2",
      "equipment": "AC",
      "actual_power_kw": 5.4,
      "normal_power_kw": 2.1,
      "status": "ANOMALY",
      "anomaly_score": -0.78
    }
  ]
}
```

---

### 4. `GET /prediction`
Returns future energy consumption forecasts.

**Example Response:**
```json
{
  "predictions": [
    {
      "date": "2026-09-18",
      "location": "Building A",
      "room": "Lab 1",
      "predicted_energy_kwh": 120.5
    }
  ]
}
```

---

### 5. `GET /rooms`
Returns dynamic hierarchy of available buildings, rooms, and equipment.

**Example Response:**
```json
{
  "buildings": [
    {
      "name": "Building A",
      "rooms": [
        {
          "name": "Lab 1",
          "equipment": ["AC", "Computer", "Lights"]
        }
      ]
    }
  ]
}
```

---

### 6. `GET /recommendations`
Returns rule-based energy-saving recommendations categorized by priority (`HIGH`, `MEDIUM`, `LOW`).

**Example Response:**
```json
{
  "recommendations": [
    {
      "building": "Building A",
      "room": "Lab 2",
      "equipment": "AC",
      "priority": "HIGH",
      "message": "AC consumption is significantly above normal. (Actual: 5.4 kW, Expected: 2.1 kW). Inspect operation and check settings."
    }
  ]
}
```

---

## 6. Assumptions & Configurations

- **Electricity Tariff:** Configured at `8.0` units/kWh (can be overridden via `/summary?tariff=10.0`).
- **CO₂ Emission Factor:** Configured at `0.5` kg CO₂/kWh (can be overridden via `/summary?co2_factor=0.6`).
- **CORS:** Enabled for all origins (`*`) to support Streamlit and local frontend development.
