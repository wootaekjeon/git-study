"""정류장 x 시간대 혼잡도 히트맵 HTML 생성 -> results/congestion_heatmap.html

혼잡도 지표: 일평균 하차 인원(alight_cnt). 승차·차량 용량 데이터가 없어
하차 인원을 혼잡도의 대리 지표로 쓴다.
"""
import json
from pathlib import Path

import pandas as pd

from read_data import load_alighting, load_routes

ROOT = Path(__file__).parent
OUT_DIR = ROOT / "results"
OUT_DIR.mkdir(exist_ok=True)
OUT_FILE = OUT_DIR / "congestion_heatmap.html"

HOURS = list(range(5, 24))  # 데이터에 존재하는 시간대 (05~23시)

sheets = load_routes()
routes, stops = sheets["routes"], sheets["stops"]
alight = load_alighting()

df = alight.merge(routes[["route_id", "stop_id", "stop_name"]], on=["route_id", "stop_id"], how="left")


def daily_mean_matrix(frame: pd.DataFrame) -> pd.DataFrame:
    """정류장(행) x 시간대(열) 일평균 하차 인원"""
    per_day = frame.groupby(["date", "stop_name", "hour"])["alight_cnt"].sum().reset_index()
    mean = per_day.groupby(["stop_name", "hour"])["alight_cnt"].sum() / per_day["date"].nunique()
    return mean.unstack("hour").reindex(columns=HOURS).fillna(0).round(1)


# 노선별 + 전체. 색은 모든 옵션에 같은 최대값으로 맞춰 옵션끼리 비교 가능하게 한다.
options = {"전체": daily_mean_matrix(df)}
for rid in sorted(routes["route_id"].unique()):
    options[rid] = daily_mean_matrix(df[df["route_id"] == rid])

# 행 순서는 전체 합계 내림차순으로 고정 (옵션을 바꿔도 정류장 위치가 바뀌지 않게)
order = options["전체"].sum(axis=1).sort_values(ascending=False).index.tolist()
payload = {
    "hours": HOURS,
    "stops": order,
    "options": {k: m.reindex(order).fillna(0).values.tolist() for k, m in options.items()},
    "max": float(max(m.values.max() for m in options.values())),
    "dates": f"{alight['date'].min():%Y-%m-%d} ~ {alight['date'].max():%Y-%m-%d}",
}

HTML = """<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>정류장별 시간대 혼잡도</title>
<style>
:root {
  color-scheme: light;
  --surface-1: #fcfcfb;
  --page: #f9f9f7;
  --text-primary: #0b0b0b;
  --text-secondary: #52514e;
  --muted: #898781;
  --hairline: #e1e0d9;
  --cell-stroke: #fcfcfb;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    color-scheme: dark;
    --surface-1: #1a1a19;
    --page: #0d0d0d;
    --text-primary: #ffffff;
    --text-secondary: #c3c2b7;
    --muted: #898781;
    --hairline: #2c2c2a;
    --cell-stroke: #1a1a19;
  }
}
:root[data-theme="dark"] {
  color-scheme: dark;
  --surface-1: #1a1a19;
  --page: #0d0d0d;
  --text-primary: #ffffff;
  --text-secondary: #c3c2b7;
  --muted: #898781;
  --hairline: #2c2c2a;
  --cell-stroke: #1a1a19;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background: var(--page);
  color: var(--text-primary);
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
}
.viz {
  max-width: 1100px;
  margin: 0 auto;
  padding: 24px 16px 40px;
}
h1 { font-size: 20px; margin: 0 0 4px; }
.sub { color: var(--text-secondary); font-size: 13px; margin: 0 0 16px; }
.card {
  background: var(--surface-1);
  border: 1px solid var(--hairline);
  border-radius: 8px;
  padding: 16px;
}
.controls {
  display: flex; flex-wrap: wrap; gap: 12px; align-items: center;
  margin-bottom: 12px; font-size: 13px; color: var(--text-secondary);
}
select {
  font: inherit; font-size: 13px; color: var(--text-primary);
  background: var(--surface-1); border: 1px solid var(--hairline);
  border-radius: 6px; padding: 4px 8px;
}
.legend { display: flex; align-items: center; gap: 8px; margin-left: auto; font-size: 12px; color: var(--muted); }
.legend .bar { width: 160px; height: 10px; border-radius: 3px; }
.grid-wrap { overflow-x: auto; }
table { border-collapse: separate; border-spacing: 2px; font-size: 12px; }
th {
  font-weight: 400; color: var(--muted); padding: 0 4px; text-align: center; white-space: nowrap;
}
th.row { text-align: right; color: var(--text-secondary); padding-right: 8px; }
td.cell {
  width: 34px; height: 24px; min-width: 34px; border-radius: 3px;
  text-align: center; font-size: 11px; font-variant-numeric: tabular-nums;
  cursor: default; position: relative;
}
td.cell:hover { outline: 2px solid var(--text-primary); outline-offset: -1px; }
.tip {
  position: fixed; pointer-events: none; display: none; z-index: 10;
  background: var(--surface-1); color: var(--text-primary);
  border: 1px solid var(--hairline); border-radius: 6px;
  padding: 6px 8px; font-size: 12px; box-shadow: 0 2px 8px rgba(0,0,0,0.12);
  white-space: nowrap;
}
.note { color: var(--muted); font-size: 12px; margin-top: 12px; line-height: 1.6; }
@media (max-width: 600px) {
  .legend { margin-left: 0; width: 100%; }
}
</style>
</head>
<body>
<div class="viz">
  <h1>정류장별 시간대 혼잡도</h1>
  <p class="sub" id="sub"></p>
  <div class="card">
    <div class="controls">
      <label>노선
        <select id="route"></select>
      </label>
      <div class="legend">
        <span>낮음</span>
        <div class="bar" id="bar"></div>
        <span id="maxlab"></span>
      </div>
    </div>
    <div class="grid-wrap"><table id="grid"></table></div>
    <p class="note">
      셀 값은 하루 평균 하차 인원(명)입니다. 승차 데이터와 차량 정원이 없어 하차 인원을 혼잡도의 대리 지표로 씁니다.
      행은 전체 하차 합계가 많은 순서로 고정되어 있고, 모든 노선이 같은 색 기준을 씁니다.
      데이터가 없는 시간대나 노선에 정차하지 않는 정류장은 0으로 표시됩니다.
    </p>
  </div>
</div>
<div class="tip" id="tip"></div>
<script>
const DATA = __PAYLOAD__;

// 순차(sequential) 색: 기본 파랑 계열, 밝은 쪽 = 낮은 값
const RAMP_LIGHT = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#104281", "#0d366b"];
const RAMP_DARK  = ["#104281", "#184f95", "#1c5cab", "#256abf", "#2a78d6", "#3987e5", "#86b6ef"];

const dark = window.matchMedia("(prefers-color-scheme: dark)");

function hexToRgb(h) {
  return [1, 3, 5].map(i => parseInt(h.slice(i, i + 2), 16));
}
function colorFor(v, ramp) {
  const t = Math.min(Math.max(v / DATA.max, 0), 1);
  if (t === 0) return ramp[0];
  const pos = t * (ramp.length - 1);
  const i = Math.floor(pos), f = pos - i;
  const a = hexToRgb(ramp[i]), b = hexToRgb(ramp[Math.min(i + 1, ramp.length - 1)]);
  const c = a.map((x, k) => Math.round(x + (b[k] - x) * f));
  return "rgb(" + c.join(",") + ")";
}
function textFor(v, ramp) {
  // 진한 셀 위에서는 밝은 글자
  const t = v / DATA.max;
  return t > 0.55 ? "#ffffff" : "var(--text-primary)";
}

const routeSel = document.getElementById("route");
Object.keys(DATA.options).forEach(k => {
  const o = document.createElement("option");
  o.value = k; o.textContent = k === "전체" ? "전체 노선" : k + "번";
  routeSel.appendChild(o);
});

document.getElementById("sub").textContent =
  "분석 기간 " + DATA.dates + " · 시간대 " + DATA.hours[0] + "~" + (DATA.hours[DATA.hours.length - 1]) + "시";
document.getElementById("maxlab").textContent = DATA.max.toFixed(0) + "명";

function ramp() { return dark.matches ? RAMP_DARK : RAMP_LIGHT; }

function drawLegend() {
  const r = ramp();
  document.getElementById("bar").style.background =
    "linear-gradient(to right, " + r.join(",") + ")";
}

function render() {
  const key = routeSel.value;
  const rows = DATA.options[key];
  const r = ramp();
  const table = document.getElementById("grid");
  const tip = document.getElementById("tip");
  let html = "<thead><tr><th></th>";
  DATA.hours.forEach(h => { html += "<th>" + h + "</th>"; });
  html += "</tr></thead><tbody>";
  rows.forEach((vals, i) => {
    html += "<tr><th class='row'>" + DATA.stops[i] + "</th>";
    vals.forEach((v, j) => {
      const label = DATA.stops[i] + " · " + DATA.hours[j] + "시 · " + v.toFixed(1) + "명";
      html += "<td class='cell' data-label='" + label.replace(/'/g, "&#39;") + "'" +
        " style='background:" + colorFor(v, r) + ";color:" + textFor(v, r) + "'>" +
        (v >= 1 ? v.toFixed(0) : "") + "</td>";
    });
    html += "</tr>";
  });
  html += "</tbody>";
  table.innerHTML = html;
  drawLegend();
}

table_events();
function table_events() {
  const table = document.getElementById("grid");
  const tip = document.getElementById("tip");
  table.addEventListener("mousemove", e => {
    const td = e.target.closest("td.cell");
    if (!td) { tip.style.display = "none"; return; }
    tip.textContent = td.dataset.label;
    tip.style.display = "block";
    tip.style.left = (e.clientX + 12) + "px";
    tip.style.top = (e.clientY + 12) + "px";
  });
  table.addEventListener("mouseleave", () => { tip.style.display = "none"; });
}

routeSel.addEventListener("change", render);
dark.addEventListener("change", render);
routeSel.value = "전체";
render();
</script>
</body>
</html>
"""

OUT_FILE.write_text(HTML.replace("__PAYLOAD__", json.dumps(payload, ensure_ascii=False)), encoding="utf-8")
print(f"정류장 {len(order)}개 x 시간대 {len(HOURS)}개 -> {OUT_FILE}")
