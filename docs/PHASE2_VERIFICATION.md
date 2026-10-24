# Phase 2 verification and resume record

Verified: 2026-10-24. Phase 2 / resume verdict: **PASS**. Ready for Phase 3 packaging.

## Resume boundary

The existing implementation was inspected before further changes: `AGENTS.md`, `PLANS.md`, build status, traceability, README, entrypoint, presentation helpers/views, thin page scripts, theme, diagram builder, UI tests and repository state. Git is initialized but has no commits; all project files are untracked, so a historical Git diff cannot reliably identify which files were changed by the interrupted run. No existing working code or canonical model was discarded.

Already present at resume: six artifact-driven page implementations, light theme, cached artifact loader, native navigation conversion, forecast explorer, performance/importance, peak/scenario view, error analysis, responsible-AI content, separate architecture assets, initial screenshots and UI tests. The resumed baseline suite passed 42 tests. Documentation still described only Phase 1 and browser acceptance was incomplete.

Completed after resume: full rendered-page/interaction verification, fresh-start checks, fixes below, regression tests, clean screenshots, hash reconciliation and documentation. No training command was run in Phase 2, and no ML source, data, model, metric, threshold, prediction or original chart needed repair.

## Repairs and relevant files

- `app.py`, `ui_pages/*.py`: six thin page scripts moved out of the legacy auto-discovered `pages/` directory. A fresh server opening `/forecast` had bypassed `app.py` and raised a missing `_dashboard_data` error. Using `ui_pages/` forces entrypoint initialization before native routing. A clean restart directly into `/forecast` now renders normally.
- `src/views.py`: display-only signed-zero normalization so an unchanged what-if scenario reads `+0.00 kWh`, not `-0.00 kWh`. Model output is not altered.
- `tests/test_dashboard_ui.py`: missing-package recovery test, routing-discovery guard, stronger scenario-default assertion; all six native page routes execute without exceptions.
- `requirements.txt`: minimum Streamlit version aligned with the verified 1.66.1 UI runtime; no environment reinstall performed.
- README, plan, build status and traceability updated; hash evidence added separately.

Earlier Phase 2 presentation fixes retained: header spacing, chart numeric tooltip types, fixed ledger/validation number formatting, and native navigation to reset page scroll rather than retaining the old page's scrolled position.

## Acceptance evidence

| Check | Actual evidence | Result |
|---|---|---|
| Overview | Period 30 June 2026; 1,225.6 kWh total; 86.1 kWh peak at 13:00; 2/24 HIGH USE; canonical MAE improvement strip | PASS |
| Forecast | 24-hour plot with baseline, training P90 and triangle HIGH USE markers; selected 13:00 and 00:00; complete ledger and readable hour detail | PASS |
| Tooltip | Real 13:00 tooltip: forecast 86.11, baseline 84.73 kWh, assumed 31.5 °C, occupied, HIGH USE | PASS |
| Performance | Canonical validation and final metrics; explicit near-tie caveat; chronological split image; last-7-days/full-test selector; human-readable permutation importance and reproducibility expander | PASS |
| Peaks and recommendations | 12:00 and 13:00; 84.882 kWh training threshold; consecutive-peak scheduling checks; mandatory human verification | PASS |
| What-if | At 13:00, keyboard temperature change to 31.6 °C and unoccupied produced 38.12 kWh / −47.98 kWh versus original; changing to 00:00 restores that hour's default assumptions | PASS |
| Scenario honesty | Non-causal warning remains visible; fixed calendar/lags and out-of-training-range caveat; canonical forecast never replaced | PASS |
| Errors | Worst case 17 June 12:00: actual 126.25, ML 83.67, baseline 79.96, absolute error 42.58 kWh; eight largest and eight smallest errors; all-test scatter with event markers | PASS |
| Retrospective event labels | Explicitly not model inputs or live operational information | PASS |
| Responsible AI | Dataset disclosure, privacy, bias/coverage, security as deployment requirements, accessible warnings, human oversight and limitations | PASS |
| SDGs / future boundary | SDG 7 with supporting 11/12/13, no measured savings; working features separated from future integrations | PASS |
| Architecture | Separate PNG/SVG asset; inputs through validation, features, split, baseline/candidates, selection, evaluation/forecast and human decision; no fictional cloud or live IoT | PASS |
| Interactions | Native page links, hour selectors, scenario slider/occupancy, chart hover, table column menu and expanders exercised in browser | PASS |
| Startup / direct route | Local-only Streamlit startup, HTTP 200 at root, health `ok`, cold direct forecast route after restart | PASS |
| Automated suite | 44 passed, 0 failed in final run (15.72 s); pip check and compileall pass | PASS |
| Canonical preservation | SHA-256 comparison of 20 frozen files: zero differences, including original eight chart PNGs | PASS |

## Visual inspection

All six pages were inspected in the actual in-app browser at 1440 × 1000, including lower content. Titles, legends, units, candidate metrics, warnings, failure-case tables, importance labels and architecture were checked. Overview and sidebar were additionally inspected at the native 638 × 738 panel size: cards stack and navigation collapses appropriately. The browser viewport override was reset afterward.

Genuine browser screenshots (not mockups) are in `outputs/phase2/screenshots/`: `overview.png`, `forecast_explorer.png`, `forecast_tooltip.png`, `performance.png`, `peaks.png`, `what_if.png`, `errors.png`, `about.png`. These are viewport captures, not full-page exports. Architecture assets: `outputs/phase2/architecture.png` and `.svg`; originals in `outputs/charts/` remain unchanged.

## Short professor demo route

The following interaction sequence was exercised during browser acceptance. Allow roughly 3–5 minutes when narrating; this is a suggested pacing, not a timed usability study.

1. **Overview:** “CampusEnergy AI forecasts one building's next 24 hourly energy intervals and provides checks for a human facility manager.” State immediately that the data are synthetic.
2. Show the date, total energy, 13:00 peak and 12:00/13:00 HIGH USE markers; read the manager recommendation, including human verification.
3. **24-Hour Forecast:** inspect 13:00, then a normal hour; show assumed inputs, baseline delta and ledger.
4. **Model Performance:** compare final MAE/RMSE; explain forward-only splits and validation-only selection. Say the candidates were effectively tied, not that RF is universally best. Importance is predictive, not causal.
5. **Peak Insights:** change occupancy/temperature in the what-if section; point to the original/scenario/delta cards and non-causal disclaimer. Do not interpret the delta as guaranteed savings.
6. **Error Analysis:** show the 42.58 kWh failure and explain that unusual events are not supplied to the model and remain in the reported metrics.
7. **Responsible AI / About:** end with human oversight, synthetic-data limitations, SDGs, implemented-versus-future and architecture.

## Commands and remaining limitations

Run from the project directory; the demo does not require regeneration:

```powershell
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8511
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m pip check
.venv\Scripts\python.exe -m compileall -q app.py src ui_pages scripts tests
```

Phase 1 limitations remain: synthetic single-building relationships, assumed future inputs, retrospective evaluation using observed covariates/lag updates, and a marginal validation-MAE gap sensitive to processed-CSV floating-point round-tripping. Do not retrain from serialized processed features. Load the frozen package in later phases.

UX limitations: large ledgers use internal horizontal/vertical scrolling; complete recommendations are available in the selected-hour card. The primary demo target is desktop. The narrow overview was checked, but this is not a comprehensive mobile-device, cross-browser, or screen-reader accessibility audit. No production authentication, live meter/weather service, BMS control or measured energy/carbon savings are claimed.

Phase 3 remains: final report/DOCX, PPT, full demo/viva guide and submission consistency audit. None of those final submission artifacts was created in this phase.
