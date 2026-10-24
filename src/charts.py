"""Static, report-ready charts generated from canonical pipeline results."""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
import pandas as pd

from .config import CHARTS, ensure_directories


def _finish(fig, name: str) -> None:
    ensure_directories()
    fig.tight_layout()
    fig.savefig(CHARTS / name, dpi=170, bbox_inches="tight")
    plt.close(fig)


def create_all_charts(
    train: pd.DataFrame,
    validation: pd.DataFrame,
    test: pd.DataFrame,
    predictions: pd.DataFrame,
    future: pd.DataFrame,
    importance: pd.DataFrame,
    validation_metrics: dict,
    test_metrics: dict,
    threshold: float,
) -> None:
    colors = {"train": "#2563eb", "validation": "#f59e0b", "test": "#dc2626", "ml": "#0f766e", "baseline": "#64748b"}

    fig, ax = plt.subplots(figsize=(11, 2.8))
    for frame, label in ((train, "Train"), (validation, "Validation"), (test, "Test")):
        ax.plot(frame["timestamp"], [label] * len(frame), linewidth=6, label=label)
    ax.set_title("Chronological train / validation / test periods")
    ax.set_xlabel("Timestamp")
    ax.grid(axis="x", alpha=0.2)
    _finish(fig, "chronological_split.png")

    sample = predictions.tail(24 * 7)
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.plot(sample["timestamp"], sample["actual_kwh"], label="Actual", color="#111827", linewidth=1.8)
    ax.plot(sample["timestamp"], sample["predicted_kwh"], label="ML forecast", color=colors["ml"], linewidth=1.5)
    ax.set_title("Test period: actual vs ML prediction (last 7 days)")
    ax.set_ylabel("Electricity consumption (kWh)")
    ax.legend()
    ax.grid(alpha=0.2)
    _finish(fig, "test_actual_vs_ml.png")

    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.plot(sample["timestamp"], sample["actual_kwh"], label="Actual", color="#111827", linewidth=1.8)
    ax.plot(sample["timestamp"], sample["predicted_kwh"], label="ML", color=colors["ml"], alpha=0.9)
    ax.plot(sample["timestamp"], sample["baseline_kwh"], label="Previous-day baseline", color=colors["baseline"], alpha=0.8)
    ax.set_title("Baseline vs ML comparison (last 7 test days)")
    ax.set_ylabel("kWh")
    ax.legend(ncol=3)
    ax.grid(alpha=0.2)
    _finish(fig, "baseline_vs_ml.png")

    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.plot(future["timestamp"], future["predicted_kwh"], marker="o", label="Predicted", color=colors["ml"])
    ax.plot(future["timestamp"], future["baseline_kwh"], linestyle="--", label="Previous-day baseline", color=colors["baseline"])
    ax.axhline(threshold, color=colors["test"], linestyle=":", label="Training 90th percentile")
    flagged = future[future["high_use"]]
    ax.scatter(flagged["timestamp"], flagged["predicted_kwh"], color=colors["test"], s=55, label="HIGH USE", zorder=5)
    ax.set_title("Next 24-hour electricity forecast")
    ax.set_ylabel("kWh")
    ax.legend(ncol=2)
    ax.grid(alpha=0.2)
    _finish(fig, "future_24h_forecast.png")

    fig, ax = plt.subplots(figsize=(8, 5))
    ordered = importance.sort_values("importance_mean")
    ax.barh(ordered["feature"], ordered["importance_mean"], color=colors["train"])
    ax.set_title("Permutation importance on validation data")
    ax.set_xlabel("Increase in MAE after permutation")
    ax.grid(axis="x", alpha=0.2)
    _finish(fig, "feature_importance.png")

    labels = list(validation_metrics)
    values = [validation_metrics[name]["mae"] for name in labels]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.bar(labels, values, color=[colors["train"], colors["validation"]][: len(labels)])
    ax.set_title("Candidate validation MAE (lower is better)")
    ax.set_ylabel("MAE (kWh)")
    ax.grid(axis="y", alpha=0.2)
    _finish(fig, "model_performance_comparison.png")

    fig, ax = plt.subplots(figsize=(7, 4.5))
    metric_labels = ["Baseline MAE", "ML MAE", "Baseline RMSE", "ML RMSE"]
    metric_values = [
        test_metrics["baseline"]["mae"],
        test_metrics["ml_model"]["mae"],
        test_metrics["baseline"]["rmse"],
        test_metrics["ml_model"]["rmse"],
    ]
    ax.bar(metric_labels, metric_values, color=[colors["baseline"], colors["ml"], colors["baseline"], colors["ml"]])
    ax.set_title("Final test performance")
    ax.set_ylabel("Error (kWh)")
    ax.tick_params(axis="x", rotation=15)
    ax.grid(axis="y", alpha=0.2)
    _finish(fig, "final_test_metrics.png")

    steps = [
        "Historical energy +\ntemperature + occupancy",
        "Validation +\nfeature engineering",
        "Chronological\ntrain / validation / test",
        "t-24 baseline +\nselected ML model",
        "MAE / RMSE +\n24-hour forecast",
        "High-use explanation +\nrecommendations",
        "Facility manager\nverification + decision",
    ]
    fig, ax = plt.subplots(figsize=(13, 3.2))
    ax.axis("off")
    width = 0.12
    for i, step in enumerate(steps):
        x = 0.01 + i * 0.141
        box = FancyBboxPatch((x, 0.35), width, 0.3, boxstyle="round,pad=0.012", facecolor="#e0f2fe", edgecolor="#0369a1")
        ax.add_patch(box)
        ax.text(x + width / 2, 0.5, step, ha="center", va="center", fontsize=8)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 0.139, 0.5), xytext=(x + width, 0.5), arrowprops={"arrowstyle": "->", "color": "#475569"})
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_title("CampusEnergy AI — implemented decision-support workflow", pad=10)
    _finish(fig, "architecture_workflow.png")

