import json
from pathlib import Path

import joblib
import pandas as pd

from src.app_support import load_dashboard_artifacts
from src.config import ARTIFACTS, CHARTS, OUTPUTS
from src.what_if import predict_scenario


def test_saved_model_artifact_exists():
    assert (ARTIFACTS / "model_bundle.joblib").exists()
    assert "model" in joblib.load(ARTIFACTS / "model_bundle.joblib")


def test_metrics_json_required_fields():
    metrics = json.loads((ARTIFACTS / "metrics.json").read_text(encoding="utf-8"))
    assert {"selection", "final_test", "high_use", "future_forecast", "split"} <= metrics.keys()
    assert {"mae", "rmse"} <= metrics["final_test"]["baseline"].keys()
    assert {"mae", "rmse"} <= metrics["final_test"]["ml_model"].keys()


def test_future_artifact_contract():
    frame = pd.read_csv(OUTPUTS / "future_24h_forecast.csv")
    assert len(frame) == 24
    assert {"timestamp", "predicted_kwh", "baseline_kwh", "temperature_c", "occupied", "high_use", "recommendation"} <= set(frame.columns)


def test_success_and_failure_exports():
    assert len(pd.read_csv(OUTPUTS / "success_cases.csv")) >= 5
    assert len(pd.read_csv(OUTPUTS / "failure_cases.csv")) >= 5


def test_chart_artifacts_exist():
    expected = {
        "chronological_split.png",
        "test_actual_vs_ml.png",
        "baseline_vs_ml.png",
        "future_24h_forecast.png",
        "feature_importance.png",
        "model_performance_comparison.png",
        "final_test_metrics.png",
        "architecture_workflow.png",
    }
    assert expected <= {path.name for path in CHARTS.glob("*.png")}


def test_artifact_loading_smoke():
    loaded = load_dashboard_artifacts()
    assert len(loaded["forecast"]) == 24
    assert not loaded["predictions"].empty


def test_what_if_backend():
    loaded = load_dashboard_artifacts()
    row = loaded["forecast"].iloc[0]
    result = predict_scenario(loaded["model_bundle"], row, float(row["temperature_c"]) + 2, 1)
    assert result["scenario_predicted_kwh"] > 0
    assert "not a guaranteed or causal outcome" in result["disclaimer"]


def test_streamlit_entrypoint_exists():
    assert Path("app.py").exists()


def test_streamlit_app_executes_without_exception():
    from streamlit.testing.v1 import AppTest

    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(app_path).run(timeout=30)
    assert not app.exception

