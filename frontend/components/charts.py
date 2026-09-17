"""
EnergiQ Frontend - Custom Plotly Charts Component
Provides sleek, interactive, dark-themed visualizations for consumption intelligence,
forecasting, anomaly detection, location breakdown, and scenario simulation.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

# Color Palette Definitions
COLOR_PRIMARY = "#00F2FE"       # Cyan Neon
COLOR_SECONDARY = "#4FACFE"     # Vibrant Blue
COLOR_ACCENT = "#7F00FF"        # Deep Violet/Purple
COLOR_SUCCESS = "#00E676"       # Emerald Green
COLOR_WARNING = "#FFAB00"       # Amber Warning
COLOR_DANGER = "#FF1744"        # Crimson Red
COLOR_BG = "#0E1117"            # Dark Background
COLOR_CARD = "#161B2E"          # Card Background
COLOR_TEXT = "#E0E6ED"          # Text Light
COLOR_GRID = "#212936"          # Grid Line Color

PLOT_TEMPLATE = "plotly_dark"

def _apply_dark_theme(fig, title=""):
    """Helper to apply consistent dark aesthetic and formatting to Plotly figures."""
    fig.update_layout(
        template=PLOT_TEMPLATE,
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=16, color=COLOR_TEXT, family="Inter, sans-serif"),
            x=0.01,
            y=0.96
        ),
        paper_bgcolor="rgba(22, 27, 46, 0.7)",
        plot_bgcolor="rgba(14, 17, 23, 0.7)",
        margin=dict(l=40, r=40, t=50, b=40),
        font=dict(family="Inter, sans-serif", color=COLOR_TEXT, size=12),
        hoverlabel=dict(
            bgcolor="#1E2638",
            font_size=13,
            font_family="Inter, sans-serif"
        ),
        xaxis=dict(
            gridcolor=COLOR_GRID,
            zerolinecolor=COLOR_GRID,
            showgrid=True
        ),
        yaxis=dict(
            gridcolor=COLOR_GRID,
            zerolinecolor=COLOR_GRID,
            showgrid=True
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0.3)",
            bordercolor="rgba(255,255,255,0.1)",
            borderwidth=1,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return fig


def render_consumption_trend_chart(df: pd.DataFrame, time_frame: str = "Hourly") -> go.Figure:
    """Renders consumption trend over time with peak indicators."""
    fig = go.Figure()
    
    # Main Consumption Curve
    fig.add_trace(go.Scatter(
        x=df['timestamp'],
        y=df['consumption_kwh'],
        mode='lines',
        name='Consumption (kWh)',
        line=dict(color=COLOR_PRIMARY, width=2.5),
        fill='tozeroy',
        fillcolor='rgba(0, 242, 254, 0.12)',
        hovertemplate='%{x|%b %d, %H:%M}<br>Usage: <b>%{y:.2f} kWh</b><extra></extra>'
    ))
    
    # Peak Usage Line
    if 'consumption_kwh' in df.columns and len(df) > 0:
        peak_val = df['consumption_kwh'].max()
        peak_row = df.loc[df['consumption_kwh'] == peak_val].iloc[0]
        fig.add_trace(go.Scatter(
            x=[peak_row['timestamp']],
            y=[peak_val],
            mode='markers+text',
            name='Peak Demand',
            marker=dict(color=COLOR_DANGER, size=12, symbol='diamond'),
            text=[f"Peak: {peak_val:.1f} kWh"],
            textposition="top center",
            hovertemplate='Peak Demand: <b>%{y:.2f} kWh</b><extra></extra>'
        ))
        
        # Mean threshold line
        avg_val = df['consumption_kwh'].mean()
        fig.add_hline(
            y=avg_val,
            line_dash="dash",
            line_color=COLOR_WARNING,
            annotation_text=f"Avg ({avg_val:.1f} kWh)",
            annotation_position="bottom right"
        )
        
    title = f"{time_frame} Energy Consumption Trend (kWh)"
    _apply_dark_theme(fig, title=title)
    fig.update_xaxes(title_text="Time")
    fig.update_yaxes(title_text="Energy Consumption (kWh)")
    return fig


def render_forecast_vs_actual_chart(df: pd.DataFrame) -> go.Figure:
    """Renders actual vs predicted energy usage with confidence bounds."""
    fig = go.Figure()
    
    # Confidence Interval Shading (Upper/Lower Bounds)
    if 'forecast_upper' in df.columns and 'forecast_lower' in df.columns:
        fig.add_trace(go.Scatter(
            x=list(df['timestamp']) + list(df['timestamp'])[::-1],
            y=list(df['forecast_upper']) + list(df['forecast_lower'])[::-1],
            fill='toself',
            fillcolor='rgba(79, 172, 254, 0.15)',
            line=dict(color='rgba(255,255,255,0)'),
            hoverinfo="none",
            showlegend=True,
            name='95% Confidence Band'
        ))
    
    # Actual Consumption Line
    if 'actual_kwh' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['actual_kwh'],
            mode='lines+markers',
            name='Actual Load (kWh)',
            line=dict(color=COLOR_SUCCESS, width=2.5),
            marker=dict(size=4),
            hovertemplate='%{x|%b %d, %H:%M}<br>Actual: <b>%{y:.2f} kWh</b><extra></extra>'
        ))
        
    # AI Forecasted Line
    if 'forecast_kwh' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['forecast_kwh'],
            mode='lines',
            name='AI Forecast (kWh)',
            line=dict(color=COLOR_PRIMARY, width=2.5, dash='dash'),
            hovertemplate='%{x|%b %d, %H:%M}<br>Forecast: <b>%{y:.2f} kWh</b><extra></extra>'
        ))
        
    _apply_dark_theme(fig, title="AI Forecasting: Actual vs Predicted Load Curve")
    fig.update_xaxes(title_text="Timestamp")
    fig.update_yaxes(title_text="Power / Energy Load (kWh)")
    return fig


def render_location_breakdown_chart(df: pd.DataFrame) -> go.Figure:
    """Renders location-wise energy breakdown using grouped bar and pie representation."""
    fig = px.bar(
        df,
        x='location',
        y='consumption_kwh',
        color='consumption_kwh',
        color_continuous_scale=['#4FACFE', '#00F2FE', '#7F00FF', '#FF1744'],
        text_auto='.1f',
        labels={'consumption_kwh': 'Consumption (kWh)', 'location': 'Campus Zone / Building'}
    )
    
    _apply_dark_theme(fig, title="Building & Location-wise Energy Distribution")
    fig.update_layout(coloraxis_showscale=False)
    fig.update_traces(textfont_size=12, textposition="outside", cliponaxis=False)
    return fig


def render_anomaly_scatter_chart(df: pd.DataFrame) -> go.Figure:
    """Renders time-series anomaly scatter plot highlighting unusual spikes."""
    fig = go.Figure()
    
    # Normal Points
    normal_df = df[~df['is_anomaly']]
    fig.add_trace(go.Scatter(
        x=normal_df['timestamp'],
        y=normal_df['consumption_kwh'],
        mode='markers',
        name='Normal Usage',
        marker=dict(color='rgba(79, 172, 254, 0.4)', size=6),
        hovertemplate='%{x|%b %d, %H:%M}<br>Usage: %{y:.2f} kWh<extra></extra>'
    ))
    
    # Anomaly Points
    anom_df = df[df['is_anomaly']]
    if len(anom_df) > 0:
        fig.add_trace(go.Scatter(
            x=anom_df['timestamp'],
            y=anom_df['consumption_kwh'],
            mode='markers',
            name='Anomaly Detected',
            marker=dict(
                color=COLOR_DANGER,
                size=12,
                symbol='triangle-up',
                line=dict(color='#FFFFFF', width=1.5)
            ),
            text=anom_df['reason'] if 'reason' in anom_df.columns else '',
            hovertemplate='%{x|%b %d, %H:%M}<br>Usage: <b>%{y:.2f} kWh</b><br>Reason: %{text}<extra></extra>'
        ))
        
    _apply_dark_theme(fig, title="Anomaly Detection: Sudden Spikes & Nighttime Wastage")
    fig.update_xaxes(title_text="Timestamp")
    fig.update_yaxes(title_text="Energy Draw (kWh)")
    return fig


def render_live_gauge(current_kw: float, peak_kw: float = 30.0) -> go.Figure:
    """Renders real-time power monitor gauge."""
    pct = (current_kw / peak_kw) * 100 if peak_kw > 0 else 0
    
    if pct > 85:
        bar_color = COLOR_DANGER
    elif pct > 60:
        bar_color = COLOR_WARNING
    else:
        bar_color = COLOR_SUCCESS

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=current_kw,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "<b>Live Load (kW)</b>", 'font': {'size': 18, 'color': COLOR_TEXT}},
        delta={'reference': peak_kw * 0.5, 'increasing': {'color': COLOR_DANGER}},
        gauge={
            'axis': {'range': [None, peak_kw], 'tickwidth': 1, 'tickcolor': COLOR_TEXT},
            'bar': {'color': bar_color},
            'bgcolor': "rgba(0,0,0,0)",
            'borderwidth': 2,
            'bordercolor': COLOR_GRID,
            'steps': [
                {'range': [0, peak_kw * 0.6], 'color': 'rgba(0, 230, 118, 0.15)'},
                {'range': [peak_kw * 0.6, peak_kw * 0.85], 'color': 'rgba(255, 171, 0, 0.15)'},
                {'range': [peak_kw * 0.85, peak_kw], 'color': 'rgba(255, 23, 68, 0.15)'}
            ],
            'threshold': {
                'line': {'color': COLOR_DANGER, 'width': 4},
                'thickness': 0.75,
                'value': peak_kw * 0.9
            }
        }
    ))
    
    fig.update_layout(
        paper_bgcolor="rgba(22, 27, 46, 0.7)",
        font=dict(color=COLOR_TEXT, family="Inter, sans-serif"),
        height=280,
        margin=dict(l=30, r=30, t=40, b=20)
    )
    return fig


def render_efficiency_score_gauge(score: int = 85) -> go.Figure:
    """Renders radial Energy Efficiency Score donut gauge."""
    if score >= 80:
        color = COLOR_SUCCESS
        rating = "Excellent"
    elif score >= 65:
        color = COLOR_PRIMARY
        rating = "Good"
    elif score >= 50:
        color = COLOR_WARNING
        rating = "Fair"
    else:
        color = COLOR_DANGER
        rating = "Needs Attention"

    fig = go.Figure(go.Indicator(
        mode="number+gauge",
        value=score,
        number={'suffix': "/100", 'font': {'size': 36, 'color': color}},
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>Efficiency Score ({rating})</b>", 'font': {'size': 16, 'color': COLOR_TEXT}},
        gauge={
            'shape': "angular",
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': COLOR_TEXT},
            'bar': {'color': color, 'thickness': 0.3},
            'bgcolor': "rgba(255,255,255,0.05)",
            'borderwidth': 1,
            'bordercolor': COLOR_GRID,
            'steps': [
                {'range': [0, 50], 'color': 'rgba(255, 23, 68, 0.1)'},
                {'range': [50, 65], 'color': 'rgba(255, 171, 0, 0.1)'},
                {'range': [65, 80], 'color': 'rgba(0, 242, 254, 0.1)'},
                {'range': [80, 100], 'color': 'rgba(0, 230, 118, 0.1)'}
            ]
        }
    ))
    fig.update_layout(
        paper_bgcolor="rgba(22, 27, 46, 0.7)",
        font=dict(color=COLOR_TEXT, family="Inter, sans-serif"),
        height=240,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    return fig


def render_simulation_comparison_chart(baseline_df: pd.DataFrame, scenario_df: pd.DataFrame, scenario_name: str = "Proposed Scenario") -> go.Figure:
    """Renders side-by-side comparison of baseline vs proposed scenario load profile."""
    fig = go.Figure()
    
    # Baseline
    fig.add_trace(go.Scatter(
        x=baseline_df['hour'],
        y=baseline_df['kwh'],
        mode='lines',
        name='Current Baseline Load',
        line=dict(color=COLOR_WARNING, width=2.5, dash='dash'),
        hovertemplate='Hour %{x:02d}:00<br>Baseline: <b>%{y:.2f} kWh</b><extra></extra>'
    ))
    
    # Optimized Scenario
    fig.add_trace(go.Scatter(
        x=scenario_df['hour'],
        y=scenario_df['kwh'],
        mode='lines',
        name=f'{scenario_name}',
        line=dict(color=COLOR_SUCCESS, width=3),
        fill='tonexty',
        fillcolor='rgba(0, 230, 118, 0.12)',
        hovertemplate='Hour %{x:02d}:00<br>Optimized: <b>%{y:.2f} kWh</b><extra></extra>'
    ))
    
    _apply_dark_theme(fig, title="What-If Simulation: Load Profile Comparison (24 Hours)")
    fig.update_xaxes(title_text="Hour of Day (0 - 23)", dtick=2)
    fig.update_yaxes(title_text="Hourly Energy Consumption (kWh)")
    return fig


def render_savings_waterfall_chart(baseline_cost: float, hvac_savings: float, lighting_savings: float, solar_gen: float) -> go.Figure:
    """Renders financial savings waterfall breakdown."""
    new_cost = max(0.0, baseline_cost - hvac_savings - lighting_savings - solar_gen)
    
    fig = go.Figure(go.Waterfall(
        name="Energy Savings Breakdown",
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "total"],
        x=["Current Bill", "HVAC Schedule", "LED Retrofit", "Solar PV Offset", "Projected Bill"],
        textposition="outside",
        text=[f"${baseline_cost:,.0f}", f"-${hvac_savings:,.0f}", f"-${lighting_savings:,.0f}", f"-${solar_gen:,.0f}", f"${new_cost:,.0f}"],
        y=[baseline_cost, -hvac_savings, -lighting_savings, -solar_gen, 0],
        connector={"line": {"color": COLOR_GRID}},
        decreasing={"marker": {"color": COLOR_SUCCESS}},
        increasing={"marker": {"color": COLOR_DANGER}},
        totals={"marker": {"color": COLOR_PRIMARY}}
    ))
    
    _apply_dark_theme(fig, title="Estimated Monthly Cost Reduction Breakdown ($)")
    fig.update_yaxes(title_text="Monthly Cost ($)")
    return fig
