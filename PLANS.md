# Phase 1 implementation plan

Current state: Phase 1 frozen; Phase 2 dashboard complete; Phase 3 submission package complete; independent final acceptance audit complete with limitations documented in `docs/FINAL_ACCEPTANCE.md`. The Phase 1 reproduction commands below are historical verification commands, not instructions to retrain during later phases.

| Phase | Acceptance evidence | Verification | Status |
|---|---|---|---|
| Repository and governance | `AGENTS.md`, this plan, build status, traceability | file inspection | PASS |
| Synthetic data | 4,320 deterministic hourly rows with validation | `python -m src.pipeline generate` and pytest | PASS |
| Features and splits | leakage-safe lags; chronological 70/15/15 periods | pytest and split metadata | PASS |
| Baseline and ML | exact t-24 baseline; HGB and RF validation comparison | metrics JSON and pytest | PASS |
| Test evaluation | untouched test MAE/RMSE and prediction exports | `python -m src.pipeline train` | PASS |
| Forecast and decisions | exactly 24 hours, high-use flags, explanations, recommendations | CSV inspection and pytest | PASS |
| Explainability and what-if | permutation importance and reusable scenario function | artifacts and pytest | PASS |
| Visual artifacts and app | report-ready PNGs; basic Streamlit sections | UI execution + HTTP smoke tests | PASS |
| Fresh verification | full pipeline, 34 tests, artifact checks | commands below | PASS |

## Acceptance criteria

Phase 1 passes when every critical item in the build brief is implemented, generated from real computations, covered by tests where practical, and documented in `docs/BUILD_STATUS.md` and `docs/REQUIREMENTS_TRACEABILITY.md`.

## Verification commands

```powershell
python -m src.pipeline all
python -m pytest -q
python -m streamlit run app.py --server.headless true
```

## Phase 2 resume and acceptance

| Work | Evidence | Status |
|---|---|---|
| Resume existing work without replacement | Inspected source, AGENTS, plan, build status, traceability; Git has no commits, so no trustworthy historical diff exists | PASS |
| Artifact-driven six-page dashboard | `app.py`, `ui_pages/`, `src/dashboard.py`, `src/views.py` | PASS |
| Forecast, peaks, scenarios, performance, errors | Real browser interactions plus AppTest regression coverage | PASS |
| Responsible AI, SDGs, implemented/future boundary | About page and browser content/layout inspection | PASS |
| Architecture and genuine screenshots | `outputs/phase2/` | PASS |
| Final verification | 44 pytest passes; HTTP 200; pip check; compileall; 20 unchanged SHA-256 files | PASS |
| Canonical preservation | `docs/PHASE2_ARTIFACT_INTEGRITY.json`; no retraining | PASS |
| Submission report, PPT and viva package | 21-page report, 16-slide deck, demo/viva/reference package and verification evidence | PASS |

Phase 2 evidence and limitations: `docs/PHASE2_VERIFICATION.md`.

