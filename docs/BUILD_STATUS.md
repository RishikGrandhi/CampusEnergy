# Build status

Last updated: 2026-10-24

## Current phase: Final acceptance — PASS WITH LIMITATIONS

The independent final audit is complete. No leakage, baseline, split, metric, forecast, threshold, recommendation, scenario or canonical-artifact defect was found. Submission-package inconsistencies and the missing report-verifier dependency were repaired and fully reverified. Final evidence and limitations are recorded in `docs/FINAL_ACCEPTANCE.md`.

Resume status: PASS. The interrupted Phase 3 work was recovered from the repository and continued rather than restarted. The already completed Demo Guide, Viva guide, references, README additions, canonical screenshots/charts and frozen Phase 1 artifacts were preserved. The incomplete items were the final Office artifacts, their page/slide visual verification, cross-artifact structural checks, final technical regression run and Phase 3 traceability.

### Phase 3 deliverables and acceptance evidence

| Deliverable / check | Result / evidence |
|---|---|
| Technical report | PASS — `docs/CampusEnergyAI_Report.docx`; 21 Letter pages, 29 numbered sections plus executive summary and references |
| Report structure | PASS — reopened with `python-docx`; 193 paragraphs, 11 tables, 10 embedded figures; only three intentional participant/team/institution placeholders |
| Report rendering | PASS — Microsoft Word reopened and exported the DOCX to PDF; all 21 rasterized pages inspected after repairing a split table and orphaned caption |
| Presentation | PASS — `docs/CampusEnergyAI_Presentation.pptx`; 16 slides, five embedded visual assets and one native editable results chart |
| Presentation validation | PASS — package integrity, 16:9 layout, Aptos font policy, native chart/workbook snapshot and first-party reimport passed with zero findings/warnings; Microsoft PowerPoint reopened 16 slides at 960 × 540 points |
| Presentation rendering | PASS — all 16 Artifact Tool PNG previews inspected at full size; repaired missing embedded images and wrapped feature-importance values, then rerendered |
| Demo / viva / references | PASS — exact launch flow, 3–5 minute demo, emergency path, 60-second version, student-friendly viva and 12 authoritative references |
| README | PASS — overview, verified results, commands, disclosure, structure, limitations, Responsible AI, SDGs and final deliverable paths |
| Cross-artifact structural audit | PASS — `scripts/verify_phase3.py`; canonical metrics/wording, required sections/slides, embedded media, placeholders and unfinished-text checks |
| Canonical preservation | PASS — document builders read frozen JSON/CSV/image artifacts and never call training; Phase 1 manifest remains the preservation baseline |
| Final app regression | PASS — 44 pytest checks, Python compilation, dependency check, Streamlit root/health HTTP verification |

The Phase 3 package was subsequently accepted by the independent final audit. See `docs/FINAL_ACCEPTANCE.md`.

## Phase 2 dashboard — PASS

Resume status: PASS. The interrupted implementation was continued, not rebuilt. The six-page UI, artifact loading, architecture asset and initial UI regressions were already present at resume; the initial resumed suite passed 42 tests. Remaining work was browser acceptance, final robustness/presentation checks, evidence capture and documentation.

Completed after resuming: verified native page navigation and all six rendered pages, hour selection, chart tooltip, table menu, disclosure expanders, scenario temperature/occupancy changes and hour defaults; added missing-artifact recovery coverage; normalized display-only signed-zero scenario deltas; aligned the Streamlit minimum version with the tested UI runtime. A clean server restart exposed legacy `pages/` auto-discovery bypassing entrypoint initialization on direct links. Moved the six thin scripts to `ui_pages/`, updated the router/tests, and verified a cold direct `/forecast` load. Updated README, plan and traceability and saved screenshot/hash evidence.

No ML implementation or canonical artifact required repair. Phase 1 remains frozen with its existing near-tie methodological limitation. The dashboard is ready for Phase 3 submission packaging.

| Phase 2 acceptance | Result / evidence |
|---|---|
| All six pages and required content | PASS — browser-rendered and AppTest coverage |
| Browser/UI | PASS — desktop 1440 × 1000 inspection plus 638 × 738 overview/sidebar check; real screenshots in `outputs/phase2/screenshots/` |
| What-if | PASS — changed temperature and occupancy, verified updated forecast/delta and non-causal warning; switching hours resets assumptions |
| Genuine error cases | PASS — largest test error 42.58 kWh, retained in metrics and visible with retrospective event context |
| Streamlit | PASS — local server on 127.0.0.1:8511; HTTP 200 startup/health |
| Full pytest | PASS — 44 passed, 0 failed |
| Dependency / syntax smoke | PASS — pip check and compileall |
| Canonical preservation | PASS — all 20 frozen data/model/prediction/metric/chart files SHA-256-identical |
| Limitations | Synthetic single-building data, assumed future inputs, non-causal scenarios; validation candidates effectively tied; wide ledgers need internal scrolling |

Detailed evidence and demo route: `docs/PHASE2_VERIFICATION.md`. Hash manifest: `docs/PHASE2_ARTIFACT_INTEGRITY.json`.

## Phase 1 historical completion record

| Area | Status | Evidence / note |
|---|---|---|
| Repository foundation | PASS | Git initialized; required structure, constraints, plan, README, and docs exist |
| Synthetic data | PASS | Deterministic seed 42; 4,320 valid hourly rows; 39 realistic unusual-event rows |
| Feature engineering | PASS | Calendar cycles, temperature, occupancy, exact lag-24 and lag-168; target excluded |
| Chronological split | PASS | 2,906 train / 622 validation / 624 test rows after lag drop; ordered and non-overlapping |
| Baseline | PASS | Exact previous-day same-hour actual on all 624 test timestamps |
| ML selection and evaluation | PASS | Random Forest selected by validation MAE; untouched test MAE 2.9061 kWh |
| 24-hour forecast | PASS | Exactly 24 hours, 2026-06-30 00:00–23:00; observed-history lags only |
| Decision support | PASS | Two HIGH USE hours plus human-verification recommendations and non-causal explanations |
| Explainability | PASS | Validation-set permutation importance CSV and chart |
| What-if engine | PASS WITH LIMITATION | Works for temperature/occupancy scenarios; model association, not a causal guarantee |
| Static assets | PASS | Eight generated PNG assets visually inspected |
| Streamlit foundation | PASS | AppTest execution has no exceptions; real server returned HTTP 200 |
| Automated tests | PASS | 34 passed, 0 failed after integrity-audit regressions; pip check and compileall also pass |

## Measured evaluation summary

- Selected model: RandomForestRegressor.
- Validation: HistGradientBoosting MAE 2.6283 / RMSE 4.8955 kWh; Random Forest MAE 2.6187 / RMSE 4.9077 kWh.
- Final test baseline: MAE 9.2585 / RMSE 16.7316 kWh.
- Final test selected ML: MAE 2.9061 / RMSE 5.3521 kWh.
- MAE improvement over baseline: 68.6112%.
- Training-derived HIGH USE threshold: 84.882 kWh (training-period 90th percentile).

## Phase 1 integrity re-audit

The 2026-10-24 audit independently reconciled every saved test timestamp, baseline value, metric, future lag, threshold, and high-use flag. Rebuilding features from canonical raw data reproduced both validation candidates exactly and selected Random Forest before final-test evaluation. One non-blocking stability limitation was identified: the validation-MAE gap is only 0.0096 kWh, and retraining HistGradientBoosting from the serialized processed-feature CSV (rather than rebuilding features from raw data) changes its histogram bins after approximately 1e-16 cyclic-feature round-trip differences and can reverse the candidate order. The documented pipeline does not use that path; no canonical artifact or model result was changed.

Allowed statuses: NOT STARTED, IN PROGRESS, PASS, PASS WITH LIMITATION, BLOCKED.

