import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "C:/Coding/Projects/CampusEnergy";
const BUILD = path.join(ROOT, ".phase3", "ppt_build");
const PREVIEWS = path.join(BUILD, "previews");
const FINAL = path.join(ROOT, "docs", "CampusEnergyAI_Presentation.pptx");
const SKILL = "C:/Users/Rishik Grandhi/.codex/plugins/cache/openai-primary-runtime/presentations/26.1015.12040/skills/presentations";
const PYTHON = "C:/Users/Rishik Grandhi/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe";
process.env.RUNTIME_NODE_MODULES = "C:/Users/Rishik Grandhi/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules";

const C = {
  navy: "#16324F", ink: "#102A43", teal: "#159D9A", mint: "#D9F0EC",
  sky: "#DCEFFA", pale: "#F3F7F9", white: "#FFFFFF", gray: "#52616B",
  line: "#CBD8DE", amber: "#F2B84B", coral: "#E66C5C", green: "#2E8B74",
};
const FONT = "Aptos";
const metrics = JSON.parse(await fs.readFile(path.join(ROOT, "artifacts", "metrics.json"), "utf8"));
const split = metrics.split;
const finalTest = metrics.final_test;
const candidates = metrics.selection.validation_candidates;
const highUse = metrics.high_use;
const imageFiles = [
  "outputs/phase2/architecture.png",
  "outputs/phase2/screenshots/overview.png",
  "outputs/charts/future_24h_forecast.png",
  "outputs/phase2/screenshots/what_if.png",
];
const imageBytes = new Map();
for (const rel of imageFiles) imageBytes.set(rel, await fs.readFile(path.join(ROOT, rel)));

await fs.mkdir(PREVIEWS, { recursive: true });

const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });

function addText(slide, text, left, top, width, height, size = 22, color = C.ink, bold = false, align = "left") {
  const shape = slide.shapes.add({
    geometry: "textbox", position: { left, top, width, height },
    fill: "none", line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = { fontFamily: FONT, fontSize: size, color, bold, alignment: align, verticalAlignment: "middle" };
  return shape;
}

function addRect(slide, left, top, width, height, fill = C.white, line = C.line, radius = "rounded-lg") {
  return slide.shapes.add({
    geometry: "roundRect", position: { left, top, width, height }, fill,
    line: { style: "solid", fill: line, width: line === "none" ? 0 : 1 }, borderRadius: radius,
  });
}

function addImage(slide, rel, left, top, width, height, fit = "contain", alt = "Project visual") {
  return slide.images.add({ blob: imageBytes.get(rel), contentType: "image/png", alt, fit, position: { left, top, width, height } });
}

function addHeader(slide, number, title, kicker = "CAMPUSENERGY AI") {
  slide.background.fill = C.pale;
  addText(slide, kicker, 58, 30, 520, 22, 12, C.teal, true);
  addText(slide, title, 58, 56, 1060, 62, 34, C.navy, true);
  addText(slide, String(number).padStart(2, "0"), 1170, 38, 52, 30, 13, C.gray, true, "right");
  slide.shapes.add({ geometry: "rect", position: { left: 58, top: 122, width: 1164, height: 2 }, fill: C.teal, line: { fill: "none", width: 0 } });
}

function addFooter(slide, text = "Synthetic / simulated prototype data · Decision support only") {
  addText(slide, text, 58, 682, 1000, 20, 11, C.gray, false);
}

function addMetric(slide, value, label, left, top, width, accent = C.teal) {
  addRect(slide, left, top, width, 132, C.white, C.line);
  slide.shapes.add({ geometry: "rect", position: { left, top, width: 8, height: 132 }, fill: accent, line: { fill: "none", width: 0 } });
  addText(slide, value, left + 26, top + 18, width - 44, 54, 31, C.navy, true);
  addText(slide, label, left + 26, top + 76, width - 44, 36, 15, C.gray, false);
}

function addPill(slide, text, left, top, width, fill = C.mint, color = C.green) {
  addRect(slide, left, top, width, 38, fill, "none", "rounded-full");
  addText(slide, text, left + 10, top + 3, width - 20, 30, 14, color, true, "center");
}

// 1. Cover
{
  const s = deck.slides.add();
  s.background.fill = C.navy;
  addText(s, "CAMPUS ENERGY · DECISION SUPPORT", 72, 58, 600, 28, 13, C.teal, true);
  addText(s, "CampusEnergy AI", 72, 132, 720, 78, 50, C.white, true);
  addText(s, "24-Hour Campus Energy\nForecasting & Decision Support", 72, 214, 650, 130, 28, "#DCEFFA", true);
  addText(s, "Forecast demand. Detect peaks. Support smarter energy decisions.", 72, 370, 630, 60, 20, "#C7D4DD", false);
  addImage(s, "outputs/phase2/architecture.png", 748, 102, 472, 390, "contain", "CampusEnergy AI verified architecture");
  addPill(s, "WORKING PROTOTYPE", 72, 496, 220, C.mint, C.green);
  addPill(s, "HUMAN IN THE LOOP", 308, 496, 220, C.sky, C.navy);
  addText(s, "Hackathon project · Synthetic / simulated prototype campus energy data", 72, 642, 860, 26, 13, "#B8C7D1", false);
}

// 2. Problem
{
  const s = deck.slides.add(); addHeader(s, 2, "Peaks are often visible only after they happen", "THE PROBLEM");
  addText(s, "Reactive reporting", 76, 176, 320, 46, 27, C.navy, true);
  addText(s, "A high-demand period appears in a daily or monthly report after the opportunity to investigate has passed.", 76, 234, 380, 120, 20, C.gray);
  addRect(s, 506, 176, 270, 220, C.white, C.line);
  addText(s, "PEAK", 544, 205, 194, 40, 15, C.coral, true, "center");
  addText(s, "126.25", 538, 249, 206, 72, 45, C.navy, true, "center");
  addText(s, "kWh observed", 538, 325, 206, 32, 16, C.gray, false, "center");
  addText(s, "›", 805, 240, 54, 72, 46, C.teal, true, "center");
  addRect(s, 882, 176, 310, 220, C.navy, C.navy);
  addText(s, "THE OPPORTUNITY", 912, 205, 250, 32, 14, C.teal, true, "center");
  addText(s, "See tomorrow\nbefore tomorrow", 912, 250, 250, 92, 30, C.white, true, "center");
  addText(s, "Advance warning makes verification and scheduling possible.", 76, 472, 1050, 58, 28, C.ink, true);
  addText(s, "The prototype predicts demand and surfaces likely high-use hours. It does not control equipment.", 76, 548, 1020, 56, 20, C.gray);
  addFooter(s);
}

// 3. User and goal
{
  const s = deck.slides.add(); addHeader(s, 3, "Designed for the facility energy manager", "INTENDED USER");
  addRect(s, 64, 164, 350, 442, C.navy, C.navy);
  addText(s, "FACILITY\nMANAGER", 100, 220, 270, 120, 38, C.white, true, "center");
  addText(s, "Reviews forecasts, verifies context, and decides what action is safe and useful.", 104, 372, 262, 112, 18, "#DCEFFA", false, "center");
  const goals = [
    ["01", "Predict", "Next 24 hourly demand values"],
    ["02", "Detect", "Likely high-use periods"],
    ["03", "Support", "Specific checks before a human decision"],
  ];
  goals.forEach((g, i) => {
    const y = 170 + i * 142;
    addText(s, g[0], 478, y, 70, 70, 28, C.teal, true, "center");
    addText(s, g[1], 570, y, 300, 40, 25, C.navy, true);
    addText(s, g[2], 570, y + 44, 560, 52, 18, C.gray);
  });
  addFooter(s);
}

// 4. Solution loop
{
  const s = deck.slides.add(); addHeader(s, 4, "More than an ML notebook", "INTEGRATED SOLUTION");
  const items = [
    ["FORECAST", "24 hourly values"], ["DETECT", "Training-based peaks"], ["EXPLAIN", "Context and importance"],
    ["RECOMMEND", "Transparent checks"], ["DECIDE", "Human verification"],
  ];
  items.forEach((it, i) => {
    const x = 62 + i * 238;
    addRect(s, x, 232, 198, 166, i === 4 ? C.navy : C.white, i === 4 ? C.navy : C.line);
    addText(s, String(i + 1).padStart(2, "0"), x + 20, 250, 58, 30, 14, i === 4 ? C.teal : C.teal, true);
    addText(s, it[0], x + 20, 290, 158, 38, 21, i === 4 ? C.white : C.navy, true);
    addText(s, it[1], x + 20, 338, 158, 42, 15, i === 4 ? "#DCEFFA" : C.gray);
    if (i < 4) addText(s, "›", x + 200, 276, 38, 72, 38, C.teal, true, "center");
  });
  addText(s, "The innovation is the verified forecast-to-decision workflow, not a claim of a new algorithm.", 98, 476, 1084, 74, 25, C.ink, true, "center");
  addFooter(s);
}

// 5. Architecture
{
  const s = deck.slides.add(); addHeader(s, 5, "Verified end-to-end architecture", "SYSTEM ARCHITECTURE");
  addImage(s, "outputs/phase2/architecture.png", 86, 150, 1108, 470, "contain", "CampusEnergy AI system architecture");
  addText(s, "Observed history and assumed future context feed a human-reviewed recommendation, never automatic control.", 110, 627, 1060, 34, 17, C.gray, false, "center");
  addFooter(s);
}

// 6. Dataset
{
  const s = deck.slides.add(); addHeader(s, 6, "A reproducible prototype dataset", "SYNTHETIC DATASET");
  addMetric(s, "4,320", "hourly observations", 64, 166, 254, C.teal);
  addMetric(s, "4,152", "leakage-safe feature rows", 338, 166, 254, C.navy);
  addMetric(s, "42", "fixed random seed", 612, 166, 254, C.amber);
  addMetric(s, "39", "event-like rows", 886, 166, 254, C.coral);
  const inputs = [["ENERGY", "consumption_kwh"], ["WEATHER", "temperature_c"], ["SCHEDULE", "occupied"], ["CALENDAR", "hour and weekday"]];
  inputs.forEach((it, i) => {
    const x = 64 + i * 276;
    addRect(s, x, 350, 246, 116, C.white, C.line);
    addText(s, it[0], x + 20, 370, 206, 30, 14, C.teal, true);
    addText(s, it[1], x + 20, 406, 206, 36, 19, C.navy, true);
  });
  addRect(s, 64, 504, 1076, 88, C.mint, "none");
  addText(s, "Clear disclosure", 90, 518, 190, 26, 14, C.green, true);
  addText(s, "Synthetic / simulated prototype campus energy data. Not real VIT data and not evidence of real-campus accuracy.", 90, 548, 1010, 30, 18, C.ink, true);
  addFooter(s);
}

// 7. Methodology
{
  const s = deck.slides.add(); addHeader(s, 7, "Time order is part of the model contract", "TIME-SERIES METHODOLOGY");
  const blocks = [
    ["TRAIN", `${split.train.rows.toLocaleString()} rows`, "08 Jan to 09 May"],
    ["VALIDATION", `${split.validation.rows.toLocaleString()} rows`, "09 May to 03 Jun"],
    ["FINAL TEST", `${split.test.rows.toLocaleString()} rows`, "04 Jun to 29 Jun"],
  ];
  blocks.forEach((b, i) => {
    const x = 64 + i * 386;
    addRect(s, x, 174, 340, 170, i === 2 ? C.navy : C.white, i === 2 ? C.navy : C.line);
    addText(s, b[0], x + 24, 194, 292, 30, 14, i === 2 ? C.teal : C.teal, true);
    addText(s, b[1], x + 24, 236, 292, 46, 27, i === 2 ? C.white : C.navy, true);
    addText(s, b[2], x + 24, 287, 292, 28, 15, i === 2 ? "#DCEFFA" : C.gray);
    if (i < 2) addText(s, "›", x + 340, 220, 46, 64, 38, C.teal, true, "center");
  });
  addRect(s, 64, 392, 516, 150, C.white, C.line);
  addText(s, "lag_24", 92, 412, 170, 36, 24, C.navy, true);
  addText(s, "actual consumption 24 hours earlier", 92, 455, 430, 34, 17, C.gray);
  addText(s, "lag_168", 92, 495, 170, 36, 24, C.navy, true);
  addText(s, "actual consumption one week earlier", 270, 495, 270, 36, 17, C.gray);
  addRect(s, 616, 392, 588, 150, C.mint, "none");
  addText(s, "NO RANDOM SHUFFLING", 648, 416, 520, 42, 24, C.green, true, "center");
  addText(s, "The model learns from the past before predicting later timestamps.", 656, 468, 504, 48, 18, C.ink, false, "center");
  addFooter(s);
}

// 8. Baseline vs AI
{
  const s = deck.slides.add(); addHeader(s, 8, "The baseline asks a hard, useful question", "BASELINE VS AI");
  addRect(s, 64, 166, 350, 394, C.white, C.line);
  addText(s, "BASELINE", 90, 190, 296, 32, 14, C.teal, true);
  addText(s, "Same hour\nyesterday", 90, 244, 296, 96, 34, C.navy, true);
  addText(s, "prediction(t) = actual(t - 24 h)", 90, 354, 296, 48, 18, C.gray);
  addText(s, "Evaluated on the same 624 final-test timestamps as ML.", 90, 430, 288, 68, 17, C.gray);
  addText(s, "›", 436, 294, 60, 72, 44, C.teal, true, "center");
  addRect(s, 514, 166, 690, 394, C.navy, C.navy);
  addText(s, "VALIDATION MODEL CHOICE", 550, 190, 610, 30, 14, C.teal, true);
  addText(s, "HistGradientBoosting", 550, 246, 330, 34, 21, C.white, true);
  addText(s, `MAE ${candidates.HistGradientBoostingRegressor.mae.toFixed(4)} kWh`, 884, 246, 250, 34, 19, "#DCEFFA", true, "right");
  addText(s, "Random Forest", 550, 312, 330, 34, 21, C.white, true);
  addText(s, `MAE ${candidates.RandomForestRegressor.mae.toFixed(4)} kWh`, 884, 312, 250, 34, 19, "#DCEFFA", true, "right");
  slideLine(s, 550, 294, 584, C.teal);
  addRect(s, 550, 390, 584, 116, "#214968", "none");
  addText(s, "EFFECTIVELY TIED", 576, 406, 530, 28, 14, C.amber, true, "center");
  addText(s, "Random Forest was selected only because canonical validation MAE was marginally lower.", 584, 442, 514, 48, 17, C.white, false, "center");
  addFooter(s);
}

// 9. Evaluation
{
  const s = deck.slides.add(); addHeader(s, 9, "ML reduced final-test MAE by 68.61%", "ACTUAL EVALUATION");
  s.charts.add("bar", {
    position: { left: 64, top: 172, width: 690, height: 392 },
    title: "Untouched final test · 624 hourly rows",
    titleTextStyle: { fontSize: 17, fontFamily: FONT, bold: true, color: C.navy },
    categories: ["MAE", "RMSE"],
    series: [
      { name: "Previous-day baseline", values: [Number(finalTest.baseline.mae.toFixed(4)), Number(finalTest.baseline.rmse.toFixed(4))], fill: C.coral },
      { name: "Selected ML", values: [Number(finalTest.ml_model.mae.toFixed(4)), Number(finalTest.ml_model.rmse.toFixed(4))], fill: C.teal },
    ],
    hasLegend: true, legend: { position: "bottom", fontSize: 12 },
    barOptions: { direction: "column", grouping: "clustered", gapWidth: 70 },
    dataLabels: { showValue: true, position: "outEnd", numberFormatCode: "0.00" },
    yAxis: { minimumScale: 0, maximumScale: 20, majorUnit: 5, majorGridlines: { style: "solid", fill: C.line, width: 1 } },
    chartFill: C.white, chartLine: { fill: C.line, width: 1 },
  });
  addRect(s, 796, 178, 406, 248, C.navy, C.navy);
  addText(s, "68.61%", 828, 218, 342, 80, 52, C.white, true, "center");
  addText(s, "lower MAE than baseline", 828, 308, 342, 40, 21, C.teal, true, "center");
  addText(s, "Baseline MAE  9.2585 kWh\nML MAE          2.9061 kWh", 840, 356, 318, 64, 17, "#DCEFFA", false, "center");
  addRect(s, 796, 450, 406, 114, C.mint, "none");
  addText(s, "Result boundary", 824, 466, 350, 24, 14, C.green, true);
  addText(s, "Specific to the synthetic prototype dataset. Not guaranteed on real campus data.", 824, 496, 350, 52, 17, C.ink);
  addFooter(s);
}

// 10. Dashboard
{
  const s = deck.slides.add(); addHeader(s, 10, "A working product, not a static mockup", "STREAMLIT DASHBOARD");
  addImage(s, "outputs/phase2/screenshots/overview.png", 64, 150, 840, 480, "contain", "CampusEnergy AI Overview page");
  addRect(s, 934, 160, 270, 442, C.navy, C.navy);
  addText(s, "6", 966, 194, 206, 72, 50, C.white, true, "center");
  addText(s, "routed pages", 966, 268, 206, 34, 19, C.teal, true, "center");
  const nav = ["Overview", "24-Hour Forecast", "Model Performance", "Peak Insights", "Error Analysis", "Responsible AI / About"];
  nav.forEach((t, i) => addText(s, `0${i + 1}  ${t}`, 960, 326 + i * 43, 222, 30, 15, "#DCEFFA", i === 0));
  addFooter(s, "Real Phase 2 browser capture · Synthetic / simulated prototype data");
}

// 11. Forecast
{
  const s = deck.slides.add(); addHeader(s, 11, "Two forecast hours cross the training threshold", "NEXT 24 HOURS + PEAKS");
  addImage(s, "outputs/charts/future_24h_forecast.png", 58, 166, 760, 390, "contain", "Canonical 24-hour forecast chart");
  addRect(s, 850, 172, 352, 164, C.white, C.line);
  addText(s, "12:00", 874, 194, 140, 44, 30, C.navy, true);
  addText(s, "84.916 kWh", 1010, 198, 164, 38, 21, C.coral, true, "right");
  addPill(s, "HIGH USE", 874, 256, 142, C.sky, C.navy);
  addRect(s, 850, 356, 352, 164, C.navy, C.navy);
  addText(s, "13:00", 874, 378, 140, 44, 30, C.white, true);
  addText(s, "86.109 kWh", 1010, 382, 164, 38, 21, C.amber, true, "right");
  addPill(s, "HIGH USE", 874, 440, 142, C.mint, C.green);
  addText(s, `Training 90th percentile  ${highUse.threshold_kwh.toFixed(3)} kWh`, 858, 544, 334, 46, 18, C.ink, true, "center");
  addText(s, "Temperature and occupancy are explicit assumptions. Lags use observed history only.", 96, 598, 1080, 50, 17, C.gray, false, "center");
  addFooter(s);
}

// 12. Action
{
  const s = deck.slides.add(); addHeader(s, 12, "Turn a peak into a defensible manager check", "FROM PREDICTION TO ACTION");
  const steps = [
    ["1", "PEAK FORECAST", "13:00 · 86.109 kWh"],
    ["2", "CONTEXT", "Warm · occupied · high lag"],
    ["3", "RECOMMEND", "Verify HVAC and scheduled equipment"],
    ["4", "HUMAN DECISION", "Approve, defer, or investigate"],
  ];
  steps.forEach((st, i) => {
    const y = 166 + i * 112;
    addPill(s, st[0], 72, y + 12, 54, i === 3 ? C.navy : C.mint, i === 3 ? C.white : C.green);
    addText(s, st[1], 154, y, 310, 34, 17, C.teal, true);
    addText(s, st[2], 154, y + 38, 750, 45, 23, C.navy, true);
    if (i < 3) slideLine(s, 99, y + 72, 42, C.line, true);
  });
  addRect(s, 930, 174, 272, 434, C.navy, C.navy);
  addText(s, "BOUNDARY", 962, 214, 208, 32, 14, C.teal, true, "center");
  addText(s, "No automatic\nequipment\ncontrol", 958, 278, 216, 150, 32, C.white, true, "center");
  addText(s, "Facility procedures, comfort, and safety stay in human hands.", 960, 468, 212, 94, 17, "#DCEFFA", false, "center");
  addFooter(s);
}

// 13. What-if and explainability
{
  const s = deck.slides.add(); addHeader(s, 13, "Explore sensitivity without claiming causation", "WHAT-IF + EXPLAINABILITY");
  addImage(s, "outputs/phase2/screenshots/what_if.png", 54, 154, 676, 432, "contain", "What-if scenario page");
  addRect(s, 758, 162, 446, 424, C.white, C.line);
  addText(s, "VALIDATION PERMUTATION IMPORTANCE", 786, 188, 390, 28, 14, C.teal, true);
  const imps = [["occupied", 16.35], ["temperature", 3.69], ["lag_24", 0.80], ["lag_168", 0.61]];
  imps.forEach((it, i) => {
    const y = 246 + i * 64;
    addText(s, it[0], 786, y, 120, 26, 15, C.gray, true);
    addRect(s, 914, y + 2, Math.max(12, it[1] / 16.35 * 224), 22, i === 0 ? C.teal : C.sky, "none", "rounded-sm");
    addText(s, it[1].toFixed(2), 1124, y - 2, 58, 28, 12, C.navy, true, "right");
  });
  addRect(s, 786, 506, 390, 54, C.mint, "none");
  addText(s, "Scenario analysis is not a causal guarantee.", 800, 516, 362, 34, 16, C.green, true, "center");
  addFooter(s);
}

// 14. Testing and failure
{
  const s = deck.slides.add(); addHeader(s, 14, "Strong averages still contain difficult hours", "TESTING + FAILURE ANALYSIS");
  addMetric(s, "44 / 44", "pytest checks passed", 64, 162, 280, C.green);
  addMetric(s, "HTTP 200", "real Streamlit startup", 364, 162, 280, C.teal);
  addMetric(s, "20 / 20", "canonical files hash-identical", 664, 162, 280, C.navy);
  addMetric(s, "0", "future targets used", 964, 162, 240, C.amber);
  addRect(s, 64, 334, 1140, 244, C.navy, C.navy);
  addText(s, "GENUINE DIFFICULT CASE", 92, 356, 360, 28, 14, C.teal, true);
  addText(s, "17 Jun · 12:00", 92, 400, 310, 46, 29, C.white, true);
  addText(s, "Actual 126.25 kWh", 430, 400, 260, 38, 21, "#DCEFFA", true);
  addText(s, "Prediction 83.67 kWh", 704, 400, 286, 38, 21, "#DCEFFA", true);
  addText(s, "42.58 kWh error", 996, 400, 170, 38, 21, C.amber, true, "right");
  slideLine(s, 92, 464, 1074, "#3D617E");
  addText(s, "Retrospective context: a simulated laboratory-load event was intentionally unavailable to the model.", 92, 482, 1044, 44, 18, C.white, false);
  addText(s, "Why show it?", 92, 536, 160, 28, 15, C.teal, true);
  addText(s, "Honest error analysis reveals omitted context and guides safer deployment.", 248, 532, 868, 34, 18, "#DCEFFA");
  addFooter(s);
}

// 15. Responsible AI and SDGs
{
  const s = deck.slides.add(); addHeader(s, 15, "Useful only when its boundaries stay visible", "RESPONSIBLE AI + SDGS");
  addRect(s, 64, 162, 586, 426, C.navy, C.navy);
  addText(s, "HUMAN OVERSIGHT", 92, 188, 530, 30, 14, C.teal, true);
  const flow = ["AI FORECAST", "RECOMMENDATION", "MANAGER VERIFICATION", "HUMAN DECISION"];
  flow.forEach((t, i) => {
    addRect(s, 100, 246 + i * 72, 504, 48, i === 3 ? C.teal : "#214968", "none");
    addText(s, t, 118, 252 + i * 72, 468, 34, 17, C.white, true, "center");
  });
  addText(s, "Aggregate occupancy · visible warnings · access controls in production", 94, 548, 526, 26, 14, "#DCEFFA", false, "center");
  addText(s, "Primary alignment", 704, 174, 430, 30, 14, C.gray, true);
  addRect(s, 704, 216, 430, 112, C.mint, "none");
  addText(s, "SDG 7", 732, 234, 126, 38, 28, C.green, true);
  addText(s, "Affordable and Clean Energy", 860, 236, 246, 36, 20, C.ink, true);
  addText(s, "Advance demand visibility can support efficient operations.", 732, 276, 374, 36, 15, C.gray);
  addText(s, "Supporting relevance", 704, 358, 430, 30, 14, C.gray, true);
  [["11", "Sustainable communities"], ["12", "Responsible consumption"], ["13", "Climate action"]].forEach((it, i) => {
    addPill(s, `SDG ${it[0]}`, 704, 404 + i * 58, 108, C.sky, C.navy);
    addText(s, it[1], 832, 406 + i * 58, 302, 34, 17, C.navy, true);
  });
  addText(s, "No measured carbon reduction is claimed.", 704, 590, 430, 32, 15, C.coral, true);
  addFooter(s);
}

// 16. Close
{
  const s = deck.slides.add(); addHeader(s, 16, "A verified prototype with a clear production path", "IMPLEMENTED · FUTURE · CONCLUSION");
  addRect(s, 64, 160, 530, 390, C.white, C.line);
  addText(s, "IMPLEMENTED NOW", 92, 184, 474, 34, 16, C.teal, true);
  ["Leakage-safe chronological pipeline", "Baseline and two ML candidates", "24-hour forecast with peak flags", "Explainability, scenarios, errors", "Six-page human-reviewed dashboard"].forEach((t, i) => {
    addText(s, "✓", 94, 244 + i * 54, 30, 28, 18, C.green, true);
    addText(s, t, 136, 242 + i * 54, 414, 32, 18, C.navy, i === 0);
  });
  addRect(s, 620, 160, 584, 390, C.navy, C.navy);
  addText(s, "PRODUCTION ROADMAP", 650, 184, 524, 34, 16, C.teal, true);
  ["Approved smart-meter data", "Live weather and occupancy", "Multiple buildings and drift monitoring", "Longer horizons and uncertainty", "Human-approved BMS integration"].forEach((t, i) => {
    addText(s, `0${i + 1}`, 652, 244 + i * 54, 38, 28, 14, C.amber, true);
    addText(s, t, 708, 242 + i * 54, 446, 32, 18, C.white, i === 0);
  });
  addText(s, "Forecast demand. Detect peaks. Support smarter energy decisions.", 86, 590, 1108, 44, 26, C.ink, true, "center");
  addText(s, "CampusEnergy AI keeps the final decision with the facility manager.", 86, 636, 1108, 30, 17, C.gray, false, "center");
}

function slideLine(slide, left, top, width, color, vertical = false) {
  slide.shapes.add({ geometry: "rect", position: { left, top, width: vertical ? 2 : width, height: vertical ? width : 2 }, fill: color, line: { fill: "none", width: 0 } });
}

async function writeBlob(file, blob) {
  await fs.writeFile(file, new Uint8Array(await blob.arrayBuffer()));
}

for (const [index, slide] of deck.slides.items.entries()) {
  const file = path.join(PREVIEWS, `slide-${String(index + 1).padStart(2, "0")}.png`);
  await writeBlob(file, await deck.export({ slide, format: "png", scale: 1 }));
}

const { finalizePresentation } = await import(pathToFileURL(path.join(SKILL, "container_tools", "artifact_tool_utils.mjs")).href);
const staging = path.join(BUILD, ".codex-finalizer");
await fs.mkdir(staging, { recursive: true });
await fs.rm(FINAL, { force: true });
await fs.rm(path.join(staging, "CampusEnergyAI_Presentation.validation.json"), { force: true });
const candidate = path.join(staging, "CampusEnergyAI_Presentation.candidate.pptx");
await (await PresentationFile.exportPptx(deck)).save(candidate);
const result = await finalizePresentation({
  workspaceDir: ROOT,
  candidatePath: candidate,
  finalPath: FINAL,
  pythonExecutable: PYTHON,
  integrityValidatorPath: path.join(SKILL, "container_tools", "inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(SKILL, "container_tools", "inspect_presentation_layout_geometry.py"),
  layoutArgs: ["--expected-slide-size-emu", "12192000,6858000", "--validate-heading-fit"],
  explicitTotalSlideCount: 16,
  requiredNativeTableOwnerSlides: [],
  requiredNativeChartOwnerSlides: [9],
  materializeLiteralChartWorkbooks: true,
  fontPolicy: { basis: "design", families: [FONT] },
  verifyArtifactToolImport: true,
  receiptPath: path.join(staging, "CampusEnergyAI_Presentation.validation.json"),
});
console.log(JSON.stringify({ final: FINAL, previews: PREVIEWS, result }, null, 2));
