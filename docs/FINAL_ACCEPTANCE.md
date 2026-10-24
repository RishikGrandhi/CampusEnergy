# Final acceptance audit

Audit date: 24 October 2026  
Final verdict: **PASS WITH LIMITATIONS**

CampusEnergy AI is accepted as a completed hackathon prototype and submission package. All energy observations, labels, forecasts and scenarios are synthetic / simulated prototype data; none are represented as real VIT or campus-meter measurements.

## Issue disposition

### Critical issues

None found.

### Major issues found and repaired

1. The repository verifier imported `python-docx`, but the dependency was absent from `requirements.txt`; `scripts/verify_phase3.py` therefore failed in the project `.venv`. `python-docx>=1.1,<2.0` was declared and installed, after which the verifier passed in the declared environment.
2. The report and slide 10 described the six Streamlit routes incorrectly by presenting What-if as a separate routed page and merging Error Analysis with About. Both builders now use the real routes: Overview, 24-Hour Forecast, Model Performance, Peak Insights, Error Analysis, and Responsible AI / About. What-if remains correctly identified as part of Peak Insights.

### Minor issues found and repaired

1. The report references rendered Markdown asterisks literally. The builder now converts the limited `*italic*` markup into genuine italic DOCX runs.
2. A malformed viva heading, `What is Why might this hour be high`, was corrected without changing its answer.
3. The cross-artifact verifier now rejects raw Markdown in the report references and requires the corrected Error Analysis and Responsible AI / About route labels in the presentation.

## Independent ML and leakage reconciliation

- **NO LEAKAGE FOUND.** Only positive historical shifts create `lag_24` and `lag_168`; no target-at-t, negative shift, centered rolling window, backward fill, future event label, or test-fitted preprocessing enters the feature matrix.
- Raw history contains 4,320 unique, monotonic hourly rows. The first 168 rows are removed only because a weekly lag is unavailable, leaving 4,152 feature rows.
- Chronological split: training 2,906 rows (08 Jan 2026 00:00–09 May 2026 01:00); validation 622 rows (09 May 2026 02:00–03 Jun 2026 23:00); final test 624 rows (04 Jun 2026 00:00–29 Jun 2026 23:00). The boundaries are strictly ordered and no shuffle is used.
- Every stored `lag_24` and `lag_168` value independently matched the earlier observed target at exactly t−24 h and t−168 h.
- Candidate selection used validation MAE only. HistGradientBoostingRegressor: MAE 2.62827747647311 kWh, RMSE 4.895527511849466 kWh. RandomForestRegressor: MAE 2.618686365580432 kWh, RMSE 4.907737808341891 kWh. Random Forest was frozen before the final test; the candidates are accurately described as effectively tied.
- Model-bundle inspection confirmed the target is excluded and the fitted data ends before the final test begins.

## Baseline and final metrics

The required baseline is exactly the observed consumption from the same hour on the previous day. All 624 stored baseline predictions independently matched t−24 h history and use the same timestamps and actuals as the ML model.

| Final 624-hour test | MAE (kWh) | RMSE (kWh) |
|---|---:|---:|
| Previous-day same-hour baseline | 9.258522435897438 | 16.73162966423635 |
| Selected Random Forest | 2.9061409264601386 | 5.352083025361685 |

The independently recomputed MAE improvement is 68.6111801685293%. All values match the canonical `artifacts/metrics.json` exactly.

## Forecast and HIGH USE integrity

- The frozen future artifact contains exactly 24 consecutive hourly timestamps from 30 Jun 2026 00:00 through 23:00 and no future target column.
- Forecast `lag_24` and `lag_168` values use observed history only.
- Future temperature and occupancy are explicitly disclosed planning assumptions, not observed future values or live forecasts.
- The HIGH USE rule is the training-period consumption 90th percentile, 84.882 kWh. Validation, test and future values do not tune the threshold.
- Exactly two forecast hours are flagged: 12:00 at 84.91592938953512 kWh and 13:00 at 86.1091511528742 kWh.

## Recommendation and scenario audit

Recommendations are deterministic, context-specific manager checks. The 13:00 peak asks the manager to verify HVAC cooling demand and temperature set-points and to review flexible-load scheduling and peak-demand planning. Human verification is explicitly required before action.

What-if controls alter assumed temperature and occupancy for a selected forecast hour while calendar and historical lags remain fixed. The app, report, presentation and guides consistently state that scenarios are model-sensitivity explorations, not causal guarantees or automatic control instructions.

## Application and interaction acceptance

All six routed pages were inspected in a real browser. Navigation, the selected-hour forecast card, full-test chart range, tables, expanders, scenario temperature/occupancy/hour changes, signed-zero display behavior, retained success/failure cases, synthetic-data disclosure, Responsible AI content, SDG boundaries and implemented-versus-future wording were verified. The largest retained error is 42.58 kWh on 17 Jun 2026 at 12:00, with retrospective simulated laboratory-load context that was not provided to the model.

Streamlit returned HTTP 200 at both the root and health endpoint; the health body was `ok`.

## Submission artifact acceptance

- Report: PASS — 21 rendered Letter pages, 193 paragraphs, 11 tables and 10 figures. All pages were reinspected after repair; no clipping, overlap, literal Markdown, unexpected placeholder or corrupt package was found. The only placeholders are the intentional participant, team and institution fields.
- Presentation: PASS — 16 visually inspected 16:9 slides, five embedded visual assets and one native editable results chart. Package integrity, layout, Aptos font policy, first-party reimport and native chart/workbook validation reported zero findings or warnings.
- Demo guide: PASS — accurate normal route, 3–5 minute route, 60-second route, fallback material and exact launch command.
- Viva guide: PASS — accurate student-level answers for leakage, baseline, chronological evaluation, validation/test separation, tied candidates, HIGH USE, explainability, non-causal scenarios, failure cases, Responsible AI and SDGs.
- References: PASS — 12 relevant authoritative sources. The Breiman paper, scikit-learn documentation, OTexts time-series cross-validation material, Streamlit multipage documentation, NIST AI RMF and UN SDG pages were independently checked.

## Verification evidence

- `pytest -q`: **44 passed, 0 failed**.
- `pip check`: no broken requirements.
- `compileall`: passed for the application, source, page, script and test modules.
- `scripts/verify_phase3.py`: passed in the project `.venv`; report 193 paragraphs / 11 tables / 10 figures, presentation 16 slides / five media assets / one chart.
- Streamlit root and health: HTTP 200 / HTTP 200, body `ok`.
- Canonical preservation: **20 of 20** files in `docs/PHASE2_ARTIFACT_INTEGRITY.json` remain SHA-256-identical after all audit repairs. No canonical model, dataset, forecast, prediction, chart or metrics artifact was changed.

## Remaining limitations

1. Results use one synthetic building and do not establish real-campus accuracy or savings.
2. Temperature and occupancy for the next day are assumptions; unusual events and equipment state are not fully represented.
3. Random Forest and HistGradientBoosting are effectively tied on validation; Random Forest is not claimed to be decisively superior.
4. Scenario outputs are associational, not causal, and recommendations require human verification. There is no live meter/BMS integration or automatic control.
5. The UI is desktop-first and has not received a comprehensive cross-browser, mobile, keyboard, screen-reader or formal contrast audit.
6. The Git repository has no commits and every project file is currently untracked, so no historical Git diff can serve as an independent provenance baseline. Preservation instead relies on the explicit 20-file SHA-256 manifest.
7. On this Windows host, the bundled presentation-authoring Node process terminated with status `0xC0000409` after it had written the deck and complete success receipt. The generated PPTX nevertheless passed package, layout, font, chart, reimport and visual checks. This post-finalization tool-runtime exit remains a packaging-tool limitation rather than a detected artifact defect.

## Live demonstration command

Run from `C:\Coding\Projects\CampusEnergy`:

```powershell
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8511
```

Open `http://127.0.0.1:8511/`.

## Final submission files

1. `docs/CampusEnergyAI_Report.docx`
2. `docs/CampusEnergyAI_Presentation.pptx`
3. `docs/Demo_Guide.md`
4. `docs/Viva_QA.md`
5. `docs/references.md`
6. `README.md`
7. `docs/RESPONSIBLE_AI.md`
8. `docs/SDG_ALIGNMENT.md`
9. `docs/REQUIREMENTS_TRACEABILITY.md`
10. `docs/BUILD_STATUS.md`
11. `docs/FINAL_ACCEPTANCE.md`

