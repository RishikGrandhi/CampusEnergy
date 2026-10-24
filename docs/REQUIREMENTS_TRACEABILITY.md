# Requirements traceability

Verified on 2026-10-24. All performance values are generated and read from the canonical `artifacts/metrics.json` artifact.

| Requirement | Implementation | Artifact | Verification | Status |
|---|---|---|---|---|
| Chronological training, validation, and test periods | `src/features.py` | `artifacts/split_metadata.json`, split chart | `test_train_precedes_validation`, `test_validation_precedes_test` | PASS |
| Previous-day same-hour baseline | `src/features.py`, `src/pipeline.py` | `outputs/test_predictions.csv` | `test_exact_t_minus_24_baseline` | PASS |
| Flag predicted high-use periods | `src/recommendations.py` | forecast CSV and chart; 2 flagged hours | `test_training_derived_threshold`, `test_future_artifact_contract` | PASS |
| Practical checks, no automatic control claims | `src/recommendations.py`, `app.py` | recommendation and explanation columns | four decision-rule tests; wording inspection | PASS |
| Forecast chart | `src/charts.py`, `app.py` | `outputs/charts/future_24h_forecast.png` | chart artifact test and visual inspection | PASS |
| MAE/RMSE | `src/evaluation.py`, `src/pipeline.py` | `artifacts/metrics.json` | metric sanity and JSON contract tests | PASS |
| Baseline comparison | `src/pipeline.py`, `app.py` | metrics JSON and baseline comparison chart | same-timestamp prediction export inspection | PASS |
| Data limitations | `docs/RESPONSIBLE_AI.md`, `README.md` | reusable documentation and app content | documentation inspection | PASS |
| Synthetic dataset source and target | `src/data.py`, `src/config.py` | raw CSV and dataset metadata | deterministic/data-domain tests | PASS |
| Leakage-safe preprocessing and lags | `src/features.py` | processed feature CSV | lag-24, lag-168, target-exclusion tests | PASS |
| Two genuine ML candidates and validation-only selection | `src/pipeline.py` | model bundle, training metadata, metrics JSON | pipeline run; `test_used_for_selection=false` | PASS |
| Representative success and failure cases | `src/pipeline.py` | success/failure CSV exports | export tests and honest event-context notes | PASS |
| Exactly 24 future hours | `src/forecasting.py` | future forecast CSV | row-count, timestamp, and history-lag tests | PASS |
| Explainability | `src/pipeline.py`, `src/recommendations.py` | feature importance CSV/chart and per-hour indicators | artifact and content inspection | PASS |
| What-if scenario analysis | `src/what_if.py`, `app.py` | interactive scenario panel | `test_what_if_backend` | PASS WITH LIMITATION |
| Working prototype and UX foundation | `app.py`, `ui_pages/`, `src/app_support.py`, `src/views.py` | six-page Streamlit app | Six routed AppTests + real browser + HTTP 200 startup smoke | PASS |
| Architecture/workflow | `src/charts.py` | architecture workflow PNG | visual inspection against real system | PASS |
| Responsible AI | `docs/RESPONSIBLE_AI.md`, `app.py` | privacy, bias, security, accessibility, limitations, oversight | content inspection | PASS |
| SDG alignment | `docs/SDG_ALIGNMENT.md`, `app.py` | cautious SDG 7/11/12/13 wording | content inspection | PASS |
| Automated tests | `tests/` | pytest result | 44 passed, 0 failed, including artifact-level integrity reconciliation and UI regression checks | PASS |
| Polished dashboard and short demo route | Phase 2 implementation | `outputs/phase2/`, `docs/PHASE2_VERIFICATION.md` | Rendered desktop inspection and interaction checks | PASS |
| Report, PPT and final viva/submission package | `scripts/build_phase3_report.py`, `scripts/build_phase3_presentation.mjs` | DOCX, PPTX, demo/viva/reference package | `scripts/verify_phase3.py`, Word/PDF page inspection, 16 rendered slide inspection | PASS |
| Independent final acceptance | `docs/FINAL_ACCEPTANCE.md` | Final audit record | 44 tests, HTTP/health, package renders, 20-file SHA-256 preservation, independent metric/lag/baseline reconciliation | PASS WITH LIMITATIONS |

## Phase 2 acceptance traceability

| Requirement | Implementation / evidence | Verification | Status |
|---|---|---|---|
| Overview with energy, peak/time, HIGH USE, baseline and recommendation | `src/views.py`, `src/dashboard.py`; `overview.png` | Real browser; artifact-driven metrics | PASS |
| 24-hour explorer and readable table | Forecast route, hour detail, Δ baseline, assumption/status columns; `forecast_explorer.png` | Selected 13:00 HIGH USE and 00:00 NORMAL; table formatting | PASS |
| Useful chart hover with units | Mixed-type numeric customdata; `forecast_tooltip.png` | Actual 13:00 tooltip: 86.11 forecast, 84.73 baseline, 31.5 °C, occupied, HIGH USE | PASS |
| Validation-only selection, near-tie caveat and final evaluation | Performance route; `performance.png` | Canonical validation/test metrics, split visual, last-7/full-period selector, importance and expander | PASS |
| Operational peaks, consecutive-period checks and oversight | Peak route; `peaks.png` | 12:00/13:00 flags; flexible-load scheduling recommendation and mandatory human verification | PASS |
| Interactive what-if with baseline assumptions and delta | `src/views.py` delegates to unchanged `src/what_if.py`; `what_if.png` | Browser temperature/occupancy/hour changes; backend-equivalence AppTest; signed-zero regression | PASS |
| Genuine successes and failures | Error route; `errors.png` | Highest and lowest error rows from canonical test predictions; no event labels supplied to model | PASS |
| Responsible AI, SDGs and future-work distinction | About route; `about.png` | All requested sections visually/content checked; no measured-savings or live-data claims | PASS |
| Presentation-ready accurate architecture | `scripts/build_phase2_diagram.py`; PNG + SVG in `outputs/phase2/` | Asset and in-app visual review; no invented infrastructure | PASS |
| Cache and graceful missing-package handling | `app.py`, `src/app_support.py` | Dedicated missing-artifact AppTest; no training on UI reruns | PASS |
| Cold direct page loads | `app.py`, `ui_pages/` | Restarted server directly at `/forecast`; legacy auto-discovery regression guard | PASS |
| Preserve Phase 1 | `docs/PHASE2_ARTIFACT_INTEGRITY.json` | 20 pre/post SHA-256 matches; no retraining | PASS |
| Startup, full tests, dependencies and syntax | `.venv` verification commands | HTTP 200; 44 tests; pip check; compileall | PASS |

## Phase 3 submission traceability

| Hackathon requirement | Code / canonical artifact | Dashboard page | Report section | PPT slide | Verification evidence | Status |
|---|---|---|---|---|---|---|
| Problem, user and goal | README, `src/views.py` | Overview | Executive Summary; 1–3 | 2–3 | DOCX/PPT text extraction and visual inspection | PASS |
| Integrated innovation | `src/dashboard.py`, `src/views.py` | Overview | 4 | 4 | Workflow wording and rendered slide | PASS |
| Architecture | `outputs/phase2/architecture.png` | Responsible AI / About | 5 | 5 | Genuine architecture embedded and visually legible | PASS |
| Synthetic dataset and disclosure | `src/data.py`, raw CSV, metrics JSON | All pages / sidebar | 6 | 6 | 4,320 rows, seed 42 and no-real-data wording reconciled | PASS |
| Target, features and preprocessing | `src/features.py`, featured CSV | Model Performance | 7–8 | 6–7 | 4,152 rows and lag feature contract | PASS |
| Chronological split / no shuffle | `src/features.py`, split metadata | Model Performance | 9 | 7 | 2,906 / 622 / 624 ordered rows and split figure | PASS |
| Leakage prevention | feature and integrity tests | Model Performance | 10 | 7–8 | NO LEAKAGE FOUND audit wording and pytest integrity tests | PASS |
| Exact t−24 baseline | `src/features.py`, test predictions | Model Performance | 11 | 8 | Same 624 timestamps; baseline tests | PASS |
| Candidate models and selection | pipeline, metrics JSON, model bundle | Model Performance | 12 | 8 | Effectively-tied wording and validation-only choice | PASS |
| MAE / RMSE | evaluation module, metrics JSON | Model Performance | 13–14 | 9 | Canonical values and native editable chart | PASS |
| Baseline improvement boundary | metrics JSON | Overview / Performance | 14–15 | 9 | 68.61% with synthetic-dataset qualification | PASS |
| Next 24-hour forecast | forecasting module, forecast CSV | Overview / 24-Hour Forecast | 16 | 11 | 24 consecutive timestamps and genuine chart | PASS |
| HIGH USE threshold and hours | recommendations module, forecast CSV | Forecast / Peak Insights | 17 | 11 | Training P90 84.882 kWh; 12:00 and 13:00 | PASS |
| Recommendations and no control | recommendations module | Overview / Peak Insights | 18 | 12 | Human-decision boundary visible in all artifacts | PASS |
| Explainability | feature importance artifact | Performance / Peak Insights | 19 | 13 | Validation permutation importance; no causation claim | PASS |
| What-if scenario | `src/what_if.py` | Peak Insights | 20 | 13 | Genuine screenshot and non-causal disclaimer | PASS WITH LIMITATION |
| Working prototype | `app.py`, `ui_pages/`, UI helpers | Six routed pages | 21 | 10 | Real Phase 2 browser screenshots, no mock UI | PASS |
| Testing and verification | `tests/`, preservation manifest | About / app routes | 22 | 14 | Final 44 tests, HTTP/health, compile and dependency checks | PASS |
| Successful cases | success-case CSV | Error Analysis | 23 | Referenced through validation narrative | Five real low-error rows in report | PASS |
| Failure analysis | failure-case CSV | Error Analysis | 24 | 14 | Genuine 42.58 kWh failure and event-context boundary | PASS |
| Privacy, bias, security, accessibility | Responsible AI docs and UI | Responsible AI / About | 25 | 15 | Required subsections in report and concise slide coverage | PASS |
| Human oversight | recommendation wording and app | Overview / About | 18 and 25 | 12 and 15 | Forecast → recommendation → verification → decision | PASS |
| Limitations | metrics limitations, responsible AI docs | Responsible AI / About | 26 | 9, 13, 15–16 | Synthetic, assumptions, events, near tie, desktop-first | PASS |
| SDG alignment | `docs/SDG_ALIGNMENT.md` | Responsible AI / About | 27 | 15 | SDG 7 primary; 11/12/13 supporting; no measured carbon claim | PASS |
| Implemented vs future | app About content | Responsible AI / About | 28 | 16 | Working features kept separate from roadmap | PASS |
| Conclusion and production path | README | Overview / About | 29 | 16 | Grounded closing, human-controlled roadmap | PASS |
| Demo readiness | app + frozen artifacts | Demo route across pages | `docs/Demo_Guide.md` | Deck supports same flow | Exact command, 3–5 minute route, fallback and 60-second route | PASS |
| Viva readiness | canonical code/artifacts | All relevant pages | `docs/Viva_QA.md` | Supporting slides 6–15 | Required concepts and professor trick questions present | PASS |
| References | source documentation | About references where applicable | References | UN source identified on SDG slide content | 12 authoritative sources; no invented citations | PASS |
| Cross-artifact consistency | metrics JSON + `scripts/verify_phase3.py` | Dashboard source values | DOCX | PPTX | Project/model/rows/metrics/threshold/hours/disclosures reconciled | PASS |

