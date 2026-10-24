"""Presentation helpers; read canonical artifacts without training or writing them."""
from html import escape

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

TEAL, SLATE, AMBER, INK = "#087F78", "#718198", "#B35A00", "#182D40"
PAGES = ["Overview", "24-Hour Forecast", "Model Performance", "Peak Insights", "Error Analysis", "Responsible AI / About"]
FEATURE_NAMES = {
    "hour": "Hour of day", "day_of_week": "Day of week", "is_weekend": "Weekend",
    "temperature_c": "Outdoor temperature", "occupied": "Building occupancy",
    "lag_24": "Usage 24 hours earlier", "lag_168": "Usage 1 week earlier",
    "sin_hour": "Hour cycle · sine", "cos_hour": "Hour cycle · cosine",
    "sin_day_of_week": "Week cycle · sine", "cos_day_of_week": "Week cycle · cosine",
}
MODEL_CAVEAT = (
    "Random Forest was selected because it achieved the lowest validation MAE in the canonical run. "
    "Its validation performance was effectively tied with HistGradientBoosting; we do not claim decisive superiority."
)


def apply_style():
    st.markdown("""<style>
    .block-container {max-width:1440px;padding-top:4.5rem!important;padding-bottom:2rem;}
    h1 {font-size:2.15rem!important;letter-spacing:-.045em;line-height:1.15!important;}
    h2 {font-size:1.4rem!important;letter-spacing:-.025em;}
    h3 {font-size:1.08rem!important;}
    [data-testid="stSidebar"] {background:#edf2f5;border-right:1px solid #dce4eb;}
    [data-testid="stMetric"] {background:white;border:1px solid #dce4eb;border-radius:12px;padding:16px;}
    [data-testid="stMetricValue"] {font-size:1.65rem;}
    [data-testid="stMetricLabel"] {font-size:.85rem;color:#435b70;}
    .eyebrow {font-size:.72rem;letter-spacing:.14em;font-weight:750;color:#087f78;text-transform:uppercase;margin-bottom:.5rem;}
    .badge {display:inline-block;background:#e2efeb;color:#24574e;border:1px solid #c4ddd4;border-radius:20px;padding:4px 11px;font-size:.76rem;font-weight:600;}
    .attention {background:#fff9ef;border:1px solid #e8cda1;border-left:4px solid #b35a00;border-radius:12px;padding:19px 22px;margin:8px 0 16px;}
    .attention h3 {margin:0 0 8px;color:#754100;}
    .attention p {margin:4px 0;font-size:.93rem;}
    .proof {background:#e7f2ef;border-radius:10px;padding:12px 18px;color:#235c53;font-size:.9rem;margin:12px 0;}
    .footnote {border-top:1px solid #dce4eb;margin-top:22px;padding-top:12px;color:#526779;font-size:.78rem;}
    [data-testid="stRadio"] label {padding:5px 0;}
    @media(max-width:900px) {.block-container {padding:4rem 1rem 1.3rem;} h1 {font-size:1.8rem!important;}}
    </style>""", unsafe_allow_html=True)


def chart_style(fig, height=380):
    fig.update_layout(template="plotly_white", height=height, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="white",
        font=dict(family="Arial, sans-serif", color=INK, size=12), margin=dict(l=12, r=22, t=30, b=20),
        legend=dict(orientation="h", y=1.16, x=0, font=dict(size=11)), hoverlabel=dict(bgcolor="white", font=dict(color=INK)))
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#e9eef3", zeroline=False)
    return fig


def forecast_chart(frame, threshold):
    custom = [[float(row.baseline_kwh), float(row.temperature_c), "Occupied" if row.occupied else "Unoccupied", "HIGH USE" if row.high_use else "Normal"] for row in frame.itertuples()]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=frame.timestamp, y=frame.predicted_kwh, name="ML forecast", mode="lines+markers",
        line=dict(color=TEAL, width=3), marker=dict(size=5), customdata=custom,
        hovertemplate="%{x|%d %b · %H:%M}<br>Forecast: %{y:.2f} kWh<br>Baseline: %{customdata[0]:.2f} kWh<br>Assumed temperature: %{customdata[1]:.1f} °C<br>%{customdata[2]} · %{customdata[3]}<extra></extra>"))
    fig.add_trace(go.Scatter(x=frame.timestamp, y=frame.baseline_kwh, name="Previous-day baseline", mode="lines",
        line=dict(color=SLATE, width=2, dash="dash"), hovertemplate="Baseline: %{y:.2f} kWh<extra></extra>"))
    fig.add_trace(go.Scatter(x=frame.timestamp, y=[threshold]*len(frame), name="Training P90 threshold", mode="lines",
        line=dict(color=AMBER, width=1.5, dash="dot"), hovertemplate="Threshold: %{y:.3f} kWh<extra></extra>"))
    high = frame.loc[frame.high_use]
    fig.add_trace(go.Scatter(x=high.timestamp, y=high.predicted_kwh, name="▲ HIGH USE", mode="markers",
        marker=dict(color=AMBER, symbol="triangle-up", size=13, line=dict(color="white", width=1)),
        hovertemplate="HIGH USE · %{x|%H:%M}<br>%{y:.2f} kWh<extra></extra>"))
    fig.update_layout(hovermode="x unified")
    fig.update_xaxes(title="Forecast hour", tickformat="%H:%M", dtick=3*3600000)
    fig.update_yaxes(title="Hourly energy (kWh)", rangemode="tozero")
    return chart_style(fig, 375)


def show_chart(fig, key):
    st.plotly_chart(fig, width="stretch", key=key, config={"displaylogo": False, "scrollZoom": False})


def forecast_table(frame):
    return pd.DataFrame({"Hour": frame.timestamp.dt.strftime("%d %b %H:%M"),
        "Forecast (kWh)": frame.predicted_kwh.round(2), "Baseline (kWh)": frame.baseline_kwh.round(2),
        "Δ baseline (kWh)": (frame.predicted_kwh-frame.baseline_kwh).round(2), "Temperature (°C)": frame.temperature_c.round(1),
        "Occupancy": np.where(frame.occupied, "Occupied", "Unoccupied"), "Status": np.where(frame.high_use, "▲ HIGH USE", "Normal"),
        "Recommended check": frame.recommendation})


def hour_detail(row, threshold):
    status = "▲ HIGH USE" if row.high_use else "NORMAL"
    st.markdown(f"### {row.timestamp:%d %b · %H:%M} · {status}")
    a,b,c = st.columns(3)
    a.metric("Forecast", f"{row.predicted_kwh:.2f} kWh")
    b.metric("Assumed temperature", f"{row.temperature_c:.1f} °C")
    c.metric("Building schedule", "Occupied" if row.occupied else "Unoccupied")
    st.caption(f"Training threshold: {threshold:.3f} kWh · Difference vs baseline: {row.predicted_kwh-row.baseline_kwh:+.2f} kWh")
    st.markdown("**Why might this hour be high?**" if row.high_use else "**What contributes to this forecast?**")
    st.write(row.explanation)
    st.info(row.recommendation)


def attention_card(forecast, threshold):
    peak = forecast.loc[forecast.predicted_kwh.idxmax()]
    hours = ", ".join(forecast.loc[forecast.high_use].timestamp.dt.strftime("%H:%M")) or "None"
    st.markdown(f'''<div class="attention"><div class="eyebrow">Manager attention</div>
    <h3>Peak at {peak.timestamp:%H:%M} · {peak.predicted_kwh:.2f} kWh</h3>
    <p><b>HIGH USE hours: {hours}</b> · threshold {threshold:.3f} kWh</p>
    <p>{peak.temperature_c:.1f} °C assumed · {"Occupied" if peak.occupied else "Unoccupied"}</p>
    <p>{escape(peak.recommendation)}</p></div>''', unsafe_allow_html=True)


def error_table(frame):
    return frame.rename(columns={"timestamp":"Timestamp", "actual_kwh":"Actual (kWh)", "predicted_kwh":"ML (kWh)",
        "baseline_kwh":"Baseline (kWh)", "absolute_error":"ML error (kWh)", "temperature_c":"Temperature (°C)",
        "occupied":"Occupied (0/1)", "event_type":"Simulated context"})[["Timestamp", "Actual (kWh)", "ML (kWh)",
        "Baseline (kWh)", "ML error (kWh)", "Temperature (°C)", "Occupied (0/1)", "Simulated context"]].round(2)
