"""Artifact-level regression checks for the Phase 1 integrity contract."""

from __future__ import annotations

import json
from datetime import timedelta

import joblib
import numpy as np
import pandas as pd

from src.config import ARTIFACTS, DATA_PROCESSED, DATA_RAW, OUTPUTS


def test_canonical_evaluation_artifacts_reconcile_independently():
    """Rebuild evaluation alignment and metrics without pipeline helpers."""
    raw = pd.read_csv(DATA_RAW / "campus_energy_hourly.csv", parse_dates=["timestamp"])
    processed = pd.read_csv(DATA_PROCESSED / "featured_energy_data.csv", parse_dates=["timestamp"])
    predictions = pd.read_csv(OUTPUTS / "test_predictions.csv", parse_dates=["timestamp"])
    metrics = json.loads((ARTIFACTS / "metrics.json").read_text(encoding="utf-8"))

    train_end = int(len(processed) * 0.70)
    validation_end = train_end + int(len(processed) * 0.15)
    test = processed.iloc[validation_end:].reset_index(drop=True)
    lookup = raw.set_index("timestamp")["consumption_kwh"]
    independent_baseline = test["timestamp"].map(lambda ts: lookup.loc[ts - timedelta(hours=24)])

    assert predictions["timestamp"].tolist() == test["timestamp"].tolist()
    assert len(predictions) == len(test) == metrics["final_test"]["test_rows"]
    np.testing.assert_allclose(predictions["baseline_kwh"], independent_baseline, rtol=0, atol=1e-12)
    np.testing.assert_allclose(predictions["actual_kwh"], test["consumption_kwh"], rtol=0, atol=1e-12)

    baseline_error = predictions["actual_kwh"] - independent_baseline
    model_error = predictions["actual_kwh"] - predictions["predicted_kwh"]
    recomputed = {
        "baseline_mae": float(np.abs(baseline_error).mean()),
        "baseline_rmse": float(np.sqrt(np.square(baseline_error).mean())),
        "model_mae": float(np.abs(model_error).mean()),
        "model_rmse": float(np.sqrt(np.square(model_error).mean())),
    }
    recomputed["improvement"] = (
        (recomputed["baseline_mae"] - recomputed["model_mae"]) / recomputed["baseline_mae"] * 100
    )
    expected = metrics["final_test"]
    assert np.isclose(recomputed["baseline_mae"], expected["baseline"]["mae"])
    assert np.isclose(recomputed["baseline_rmse"], expected["baseline"]["rmse"])
    assert np.isclose(recomputed["model_mae"], expected["ml_model"]["mae"])
    assert np.isclose(recomputed["model_rmse"], expected["ml_model"]["rmse"])
    assert np.isclose(recomputed["improvement"], expected["mae_improvement_percent"])


def test_saved_artifacts_preserve_temporal_provenance():
    """Protect split, selection, threshold, and future-history provenance."""
    raw = pd.read_csv(DATA_RAW / "campus_energy_hourly.csv", parse_dates=["timestamp"])
    processed = pd.read_csv(DATA_PROCESSED / "featured_energy_data.csv", parse_dates=["timestamp"])
    future = pd.read_csv(OUTPUTS / "future_24h_forecast.csv", parse_dates=["timestamp"])
    metrics = json.loads((ARTIFACTS / "metrics.json").read_text(encoding="utf-8"))
    bundle = joblib.load(ARTIFACTS / "model_bundle.joblib")

    train_end = int(len(processed) * 0.70)
    validation_end = train_end + int(len(processed) * 0.15)
    train = processed.iloc[:train_end]
    validation = processed.iloc[train_end:validation_end]
    test = processed.iloc[validation_end:]
    assert train["timestamp"].max() < validation["timestamp"].min()
    assert validation["timestamp"].max() < test["timestamp"].min()
    assert pd.Timestamp(bundle["fit_period"]["end"]) == validation["timestamp"].max()
    assert pd.Timestamp(bundle["fit_period"]["end"]) < test["timestamp"].min()

    candidates = metrics["selection"]["validation_candidates"]
    assert metrics["selection"]["selected_model"] == min(candidates, key=lambda name: candidates[name]["mae"])
    assert metrics["selection"]["test_used_for_selection"] is False

    independent_threshold = float(train["consumption_kwh"].quantile(0.90))
    assert np.isclose(independent_threshold, metrics["high_use"]["threshold_kwh"])
    assert future["high_use"].tolist() == (future["predicted_kwh"] >= independent_threshold).tolist()
    assert int(future["high_use"].sum()) == metrics["high_use"]["future_flagged_hours"] == 2

    expected_timestamps = pd.date_range(raw["timestamp"].max() + timedelta(hours=1), periods=24, freq="h")
    assert future["timestamp"].tolist() == expected_timestamps.tolist()
    assert "actual_kwh" not in future.columns
    assert "consumption_kwh" not in future.columns
    history = raw.set_index("timestamp")["consumption_kwh"]
    for row in future.itertuples(index=False):
        assert row.timestamp <= expected_timestamps[-1]
        assert row.timestamp - timedelta(hours=24) <= raw["timestamp"].max()
        assert row.timestamp - timedelta(hours=168) <= raw["timestamp"].max()
        assert np.isclose(row.lag_24, history.loc[row.timestamp - timedelta(hours=24)])
        assert np.isclose(row.lag_168, history.loc[row.timestamp - timedelta(hours=168)])

    expected_occupancy = [
        int((ts.dayofweek < 5 and 8 <= ts.hour <= 18) or (ts.dayofweek == 5 and 9 <= ts.hour <= 13))
        for ts in expected_timestamps
    ]
    assert future["occupied"].tolist() == expected_occupancy
    recent = raw[raw["timestamp"] > raw["timestamp"].max() - timedelta(days=21)]
    hourly_climatology = recent.groupby(recent["timestamp"].dt.hour)["temperature_c"].mean()
    expected_temperature = np.array(
        [hourly_climatology.loc[ts.hour] for ts in expected_timestamps]
    ) + 2.0 + 0.4 * np.sin(2 * np.pi * np.arange(24) / 24)
    np.testing.assert_allclose(future["temperature_c"], np.round(expected_temperature, 2), rtol=0, atol=1e-12)
    assert future["input_disclosure"].str.contains("simulated/assumed", regex=False).all()

