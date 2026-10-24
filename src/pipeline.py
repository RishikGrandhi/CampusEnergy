"""End-to-end data, training, evaluation, forecasting, and artifact pipeline."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingRegressor, RandomForestRegressor
from sklearn.inspection import permutation_importance

from .charts import create_all_charts
from .config import ARTIFACTS, DATA_PROCESSED, DATA_RAW, FEATURE_COLUMNS, OUTPUTS, RANDOM_SEED, TARGET_COLUMN, ensure_directories
from .data import generate_synthetic_data, save_raw_data, validate_raw_data
from .evaluation import mae_improvement_percent, regression_metrics
from .features import build_features, chronological_split, feature_matrix, previous_day_baseline
from .forecasting import forecast_next_24_hours
from .recommendations import add_decision_support, training_high_use_threshold


def generate() -> pd.DataFrame:
    frame = generate_synthetic_data()
    destination = save_raw_data(frame)
    print(f"Generated {len(frame)} synthetic hourly rows at {destination}")
    return frame


def _candidate_models() -> dict:
    return {
        "HistGradientBoostingRegressor": HistGradientBoostingRegressor(
            learning_rate=0.06, max_iter=260, max_leaf_nodes=25, l2_regularization=1.0, random_state=RANDOM_SEED
        ),
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=260, max_depth=18, min_samples_leaf=2, n_jobs=-1, random_state=RANDOM_SEED
        ),
    }


def train_evaluate(raw: pd.DataFrame | None = None) -> dict:
    ensure_directories()
    if raw is None:
        raw_path = DATA_RAW / "campus_energy_hourly.csv"
        if not raw_path.exists():
            raw = generate()
        else:
            raw = pd.read_csv(raw_path, parse_dates=["timestamp"])
    validate_raw_data(raw)
    featured = build_features(raw)
    train, validation, test = chronological_split(featured)
    featured.to_csv(DATA_PROCESSED / "featured_energy_data.csv", index=False)

    split_metadata = {
        "method": "chronological, no shuffle",
        "rows_after_lags": len(featured),
        "train": {"rows": len(train), "start": str(train["timestamp"].min()), "end": str(train["timestamp"].max())},
        "validation": {"rows": len(validation), "start": str(validation["timestamp"].min()), "end": str(validation["timestamp"].max())},
        "test": {"rows": len(test), "start": str(test["timestamp"].min()), "end": str(test["timestamp"].max())},
    }
    (ARTIFACTS / "split_metadata.json").write_text(json.dumps(split_metadata, indent=2), encoding="utf-8")

    models = _candidate_models()
    validation_metrics: dict[str, dict[str, float]] = {}
    validation_fitted: dict[str, object] = {}
    for name, model in models.items():
        model.fit(feature_matrix(train), train[TARGET_COLUMN])
        prediction = model.predict(feature_matrix(validation))
        validation_metrics[name] = regression_metrics(validation[TARGET_COLUMN], prediction)
        validation_fitted[name] = model

    selected_name = min(validation_metrics, key=lambda name: validation_metrics[name]["mae"])
    selected_validation_model = validation_fitted[selected_name]

    permutation = permutation_importance(
        selected_validation_model,
        feature_matrix(validation),
        validation[TARGET_COLUMN],
        scoring="neg_mean_absolute_error",
        n_repeats=10,
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    importance = pd.DataFrame(
        {"feature": FEATURE_COLUMNS, "importance_mean": permutation.importances_mean, "importance_std": permutation.importances_std}
    ).sort_values("importance_mean", ascending=False)
    importance.to_csv(ARTIFACTS / "feature_importance.csv", index=False)

    selected_model = _candidate_models()[selected_name]
    development = pd.concat([train, validation], ignore_index=True)
    selected_model.fit(feature_matrix(development), development[TARGET_COLUMN])
    test_prediction = selected_model.predict(feature_matrix(test))
    baseline_prediction = previous_day_baseline(test).to_numpy()

    predictions = pd.DataFrame(
        {
            "timestamp": test["timestamp"].to_numpy(),
            "actual_kwh": test[TARGET_COLUMN].to_numpy(),
            "predicted_kwh": test_prediction,
            "baseline_kwh": baseline_prediction,
            "absolute_error": np.abs(test[TARGET_COLUMN].to_numpy() - test_prediction),
            "baseline_absolute_error": np.abs(test[TARGET_COLUMN].to_numpy() - baseline_prediction),
            "temperature_c": test["temperature_c"].to_numpy(),
            "occupied": test["occupied"].to_numpy(),
            "event_type": test["event_type"].to_numpy(),
        }
    )
    predictions.to_csv(OUTPUTS / "test_predictions.csv", index=False)
    success = predictions.nsmallest(8, "absolute_error").copy()
    failure = predictions.nlargest(8, "absolute_error").copy()
    success["analysis_note"] = "Representative low-error prediction from untouched final test data."
    failure["analysis_note"] = failure["event_type"].map(
        lambda value: "Known simulated unusual event was not supplied to the model."
        if value != "normal"
        else "Likely noise or a pattern not fully represented by calendar, weather, and historical lags."
    )
    success.to_csv(OUTPUTS / "success_cases.csv", index=False)
    failure.to_csv(OUTPUTS / "failure_cases.csv", index=False)

    baseline_metrics = regression_metrics(test[TARGET_COLUMN], baseline_prediction)
    model_metrics = regression_metrics(test[TARGET_COLUMN], test_prediction)
    improvement = mae_improvement_percent(baseline_metrics["mae"], model_metrics["mae"])
    high_use_threshold = training_high_use_threshold(train[TARGET_COLUMN])

    model_bundle = {
        "model": selected_model,
        "model_name": selected_name,
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "random_seed": RANDOM_SEED,
        "fit_period": {"start": str(development["timestamp"].min()), "end": str(development["timestamp"].max())},
        "selection_basis": "lowest validation MAE; final test was not used for selection",
        "high_use_threshold_kwh": high_use_threshold,
    }
    joblib.dump(model_bundle, ARTIFACTS / "model_bundle.joblib")

    future = forecast_next_24_hours(selected_model, raw)
    future = add_decision_support(future, high_use_threshold)
    future.to_csv(OUTPUTS / "future_24h_forecast.csv", index=False)

    metrics = {
        "project": "CampusEnergy AI",
        "data_disclosure": "Synthetic / simulated prototype campus energy data",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "random_seed": RANDOM_SEED,
        "selection": {
            "criterion": "lowest validation MAE",
            "selected_model": selected_name,
            "test_used_for_selection": False,
            "validation_candidates": validation_metrics,
        },
        "final_test": {
            "baseline_name": "Previous-day same-hour actual (t-24)",
            "baseline": baseline_metrics,
            "ml_model": model_metrics,
            "mae_improvement_percent": improvement,
            "test_rows": len(test),
        },
        "high_use": {
            "rule": "90th percentile of training-period consumption",
            "threshold_kwh": high_use_threshold,
            "future_flagged_hours": int(future["high_use"].sum()),
        },
        "future_forecast": {
            "rows": len(future),
            "start": str(future["timestamp"].min()),
            "end": str(future["timestamp"].max()),
            "input_disclosure": str(future["input_disclosure"].iloc[0]),
            "lags_use_observed_history_only": True,
        },
        "split": split_metadata,
        "limitations": [
            "synthetic single-building data",
            "simplified occupancy",
            "assumed future temperature and occupancy",
            "unexpected events are not known to the model",
            "no live meter or BMS integration",
            "scenario predictions are non-causal",
        ],
    }
    (ARTIFACTS / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    (ARTIFACTS / "training_metadata.json").write_text(
        json.dumps({key: value for key, value in model_bundle.items() if key != "model"}, indent=2), encoding="utf-8"
    )

    create_all_charts(
        train,
        validation,
        test,
        predictions,
        future,
        importance,
        validation_metrics,
        metrics["final_test"],
        high_use_threshold,
    )
    print(json.dumps(metrics["selection"], indent=2))
    print(json.dumps(metrics["final_test"], indent=2))
    print(f"Saved exactly {len(future)} future forecast rows; high-use flags: {int(future['high_use'].sum())}")
    return metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="CampusEnergy AI reproducible pipeline")
    parser.add_argument("command", choices=["generate", "train", "all"], nargs="?", default="all")
    args = parser.parse_args()
    if args.command == "generate":
        generate()
    elif args.command == "train":
        train_evaluate()
    else:
        train_evaluate(generate())


if __name__ == "__main__":
    main()

