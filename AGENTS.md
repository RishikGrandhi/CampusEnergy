# CampusEnergy AI engineering constraints

These constraints apply to all work in this repository.

- Treat every dataset and future input as synthetic/simulated prototype data. Never imply that it is real VIT or campus meter data.
- Keep the project CPU-friendly and reproducible; the canonical random seed is `42`.
- Preserve chronological ordering. Never shuffle time-series splits or use the final test period for model selection.
- `lag_24` and `lag_168` must be computed only from earlier observed targets. The required baseline is exactly the previous day's same-hour actual (`lag_24`).
- Select the ML model using validation MAE, freeze that decision, and evaluate the selected configuration once on the untouched test period.
- High-use thresholds must come only from training-period consumption. Never tune them on validation, test, or future forecasts.
- Recommendations are decision support. Do not claim automatic control of HVAC, lighting, meters, or a building-management system. Human verification and decisions are required.
- Keep `artifacts/metrics.json` the canonical source for reported performance numbers.
- Do not hide failure cases or alter labels, rows, or the baseline to improve metrics.
- Add or update tests for behavior changes and keep README commands executable.

