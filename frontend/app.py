"""
⚡ EnergiQ - AI-Based Energy Consumption Intelligence & Optimization System
Main Streamlit Application Entry Point
"""

import streamlit as st
import pandas as pd
from datetime import datetime

# Import modular components
from components.dashboard import (
    generate_mock_energy_data,
    render_overview_kpis,
    render_consumption_intelligence,
    render_location_analytics,
    render_forecasting_section,
    render_anomaly_and_wastage_section,
    render_live_monitor,
    render_recommendations
)
from components.simulator import render_simulator_page

# Page Configuration
st.set_page_config(
    page_title="EnergiQ | AI Energy Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Simple and friendly dashboard theme
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background: linear-gradient(180deg, #0d1117 0%, #111827 100%);
        color: #f3f4f6;
    }

    .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
    .stApp p, .stApp li, .stApp span, .stApp div,
    .stApp label, .stApp .stMarkdown {
        color: #f3f4f6 !important;
    }

    section[data-testid="stSidebar"] {
        background: #050505 !important;
        border-right: 1px solid #1f1f1f;
    }

    .main-header {
        background: #111827;
        border: 1px solid #2a3448;
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 18px;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.25);
    }

    .brand-title {
        font-size: 30px;
        font-weight: 800;
        color: #ffffff;
        margin: 0;
    }

    .brand-subtitle {
        color: #d1d5db;
        font-size: 14px;
        margin-top: 6px;
    }

    div[data-testid="stMetric"] {
        background: rgba(17, 24, 39, 0.92);
        border: 1px solid #2a3448;
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 6px 16px rgba(0, 0, 0, 0.15);
    }

    div[data-testid="stMetricLabel"] {
        color: #d1d5db !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 24px !important;
        font-weight: 800 !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(255, 255, 255, 0.6);
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #475569;
        padding: 8px 16px;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #111111, #2a2a2a) !important;
        color: #ffffff !important;
    }

    section[data-testid="stSidebar"] .stRadio > div,
    section[data-testid="stSidebar"] .stMultiSelect,
    section[data-testid="stSidebar"] .stSelectbox,
    section[data-testid="stSidebar"] .stMarkdown,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] div,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] li {
        color: #ffffff !important;
        opacity: 1 !important;
    }

    section[data-testid="stSidebar"] .stRadio [role="radio"] {
        accent-color: #ffffff !important;
    }

    section[data-testid="stSidebar"] .stRadio > label,
    section[data-testid="stSidebar"] .stMultiSelect > label,
    section[data-testid="stSidebar"] .stSelectbox > label {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    section[data-testid="stSidebar"] .st-bb {
        background-color: #111111 !important;
    }

    section[data-testid="stSidebar"] .stAlert,
    section[data-testid="stSidebar"] .stInfo {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #ffffff !important;
    }

    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
    }

    .stAlert {
        border-radius: 12px;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_dataset():
    """Loads datasets and caches for 5 minutes."""
    return generate_mock_energy_data()


def normalize_energy_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Standardizes uploaded CSV columns to the app's expected schema."""
    if df is None or df.empty:
        return df

    normalized = df.copy()
    normalized.columns = [str(col).strip() for col in normalized.columns]

    rename_map = {
        'datetime': 'timestamp',
        'date_time': 'timestamp',
        'time': 'timestamp',
        'building': 'location',
        'zone': 'location',
        'campus_area': 'location',
        'usage_kwh': 'consumption_kwh',
        'energy_kwh': 'consumption_kwh',
        'kwh': 'consumption_kwh',
        'power_kw': 'consumption_kwh',
        'load_kwh': 'consumption_kwh',
        'actual': 'actual_kwh',
        'actual_kwh': 'actual_kwh',
        'forecast': 'forecast_kwh',
        'predicted_kwh': 'forecast_kwh',
    }
    normalized = normalized.rename(columns=rename_map)

    if 'timestamp' not in normalized.columns and 'date' in normalized.columns:
        normalized = normalized.rename(columns={'date': 'timestamp'})

    if 'location' not in normalized.columns and 'building_name' in normalized.columns:
        normalized = normalized.rename(columns={'building_name': 'location'})

    if 'location' not in normalized.columns:
        normalized['location'] = 'Unknown'

    if 'consumption_kwh' not in normalized.columns:
        if 'actual_kwh' in normalized.columns:
            normalized['consumption_kwh'] = normalized['actual_kwh']
        else:
            normalized['consumption_kwh'] = 0.0

    if 'actual_kwh' not in normalized.columns:
        normalized['actual_kwh'] = normalized['consumption_kwh']

    if 'forecast_kwh' not in normalized.columns:
        normalized['forecast_kwh'] = normalized['consumption_kwh']

    if 'forecast_upper' not in normalized.columns:
        normalized['forecast_upper'] = normalized['forecast_kwh'] * 1.10

    if 'forecast_lower' not in normalized.columns:
        normalized['forecast_lower'] = normalized['forecast_kwh'] * 0.90

    if 'is_anomaly' not in normalized.columns:
        normalized['is_anomaly'] = False

    if 'reason' not in normalized.columns:
        normalized['reason'] = ''

    if 'timestamp' in normalized.columns:
        normalized['timestamp'] = pd.to_datetime(normalized['timestamp'], errors='coerce')
        normalized = normalized.dropna(subset=['timestamp']).copy()

    if 'hour' not in normalized.columns and 'timestamp' in normalized.columns:
        normalized['hour'] = normalized['timestamp'].dt.hour

    if 'day_name' not in normalized.columns and 'timestamp' in normalized.columns:
        normalized['day_name'] = normalized['timestamp'].dt.strftime('%A')

    return normalized


def main():
    df = normalize_energy_dataframe(load_dataset())

    uploaded_file = st.sidebar.file_uploader(
        "Upload energy CSV file",
        type=["csv"],
        help="Upload a CSV containing columns like timestamp, location, consumption_kwh, forecast_kwh, is_anomaly, reason."
    )

    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file)
            df = normalize_energy_dataframe(uploaded_df)
            st.sidebar.success("Custom CSV uploaded successfully.")
        except Exception:
            st.sidebar.warning("Could not read the uploaded file. Using demo dataset instead.")
            df = normalize_energy_dataframe(load_dataset())

    # Render Main Brand Header
    st.markdown("""
    <div class="main-header">
        <div>
            <h1 class="brand-title">⚡ EnergiQ</h1>
            <div class="brand-subtitle">Your simple energy dashboard for smarter usage, forecasting, and savings.</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Welcome back! Here is a quick view of your energy performance.")

    # Sidebar Navigation
    st.sidebar.markdown("## Menu")
    nav_option = st.sidebar.radio(
        "Go to:",
        options=[
            "Dashboard",
            "Usage Insights",
            "Forecasts",
            "Alerts & Waste",
            "Building View",
            "Live Monitor",
            "Savings Simulator"
        ],
        index=0
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Filters")

    if 'timestamp' in df.columns and not df.empty:
        df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
        df = df.dropna(subset=['timestamp']).copy()

    if df.empty:
        st.sidebar.warning("No valid records found. Please upload a valid energy dataset.")
        return

    min_date = df['timestamp'].min().date()
    max_date = df['timestamp'].max().date()
    start_date, end_date = st.sidebar.date_input(
        "Select date range:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )

    campus_filter = st.sidebar.multiselect(
        "Select area(s):",
        options=list(df['location'].unique()),
        default=list(df['location'].unique())
    )

    if isinstance(start_date, tuple):
        start_date, end_date = start_date

    filtered_df = df[
        (df['timestamp'].dt.date >= start_date) &
        (df['timestamp'].dt.date <= end_date)
    ]

    if campus_filter:
        active_df = filtered_df[filtered_df['location'].isin(campus_filter)]
    else:
        active_df = filtered_df

    st.sidebar.markdown("---")
    st.sidebar.info(f"🟢 Status: Online\n\n📅 Period: {active_df['timestamp'].min().strftime('%b %d')} - {active_df['timestamp'].max().strftime('%b %d, %Y')}\n\n🏢 Locations: {', '.join(active_df['location'].unique()) if len(active_df) else 'None'}")

    # Render Selected View
    if nav_option == "Dashboard":
        st.markdown("## Dashboard Overview")
        render_recommendations(active_df)
        render_overview_kpis(active_df)
        st.markdown("<br>", unsafe_allow_html=True)
        render_consumption_intelligence(active_df)

    elif nav_option == "Usage Insights":
        st.markdown("## Usage Insights")
        render_consumption_intelligence(active_df)

    elif nav_option == "Forecasts":
        st.markdown("## Forecasts")
        render_forecasting_section(active_df)

    elif nav_option == "Alerts & Waste":
        st.markdown("## Alerts & Waste")
        render_anomaly_and_wastage_section(active_df)

    elif nav_option == "Building View":
        st.markdown("## Building View")
        render_location_analytics(active_df)

    elif nav_option == "Live Monitor":
        st.markdown("## Live Monitor")
        render_live_monitor(active_df)

    elif nav_option == "Savings Simulator":
        st.markdown("## Savings Simulator")
        render_simulator_page()


if __name__ == "__main__":
    main()
