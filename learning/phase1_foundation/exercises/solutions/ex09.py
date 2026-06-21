"""L09 课后练习参考答案：向量化。

运行：
    .venv/Scripts/python.exe -m learning.phase1_foundation.exercises.solutions.ex09
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_P1 = _HERE.parents[2]
if str(_P1) not in sys.path:
    sys.path.insert(0, str(_P1))

import numpy as np
import pandas as pd


# ---------- 题 1 ----------
def rsi_vectorized(prices: pd.Series, period: int = 14) -> pd.Series:
    """向量化 RSI（Wilder 平滑可用 EMA 近似，也可直接 rolling.mean）。"""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0.0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - 100 / (1 + rs)
    return rsi


# ---------- 题 2 ----------
def batch_cumulative_nav(rets: np.ndarray) -> np.ndarray:
    """批量计算多条净值曲线（纯 NumPy 向量化）。

    Args:
        rets: shape (T, N) 的日收益率矩阵

    Returns:
        shape (T, N) 的累计净值，首日为 1.0
    """
    return np.cumprod(1 + rets, axis=0)


# ---------- 题 3 ----------
def n_largest_drawdowns(nav: pd.Series, n: int = 5) -> pd.DataFrame:
    """找出历史最大 N 次回撤（向量化实现）。

    Returns:
        DataFrame 含 [peak_date, trough_date, drawdown]
    """
    running_max = nav.cummax()
    dd = nav / running_max - 1.0

    # 识别"回撤段"：连续 dd < 0 的片段
    in_dd = dd < 0
    segment_id = (in_dd != in_dd.shift(1).fillna(False)).cumsum()
    # 仅保留确实在回撤中的段
    dd_segments = pd.DataFrame({"dd": dd, "seg": segment_id, "in": in_dd})
    dd_segments = dd_segments[dd_segments["in"]]

    if len(dd_segments) == 0:
        return pd.DataFrame(columns=["peak_date", "trough_date", "drawdown"])

    # 每段取最小 dd（最大回撤幅度）
    rows = []
    for seg_id, group in dd_segments.groupby("seg"):
        trough_idx = group["dd"].idxmin()
        worst = group["dd"].min()
        # peak = 该段开始前的最后一个历史最高点对应的日期
        peak_idx = nav.loc[:trough_idx].idxmax()
        rows.append({
            "peak_date": peak_idx,
            "trough_date": trough_idx,
            "drawdown": float(worst),
        })

    result = pd.DataFrame(rows).sort_values("drawdown").head(n).reset_index(drop=True)
    return result


def run_all() -> None:
    from _data import get_stock_data

    print("=" * 60); print("题 1：RSI 向量化"); print("=" * 60)
    byd = get_stock_data("002594").set_index("date")
    rsi = rsi_vectorized(byd["close"])
    print(f"比亚迪 RSI 末值: {rsi.iloc[-1]:.2f}")

    print(); print("=" * 60); print("题 2：批量净值"); print("=" * 60)
    rng = np.random.default_rng(42)
    rets = rng.normal(0.0005, 0.02, size=(2520, 5))
    navs = batch_cumulative_nav(rets)
    print(f"shape: {navs.shape}, 末值: {navs[-1].round(3)}")

    print(); print("=" * 60); print("题 3：Top 5 回撤"); print("=" * 60)
    nav = (1 + byd["close"].pct_change().fillna(0)).cumprod()
    print(n_largest_drawdowns(nav, n=5))


if __name__ == "__main__":
    run_all()
