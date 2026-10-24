"""Render the six artifact-driven dashboard views."""
from html import escape
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from src.config import OUTPUTS
from src.dashboard import (FEATURE_NAMES, MODEL_CAVEAT, TEAL, SLATE, AMBER,
    chart_style, show_chart, forecast_chart, forecast_table, hour_detail, attention_card, error_table)
from src.what_if import predict_scenario


def render_page(page, data):
    metrics, forecast, predictions, importance = data["metrics"], data["forecast"], data["predictions"], data["importance"]
    final, threshold = metrics["final_test"], metrics["high_use"]["threshold_kwh"]
    selected_model_label = metrics["selection"]["selected_model"].replace("Regressor", "").replace("RandomForest", "Random Forest")
    peak = forecast.loc[forecast.predicted_kwh.idxmax()]
    st.markdown('<div class="eyebrow">CampusEnergy AI / Decision support</div>', unsafe_allow_html=True)
    st.title("Energy foresight for your campus." if page == "Overview" else page)
    st.caption("24-Hour Campus Energy Forecasting & Decision Support" if page == "Overview" else {
        "24-Hour Forecast":"Explore every hour, its assumptions, and the manager check behind it.",
        "Model Performance":"A chronological evaluation, an exact previous-day baseline, and transparent model selection.",
        "Peak Insights":"Turn likely high-use periods into informed checks for the facilities team.",
        "Error Analysis":"Good predictions and genuine failures, shown side by side.",
        "Responsible AI / About":"Understand the purpose, boundaries, and human responsibility behind the prototype.",
    }[page])
    
    if page == "Overview":
        st.markdown(f"**{forecast.timestamp.min():%A, %d %B %Y} · {forecast.timestamp.min():%H:%M}–{forecast.timestamp.max():%H:%M}**  ·  Synthetic prototype campus energy data")
        a,b,c,d = st.columns(4)
        a.metric("Next 24h predicted energy", f"{forecast.predicted_kwh.sum():,.1f} kWh")
        b.metric("Peak hourly energy", f"{peak.predicted_kwh:.1f} kWh", help="Energy consumed during one hour; not an instantaneous kW reading.")
        c.metric("Peak forecast time", f"{peak.timestamp:%H:%M}")
        d.metric("HIGH USE hours", f"{int(forecast.high_use.sum())} / {len(forecast)}")
        st.markdown(f'<div class="proof"><b>{final["mae_improvement_percent"]:.2f}% lower test MAE</b> than the previous-day baseline · ML {final["ml_model"]["mae"]:.2f} kWh vs baseline {final["baseline"]["mae"]:.2f} kWh · {final["test_rows"]} held-out hours</div>', unsafe_allow_html=True)
        st.subheader("Next 24 hours at a glance")
        chart_column, attention_column = st.columns([2,1])
        with chart_column:
            show_chart(forecast_chart(forecast, threshold), "overview_forecast")
        with attention_column:
            attention_card(forecast, threshold)
        st.caption(metrics["future_forecast"]["input_disclosure"])
    
    elif page == "24-Hour Forecast":
        show_chart(forecast_chart(forecast, threshold), "detailed_forecast")
        st.caption(metrics["future_forecast"]["input_disclosure"])
        selected = st.selectbox("Inspect a forecast hour", list(range(len(forecast))), index=int(forecast.predicted_kwh.argmax()),
                                format_func=lambda i: forecast.iloc[i].timestamp.strftime("%d %b · %H:%M"), key="inspect_hour")
        with st.container(border=True):
            hour_detail(forecast.iloc[selected], threshold)
        st.subheader("Hourly forecast ledger")
        st.caption("Scroll within the table to inspect all hours. Δ is forecast minus the exact previous-day baseline.")
        st.dataframe(forecast_table(forecast), hide_index=True, width="stretch", height=430,
            column_config={"Recommended check": st.column_config.TextColumn(width="large"),
                **{name: st.column_config.NumberColumn(format="%.2f") for name in ["Forecast (kWh)", "Baseline (kWh)", "Δ baseline (kWh)"]},
                "Temperature (°C)": st.column_config.NumberColumn(format="%.1f")})
        st.download_button("Download 24-hour forecast CSV", data=forecast.to_csv(index=False).encode("utf-8"),
                           file_name="campusenergy_24h_forecast.csv", mime="text/csv")
    
    elif page == "Model Performance":
        a,b,c = st.columns(3)
        a.metric("ML test MAE", f"{final['ml_model']['mae']:.4f} kWh")
        b.metric("Baseline test MAE", f"{final['baseline']['mae']:.4f} kWh")
        c.metric("MAE improvement", f"{final['mae_improvement_percent']:.2f}%")
        left, right = st.columns([1,1])
        with left:
            st.subheader("Final held-out evaluation")
            fig = go.Figure()
            for name, values, color in [("Previous-day baseline", final["baseline"], SLATE), (selected_model_label,final["ml_model"],TEAL)]:
                fig.add_trace(go.Bar(name=name,x=["MAE","RMSE"],y=[values["mae"],values["rmse"]],marker_color=color,text=[f'{values["mae"]:.2f}',f'{values["rmse"]:.2f}'],textposition="auto"))
            fig.update_yaxes(title="Error (kWh) · lower is better")
            show_chart(chart_style(fig,300), "test_errors")
            st.caption(f"ML RMSE: {final['ml_model']['rmse']:.4f} kWh · Baseline RMSE: {final['baseline']['rmse']:.4f} kWh")
        with right:
            st.subheader("Validation selects the model")
            candidate = pd.DataFrame(metrics["selection"]["validation_candidates"]).T
            candidate.index = [name.replace("Regressor", "") for name in candidate.index]
            candidate = candidate.rename(columns={"mae":"MAE (kWh)","rmse":"RMSE (kWh)"})
            st.dataframe(candidate, width="stretch", column_config={
                name: st.column_config.NumberColumn(format="%.4f") for name in candidate.columns})
            st.info(MODEL_CAVEAT)
            st.caption("Selection uses validation MAE only. After selection, the fixed configuration is refitted on train + validation before the held-out test evaluation.")
        st.subheader("Time moves forward. So does evaluation.")
        split = metrics["split"]
        for col, key, label in zip(st.columns(3), ["train","validation","test"], ["01 · Train","02 · Validate","03 · Test"]):
            with col:
                st.markdown(f"**{label} · {split[key]['rows']:,} hours**")
                st.caption(f"{split[key]['start']} → {split[key]['end']}")
        st.image(str(OUTPUTS/"charts"/"chronological_split.png"), width="stretch")
        st.caption("Past data trains the model. Later data validates it. The latest period is held out for final testing. No random shuffling; training uses no future targets.")
        st.info("Baseline at time t = actual usage at t−24 hours. Both methods are evaluated on exactly the same test timestamps.")
        st.subheader("Actual vs forecast in the test period")
        window = st.selectbox("Test chart window", ["Last 7 days", "Full test period"], key="test_window")
        plotted = predictions.tail(168) if window == "Last 7 days" else predictions
        fig = go.Figure()
        for col,label,color,dash in [("actual_kwh","Actual","#182D40","solid"),("predicted_kwh","ML forecast",TEAL,"solid"),("baseline_kwh","Previous-day baseline",SLATE,"dash")]:
            fig.add_trace(go.Scatter(x=plotted.timestamp,y=plotted[col],name=label,line=dict(color=color,dash=dash,width=2)))
        fig.update_yaxes(title="Hourly energy (kWh)")
        fig.update_layout(hovermode="x unified")
        show_chart(chart_style(fig), "test_timeseries")
        st.caption("Retrospective evaluation uses historical temperature and occupancy and updates lags with observations as time advances. It does not measure error in future weather assumptions or a single 26-day-ahead forecast.")
        st.subheader("What does the model rely on most?")
        ordered = importance.sort_values("importance_mean")
        fig = go.Figure(go.Bar(x=ordered.importance_mean, y=ordered.feature.map(FEATURE_NAMES), orientation="h",marker_color=TEAL,
            error_x=dict(type="data",array=ordered.importance_std,color=SLATE),hovertemplate="%{y}<br>MAE increase: %{x:.3f} kWh<extra></extra>"))
        fig.update_xaxes(title="Increase in validation MAE after permutation (kWh)")
        show_chart(chart_style(fig,420), "importance")
        st.caption("Feature importance indicates which inputs most affected predictive performance. It does not prove that a feature causes energy consumption. Error bars show standard deviation across permutations; this uses the train-fitted validation model.")
        with st.expander("Reproducibility nuance"):
            st.write("The candidates are effectively tied. Tiny cyclic-feature float changes after CSV round-tripping can alter histogram binning and candidate order. The canonical pipeline rebuilds features from raw data; this dashboard loads the frozen model and metrics.")
    
    elif page == "Peak Insights":
        high = forecast[forecast.high_use]
        st.markdown(f"**{len(high)} HIGH USE hours** exceed the training-period 90th percentile of **{threshold:.3f} kWh**.")
        if high.empty:
            st.info("No forecast hour exceeds the historical threshold. Continue normal monitoring.")
        for _, row in high.iterrows():
            with st.expander(f"▲ HIGH USE · {row.timestamp:%H:%M} · {row.predicted_kwh:.2f} kWh", expanded=True):
                hour_detail(row, threshold)
        st.divider()
        st.subheader("Explore a what-if scenario")
        st.write("Adjust the assumptions for one forecast hour and compare the model's response.")
        chosen = st.selectbox("Scenario hour", list(range(len(forecast))), index=int(forecast.predicted_kwh.argmax()),
                              format_func=lambda i: forecast.iloc[i].timestamp.strftime("%d %b · %H:%M"), key="scenario_hour")
        original = forecast.iloc[chosen]
        st.caption(f"Original assumptions: {original.temperature_c:.1f} °C · {'Occupied' if original.occupied else 'Unoccupied'} · {original.predicted_kwh:.2f} kWh")
        left,right = st.columns(2)
        temp = left.slider("Scenario temperature (°C)",10.0,45.0,float(original.temperature_c),0.1,key=f"scenario_temp_{chosen}")
        occ = right.selectbox("Scenario occupancy",[0,1],index=int(original.occupied),format_func=lambda x:"Occupied" if x else "Unoccupied",key=f"scenario_occ_{chosen}")
        scenario = predict_scenario(data["model_bundle"],original,temp,occ)
        value = scenario["scenario_predicted_kwh"]
        # Normalize signed zero from sub-cent floating-point round-off for display only.
        display_delta = round(value-float(original.predicted_kwh), 2) or 0.0
        a,b,c = st.columns(3)
        a.metric("Original forecast",f"{original.predicted_kwh:.2f} kWh")
        b.metric("Scenario forecast",f"{value:.2f} kWh")
        c.metric("Difference from original",f"{display_delta:+.2f} kWh")
        st.warning("Scenario analysis — not a guaranteed or causal outcome.")
        st.caption("Calendar and historical lag inputs stay fixed. This scenario does not replace the canonical forecast. Extreme inputs may be outside the model's training experience.")
    
    elif page == "Error Analysis":
        worst, best = predictions.nlargest(8,"absolute_error"), predictions.nsmallest(8,"absolute_error")
        row = worst.iloc[0]
        st.markdown(f'<div class="attention"><div class="eyebrow">A genuine difficult case</div><h3>{row.timestamp:%d %b · %H:%M} · {row.absolute_error:.2f} kWh absolute error</h3><p>Actual {row.actual_kwh:.2f} kWh · ML {row.predicted_kwh:.2f} kWh · baseline {row.baseline_kwh:.2f} kWh</p><p>Simulated context: {escape(row.event_type.replace("_"," "))}. Event labels are retained for retrospective analysis only; they are never model inputs.</p></div>',unsafe_allow_html=True)
        st.write("The model performs less accurately during unusual loads that temperature, occupancy and historical patterns cannot fully explain. These are retained in the final test metrics.")
        st.subheader("Hardest prediction cases")
        st.dataframe(error_table(worst),hide_index=True,width="stretch")
        st.subheader("Representative good predictions")
        st.caption("Eight lowest-error cases, selected from the same held-out test predictions. They do not summarize typical performance.")
        st.dataframe(error_table(best),hide_index=True,width="stretch")
        st.subheader("Every test hour, including unusual events")
        fig=go.Figure()
        for mask,label,color,symbol in [(predictions.event_type=="normal","Normal simulated hours",TEAL,"circle"),(predictions.event_type!="normal","Simulated events",AMBER,"diamond")]:
            subset=predictions.loc[mask]
            fig.add_trace(go.Scatter(x=subset.actual_kwh,y=subset.predicted_kwh,mode="markers",name=label,marker=dict(color=color,symbol=symbol,size=7,opacity=.65),text=subset.timestamp.astype(str),hovertemplate="%{text}<br>Actual %{x:.2f} · ML %{y:.2f} kWh<extra></extra>"))
        bounds=[0,float(max(predictions.actual_kwh.max(),predictions.predicted_kwh.max()))*1.05]
        fig.add_trace(go.Scatter(x=bounds,y=bounds,mode="lines",name="Perfect prediction",line=dict(color=SLATE,dash="dot")))
        fig.update_xaxes(title="Actual hourly energy (kWh)")
        fig.update_yaxes(title="Predicted hourly energy (kWh)")
        show_chart(chart_style(fig,420),"errors_scatter")
    
    else:
        st.markdown("### Earlier visibility. Informed human decisions.")
        st.write("Campus facility managers need earlier visibility into likely electricity peaks. CampusEnergy AI combines a 24-hour forecast, historical comparison and transparent checks for the building energy manager or facilities team.")
        st.info("Synthetic prototype campus energy data. This prototype does not use real VIT meter or student data.")
        cards = [
            ("Privacy by scope", "Aggregate building-level occupancy only. No names, face recognition, phone tracking or individual student movement."),
            ("Bias and coverage", "Performance may differ during holidays, exams, vacations, festivals, major events and unusual weather."),
            ("Security for deployment", "A real deployment would require authentication, authorization, secure data transport, protected meter/BMS access and logging/auditing."),
            ("Accessible interpretation", "Clear units, labeled charts and textual HIGH USE warnings. Triangle markers supplement colour; controls have readable labels."),
        ]
        for offset in [0,2]:
            for col,(title,body) in zip(st.columns(2),cards[offset:offset+2]):
                with col, st.container(border=True):
                    st.subheader(title)
                    st.write(body)
        st.subheader("People remain in control")
        st.success("AI forecast → Recommendation → Facility manager verification → Human decision")
        st.caption("The prototype does not directly control HVAC, lighting, meters or other equipment.")
        st.subheader("Limitations to keep in view")
        st.write("Synthetic data · Single-building prototype · Assumed future temperature · Simplified occupancy · Unexpected events · Historical-pattern dependence · No causal equipment knowledge · No live BMS integration · 24-hour horizon.")
        with st.container(border=True):
            st.subheader("SDG 7 · Affordable and Clean Energy")
            st.write("Forecasting and peak awareness can support more informed energy management. They can support decisions that may reduce unnecessary electricity use and associated emissions.")
            st.caption("Supporting: SDG 11 — Sustainable Cities and Communities · SDG 12 — Responsible Consumption and Production · SDG 13 — Climate Action. No measured carbon or energy savings are claimed.")
        left,right=st.columns(2)
        with left:
            st.subheader("Implemented")
            st.markdown("- Reproducible synthetic hourly data\n- Chronological split and validation selection\n- Exact t−24 baseline and MAE/RMSE\n- 24-hour forecast and peak detection\n- Recommendations and explainability\n- What-if scenarios and error analysis\n- Streamlit dashboard")
        with right:
            st.subheader("Future work")
            st.markdown("- Real campus smart-meter integration\n- Live weather and aggregate occupancy inputs\n- Multiple buildings\n- Equipment-level anomaly detection\n- Human-approved BMS integration\n- Longer forecast horizons\n- Automated periodic retraining")
        st.subheader("How the implemented system fits together")
        diagram = OUTPUTS/"phase2"/"architecture.png"
        if diagram.exists():
            st.image(str(diagram),width="stretch")
            st.download_button("Download architecture diagram",data=diagram.read_bytes(),file_name="campusenergy_architecture.png",mime="image/png")
        st.caption(MODEL_CAVEAT)
    
    st.markdown('<div class="footnote">CampusEnergy AI · Synthetic prototype campus energy data · Decision support with human oversight</div>',unsafe_allow_html=True)
