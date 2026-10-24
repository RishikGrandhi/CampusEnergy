"""Transparent high-use explanations and human decision-support rules."""

from __future__ import annotations

import pandas as pd


def training_high_use_threshold(train_consumption: pd.Series, quantile: float = 0.90) -> float:
    if train_consumption.empty:
        raise ValueError("Training consumption cannot be empty")
    return float(train_consumption.quantile(quantile))


def recommendation_for_hour(row: pd.Series, consecutive_high: bool = False) -> str:
    checks: list[str] = []
    if bool(row.get("high_use", False)) and int(row["occupied"]) == 0:
        checks.append("Recommended check: verify after-hours HVAC, lighting and plug loads")
    elif bool(row.get("high_use", False)) and float(row["temperature_c"]) >= 30 and int(row["occupied"]) == 1:
        checks.append("Recommended check: verify HVAC cooling demand and temperature setpoints during this period")
    elif bool(row.get("high_use", False)):
        checks.append("Recommended check: review the drivers of predicted high building demand")
    if float(row["predicted_kwh"]) > float(row["baseline_kwh"]) * 1.15:
        checks.append("Facility manager should verify whether unusual events or high-power equipment are scheduled")
    if consecutive_high:
        checks.append("Decision-support recommendation: review flexible-load scheduling and peak-demand planning")
    if not checks:
        checks.append("Recommended check: monitor the forecast; no high-use condition is currently flagged")
    return "; ".join(checks) + ". Human verification is required before any action."


def explanation_for_hour(row: pd.Series, threshold: float) -> str:
    factors: list[str] = []
    if float(row["temperature_c"]) >= 30:
        factors.append("high assumed outdoor temperature")
    if int(row["occupied"]) == 1:
        factors.append("scheduled building occupancy")
    if float(row["lag_24"]) >= threshold:
        factors.append("high same-hour usage one day earlier")
    if int(row["hour"]) in range(12, 18):
        factors.append("afternoon demand pattern")
    if not factors:
        factors.append("historical calendar and lag patterns")
    return "Contributing indicators: " + ", ".join(factors) + ". These indicators do not prove causation."


def add_decision_support(frame: pd.DataFrame, threshold: float) -> pd.DataFrame:
    result = frame.copy()
    result["high_use"] = result["predicted_kwh"] >= threshold
    adjacent = result["high_use"] & (result["high_use"].shift(1, fill_value=False) | result["high_use"].shift(-1, fill_value=False))
    result["recommendation"] = [
        recommendation_for_hour(row, bool(adjacent.iloc[i])) for i, (_, row) in enumerate(result.iterrows())
    ]
    result["explanation"] = [explanation_for_hour(row, threshold) for _, row in result.iterrows()]
    return result

