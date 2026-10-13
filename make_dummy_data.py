"""버스 노선 / 하차 더미 데이터 생성 -> data/*.xlsx"""
from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)
rng = np.random.default_rng(42)

STOP_NAMES = [
    "서울역", "시청", "광화문", "종로3가", "동대문", "신촌", "홍대입구", "합정",
    "여의도", "영등포", "노량진", "사당", "강남역", "교대", "양재", "잠실",
    "건대입구", "왕십리", "성수", "청량리", "미아사거리", "수유", "노원", "상계",
]
ROUTES = [
    ("100", "간선", 9), ("143", "간선", 11), ("472", "간선", 10),
    ("N13", "심야", 8), ("7016", "지선", 7), ("9401", "광역", 6),
]

# 1) 노선 마스터: 노선별 정류장 순서
stops = pd.DataFrame({
    "stop_id": [f"S{i:04d}" for i in range(1, len(STOP_NAMES) + 1)],
    "stop_name": STOP_NAMES,
})
route_rows = []
for route_id, route_type, n_stops in ROUTES:
    chosen = stops.sample(n_stops, random_state=int(rng.integers(1e6))).reset_index(drop=True)
    for seq, row in enumerate(chosen.itertuples(), start=1):
        route_rows.append({
            "route_id": route_id, "route_type": route_type, "stop_seq": seq,
            "stop_id": row.stop_id, "stop_name": row.stop_name,
        })
routes = pd.DataFrame(route_rows)

# 2) 하차 데이터: 일자 x 시간대 x 노선 x 정류장
dates = pd.date_range("2026-09-01", "2026-09-30")
peak = {7: 3.0, 8: 5.0, 9: 3.0, 12: 1.5, 17: 3.5, 18: 5.0, 19: 3.0}
rows = []
for d in dates:
    weekend = d.dayofweek >= 5
    for r in routes.itertuples():
        for hour in range(5, 24):
            base = peak.get(hour, 1.0) * (0.5 if weekend else 1.0)
            if r.route_type == "심야" and 6 <= hour <= 21:
                continue
            n = rng.poisson(base * 8 * (1 + r.stop_seq / 10))
            rows.append({
                "date": d, "hour": hour, "route_id": r.route_id, "stop_id": r.stop_id,
                "alight_cnt": int(n),
                "transfer_cnt": int(rng.binomial(n, 0.3)),
            })
alight = pd.DataFrame(rows)

with pd.ExcelWriter(DATA_DIR / "bus_routes.xlsx") as w:
    routes.to_excel(w, sheet_name="routes", index=False)
    stops.to_excel(w, sheet_name="stops", index=False)
alight.to_excel(DATA_DIR / "bus_alighting.xlsx", sheet_name="alighting", index=False)

print(f"routes: {len(routes)}행, alighting: {len(alight)}행 -> {DATA_DIR}")
