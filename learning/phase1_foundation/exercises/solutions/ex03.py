"""L03 课后练习参考答案：量价关系与聚合。

运行：
    .venv/Scripts/python.exe -m learning.phase1_foundation.exercises.solutions.ex03
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_P1 = _HERE.parents[2]  # solutions/ -> exercises/ -> phase1_foundation/
if str(_P1) not in sys.path:
    sys.path.insert(0, str(_P1))

import numpy as np
import pandas as pd

from _data import get_stock_data


# ---------- 题 1 ----------
def monthly_stats(df: pd.DataFrame) -> pd.DataFrame:
    """月度 OHLCV + 涨跌幅。

    Args:
        df: 日频 OHLCV，需含 date 列

    Returns:
        DataFrame，index=月末日期，列：
        ['open', 'high', 'low', 'close', 'volume', 'chg_pct']
        - open: 月初第一个交易日的开盘价
        - high: 月内最高
        - low: 月内最低
        - close: 月末最后一个交易日的收盘价
        - volume: 月内总成交量
        - chg_pct: 月度涨跌幅 = (月末 close - 月初 open) / 月初 open
    """
    work = df.copy()
    work["date"] = pd.to_datetime(work["date"])
    work = work.set_index("date").sort_index()

    agg = pd.DataFrame({
        "open":   work["open"].resample("ME").first(),
        "high":   work["high"].resample("ME").max(),
        "low":    work["low"].resample("ME").min(),
        "close":  work["close"].resample("ME").last(),
        "volume": work["volume"].resample("ME").sum(),
    }).dropna()
    agg["chg_pct"] = (agg["close"] - agg["open"]) / agg["open"]
    return agg


# ---------- 题 2 ----------
def rolling_sharpe(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """滚动夏普比率（简化版，无风险利率=0）。

    公式：rolling mean / rolling std * sqrt(252)

    Args:
        df: 日频 OHLC
        window: 滚动窗口，默认 20

    Returns:
        pd.Series（前 window-1 个为 NaN，已 dropna 过）
    """
    work = df.copy()
    if "date" in work.columns:
        work["date"] = pd.to_datetime(work["date"])
        work = work.set_index("date")
    rets = work["close"].pct_change()

    roll_mean = rets.rolling(window).mean()
    roll_std = rets.rolling(window).std()
    sharpe = roll_mean / roll_std * np.sqrt(252)
    return sharpe.dropna()


# ---------- 题 3 ----------
def find_crossings(
    df: pd.DataFrame, short: int = 20, long: int = 60
) -> dict:
    """找金叉/死叉日期。

    Args:
        df: 日频 OHLC
        short: 短均线周期，默认 20
        long: 长均线周期，默认 60

    Returns:
        {"golden": [pd.Timestamp...], "death": [pd.Timestamp...]}
        - golden = ma_short 从下方上穿 ma_long
        - death  = ma_short 从上方下穿 ma_long
    """
    work = df.copy()
    if "date" in work.columns:
        work["date"] = pd.to_datetime(work["date"])
        work = work.set_index("date")
    work = work.sort_index()

    ma_short = work["close"].rolling(short).mean()
    ma_long = work["close"].rolling(long).mean()

    # 关键：用前一日 diff 与今日 diff 比较，判断穿越
    diff_prev = (ma_short - ma_long).shift(1)
    diff_today = ma_short - ma_long

    golden_mask = (diff_prev < 0) & (diff_today > 0)
    death_mask = (diff_prev > 0) & (diff_today < 0)

    # 去掉开头 long 周期内的 NaN
    valid = ma_short.notna() & ma_long.notna() & diff_prev.notna()

    return {
        "golden": list(work.index[golden_mask & valid]),
        "death": list(work.index[death_mask & valid]),
    }


def run_all() -> None:
    byd = get_stock_data("002594")

    print("=" * 60)
    print("题 1：月度统计（近 6 个月）")
    print("=" * 60)
    print(monthly_stats(byd).tail(6))

    print()
    print("=" * 60)
    print("题 2：滚动夏普（近 5 个值）")
    print("=" * 60)
    print(rolling_sharpe(byd).tail())

    print()
    print("=" * 60)
    print("题 3：金叉/死叉")
    print("=" * 60)
    c = find_crossings(byd)
    print(f"比亚迪 2022-2024：金叉 {len(c['golden'])} 次，死叉 {len(c['death'])} 次")
    print("金叉日期：", [d.date() for d in c["golden"][:5]])


if __name__ == "__main__":
    run_all()
