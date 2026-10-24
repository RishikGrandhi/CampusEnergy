from __future__ import annotations

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


def regression_metrics(actual, predicted) -> dict[str, float]:
    return {
        "mae": float(mean_absolute_error(actual, predicted)),
        "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
    }


def mae_improvement_percent(baseline_mae: float, model_mae: float) -> float:
    if baseline_mae <= 0:
        raise ValueError("Baseline MAE must be positive")
    return float((baseline_mae - model_mae) / baseline_mae * 100.0)

