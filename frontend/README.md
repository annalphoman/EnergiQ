# ⚡ EnergiQ Frontend - Streamlit Web Application

This folder contains the complete user interface for **EnergiQ: AI-Based Energy Consumption Intelligence & Optimization System**, built using Streamlit and Plotly.

---

## 🚀 Key Features & Capabilities

1. **📊 Executive Overview & Efficiency Score**:
   - High-level KPIs: Total Consumption (kWh), Peak Demand (kW), Estimated Cost, Active Anomalies.
   - Dynamic **Energy Efficiency Score** (0–100) with radial gauge indicator.

2. **📈 Consumption Intelligence**:
   - Multi-timeframe trend visualization (Hourly, Daily, Weekly, Monthly).
   - Peak usage distribution analysis and baseline thresholds.

3. **🔮 AI Consumption Forecasting**:
   - Forecast vs Actual load comparison charts with 95% confidence intervals.
   - Flexible horizon views: Next-Hour, Next-Day, and 7-Day predictions.
   - Machine learning performance metrics (MAE, RMSE, R² Score).

4. **🚨 Anomaly & Energy Wastage Detection**:
   - Time-series scatter plot highlighting unexpected spikes and nighttime off-hours usage.
   - **Explainable AI (XAI)** reasoning cards explaining *why* an anomaly occurred.
   - Actionable recommendations with projected financial and energy savings ($ / kWh).

5. **🏫 Smart Campus / Building View**:
   - Independent location breakdowns for Academic Block, Computer Labs, Library, Administration, Canteen, and Hostel.
   - Interactive building comparison tables and location-wise treemap/bar charts.

6. **⚡ Live Energy Monitor**:
   - Real-time streaming power gauge with live telemetry feed.
   - Status indicators (NORMAL vs ANOMALY DETECTED).

7. **🎮 What-If Energy Simulator**:
   - Interactive scenario controls: HVAC operating schedules, temperature setpoint tuning (+°C), off-hours equipment shutdown, solar PV rooftop array (kWp), and LED lighting retrofit.
   - Real-time calculation of projected load profile, monthly cost reduction, peak shaving, CO₂ emission savings, total investment, and ROI payback period.

---

## 📁 File & Module Architecture

```text
frontend/
├── app.py                  # Main Streamlit application entry point & custom CSS dark theme
├── requirements.txt        # Python package dependencies
├── README.md               # Frontend documentation & user guide
└── components/
    ├── charts.py           # Custom Plotly dark-themed interactive chart renderers
    ├── dashboard.py        # Dashboard layouts, KPI cards, XAI insights, and live stream feed
    └── simulator.py        # Interactive What-If Scenario Builder & ROI calculator
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
Ensure Python 3.9+ is installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch Application
From the `frontend/` directory (or workspace root):
```bash
streamlit run app.py
```
or from the root folder:
```bash
streamlit run frontend/app.py
```

The application will launch in your default browser at `http://localhost:8501`.
