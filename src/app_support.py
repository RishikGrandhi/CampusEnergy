from __future__ import annotations

import json

import joblib
import pandas as pd

from .config import ARTIFACTS, OUTPUTS


def load_dashboard_artifacts() -> dict:
    required = {
        "metrics": ARTIFACTS / "metrics.json",
        "model": ARTIFACTS / "model_bundle.joblib",
        "forecast": OUTPUTS / "future_24h_forecast.csv",
        "predictions": OUTPUTS / "test_predictions.csv",
        "importance": ARTIFACTS / "feature_importance.csv",
    }
    missing = [str(path) for path in required.values() if not path.exists()]
    if missing:
        raise FileNotFoundError("Run `python -m src.pipeline all` first. Missing: " + ", ".join(missing))
    return {
        "metrics": json.loads(required["metrics"].read_text(encoding="utf-8")),
        "model_bundle": joblib.load(required["model"]),
        "forecast": pd.read_csv(required["forecast"], parse_dates=["timestamp"]),
        "predictions": pd.read_csv(required["predictions"], parse_dates=["timestamp"]),
        "importance": pd.read_csv(required["importance"]),
    }

