"""L06 课后练习参考答案：统计基础与交易成本。

运行：
    .venv/Scripts/python.exe -m learning.phase1_foundation.exercises.solutions.ex06
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

from _data import get_stock_data


# ---------- 题 1 ----------
def risk_metrics(df: pd.DataFrame, rf: float = 0.03) -> dict:
    """计算风险指标。

    Args:
        df: OHLC DataFrame
        rf: 无风险年利率，默认 3%

    Returns:
        {
            'mean_daily': 日均收益率
            'std_daily': 日波动
            'mean_annual': 年化收益
            'std_annual': 年化波动
            'sharpe': 夏普比率
            'max_drawdown': 最大回撤（负数，如 -0.35）
        }
    """
    work = df.copy()
    if "date" in work.columns:
        work = work.set_index("date")
    rets = work["close"].pct_change().dropna()

    mean_d = float(rets.mean())
    std_d = float(rets.std(ddof=0))
    mean_a = mean_d * 252
    std_a = std_d * np.sqrt(252)
    sharpe = (mean_a - rf) / std_a if std_a > 0 else float("nan")

    nav = (1 + rets).cumprod()
    drawdown = nav / nav.cummax() - 1.0
    max_dd = float(drawdown.min())

    return {
        "mean_daily": mean_d,
        "std_daily": std_d,
        "mean_annual": mean_a,
        "std_annual": std_a,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
    }


# ---------- 题 2 ----------
def backtest_with_cost(
    df: pd.DataFrame,
    signal: pd.Series,
    cost_bps: int = 15,
) -> pd.Series:
    """含交易成本的策略回测。

    Args:
        df: OHLC DataFrame
        signal: 目标仓位 Series（0~1），index 与 df 对齐
        cost_bps: 每次调仓的总成本（双边，单位万分之一），默认 15

    Returns:
        净值 Series（从 1.0 开始）
    """
    work = df.copy()
    if "date" in work.columns:
        work = work.set_index("date")
    rets = work["close"].pct_change().fillna(0.0)

    # 用前一日 signal 算今日收益（避免未来函数）
    position_prev = signal.shift(1).fillna(0.0)
    gross = rets * position_prev

    # 每日调仓成本：仓位变化的绝对值 * cost_bps / 10000
    turnover = signal.diff().abs().fillna(signal.iloc[0] if len(signal) > 0 else 0.0)
    cost = turnover * cost_bps / 10000

    net_ret = gross - cost
    nav = (1 + net_ret).cumprod()
    nav.name = "nav"
    return nav


# ---------- 题 3 ----------
def least_correlated_with(
    target_code: str = "002594",
    candidates: list[str] | None = None,
) -> tuple[str, float]:
    """找出和 target_code 相关性最低的股票。

    Args:
        target_code: 目标股票代码
        candidates: 候选股票列表

    Returns:
        (code, correlation) 二元组
    """
    if candidates is None:
        candidates = ["002602", "002624", "600519", "300750", "000001"]

    target_df = get_stock_data(target_code).set_index("date")
    target_ret = target_df["close"].pct_change().dropna()

    best_code = ""
    best_corr = 2.0  # 不可能的高值
    for code in candidates:
        if code == target_code:
            continue
        cand_df = get_stock_data(code).set_index("date")
        cand_ret = cand_df["close"].pct_change().dropna()
        # 对齐日期
        aligned = pd.concat([target_ret, cand_ret], axis=1).dropna()
        aligned.columns = ["tgt", "cand"]
        if len(aligned) < 10:
            continue
        corr = float(aligned["tgt"].corr(aligned["cand"]))
        if abs(corr) < abs(best_corr):
            best_corr = corr
            best_code = code

    return best_code, best_corr


def run_all() -> None:
    byd = get_stock_data("002594").set_index("date")

    print("=" * 60); print("题 1：风险指标"); print("=" * 60)
    m = risk_metrics(byd, rf=0.0175)
    for k, v in m.items():
        if isinstance(v, float):
            print(f"  {k:>15}: {v:.4f}")

    print(); print("=" * 60); print("题 2：含成本回测（BYD 持有信号对比）"); print("=" * 60)
    # 简单信号：第 100 天后开始全仓持有
    sig = pd.Series(0.0, index=byd.index)
    sig.iloc[100:] = 1.0
    nav = backtest_with_cost(byd, sig, cost_bps=15)
    print(f"  最终净值: {nav.iloc[-1]:.3f}")

    print(); print("=" * 60); print("题 3：和比亚迪相关性最低的股票"); print("=" * 60)
    code, corr = least_correlated_with("002594")
    print(f"  代码: {code}, 相关系数: {corr:.3f}")


if __name__ == "__main__":
    run_all()
