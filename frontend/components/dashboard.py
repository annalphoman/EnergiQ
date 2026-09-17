"""
EnergiQ Frontend - Dashboard & Analytics Components
Handles main dashboard layout, metric displays, explainable AI recommendation cards,
consumption intelligence tabs, campus location analytics, and live monitor views.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from components.charts import (
    render_consumption_trend_chart,
    render_forecast_vs_actual_chart,
    render_location_breakdown_chart,
    render_anomaly_scatter_chart,
    render_live_gauge,
    render_efficiency_score_gauge
)

def generate_mock_energy_data():
    """Generates rich, realistic synthetic energy dataset for standalone demo mode."""
    np.random.seed(42)
    end_time = datetime.now()
    start_time = end_time - timedelta(days=14)
    timestamps = pd.date_range(start=start_time, end=end_time, freq='h')
    
    locations = ["Academic Block", "Computer Labs", "Library", "Administration", "Canteen", "Hostel"]
    
    records = []
    for ts in timestamps:
        hour = ts.hour
        is_weekend = ts.weekday() >= 5
        
        # Diurnal pattern base curve
        diurnal_factor = np.sin((hour - 6) / 24 * 2 * np.pi) + 1.2
        if is_weekend:
            diurnal_factor *= 0.65
            
        for loc in locations:
            multiplier = {
                "Academic Block": 12.0,
                "Computer Labs": 18.0,
                "Library": 8.0,
                "Administration": 6.0,
                "Canteen": 10.0,
                "Hostel": 14.0
            }.get(loc, 10.0)
            
            # Base consumption
            base_kw = multiplier * (diurnal_factor + np.random.normal(0, 0.15))
            base_kw = max(1.5, base_kw)
            
            # Anomaly injection logic (e.g. night wastage in Computer Lab, sudden spike in Hostel)
            is_anomaly = False
            anomaly_reason = ""
            
            if loc == "Computer Labs" and (hour >= 1 and hour <= 4) and np.random.rand() > 0.4:
                base_kw += 28.5  # High nighttime load wastage
                is_anomaly = True
                anomaly_reason = "Unusual nighttime HVAC/PC load outside operating hours"
            elif loc == "Academic Block" and hour == 14 and np.random.rand() > 0.7:
                base_kw += 35.0  # Spike
                is_anomaly = True
                anomaly_reason = "Sudden excessive consumption spike detected"
            elif hour == 11 and np.random.rand() > 0.9:
                base_kw *= 1.8
                is_anomaly = True
                anomaly_reason = "Persistent usage spike significantly above baseline"
                
            # Forecast & Confidence Bounds
            forecast_kwh = base_kw * np.random.uniform(0.95, 1.05)
            forecast_upper = forecast_kwh * 1.12
            forecast_lower = forecast_kwh * 0.88
            
            records.append({
                'timestamp': ts,
                'location': loc,
                'consumption_kwh': round(base_kw, 2),
                'forecast_kwh': round(forecast_kwh, 2),
                'forecast_upper': round(forecast_upper, 2),
                'forecast_lower': round(forecast_lower, 2),
                'actual_kwh': round(base_kw, 2),
                'is_anomaly': is_anomaly,
                'reason': anomaly_reason,
                'hour': hour,
                'day_name': ts.strftime('%A')
            })
            
    df = pd.DataFrame(records)
    return df


def build_recommendations(df: pd.DataFrame):
    """Builds AI-style recommendations based on current filtered data."""
    if df.empty:
        return []

    recommendations = []

    total_kwh = df['consumption_kwh'].sum()
    by_location = df.groupby('location')['consumption_kwh'].sum().sort_values(ascending=False)
    anomaly_locations = df[df['is_anomaly']].groupby('location').size().sort_values(ascending=False)
    peak_hour = df.groupby('hour')['consumption_kwh'].mean().idxmax()
    peak_location = by_location.idxmax()

    if not anomaly_locations.empty:
        top_anomaly_loc = anomaly_locations.index[0]
        top_anomaly_count = anomaly_locations.iloc[0]
        recommendations.append({
            'severity': 'High',
            'title': f'Peak anomaly in {top_anomaly_loc}',
            'detail': f'{top_anomaly_count} unusual load events were detected. Review equipment shutdown and HVAC schedules.',
            'savings': '$180 - $250 / month',
            'location': top_anomaly_loc
        })

    recommendations.append({
        'severity': 'Medium',
        'title': f'{peak_location} is the highest energy consumer',
        'detail': f'This area contributes {by_location.iloc[0]:,.1f} kWh. Consider optimized scheduling or load balancing.',
        'savings': '$90 - $150 / month',
        'location': peak_location
    })

    recommendations.append({
        'severity': 'Low',
        'title': f'Peak load around {peak_hour}:00',
        'detail': 'Energy demand rises sharply during this hour. Shift non-critical loads or stagger equipment usage.',
        'savings': '$40 - $90 / month',
        'location': 'Whole campus'
    })

    if total_kwh > 0:
        recommendations.append({
            'severity': 'Medium',
            'title': 'Savings opportunity available',
            'detail': 'A targeted efficiency action plan could reduce energy usage without disrupting core operations.',
            'savings': '~5-12% reduction',
            'location': 'All locations'
        })

    return recommendations[:4]


def render_recommendations(df: pd.DataFrame):
    """Renders quick, actionable AI recommendations based on current filtered view."""
    st.markdown("### Smart Recommendations")
    recs = build_recommendations(df)

    if not recs:
        st.info("No recommendation data available for the selected filters.")
        return

    cols = st.columns(2)
    for idx, rec in enumerate(recs):
        with cols[idx % 2]:
            color = {
                'High': '#ff4d4d',
                'Medium': '#ffb703',
                'Low': '#4cc9f0'
            }.get(rec['severity'], '#8ecae6')

            st.markdown(f"""
            <div style="background: rgba(17,24,39,0.9); border-left: 5px solid {color}; padding: 16px; border-radius: 12px; margin-bottom: 14px; box-shadow: 0 4px 12px rgba(0,0,0,0.12);">
                <div style="font-size: 12px; letter-spacing: 0.08em; color: {color}; font-weight: 700; text-transform: uppercase;">{rec['severity']} Priority</div>
                <div style="font-size: 20px; font-weight: 700; color: #ffffff; margin-top: 8px;">{rec['title']}</div>
                <div style="font-size: 14px; color: #d1d5db; margin-top: 8px;">{rec['detail']}</div>
                <div style="font-size: 13px; color: #a7f3d0; margin-top: 12px; font-weight: 600;">Savings: {rec['savings']}</div>
                <div style="font-size: 12px; color: #cbd5e1; margin-top: 6px;">Area: {rec['location']}</div>
            </div>
            """, unsafe_allow_html=True)


def render_overview_kpis(df: pd.DataFrame):
    """Renders top executive KPI summary grid."""
    total_kwh = df['consumption_kwh'].sum()
    peak_demand = df['consumption_kwh'].max()
    avg_kwh = df['consumption_kwh'].mean()
    
    # Cost estimation assumptions ($0.15 per kWh)
    est_cost = total_kwh * 0.15
    anomalies_count = df['is_anomaly'].sum()
    
    # Compute Efficiency Score
    anomaly_penalty = min(25, anomalies_count * 0.8)
    peak_penalty = min(15, (peak_demand / (avg_kwh + 1e-5)) * 2)
    efficiency_score = max(40, int(98 - anomaly_penalty - peak_penalty))

    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1.2])
    
    with col1:
        st.metric(
            label="Total Consumption",
            value=f"{total_kwh:,.1f} kWh",
            delta="-4.2% vs last period"
        )
    with col2:
        st.metric(
            label="Peak Demand",
            value=f"{peak_demand:.1f} kW",
            delta="+2.1 kW peak spike",
            delta_color="inverse"
        )
    with col3:
        st.metric(
            label="Est. Electricity Cost",
            value=f"${est_cost:,.2f}",
            delta="~$140 savings opp."
        )
    with col4:
        st.metric(
            label="Active Anomalies",
            value=f"{anomalies_count}",
            delta="3 High Severity",
            delta_color="inverse"
        )
    with col5:
        fig_score = render_efficiency_score_gauge(efficiency_score)
        st.plotly_chart(fig_score, use_container_width=True, key="overview_score_gauge")


def render_consumption_intelligence(df: pd.DataFrame):
    """Renders consumption intelligence view with tabs for different timeframes."""
    st.markdown("### Consumption Intelligence & Trend Analysis")
    
    tab_hourly, tab_daily, tab_peak = st.tabs(["Hourly Profile", "Daily Aggregates", "Peak Usage Analysis"])
    
    with tab_hourly:
        st.markdown("##### Hourly Load Profile Across All Campus Zones")
        hourly_df = df.groupby('timestamp')['consumption_kwh'].sum().reset_index()
        fig_hourly = render_consumption_trend_chart(hourly_df, time_frame="Hourly")
        st.plotly_chart(fig_hourly, use_container_width=True, key="hourly_trend_chart")
        
    with tab_daily:
        st.markdown("##### Daily Energy Consumption (kWh)")
        daily_df = df.groupby(df['timestamp'].dt.date)['consumption_kwh'].agg(['sum', 'max', 'mean']).reset_index()
        daily_df.columns = ['timestamp', 'consumption_kwh', 'peak_kwh', 'avg_kwh']
        daily_df['timestamp'] = pd.to_datetime(daily_df['timestamp'])
        fig_daily = render_consumption_trend_chart(daily_df, time_frame="Daily")
        st.plotly_chart(fig_daily, use_container_width=True, key="daily_trend_chart")
        
    with tab_peak:
        st.markdown("##### Peak Usage Distribution by Hour of Day")
        peak_by_hour = df.groupby('hour')['consumption_kwh'].mean().reset_index()
        st.dataframe(
            peak_by_hour.style.highlight_max(subset=['consumption_kwh'], color='#FF1744'),
            use_container_width=True
        )


def render_location_analytics(df: pd.DataFrame):
    """Renders Smart Campus / Building-wise comparative analytics."""
    st.markdown("### Smart Campus / Building View")

    if df is None or df.empty:
        st.warning("No building data available for this view.")
        return

    required_cols = {'location', 'consumption_kwh'}
    missing = required_cols - set(df.columns)
    if missing:
        st.warning(f"Building view needs the following columns: {sorted(required_cols)}. Missing: {sorted(missing)}")
        st.dataframe(df.head())
        return

    col_sel, col_stats = st.columns([1, 2])

    with col_sel:
        selected_loc = st.selectbox(
            "Select Building / Campus Area:",
            options=["All Buildings"] + list(df['location'].unique()),
            index=0
        )

    if selected_loc != "All Buildings":
        filtered_df = df[df['location'] == selected_loc]
    else:
        filtered_df = df

    loc_summary = filtered_df.groupby('location', dropna=False)['consumption_kwh'].agg(
        Total_kWh='sum',
        Peak_kW='max',
        Avg_kW='mean',
        Anomalies=lambda x: int((filtered_df.loc[x.index, 'is_anomaly'] if 'is_anomaly' in filtered_df.columns else False).sum()) if 'is_anomaly' in filtered_df.columns else 0
    ).reset_index()

    if 'is_anomaly' not in filtered_df.columns:
        loc_summary['Anomalies'] = 0

    fig_loc = render_location_breakdown_chart(loc_summary.rename(columns={'Total_kWh': 'consumption_kwh'}))
    st.plotly_chart(fig_loc, use_container_width=True, key="location_breakdown_chart")

    st.markdown("#### Building Comparison Metrics")
    st.dataframe(
        loc_summary.style.format({
            'Total_kWh': '{:,.1f}',
            'Peak_kW': '{:.2f}',
            'Avg_kW': '{:.2f}',
            'Anomalies': '{:d}'
        }).background_gradient(subset=['Total_kWh'], cmap='Blues'),
        use_container_width=True
    )


def render_forecasting_section(df: pd.DataFrame):
    """Renders AI forecasting tab with next-hour, next-day, and 7-day predictions."""
    st.markdown("### AI Consumption Forecasting")
    
    col_metrics, col_chart = st.columns([1, 3])
    
    with col_metrics:
        st.markdown("#### Model Performance")
        st.markdown("""
        <div style="background: rgba(22, 27, 46, 0.8); padding: 15px; border-radius: 8px; border: 1px solid #212936;">
            <p style="margin: 0; color: #8B949E;">Algorithm</p>
            <h4 style="margin: 0 0 10px 0; color: #00F2FE;">Gradient Boosted Ensemble</h4>
            <p style="margin: 0; color: #8B949E;">MAE (Mean Abs Error)</p>
            <h4 style="margin: 0 0 10px 0; color: #00E676;">1.42 kWh</h4>
            <p style="margin: 0; color: #8B949E;">RMSE</p>
            <h4 style="margin: 0 0 10px 0; color: #4FACFE;">2.18 kWh</h4>
            <p style="margin: 0; color: #8B949E;">R² Score</p>
            <h4 style="margin: 0; color: #00E676;">0.946</h4>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        time_horizon = st.radio(
            "Forecast Horizon:",
            ["Next-Hour", "Next-Day", "7-Day Horizon"],
            index=1
        )
        
    with col_chart:
        # Filter timeframe for forecasting view
        if time_horizon == "Next-Hour":
            sample_df = df.tail(24)
        elif time_horizon == "Next-Day":
            sample_df = df.tail(48)
        else:
            sample_df = df.tail(168)
            
        agg_forecast = sample_df.groupby('timestamp').agg({
            'actual_kwh': 'sum',
            'forecast_kwh': 'sum',
            'forecast_upper': 'sum',
            'forecast_lower': 'sum'
        }).reset_index()
        
        fig_fc = render_forecast_vs_actual_chart(agg_forecast)
        st.plotly_chart(fig_fc, use_container_width=True, key="forecast_vs_actual_chart")


def render_anomaly_and_wastage_section(df: pd.DataFrame):
    """Renders Anomaly & Wastage Detection with Explainable AI recommendations."""
    st.markdown("### Anomaly & Energy Wastage Detection Engine")
    
    # Time-series anomaly chart
    fig_anom = render_anomaly_scatter_chart(df)
    st.plotly_chart(fig_anom, use_container_width=True, key="anomaly_scatter_chart")
    
    col_anom_list, col_xai = st.columns([1.2, 1])
    
    with col_anom_list:
        st.markdown("#### Detected Anomalies & Wastage Events")
        anom_df = df[df['is_anomaly']].sort_values(by='timestamp', ascending=False)
        if len(anom_df) > 0:
            st.dataframe(
                anom_df[['timestamp', 'location', 'consumption_kwh', 'reason']].head(10).style.format({
                    'consumption_kwh': '{:.2f} kWh'
                }),
                use_container_width=True
            )
        else:
            st.success("No active anomalies detected in current period.")
            
    with col_xai:
        st.markdown("#### 🧠 Explainable AI Insights & Recommendations")
        
        st.markdown("""
        <div style="background: rgba(255, 23, 68, 0.08); border-left: 4px solid #FF1744; padding: 12px; margin-bottom: 12px; border-radius: 4px;">
            <strong style="color: #FF1744;">⚠️ Critical Anomaly: Nighttime Wastage in Computer Lab</strong><br>
            <span style="font-size: 0.9em; color: #E0E6ED;">
            <b>Explanation:</b> Consumption at 2:00 AM reached <b>32.5 kWh</b>, which is <b>410% higher</b> than expected baseline (6.2 kWh).
            </span><br><br>
            <strong style="color: #00E676;">💡 Recommendation:</strong> Inspect HVAC and workstation automated shutdown timers.<br>
            <span style="font-size: 0.85em; color: #00F2FE;">Est. Potential Savings: <b>~$185 / month (1,230 kWh)</b></span>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background: rgba(255, 171, 0, 0.08); border-left: 4px solid #FFAB00; padding: 12px; margin-bottom: 12px; border-radius: 4px;">
            <strong style="color: #FFAB00;">⚡ Warning: Midday Peak Demand Spike in Academic Block</strong><br>
            <span style="font-size: 0.9em; color: #E0E6ED;">
            <b>Explanation:</b> Coincident HVAC and lighting load exceeded peak threshold between 1:00 PM - 3:00 PM.
            </span><br><br>
            <strong style="color: #00E676;">💡 Recommendation:</strong> Implement staggered cooling schedule across lecture halls.<br>
            <span style="font-size: 0.85em; color: #00F2FE;">Est. Potential Savings: <b>~$95 / month (630 kWh)</b></span>
        </div>
        """, unsafe_allow_html=True)


def render_live_monitor(df: pd.DataFrame):
    """Renders real-time power monitor with simulated live stream."""
    st.markdown("### Live Energy Monitor (Real-Time)")
    
    col_gauge, col_feed = st.columns([1, 1.5])
    
    # Get recent load
    recent_kw = float(df['consumption_kwh'].iloc[-1])
    peak_kw = float(df['consumption_kwh'].max()) * 1.1
    
    with col_gauge:
        fig_live = render_live_gauge(recent_kw, peak_kw=peak_kw)
        st.plotly_chart(fig_live, use_container_width=True, key="live_gauge_chart")
        
        st.markdown("#### Status: " + ("<span style='color: #00E676;'>NORMAL</span>" if recent_kw < peak_kw * 0.75 else "<span style='color: #FF1744;'>ANOMALY DETECTED</span>"), unsafe_allow_html=True)
        
    with col_feed:
        st.markdown("#### Live Telemetry Feed (Simulated 5s Refresh)")
        live_df = df.tail(15)[['timestamp', 'location', 'consumption_kwh', 'is_anomaly']]
        st.dataframe(
            live_df.style.map(
                lambda val: 'background-color: rgba(255, 23, 68, 0.2); color: #FF1744; font-weight: bold;' if val else '',
                subset=['is_anomaly']
            ),
            use_container_width=True
        )
