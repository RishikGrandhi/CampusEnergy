"""Reusable scenario analysis for one already-defined forecast hour."""

from __future__ import annotations

import pandas as pd

from .config import FEATURE_COLUMNS


def predict_scenario(model_bundle: dict, forecast_row: pd.Series, temperature_c: float, occupied: int) -> dict:
    if occupied not in (0, 1):
        raise ValueError("occupied must be 0 or 1")
    scenario = forecast_row.copy()
    scenario["temperature_c"] = float(temperature_c)
    scenario["occupied"] = int(occupied)
    features = pd.DataFrame([{column: scenario[column] for column in FEATURE_COLUMNS}])
    prediction = float(model_bundle["model"].predict(features)[0])
    return {
        "timestamp": str(pd.Timestamp(scenario["timestamp"])),
        "scenario_predicted_kwh": prediction,
        "temperature_c": float(temperature_c),
        "occupied": int(occupied),
        "disclaimer": "Scenario analysis — not a guaranteed or causal outcome.",
    }

