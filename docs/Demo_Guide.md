# CampusEnergy AI Demo Guide

This guide supports a confident 3 to 5 minute demonstration of the verified CampusEnergy AI prototype. All data shown in the application are synthetic or simulated prototype campus energy data.

## Start the application

Project folder:

```text
C:\Coding\Projects\CampusEnergy
```

PowerShell commands:

```powershell
cd C:\Coding\Projects\CampusEnergy
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8511
```

Open `http://127.0.0.1:8511`. Wait for the Overview page to finish loading before speaking.

## 1 Overview

### What to click or show

Keep the Overview page open. Point to the date, four metric cards, forecast chart, HIGH USE triangle markers and Manager Attention panel.

### What to say to the professor

“CampusEnergy AI forecasts one campus building's hourly electricity use for the next 24 hours. It compares the machine learning forecast with the same hour yesterday, flags likely high-use periods and gives checks for a human facility manager. The prototype uses synthetic data and does not control equipment.”

### What the professor should notice

- Forecast period: 30 June 2026, 00:00 through 23:00.
- Predicted energy across the 24 hourly intervals: about 1,225.6 kWh.
- Peak forecast: 86.11 kWh at 13:00.
- Two HIGH USE hours: 12:00 and 13:00.
- The final-test MAE is 68.61% lower than the previous-day baseline.

## 2 Detailed 24 hour forecast

### What to click or show

Open **24-Hour Forecast**. Hover over 13:00 on the chart. Use **Inspect a forecast hour** to select 13:00, then select 00:00. Scroll to the hourly ledger.

### What to say to the professor

“Every forecast hour includes the ML prediction, the previous-day baseline, assumed temperature, scheduled occupancy and a recommendation. The future temperature is a disclosed warm-day planning assumption, not a live weather forecast. The lag values come only from observed history.”

### What the professor should notice

- At 13:00: 86.11 kWh forecast, 84.73 kWh baseline, 31.5 °C assumed temperature and occupied status.
- At 00:00: 24.90 kWh forecast and no HIGH USE flag.
- HIGH USE uses both triangle markers and text, so it is not encoded by colour alone.
- Every explanation says the indicators do not prove causation.

## 3 Model performance

### What to click or show

Open **Model Performance**. Show the final MAE and RMSE comparison, validation table, chronological split and feature-importance chart. Change the test chart from **Last 7 days** to **Full test period**. Expand **Reproducibility nuance**.

### What to say to the professor

“I used a chronological train, validation and test split with no random shuffling. HistGradientBoosting and Random Forest were effectively tied on validation. Random Forest had the marginally lower validation MAE in the canonical raw-data pipeline, so I froze that choice before evaluating the 624-hour test period.”

“The baseline copies actual consumption from 24 hours earlier. On the same test timestamps, its MAE was 9.2585 kWh. The ML model achieved 2.9061 kWh, a 68.61% reduction.”

### What the professor should notice

- Train: 2,906 rows, 8 January through 9 May 2026.
- Validation: 622 rows, 9 May through 3 June 2026.
- Test: 624 rows, 4 June through 29 June 2026.
- No test result influenced model selection.
- Occupancy and temperature dominate validation permutation importance. Importance measures predictive reliance, not causation.

## 4 Peak insights and what-if scenario

### What to click or show

Open **Peak Insights**. Point to the 12:00 and 13:00 HIGH USE sections. In the scenario controls, keep 13:00 selected, change occupancy to **Unoccupied**, and move temperature slightly.

### What to say to the professor

“The HIGH USE threshold is the 90th percentile of training consumption, 84.882 kWh. The two adjacent flags trigger a check of HVAC demand, temperature setpoints and flexible-load scheduling.”

“The what-if tool changes selected model inputs while calendar and historical lags remain fixed. It shows model sensitivity, not guaranteed savings or a causal effect.”

### What the professor should notice

- Original 13:00 forecast: 86.11 kWh.
- The scenario forecast and difference update immediately.
- The warning “Scenario analysis — not a guaranteed or causal outcome” remains visible.
- Recommendations require facility-manager verification before action.

## 5 Error analysis

### What to click or show

Open **Error Analysis**. Show the difficult-case banner, the hardest cases table and the scatter plot.

### What to say to the professor

“I retained the model's genuine failures. The largest test error occurred on 17 June at 12:00 during a simulated laboratory load. Actual consumption was 126.25 kWh, while the model predicted 83.67 kWh, an absolute error of 42.58 kWh. The event label is used only for retrospective analysis and was never an input feature.”

### What the professor should notice

- Unusual events remain in the test metrics.
- The system also shows genuine low-error cases from the same held-out test period.
- Failure analysis explains where additional operational data may help a future deployment.

## 6 Responsible AI and close

### What to click or show

Open **Responsible AI / About**. Show the synthetic-data disclosure, human oversight flow, limitations, SDG section, implemented/future lists and architecture diagram.

### What to say to the professor

“The prototype uses aggregate building occupancy, not personal student data. A real deployment would need authentication, restricted meter and BMS access, encryption and audit logs. The human flow is forecast, recommendation, manager verification and human decision.”

“The project primarily supports SDG 7 through better energy awareness. It may also support SDGs 11, 12 and 13, but I do not claim measured energy or carbon savings.”

### Closing statement

“CampusEnergy AI demonstrates an end-to-end, leakage-audited forecasting and decision-support workflow. It beats a meaningful baseline on this synthetic dataset, exposes its failures and keeps the facility manager in control.”

## Emergency fallback

If Streamlit stops, return to PowerShell and press `Ctrl+C`, then run:

```powershell
cd C:\Coding\Projects\CampusEnergy
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8511
```

Check the server without opening a new tool:

```powershell
Invoke-WebRequest http://127.0.0.1:8511/_stcore/health
```

The expected response is `ok`. If the application still cannot open, continue with these verified assets:

- `outputs/phase2/screenshots/overview.png`
- `outputs/phase2/screenshots/performance.png`
- `outputs/charts/future_24h_forecast.png`
- `outputs/phase2/screenshots/what_if.png`
- `outputs/phase2/screenshots/errors.png`
- `outputs/phase2/architecture.png`

Explain that the screenshots were captured from the working application during browser acceptance testing. Do not claim live operation while using the fallback.

## 60 second emergency demo

1. Show the Overview screenshot. Say: “This synthetic-data prototype forecasts the next 24 hourly energy intervals for one building and supports a human facility manager.”
2. Point to 12:00 and 13:00. Say: “These exceed the training-only 84.882 kWh threshold. The peak is 86.11 kWh at 13:00.”
3. Show the performance slide or screenshot. Say: “On 624 untouched chronological test hours, ML MAE was 2.9061 kWh versus 9.2585 kWh for the t-minus-24 baseline, a 68.61% reduction.”
4. Show the difficult case. Say: “The model still missed an unusual laboratory load by 42.58 kWh, and I retained that failure in the reported metrics.”
5. Close with: “The system recommends checks, but a facility manager verifies context and makes every decision.”
