import numpy as np
import pytest
from datetime import timedelta

from src.evaluation import mae_improvement_percent, regression_metrics
from src.features import previous_day_baseline


def test_split_nonempty(splits):
    assert all(len(part) > 0 for part in splits)


def test_train_precedes_validation(splits):
    train, validation, _ = splits
    assert train["timestamp"].max() < validation["timestamp"].min()


def test_validation_precedes_test(splits):
    _, validation, test = splits
    assert validation["timestamp"].max() < test["timestamp"].min()


def test_exact_t_minus_24_baseline(raw_data, splits):
    _, _, test = splits
    lookup = raw_data.set_index("timestamp")["consumption_kwh"]
    baseline = previous_day_baseline(test)
    expected = test["timestamp"].map(lambda t: lookup.loc[t - timedelta(hours=24)])
    assert baseline.to_numpy() == pytest.approx(expected.to_numpy())


def test_metric_calculation_sanity():
    metrics = regression_metrics([1, 2, 3], [1, 3, 5])
    assert metrics["mae"] == pytest.approx(1.0)
    assert metrics["rmse"] == pytest.approx(np.sqrt(5 / 3))
    assert mae_improvement_percent(10, 7.5) == pytest.approx(25.0)

