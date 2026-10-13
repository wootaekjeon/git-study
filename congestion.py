"""정류장 x 시간대 혼잡도 지표 계산 (HTML 생성과 분리)

혼잡도 지표: 일평균 하차 인원(alight_cnt). 승차·차량 용량 데이터가 없어
하차 인원을 혼잡도의 대리 지표로 쓴다.
"""
import pandas as pd

from read_data import load_alighting, load_routes

HOURS = list(range(5, 24))  # 데이터에 존재하는 시간대 (05~23시)
ALL = "전체"


def load_joined() -> tuple[pd.DataFrame, int]:
    """하차 데이터에 정류장 이름을 붙이고, 분석 기간의 일수를 함께 반환"""
    routes = load_routes()["routes"]
    alight = load_alighting()
    df = alight.merge(routes[["route_id", "stop_id", "stop_name"]], on=["route_id", "stop_id"], how="left")
    return df, alight["date"].nunique()


def daily_mean_matrix(frame: pd.DataFrame, n_days: int) -> pd.DataFrame:
    """정류장(행) x 시간대(열) 일평균 하차 인원. 기간 합을 일수로 나눈다."""
    total = frame.groupby(["stop_name", "hour"])["alight_cnt"].sum()
    return (total / n_days).unstack("hour").reindex(columns=HOURS).fillna(0)


def build_options(df: pd.DataFrame, n_days: int) -> dict[str, pd.DataFrame]:
    """전체 + 노선별 행렬. 같은 일수로 나눠서 옵션끼리 값을 비교할 수 있다."""
    options = {ALL: daily_mean_matrix(df, n_days)}
    for rid in sorted(df["route_id"].unique()):
        options[rid] = daily_mean_matrix(df[df["route_id"] == rid], n_days)
    return options


def stop_order(options: dict[str, pd.DataFrame]) -> list[str]:
    """행 순서: 전체 합계 내림차순. 옵션을 바꿔도 정류장 위치가 바뀌지 않게 고정한다."""
    return options[ALL].sum(axis=1).sort_values(ascending=False).index.tolist()


def check_totals(options: dict[str, pd.DataFrame], tol: float = 1e-6) -> float:
    """전체 합계가 노선별 합계의 합과 같은지 확인한다. 차이를 반환한다. (반올림 없이 비교)"""
    route_sum = sum(m.values.sum() for k, m in options.items() if k != ALL)
    diff = abs(options[ALL].values.sum() - route_sum)
    if diff > tol:
        raise ValueError(f"전체와 노선별 합계가 다릅니다: 차이 {diff:.2f}")
    return diff


def top_cells(matrix: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """정류장 x 시간대 셀 중 값이 큰 순서 n개"""
    s = matrix.stack().rename("daily_mean").reset_index()
    s.columns = ["stop_name", "hour", "daily_mean"]
    return s.sort_values("daily_mean", ascending=False).head(n).reset_index(drop=True)


if __name__ == "__main__":
    df, n_days = load_joined()
    options = build_options(df, n_days)
    diff = check_totals(options)
    print(f"분석 기간 {n_days}일, 합계 검증 차이 {diff:.6f}명 (허용 1e-6명 이내)")

    print("\n[전체] 상위 혼잡 정류장·시간대 (일평균 하차 인원)")
    print(top_cells(options[ALL]).to_string(index=False))

    for rid in sorted(k for k in options if k != ALL):
        m = options[rid]
        if m.values.max() == 0:
            continue
        print(f"\n[노선 {rid}] 상위 3개")
        print(top_cells(m, n=3).to_string(index=False))
