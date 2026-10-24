# CampusEnergy AI

CampusEnergy AI is a CPU-friendly prototype that forecasts one campus building's electricity consumption for the next 24 hours, flags likely high-use periods, and supplies transparent checks for a human facility manager.

> **Data disclosure:** all observations are synthetic / simulated prototype campus energy data. They are not VIT data and are not readings from a real campus meter.

## Problem and intended users

A facility manager needs a defensible short-horizon view of demand, a comparison with a simple previous-day forecast, and practical prompts for investigating likely peaks. The prototype is decision support only and never controls equipment.

## Verified result

Random Forest had the marginally lowest validation MAE in the canonical raw-data pipeline and was frozen before final testing. HistGradientBoosting and Random Forest were effectively tied; the project does not claim decisive superiority.

| Final 624-hour test | MAE (kWh) | RMSE (kWh) |
|---|---:|---:|
| Previous-day same-hour baseline | 9.2585 | 16.7316 |
| Random Forest | 2.9061 | 5.3521 |

The ML MAE is 68.61% lower than the baseline on the synthetic prototype dataset. This result should not be assumed to transfer unchanged to real campus data.

## Major features

- Reproducible 4,320-row synthetic hourly dataset, 4,152 leakage-safe feature rows, and historical `lag_24` / `lag_168` inputs.
- Chronological train, validation and untouched test periods with no random shuffling.
- Exact previous-day baseline and validation-only comparison of two genuine ML candidates.
- Exactly 24 forecast hours with assumed temperature, scheduled occupancy and observed-history lags.
- Training-only 84.882 kWh HIGH USE threshold, explanations and human-verification recommendations.
- Validation permutation importance, what-if scenarios and honest success/failure analysis.
- Six-page Streamlit dashboard with explicit synthetic-data and human-oversight disclosures.

## Implemented architecture

Historical synthetic energy + temperature + aggregate occupancy/calendar → validation → leakage-safe feature engineering → chronological train/validation/test periods → previous-day same-hour baseline + ML candidates → validation-only selection → untouched test MAE/RMSE → next-24-hour forecast → training-derived high-use flags → explanations and recommendations → facility-manager verification and human decision.

The target is `consumption_kwh`. Inputs include calendar cycles, temperature, occupancy, and historical `lag_24` / `lag_168` values. The final test period is never used to select the model.

## Technology

Python, pandas, NumPy, scikit-learn, joblib, matplotlib, Plotly, Streamlit, and pytest. No GPU, cloud service, database, or external API is required.

## Setup (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Reproducible commands

### Normal demo launch: use the frozen package

Phase 2 is complete. The dashboard loads the existing canonical model and artifacts; it never trains during startup, navigation, or scenario changes. From this project directory:

```powershell
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8511
```

Open `http://127.0.0.1:8511`. Navigate through Overview, 24-Hour Forecast, Model Performance, Peak Insights (including what-if), Error Analysis, and Responsible AI / About. On a narrow window, open the sidebar using the upper-left control. Tables scroll internally; long recommendations are also available in the selected-hour detail card.

The UI was verified with Streamlit 1.66.1. See `docs/PHASE2_VERIFICATION.md` for acceptance evidence and the short demo route. Screenshots and the separate PNG/SVG architecture diagram are in `outputs/phase2/`.

Random Forest had the marginally lowest validation MAE in the canonical raw-data pipeline. Its performance was effectively tied with HistGradientBoosting; it is not claimed to be decisively superior. **Do not retrain from serialized processed-feature CSV files.**

### Explicit pipeline reproduction (not needed for the demo)

The commands below regenerate canonical data/model outputs. Do not run them during UI or submission packaging work unless intentionally reproducing the raw-data pipeline or repairing a verified core bug.

Generate the deterministic 180-day, 4,320-row dataset:

```powershell
python -m src.pipeline generate
```

Train, select on validation data, evaluate once on final test data, and regenerate forecasts/charts:

```powershell
python -m src.pipeline train
```

Run everything fresh in one command:

```powershell
python -m src.pipeline all
```

Run the complete automated test suite:

```powershell
python -m pytest -q
```

Launch the dashboard:

```powershell
python -m streamlit run app.py
```

## Outputs

- `data/raw/campus_energy_hourly.csv`: canonical synthetic hourly history.
- `data/processed/featured_energy_data.csv`: leakage-safe model table.
- `artifacts/metrics.json`: canonical performance and forecast metadata.
- `artifacts/model_bundle.joblib`: selected fitted model plus its contract.
- `artifacts/feature_importance.csv`: validation-set permutation importance.
- `artifacts/split_metadata.json`: chronological boundaries.
- `outputs/test_predictions.csv`: untouched test predictions and exact t-24 baseline.
- `outputs/future_24h_forecast.csv`: exactly 24 forecast hours and decision support.
- `outputs/success_cases.csv` / `failure_cases.csv`: honest representative analysis.
- `outputs/charts/`: static visuals for later report and presentation work.

## Project structure

```text
app.py                    Streamlit entrypoint and artifact cache
ui_pages/                 Six routed dashboard pages
src/                      Data, features, training, forecasting and UI logic
tests/                    Integrity, pipeline, recommendation and UI tests
data/                     Canonical raw and processed synthetic data
artifacts/                Frozen model, metrics and metadata
outputs/                  Predictions, forecast, charts and verified screenshots
docs/                     Report, presentation, guides, references and traceability
```

## Evaluation and baseline

The mandatory baseline at timestamp `t` is the actual consumption at `t-24 hours`; it is evaluated on exactly the same final-test timestamps as the ML model. Both MAE and RMSE are computed, never hard-coded, and read by the app from `artifacts/metrics.json`.

The future-temperature input is explicitly assumed: recent same-hour temperature climatology plus a disclosed +2 °C warm-day planning offset. This produces a useful planning scenario and is not a weather forecast. Future occupancy follows the documented weekday/Saturday schedule.

## Responsible AI, limitations, and SDGs

Privacy, bias, security, accessibility, human oversight, and limitations are detailed in `docs/RESPONSIBLE_AI.md`. The central limitations are synthetic single-building data, simplified occupancy, assumed future inputs, unexpected events, pattern dependence, and no live meter/BMS integration. What-if results are scenarios, not guaranteed or causal effects.

The primary alignment is SDG 7, with cautious supporting relevance to SDGs 11, 12, and 13. See `docs/SDG_ALIGNMENT.md`; no quantified savings or emissions reduction is claimed.

## Final submission package

- Technical report: `docs/CampusEnergyAI_Report.docx`
- Presentation: `docs/CampusEnergyAI_Presentation.pptx`
- Demonstration script: `docs/Demo_Guide.md`
- Viva preparation: `docs/Viva_QA.md`
- References: `docs/references.md`
- Phase 3 build and requirement evidence: `docs/BUILD_STATUS.md` and `docs/REQUIREMENTS_TRACEABILITY.md`
- Independent final acceptance: `docs/FINAL_ACCEPTANCE.md`

## Known limitations

Synthetic single-building data, assumed future temperature and occupancy, unexpected events, historical-pattern dependence, no causal equipment understanding, no live meter or BMS integration and a fixed 24-hour horizon. What-if results are model scenarios, not guaranteed savings. The dashboard is desktop-first and has not undergone a complete cross-browser or screen-reader audit.

