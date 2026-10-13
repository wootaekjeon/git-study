"""생성된 xlsx(노선, 하차)를 pandas로 읽어 요약 출력"""
from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).parent / "data"


def load_routes() -> dict[str, pd.DataFrame]:
    """bus_routes.xlsx의 모든 시트를 {시트명: DataFrame}으로 반환"""
    return pd.read_excel(DATA_DIR / "bus_routes.xlsx", sheet_name=None, dtype={"route_id": str})


def load_alighting() -> pd.DataFrame:
    return pd.read_excel(
        DATA_DIR / "bus_alighting.xlsx",
        sheet_name="alighting",
        dtype={"route_id": str, "stop_id": str},
        parse_dates=["date"],
    )


if __name__ == "__main__":
    sheets = load_routes()
    routes, stops = sheets["routes"], sheets["stops"]
    alight = load_alighting()

    print(alight.info())
    print(alight.head())

    # 하차 + 노선 정보 결합
    df = alight.merge(routes, on=["route_id", "stop_id"], how="left")
    print("\n[노선별 총 하차]")
    print(df.groupby("route_id")["alight_cnt"].sum().sort_values(ascending=False))
    print("\n[정류장별 하차 TOP5]")
    print(df.groupby("stop_name")["alight_cnt"].sum().nlargest(5))
    print("\n[시간대별 평균 하차]")
    print(df.groupby("hour")["alight_cnt"].mean().round(1))
