"""Leakage-safe feature engineering and chronological splitting."""

from __future__ import annotations

import numpy as np
import pandas as pd

from .config import FEATURE_COLUMNS, TARGET_COLUMN


def build_features(raw: pd.DataFrame) -> pd.DataFrame:
    frame = raw.copy()
    frame["timestamp"] = pd.to_datetime(frame["timestamp"])
    frame = frame.sort_values("timestamp").reset_index(drop=True)
    frame["hour"] = frame["timestamp"].dt.hour
    frame["day_of_week"] = frame["timestamp"].dt.dayofweek
    frame["is_weekend"] = (frame["day_of_week"] >= 5).astype(int)
    frame["lag_24"] = frame[TARGET_COLUMN].shift(24)
    frame["lag_168"] = frame[TARGET_COLUMN].shift(168)
    frame["sin_hour"] = np.sin(2 * np.pi * frame["hour"] / 24)
    frame["cos_hour"] = np.cos(2 * np.pi * frame["hour"] / 24)
    frame["sin_day_of_week"] = np.sin(2 * np.pi * frame["day_of_week"] / 7)
    frame["cos_day_of_week"] = np.cos(2 * np.pi * frame["day_of_week"] / 7)
    return frame.dropna(subset=["lag_24", "lag_168"]).reset_index(drop=True)


def chronological_split(
    frame: pd.DataFrame, train_fraction: float = 0.70, validation_fraction: float = 0.15
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if not 0 < train_fraction < 1 or not 0 < validation_fraction < 1:
        raise ValueError("Split fractions must be between zero and one")
    if train_fraction + validation_fraction >= 1:
        raise ValueError("Training and validation fractions must leave a test period")
    n_rows = len(frame)
    train_end = int(n_rows * train_fraction)
    validation_end = train_end + int(n_rows * validation_fraction)
    train = frame.iloc[:train_end].copy()
    validation = frame.iloc[train_end:validation_end].copy()
    test = frame.iloc[validation_end:].copy()
    if train.empty or validation.empty or test.empty:
        raise ValueError("All chronological periods must contain rows")
    if not (
        train["timestamp"].max() < validation["timestamp"].min()
        and validation["timestamp"].max() < test["timestamp"].min()
    ):
        raise ValueError("Chronological split boundaries overlap")
    return train, validation, test


def feature_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    if TARGET_COLUMN in FEATURE_COLUMNS:
        raise AssertionError("Target leakage: target appears in feature list")
    return frame[FEATURE_COLUMNS].copy()


def previous_day_baseline(frame: pd.DataFrame) -> pd.Series:
    """Exact t-24 actual, already aligned by leakage-safe feature construction."""
    if frame["lag_24"].isna().any():
        raise ValueError("Baseline is unavailable for one or more rows")
    return frame["lag_24"].copy()

