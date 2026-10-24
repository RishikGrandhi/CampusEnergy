# CampusEnergy AI Viva Questions and Answers

Use these answers as short explanations. Give the first sentence, then add detail only if the professor asks.

## Project basics

### What is CampusEnergy AI

CampusEnergy AI is a prototype that forecasts one campus building's hourly electricity consumption for the next 24 hours, flags likely high-use periods and gives checks to a human facility manager.

### What problem are you solving

Reactive reports show peaks after they happen. The project gives the facilities team advance visibility so they can inspect schedules, HVAC demand or unusual equipment before a likely peak.

### Why is this useful

It combines a forecast with a simple benchmark, clear peak flags and practical recommendations. A manager can judge the prediction rather than receiving an unexplained number.

### Who uses it

The primary user is a building energy or facility manager. A facilities team, sustainability team, campus administration or maintenance staff could also use the information.

### What exactly is AI about it

Two supervised regression models learn relationships between hourly consumption and inputs such as occupancy, temperature, calendar patterns and historical energy use. The selected Random Forest produces the final forecast. Peak rules and recommendations are transparent rule-based logic around that forecast.

## Dataset

### Is the data real

No. It is synthetic or simulated prototype campus energy data. It is not VIT data and it is not a live campus meter feed.

### Why use synthetic data

The challenge allows sample or simulated time-series data. Synthetic data lets the project demonstrate generation, forecasting, evaluation and decision support without exposing private operational or student data.

### How many rows are there

The raw dataset has 4,320 hourly observations covering 180 days. After the one-week lag is constructed, 4,152 leakage-safe rows remain.

### What does one row represent

One row represents one clock hour and contains its timestamp, outdoor temperature, aggregate binary occupancy, electricity consumption and a retrospective simulated event label.

### How was energy consumption generated

The generator adds a base load, time-of-day shape, occupancy load, temperature-dependent cooling load, weekday laboratory load, slow efficiency drift and random noise. Seven fixed event periods add unusual loads. Seed 42 makes the data reproducible.

### Why include unusual events

They create realistic failure cases. The event labels are withheld from the model, so unexpected loads reveal limits in features that only describe weather, occupancy, calendar and historical demand.

## ML concepts

### What is regression

Regression predicts a continuous numeric value. Here the numeric target is hourly energy consumption in kWh.

### What is a feature

A feature is an input the model uses to predict the target, such as temperature, occupancy or consumption 24 hours earlier.

### What is the label or target

The target is `consumption_kwh`, the actual energy consumed during that hour.

### What is training

Training fits model parameters using earlier rows where both inputs and the target are known.

### What is validation

Validation compares candidate models on later data without touching the final test period. This project selects the model with the lowest validation MAE.

### What is testing

Testing is the final evaluation on the latest held-out 624 hours. The test set estimates performance after model selection is fixed.

### Why separate them

Using the same rows for fitting, selection and final reporting would give an optimistic result. The separation makes the test evaluation more credible.

### Why chronological splitting

Forecasting must learn from the past and predict later observations. Chronological splitting preserves that direction and prevents future rows from entering training.

### What is data leakage

Leakage occurs when training features or decisions contain information that would not be available at prediction time, especially future target values.

### What did you do to prevent leakage

The code sorts timestamps, uses only positive historical shifts, excludes the current target from the feature matrix, uses ordered slices with no shuffling, selects on validation only and evaluates the test period only after selection. A dedicated integrity audit found no leakage.

## Lag features

### What is lag 24

`lag_24` is actual consumption from exactly 24 hours earlier.

### Why use lag 24

Building demand often repeats by hour of day. It is also the required previous-day baseline.

### What is lag 168

`lag_168` is actual consumption from 168 hours, or one week, earlier.

### Why use a one-week lag

It can preserve weekly schedule patterns that yesterday alone may miss, such as weekday versus weekend behaviour.

### Are lag values available during future forecasting

Yes for this one-day horizon. Every future timestamp's lag 24 and lag 168 points to an observed historical value. No future actual energy value is used.

## Baseline

### What is a baseline

A baseline is a simple reference forecast. A useful ML model should improve on it under the same evaluation conditions.

### Why use the same hour yesterday

It is understandable, leakage-safe and captures daily repetition. The required formula is prediction at time t equals actual consumption at t minus 24 hours.

### Why not just use the baseline instead of ML

The baseline ignores current occupancy, temperature, weekly history and calendar context. The ML model can combine these signals when yesterday differs from today.

### Why was the baseline error higher

The synthetic data include occupancy changes, temperature effects and event-like loads. Copying yesterday can fail when schedules differ. This explanation is specific to the simulated relationships and does not guarantee the same gap on real data.

## Models

### What is Random Forest

Random Forest fits many decision trees on resampled training data and averages their predictions. Averaging reduces the instability of one tree and captures nonlinear relationships without requiring a neural network.

### What is HistGradientBoosting

Histogram gradient boosting builds trees sequentially. Each new tree corrects part of the previous model's error, using binned feature values for efficient training.

### Why use these models

Both work well on medium-sized tabular data, capture nonlinear interactions and run comfortably on a CPU. They provide a genuine candidate comparison without adding unnecessary deep-learning complexity.

### Why not use an LSTM

The dataset has only 4,152 feature rows after lags. Tree ensembles are faster, simpler to validate and better matched to the tabular features. An LSTM would add tuning and interpretation complexity without evidence that it would improve this prototype.

### Which model was better

They were effectively tied. Canonical validation MAE was 2.6187 kWh for Random Forest and 2.6283 kWh for HistGradientBoosting. Random Forest was selected because its canonical validation MAE was marginally lower, not because it was decisively superior.

## Metrics

### What is MAE

Mean absolute error is the average absolute difference between actual and predicted energy. It stays in kWh and is easy to interpret.

### What does 2.9061 kWh MAE mean

Across the 624 final test hours, the ML predictions differed from actual hourly energy by 2.9061 kWh on average in absolute terms.

### What is RMSE

Root mean squared error squares errors before averaging and then returns to kWh. Large misses receive more weight than in MAE.

### Why is RMSE larger

Several simulated unusual events produce large errors. Squaring those errors increases their influence, so the ML RMSE is 5.3521 kWh while MAE is 2.9061 kWh.

### What does 68.61 percent improvement mean

The ML MAE is 68.61% lower than the previous-day baseline MAE on exactly the same 624 test timestamps. It is a result on this synthetic dataset, not a guarantee for real campus data.

## Forecast

### How are the next 24 hours predicted

The frozen Random Forest receives calendar features, assumed temperature and occupancy, plus observed lag 24 and lag 168 values for each future hour. It predicts 24 rows from 30 June 2026 at 00:00 through 23:00.

### Where does future temperature come from

It uses the mean temperature for the same hour across the recent 21 days, adds a disclosed 2 °C warm-day offset and a small daily sinusoidal adjustment.

### Where does future occupancy come from

It follows a documented schedule: weekdays from 08:00 through 18:00, Saturday from 09:00 through 13:00 and unoccupied on Sunday.

### Is that real weather

No. It is an explicit planning assumption, not a weather service or observed future condition.

### Does the forecast use future actual electricity values

No. For the 24-hour horizon, both lags resolve to already observed historical consumption.

## High use

### Why use the 90th percentile

It gives a transparent definition of historically high consumption without tuning on the future forecast. The project computes it from training consumption only.

### What is the threshold

The training-period 90th percentile is 84.882 kWh.

### Which hours are high

12:00 is forecast at about 84.916 kWh and 13:00 at about 86.109 kWh on 30 June 2026.

### What does HIGH USE mean

It means the predicted hourly energy is at or above the training-derived threshold. It is an attention flag, not proof of waste or a command to shut equipment down.

## Recommendations

### How are recommendations produced

Transparent rules inspect the HIGH USE flag, occupancy, temperature, difference from baseline and whether adjacent hours are also high.

### Are the recommendations AI generated

The prediction comes from ML. The recommendation text comes from deterministic rules, so the manager can understand why each check appears.

### Does the system automatically switch off AC

No. It does not control HVAC, lighting, meters or a building-management system.

### Why require human oversight

The model lacks operational context such as scheduled experiments, safety requirements or equipment constraints. A facility manager must verify the situation before action.

## Explainability

### What is permutation importance

The method shuffles one feature on the validation set and measures how much predictive error worsens. A larger increase means the fitted model relied more on that feature for validation performance.

### Does feature importance prove causation

No. It measures predictive reliance within this model and dataset. Correlated inputs and the synthetic generator can affect the ranking.

### What does the Why might this hour be high explanation mean

It is a rule-based explanation that names visible indicators such as high assumed temperature, occupancy, high historical usage or an afternoon pattern. It explicitly avoids causal claims.

## What-if analysis

### What does the scenario simulator do

It changes temperature and occupancy for one selected forecast hour, keeps calendar and historical lags fixed and asks the frozen model for a new prediction.

### Does a changed forecast prove causality

No. The model learned associations from synthetic data. The scenario does not represent a controlled experiment, and other inputs remain fixed.

## Failure analysis

### Does the model ever fail

Yes. Its largest test error is 42.5839 kWh on 17 June 2026 at 12:00.

### Why does it fail

The largest errors occur during simulated laboratory loads and special events. The event label and extra load were not model inputs, so available features could not fully explain the change.

### What are the worst cases

The worst case has actual energy 126.252 kWh, an ML prediction of 83.668 kWh and a baseline of 79.961 kWh. Several neighbouring laboratory-load hours also exceed 35 kWh absolute error.

### Why show failures

Failure cases prevent a misleading average-only story. They identify where real deployments may need event schedules, equipment signals, monitoring and retraining.

## Responsible AI

### Privacy

The prototype uses aggregate building occupancy and no names, faces, phone tracking or individual student movement. Real data access should follow least-privilege controls.

### Bias

Performance may change during exams, holidays, festivals, vacations, schedule changes, unusual weather or events missing from training.

### Security

A production system needs authentication, authorization, encryption, protected meter and BMS access, secrets management and audit logging.

### Accessibility

The dashboard uses units, labelled charts, readable controls, text warnings and triangle markers so HIGH USE is not represented by colour alone.

### Human oversight

The control flow is AI forecast, recommendation, facility-manager verification and human decision. The system has no autonomous equipment authority.

## SDGs

### Why SDG 7

Forecasting and peak awareness can support energy-efficiency decisions. The prototype does not claim measured savings.

### Why SDG 11

Better building operations can support more sustainable campus infrastructure and communities.

### Why SDG 12

The dashboard encourages informed electricity consumption and investigation of avoidable peaks.

### Why SDG 13

Lower unnecessary electricity use may reduce associated emissions where electricity generation has emissions. The project has not measured carbon reduction.

## Production

### How would you use real campus data

Validate meter units and timestamps, align aggregate occupancy and weather, retrain with the same chronological discipline and keep a later period for final evaluation.

### How would you connect smart meters

Use an authenticated ingestion service or approved building-data gateway, validate incoming intervals, store immutable raw records and monitor missing or delayed data.

### Would you retrain periodically

Yes, after monitoring drift and collecting enough verified recent data. Each candidate model would still need chronological validation, and the production team would compare it with the currently deployed model before replacement.

### How would the system scale to multiple buildings

Add a building identifier and building-specific schedules, evaluate per-building errors and decide whether to use separate models or a shared model with building features.

### What additional security would be required

Role-based access, encrypted transport and storage, managed credentials, network isolation for BMS interfaces, audit logs, backups and an approval boundary before any control action.

## Professor trick questions

### Is 68.61 percent guaranteed on real campus data

No. It is the measured improvement on this synthetic prototype's 624-hour test period. Real performance must be established with later real data.

### Why did you not use deep learning

The dataset is small and tabular. Tree ensembles are CPU-friendly, strong for nonlinear tabular relationships and easier to validate and explain.

### Why is synthetic data acceptable

The challenge permits simulated time-series data, and private campus meter data were not required. The disclosure remains visible everywhere so synthetic results cannot be mistaken for a real deployment.

### Could the baseline sometimes beat ML

Yes. A stable day with repeated demand can favour the previous-day baseline. The reported comparison is an average across the same test timestamps, not a claim that ML wins every hour.

### Why not use the test set to select the model

That would make the test result part of the development process and bias the final performance estimate. Validation selects the model; testing reports the frozen decision.

### Why claim Random Forest if HGB can flip after tiny numerical changes

The canonical raw-data pipeline gives Random Forest the marginally lower validation MAE, so it is the frozen selection. The models are described as effectively tied. Processed-CSV round-tripping can change tiny cyclic-feature values and histogram binning, which is why later phases load the frozen artifact instead of retraining from serialized features.

### Did event labels help the model

No. Event labels appear only in retrospective error analysis and never enter the feature matrix.

### Is peak demand measured in kW

The dashboard reports energy consumed during each one-hour interval in kWh. It does not claim an instantaneous electrical-demand measurement in kW.

### Does the what-if occupancy result equal energy savings

No. It is a model scenario under fixed calendar and lag inputs. It does not prove a feasible or causal reduction.

### Does the AI control the building

No. It supports a human decision. Production control integration is future work and would require separate safety, security and approval design.
