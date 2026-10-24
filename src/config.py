from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
ARTIFACTS = ROOT / "artifacts"
OUTPUTS = ROOT / "outputs"
CHARTS = OUTPUTS / "charts"

RANDOM_SEED = 42
N_DAYS = 180
N_HOURS = N_DAYS * 24
START_TIMESTAMP = "2026-01-01 00:00:00"

FEATURE_COLUMNS = [
    "hour",
    "day_of_week",
    "is_weekend",
    "temperature_c",
    "occupied",
    "lag_24",
    "lag_168",
    "sin_hour",
    "cos_hour",
    "sin_day_of_week",
    "cos_day_of_week",
]
TARGET_COLUMN = "consumption_kwh"


def ensure_directories() -> None:
    for path in (DATA_RAW, DATA_PROCESSED, ARTIFACTS, OUTPUTS, CHARTS):
        path.mkdir(parents=True, exist_ok=True)

