from datetime import timedelta

import pandas as pd

from src.forecasting import build_future_features
from src.recommendations import add_decision_support, recommendation_for_hour, training_high_use_threshold


def test_training_derived_threshold(splits):
    train, _, _ = splits
    assert training_high_use_threshold(train["consumption_kwh"]) == train["consumption_kwh"].quantile(0.90)


def test_future_has_exactly_24_rows(raw_data):
    assert len(build_future_features(raw_data)) == 24


def test_future_strictly_follows_observations(raw_data):
    future = build_future_features(raw_data)
    assert future["timestamp"].min() == raw_data["timestamp"].max() + timedelta(hours=1)
    assert future["timestamp"].is_monotonic_increasing


def test_future_lags_use_observed_history(raw_data):
    future = build_future_features(raw_data)
    lookup = raw_data.set_index("timestamp")["consumption_kwh"]
    for _, row in future.iterrows():
        assert row["lag_24"] == lookup.loc[row["timestamp"] - timedelta(hours=24)]
        assert row["lag_168"] == lookup.loc[row["timestamp"] - timedelta(hours=168)]


def test_future_input_assumption_is_disclosed(raw_data):
    future = build_future_features(raw_data)
    assert "simulated/assumed" in future.iloc[0]["input_disclosure"]
    assert "+2.0" in future.iloc[0]["input_disclosure"]


def test_after_hours_recommendation():
    row = pd.Series({"high_use": True, "occupied": 0, "temperature_c": 27, "predicted_kwh": 100, "baseline_kwh": 90})
    text = recommendation_for_hour(row)
    assert "after-hours" in text
    assert "Human verification" in text


def test_hot_occupied_recommendation():
    row = pd.Series({"high_use": True, "occupied": 1, "temperature_c": 34, "predicted_kwh": 100, "baseline_kwh": 90})
    assert "HVAC cooling demand" in recommendation_for_hour(row)


def test_large_increase_recommendation():
    row = pd.Series({"high_use": False, "occupied": 1, "temperature_c": 25, "predicted_kwh": 120, "baseline_kwh": 90})
    assert "unusual events" in recommendation_for_hour(row)


def test_consecutive_high_rule():
    frame = pd.DataFrame(
        {
            "predicted_kwh": [40.0, 100.0, 105.0],
            "baseline_kwh": [42.0, 90.0, 92.0],
            "temperature_c": [25.0, 32.0, 32.0],
            "occupied": [0, 1, 1],
            "lag_24": [42.0, 90.0, 92.0],
            "hour": [8, 9, 10],
        }
    )
    result = add_decision_support(frame, 95.0)
    assert result["high_use"].tolist() == [False, True, True]
    assert "peak-demand planning" in result.iloc[1]["recommendation"]

