"""Next-24-hour feature construction using observed history only."""

from __future__ import annotations

from datetime import timedelta

import numpy as np
import pandas as pd

from .config import FEATURE_COLUMNS
from .features import feature_matrix


def assumed_occupancy(timestamp: pd.Timestamp) -> int:
    if timestamp.dayofweek < 5:
        return int(8 <= timestamp.hour <= 18)
    if timestamp.dayofweek == 5:
        return int(9 <= timestamp.hour <= 13)
    return 0


def build_future_features(observed: pd.DataFrame, temperature_offset_c: float = 2.0) -> pd.DataFrame:
    """Build a transparent warm-day planning forecast from observed history.

    The default +2 °C offset is an explicit, plausible planning assumption over
    the recent same-hour climatology—not observed future weather.
    """
    history = observed.copy()
    history["timestamp"] = pd.to_datetime(history["timestamp"])
    last_timestamp = history["timestamp"].max()
    future_timestamps = pd.date_range(last_timestamp + timedelta(hours=1), periods=24, freq="h")

    recent = history[history["timestamp"] > last_timestamp - timedelta(days=21)].copy()
    hourly_temp = recent.groupby(recent["timestamp"].dt.hour)["temperature_c"].mean()
    temp_values = np.array([hourly_temp.loc[ts.hour] for ts in future_timestamps], dtype=float)
    temp_values += float(temperature_offset_c) + 0.4 * np.sin(2 * np.pi * np.arange(24) / 24)

    consumption_lookup = history.set_index("timestamp")["consumption_kwh"]
    rows: list[dict[str, float | int | pd.Timestamp | str]] = []
    for timestamp, temperature in zip(future_timestamps, temp_values):
        lag_24_time = timestamp - timedelta(hours=24)
        lag_168_time = timestamp - timedelta(hours=168)
        if lag_24_time not in consumption_lookup.index or lag_168_time not in consumption_lookup.index:
            raise ValueError("Future lag requires unavailable history")
        hour = timestamp.hour
        day_of_week = timestamp.dayofweek
        rows.append(
            {
                "timestamp": timestamp,
                "hour": hour,
                "day_of_week": day_of_week,
                "is_weekend": int(day_of_week >= 5),
                "temperature_c": round(float(temperature), 2),
                "occupied": assumed_occupancy(timestamp),
                "lag_24": float(consumption_lookup.loc[lag_24_time]),
                "lag_168": float(consumption_lookup.loc[lag_168_time]),
                "sin_hour": np.sin(2 * np.pi * hour / 24),
                "cos_hour": np.cos(2 * np.pi * hour / 24),
                "sin_day_of_week": np.sin(2 * np.pi * day_of_week / 7),
                "cos_day_of_week": np.cos(2 * np.pi * day_of_week / 7),
                "input_disclosure": (
                    "Future temperature and occupancy are simulated/assumed prototype inputs. "
                    f"Temperature uses recent same-hour climatology plus a disclosed {temperature_offset_c:+.1f} °C warm-day planning offset."
                ),
            }
        )
    future = pd.DataFrame(rows)
    if len(future) != 24 or list(feature_matrix(future).columns) != FEATURE_COLUMNS:
        raise AssertionError("Invalid future feature frame")
    return future


def forecast_next_24_hours(model, observed: pd.DataFrame) -> pd.DataFrame:
    future = build_future_features(observed)
    future["predicted_kwh"] = model.predict(feature_matrix(future))
    future["baseline_kwh"] = future["lag_24"]
    return future

