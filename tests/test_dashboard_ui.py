"""Exercise actual page routing, artifact values and scenario widget state."""
from pathlib import Path

import pytest
from streamlit.testing.v1 import AppTest

from src.app_support import load_dashboard_artifacts
from src.dashboard import forecast_table
from src.what_if import predict_scenario

APP = Path(__file__).resolve().parents[1] / "app.py"


@pytest.mark.parametrize("page", ["overview", "forecast", "performance", "peaks", "errors", "about"])
def test_dashboard_page_executes(page):
    app = AppTest.from_file(APP).run(timeout=30)
    app.switch_page(f"ui_pages/{page}.py").run(timeout=30)
    assert not app.exception
    assert len(app.title) == 1


def test_scenario_controls_match_backend_and_reset_for_new_hour():
    data = load_dashboard_artifacts()
    app = AppTest.from_file(APP).run(timeout=30)
    app.switch_page("ui_pages/peaks.py").run(timeout=30)
    chosen = app.selectbox(key="scenario_hour").value
    row = data["forecast"].iloc[chosen]
    app.slider(key=f"scenario_temp_{chosen}").set_value(35.0)
    app.selectbox(key=f"scenario_occ_{chosen}").set_value(0).run(timeout=30)
    expected = predict_scenario(data["model_bundle"],row,35.0,0)["scenario_predicted_kwh"]
    values = {metric.label:metric.value for metric in app.metric}
    assert values["Scenario forecast"] == f"{expected:.2f} kWh"
    assert values["Difference from original"] == f"{expected-row.predicted_kwh:+.2f} kWh"
    assert any("not a guaranteed or causal outcome" in warning.value for warning in app.warning)
    app.selectbox(key="scenario_hour").set_value(0).run(timeout=30)
    assert app.slider(key="scenario_temp_0").value == data["forecast"].iloc[0].temperature_c
    values = {metric.label:metric.value for metric in app.metric}
    assert values["Difference from original"] == "+0.00 kWh"
    assert not app.exception


def test_displayed_forecast_delta_and_status_preserve_artifact():
    frame = load_dashboard_artifacts()["forecast"]
    table = forecast_table(frame)
    assert table["Δ baseline (kWh)"].tolist() == (frame.predicted_kwh-frame.baseline_kwh).round(2).tolist()
    assert table.Status.eq("▲ HIGH USE").tolist() == frame.high_use.tolist()


def test_missing_artifact_shows_restore_message_without_training(monkeypatch):
    import streamlit as st
    import src.app_support as support

    def missing_package():
        raise FileNotFoundError("Simulated missing canonical package")

    st.cache_resource.clear()
    monkeypatch.setattr(support, "load_dashboard_artifacts", missing_package)
    try:
        app = AppTest.from_file(APP).run(timeout=30)
        assert not app.exception
        assert len(app.error) == 1
        assert "Restore the canonical Phase 1 artifacts" in app.error[0].value
        assert not app.metric
    finally:
        st.cache_resource.clear()


def test_native_router_does_not_expose_uninitialized_legacy_pages():
    # Legacy auto-discovery can route a fresh deep link around app.py entirely.
    assert not list((APP.parent / "pages").glob("*.py"))
    assert len(list((APP.parent / "ui_pages").glob("*.py"))) == 6
