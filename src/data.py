"""Deterministic synthetic campus-building energy data."""

from __future__ import annotations

import json
from datetime import timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from .config import DATA_RAW, N_HOURS, RANDOM_SEED, START_TIMESTAMP, ensure_directories


def generate_synthetic_data(seed: int = RANDOM_SEED, n_hours: int = N_HOURS) -> pd.DataFrame:
    """Return realistic, deterministic hourly prototype data.

    Event labels are retained for honest error analysis but are never model inputs.
    """
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range(START_TIMESTAMP, periods=n_hours, freq="h")
    hour = timestamps.hour.to_numpy()
    dow = timestamps.dayofweek.to_numpy()
    day_index = np.arange(n_hours) / 24.0

    weather_shock = np.zeros(n_hours)
    innovations = rng.normal(0.0, 0.48, n_hours)
    for i in range(1, n_hours):
        weather_shock[i] = 0.92 * weather_shock[i - 1] + innovations[i]
    seasonal = 1.8 * np.sin(2 * np.pi * (day_index - 35) / 180)
    diurnal = 4.3 * np.sin(2 * np.pi * (hour - 7) / 24)
    temperature = np.clip(27.0 + seasonal + diurnal + weather_shock, 16.0, 40.0)

    weekday_hours = (dow < 5) & (hour >= 8) & (hour <= 18)
    saturday_hours = (dow == 5) & (hour >= 9) & (hour <= 13)
    occupied = (weekday_hours | saturday_hours).astype(int)

    base_load = 24.0 + 1.3 * np.sin(2 * np.pi * (hour - 4) / 24)
    daytime_shape = 7.0 * np.exp(-((hour - 14.0) / 4.5) ** 2)
    occupancy_load = occupied * (24.0 + daytime_shape)
    cooling_load = np.maximum(temperature - 22.0, 0.0) * (1.25 + 1.25 * occupied)
    weekday_lab = ((dow < 5) & (hour >= 10) & (hour <= 16)).astype(float) * 5.5
    slow_efficiency_drift = 0.012 * day_index
    noise = rng.normal(0.0, 2.2, n_hours)
    consumption = base_load + occupancy_load + cooling_load + weekday_lab + slow_efficiency_drift + noise

    event_type = np.full(n_hours, "normal", dtype=object)
    event_specs = [
        (34 * 24 + 18, 5, 28.0, "after_hours_equipment"),
        (61 * 24 + 11, 7, 32.0, "special_event"),
        (88 * 24 + 9, 4, 25.0, "laboratory_load"),
        (119 * 24 + 19, 6, 30.0, "after_hours_equipment"),
        (145 * 24 + 12, 8, 35.0, "special_event"),
        (167 * 24 + 10, 5, 38.0, "laboratory_load"),
        (176 * 24 + 17, 4, 31.0, "special_event"),
    ]
    for start, duration, increase, label in event_specs:
        if start < n_hours:
            end = min(start + duration, n_hours)
            consumption[start:end] += increase
            event_type[start:end] = label

    frame = pd.DataFrame(
        {
            "timestamp": timestamps,
            "temperature_c": np.round(temperature, 2),
            "occupied": occupied,
            "consumption_kwh": np.round(np.maximum(consumption, 1.0), 3),
            "event_type": event_type,
        }
    )
    validate_raw_data(frame)
    return frame


def validate_raw_data(frame: pd.DataFrame) -> None:
    required = {"timestamp", "temperature_c", "occupied", "consumption_kwh"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")
    timestamps = pd.to_datetime(frame["timestamp"])
    if timestamps.duplicated().any() or not timestamps.is_monotonic_increasing:
        raise ValueError("Timestamps must be unique and sorted")
    if len(timestamps) > 1 and not (timestamps.diff().dropna().dt.total_seconds() == timedelta(hours=1).total_seconds()).all():
        raise ValueError("Timestamps must have exact hourly frequency")
    if (frame["consumption_kwh"] < 0).any():
        raise ValueError("Consumption cannot be negative")
    if not set(frame["occupied"].unique()).issubset({0, 1}):
        raise ValueError("Occupied must contain only 0/1")
    if not frame["temperature_c"].between(-10, 55).all():
        raise ValueError("Temperature is outside the prototype plausibility range")


def save_raw_data(frame: pd.DataFrame, path: Path | None = None) -> Path:
    ensure_directories()
    destination = path or DATA_RAW / "campus_energy_hourly.csv"
    frame.to_csv(destination, index=False)
    metadata = {
        "disclosure": "Synthetic / simulated prototype campus energy data",
        "random_seed": RANDOM_SEED,
        "rows": int(len(frame)),
        "start": str(frame["timestamp"].min()),
        "end": str(frame["timestamp"].max()),
        "frequency": "hourly",
        "event_rows": int((frame["event_type"] != "normal").sum()),
    }
    (destination.parent / "dataset_metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return destination

