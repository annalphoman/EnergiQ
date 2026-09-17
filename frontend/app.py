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
    render_live_monitor
)
from components.simulator import render_simulator_page

# Page Configuration
st.set_page_config(
    page_title="EnergiQ | AI Energy Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS Theme (Dark Mode, Glassmorphism, Modern Typography & Glowing Metrics)
CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Global Page Styling */
    .stApp {
        background-color: #0E1117;
        color: #E0E6ED;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #121622 !important;
        border-right: 1px solid #212936;
    }

    /* Header Container */
    .main-header {
        background: linear-gradient(135deg, rgba(22, 27, 46, 0.9) 0%, rgba(14, 17, 23, 0.9) 100%);
        border: 1px solid #212936;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .brand-title {
        font-size: 28px;
        font-weight: 700;
        background: linear-gradient(90deg, #00F2FE 0%, #4FACFE 50%, #7F00FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    
    .brand-subtitle {
        color: #8B949E;
        font-size: 14px;
        margin-top: 4px;
    }

    /* Metric Card Customization */
    div[data-testid="stMetric"] {
        background: rgba(22, 27, 46, 0.7);
        border: 1px solid #212936;
        border-radius: 10px;
        padding: 16px 20px;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        border-color: #00F2FE;
        transform: translateY(-2px);
    }

    div[data-testid="stMetricLabel"] {
        color: #8B949E !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #FFFFFF !important;
        font-size: 24px !important;
        font-weight: 700 !important;
    }

    /* Tab Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(22, 27, 46, 0.5);
        padding: 6px;
        border-radius: 8px;
        border: 1px solid #212936;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        color: #8B949E;
        padding: 8px 16px;
        font-weight: 500;
    }

    .stTabs [aria-selected="true"] {
        background-color: #4FACFE !important;
        color: #FFFFFF !important;
        font-weight: 600;
    }

    /* Table Styling */
    .stDataFrame {
        border: 1px solid #212936;
        border-radius: 8px;
        overflow: hidden;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data(ttl=300)
def load_dataset():
    """Loads datasets and caches for 5 minutes."""
    return generate_mock_energy_data()


def main():
    df = load_dataset()
    
    # Render Main Brand Header
    st.markdown("""
    <div class="main-header">
        <div>
            <h1 class="brand-title">⚡ EnergiQ Platform</h1>
            <div class="brand-subtitle">AI-Based Energy Consumption Intelligence, Forecasting & Wastage Optimization</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Navigation
    st.sidebar.markdown("## 🧭 Navigation")
    nav_option = st.sidebar.radio(
        "Select Module:",
        options=[
            "📊 Executive Overview",
            "📈 Consumption Intelligence",
            "🔮 AI Consumption Forecasting",
            "🚨 Anomaly & Wastage Engine",
            "🏫 Smart Campus / Building View",
            "⚡ Live Energy Monitor",
            "🎮 What-If Energy Simulator"
        ],
        index=0
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### ⚙️ System Controls")
    campus_filter = st.sidebar.multiselect(
        "Filter Location / Zone:",
        options=list(df['location'].unique()),
        default=list(df['location'].unique())
    )
    
    # Filter dataset based on sidebar selection
    if campus_filter:
        active_df = df[df['location'].isin(campus_filter)]
    else:
        active_df = df
        
    st.sidebar.markdown("---")
    st.sidebar.info(f"🟢 **System Status**: Online\n\n📅 Data Window: {active_df['timestamp'].min().strftime('%b %d')} - {active_df['timestamp'].max().strftime('%b %d, %Y')}")

    # Render Selected View
    if nav_option == "📊 Executive Overview":
        st.markdown("## 📊 Executive Overview")
        render_overview_kpis(active_df)
        st.markdown("<br>", unsafe_allow_html=True)
        render_consumption_intelligence(active_df)
        
    elif nav_option == "📈 Consumption Intelligence":
        render_consumption_intelligence(active_df)
        
    elif nav_option == "🔮 AI Consumption Forecasting":
        render_forecasting_section(active_df)
        
    elif nav_option == "🚨 Anomaly & Wastage Engine":
        render_anomaly_and_wastage_section(active_df)
        
    elif nav_option == "🏫 Smart Campus / Building View":
        render_location_analytics(active_df)
        
    elif nav_option == "⚡ Live Energy Monitor":
        render_live_monitor(active_df)
        
    elif nav_option == "🎮 What-If Energy Simulator":
        render_simulator_page()


if __name__ == "__main__":
    main()
