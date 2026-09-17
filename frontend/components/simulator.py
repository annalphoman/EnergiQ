"""
EnergiQ Frontend - What-If Energy Simulator Component
Provides interactive scenario modeling to test energy-saving measures before implementation.
Calculates projected load profile, kWh reduction, financial savings, peak shaving, and ROI payback.
"""

import streamlit as st
import pandas as pd
import numpy as np
from components.charts import (
    render_simulation_comparison_chart,
    render_savings_waterfall_chart
)

def calculate_scenario(
    hvac_start: int,
    hvac_end: int,
    ac_temp_offset: float,
    night_shutdown_pct: float,
    solar_capacity_kwp: float,
    led_retrofit_pct: float,
    electricity_rate: float = 0.15
):
    """Calculates 24-hour baseline vs projected scenario energy curves and savings."""
    hours = np.arange(24)
    
    # Baseline 24h load profile (kWh per hour)
    baseline_hvac = np.where((hours >= 8) & (hours <= 18), 25.0, 8.0)
    baseline_lighting = np.where((hours >= 7) & (hours <= 20), 12.0, 5.0)
    baseline_equipment = np.where((hours >= 9) & (hours <= 17), 18.0, 10.0)
    baseline_other = np.full(24, 6.0)
    
    baseline_total = baseline_hvac + baseline_lighting + baseline_equipment + baseline_other
    
    # 1. HVAC Schedule Optimization
    sim_hvac = np.where((hours >= hvac_start) & (hours <= hvac_end), 25.0, 2.0)
    # AC Temperature Setpoint adjustment (approx ~6% savings per °C increase)
    temp_savings_factor = 1.0 - (ac_temp_offset * 0.06)
    sim_hvac = sim_hvac * temp_savings_factor
    
    # 2. Night Shutdown of equipment outside operating hours
    equipment_off_hours = (hours < hvac_start) | (hours > hvac_end)
    sim_equipment = np.copy(baseline_equipment)
    sim_equipment[equipment_off_hours] *= (1.0 - (night_shutdown_pct / 100.0))
    
    # 3. LED Lighting Retrofit
    sim_lighting = baseline_lighting * (1.0 - (led_retrofit_pct / 100.0 * 0.45)) # LEDs save ~45% lighting energy
    
    # 4. Solar PV Generation (bell curve centered at hour 12)
    solar_gen = np.maximum(0, np.sin((hours - 6) / 12 * np.pi)) * (solar_capacity_kwp * 0.75)
    
    # Projected Total Net Grid Draw
    sim_total = np.maximum(0, (sim_hvac + sim_lighting + sim_equipment + baseline_other) - solar_gen)
    
    # Create DataFrames
    df_baseline = pd.DataFrame({'hour': hours, 'kwh': baseline_total})
    df_scenario = pd.DataFrame({'hour': hours, 'kwh': sim_total})
    
    # Monthly calculations (30 days)
    daily_baseline_kwh = baseline_total.sum()
    daily_sim_kwh = sim_total.sum()
    daily_saved_kwh = max(0, daily_baseline_kwh - daily_sim_kwh)
    
    monthly_baseline_cost = daily_baseline_kwh * 30 * electricity_rate
    monthly_sim_cost = daily_sim_kwh * 30 * electricity_rate
    monthly_saved_cost = monthly_baseline_cost - monthly_sim_cost
    
    # Peak shaving calculation
    baseline_peak = baseline_total.max()
    sim_peak = sim_total.max()
    peak_shaved_kw = max(0, baseline_peak - sim_peak)
    
    # Savings decomposition for waterfall chart
    hvac_monthly_savings = (baseline_hvac.sum() - sim_hvac.sum()) * 30 * electricity_rate
    lighting_monthly_savings = (baseline_lighting.sum() - sim_lighting.sum()) * 30 * electricity_rate
    solar_monthly_offset = solar_gen.sum() * 30 * electricity_rate
    
    # ROI & Investment Estimation
    solar_cost = solar_capacity_kwp * 1100  # $1,100 per kWp
    led_cost = (led_retrofit_pct / 100.0) * 3500 # Estimated LED retrofit cost
    total_investment = solar_cost + led_cost
    
    payback_months = (total_investment / monthly_saved_cost) if monthly_saved_cost > 0 else 0
    
    return {
        'df_baseline': df_baseline,
        'df_scenario': df_scenario,
        'daily_saved_kwh': daily_saved_kwh,
        'monthly_saved_kwh': daily_saved_kwh * 30,
        'monthly_baseline_cost': monthly_baseline_cost,
        'monthly_sim_cost': monthly_sim_cost,
        'monthly_saved_cost': monthly_saved_cost,
        'peak_shaved_kw': peak_shaved_kw,
        'hvac_monthly_savings': max(0, hvac_monthly_savings),
        'lighting_monthly_savings': max(0, lighting_monthly_savings),
        'solar_monthly_offset': max(0, solar_monthly_offset),
        'total_investment': total_investment,
        'payback_months': payback_months,
        'co2_saved_kg': daily_saved_kwh * 30 * 0.85 # ~0.85 kg CO2 per kWh
    }


def render_simulator_page():
    """Renders the What-If Energy Simulator tab."""
    st.markdown("### 🎮 What-If Energy Simulator")
    st.markdown("Simulate potential energy efficiency scenarios and evaluate projected cost reduction before implementation.")
    
    st.markdown("---")
    
    col_controls, col_results = st.columns([1.1, 2])
    
    with col_controls:
        st.markdown("#### ⚙️ Scenario Control Levers")
        
        with st.expander("🌡️ HVAC & Cooling Optimization", expanded=True):
            hvac_hours = st.slider(
                "HVAC Operating Window (Hour of Day):",
                min_value=6, max_value=22, value=(9, 17), step=1
            )
            ac_temp_offset = st.slider(
                "Increase AC Setpoint (°C):",
                min_value=0.0, max_value=3.0, value=1.5, step=0.5,
                help="Increasing setpoint by 1.5°C saves ~9% cooling energy."
            )
            
        with st.expander("💡 Lighting & Equipment Controls", expanded=True):
            night_shutdown = st.slider(
                "Off-Hours Equipment Shutdown (%):",
                min_value=0, max_value=100, value=75, step=5,
                help="Automatically power off PCs, displays, and non-critical loads at night."
            )
            led_retrofit = st.slider(
                "LED Retrofit Conversion (%):",
                min_value=0, max_value=100, value=60, step=10,
                help="Convert traditional lighting to high-efficiency LED fixtures."
            )
            
        with st.expander("☀️ Solar PV Rooftop Integration", expanded=True):
            solar_capacity = st.number_input(
                "Solar PV Array Capacity (kWp):",
                min_value=0, max_value=150, value=30, step=5
            )
            
        electricity_rate = st.number_input(
            "Electricity Tariff Rate ($/kWh):",
            min_value=0.05, max_value=0.50, value=0.15, step=0.01
        )
        
    # Execute Scenario Calculations
    res = calculate_scenario(
        hvac_start=hvac_hours[0],
        hvac_end=hvac_hours[1],
        ac_temp_offset=ac_temp_offset,
        night_shutdown_pct=night_shutdown,
        solar_capacity_kwp=solar_capacity,
        led_retrofit_pct=led_retrofit,
        electricity_rate=electricity_rate
    )
    
    with col_results:
        st.markdown("#### 📈 Projected Load Profile Comparison")
        fig_sim = render_simulation_comparison_chart(res['df_baseline'], res['df_scenario'])
        st.plotly_chart(fig_sim, use_container_width=True, key="sim_comparison_chart")
        
        # Key Impact Metrics
        st.markdown("#### 💰 Projected Savings & Financial ROI")
        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        
        with mcol1:
            st.metric(
                label="Monthly Energy Saved",
                value=f"{res['monthly_saved_kwh']:,.0f} kWh",
                delta=f"-{(res['monthly_saved_kwh'] / (res['monthly_baseline_cost']/electricity_rate))*100:.1f}% kWh"
            )
        with mcol2:
            st.metric(
                label="Monthly Bill Savings",
                value=f"${res['monthly_saved_cost']:,.2f}",
                delta=f"-${res['monthly_saved_cost']*12:,.0f} / year"
            )
        with mcol3:
            st.metric(
                label="Peak Load Shaved",
                value=f"{res['peak_shaved_kw']:.1f} kW",
                delta="Demand Charge Savings"
            )
        with mcol4:
            st.metric(
                label="Est. ROI Payback",
                value=f"{res['payback_months']:.1f} Months",
                delta=f"CO2 Saved: {res['co2_saved_kg']:,.0f} kg/mo"
            )
            
        fig_waterfall = render_savings_waterfall_chart(
            res['monthly_baseline_cost'],
            res['hvac_monthly_savings'],
            res['lighting_monthly_savings'],
            res['solar_monthly_offset']
        )
        st.plotly_chart(fig_waterfall, use_container_width=True, key="sim_waterfall_chart")
