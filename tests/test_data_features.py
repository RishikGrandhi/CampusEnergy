from datetime import timedelta

import pandas as pd
import pytest

from src.config import FEATURE_COLUMNS, TARGET_COLUMN
from src.data import generate_synthetic_data, validate_raw_data
from src.features import feature_matrix


def test_deterministic_generation(raw_data):
    pd.testing.assert_frame_equal(raw_data, generate_synthetic_data())


def test_expected_raw_row_count(raw_data):
    assert len(raw_data) == 180 * 24


def test_unique_timestamps(raw_data):
    assert raw_data["timestamp"].is_unique


def test_chronological_timestamps(raw_data):
    assert raw_data["timestamp"].is_monotonic_increasing


def test_exact_hourly_frequency(raw_data):
    assert (raw_data["timestamp"].diff().dropna().dt.total_seconds() == 3600).all()


def test_data_domain_validation(raw_data):
    validate_raw_data(raw_data)
    assert (raw_data["consumption_kwh"] >= 0).all()
    assert set(raw_data["occupied"].unique()) <= {0, 1}


def test_lag_24_correctness(raw_data, featured):
    lookup = raw_data.set_index("timestamp")["consumption_kwh"]
    sample = featured.iloc[::137]
    expected = sample["timestamp"].map(lambda t: lookup.loc[t - timedelta(hours=24)])
    assert sample["lag_24"].to_numpy() == pytest.approx(expected.to_numpy())


def test_lag_168_correctness(raw_data, featured):
    lookup = raw_data.set_index("timestamp")["consumption_kwh"]
    sample = featured.iloc[::137]
    expected = sample["timestamp"].map(lambda t: lookup.loc[t - timedelta(hours=168)])
    assert sample["lag_168"].to_numpy() == pytest.approx(expected.to_numpy())


def test_target_excluded_from_features(featured):
    assert TARGET_COLUMN not in FEATURE_COLUMNS
    assert TARGET_COLUMN not in feature_matrix(featured).columns

