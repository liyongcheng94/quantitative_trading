"""L06 课后练习：统计基础与交易成本。"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from _data import get_stock_data


def risk_metrics(df: pd.DataFrame, rf: float = 0.0175) -> dict:
    """计算风险指标。

    Args:
        df: OHLC DataFrame
        rf: 无风险年利率，默认 1.75%（2026 年中国 10 年期国债）

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
    # TODO: ~10 行






    return {}


def backtest_with_cost(df: pd.DataFrame, signal: pd.Series,
                       cost_bps: int = 15) -> pd.Series:
    """含交易成本的策略回测。

    Args:
        df: OHLC DataFrame
        signal: 目标仓位 Series（0~1），index 与 df 对齐
        cost_bps: 每次调仓的总成本（双边，单位万分之一），默认 15

    Returns:
        净值 Series（从 1.0 开始）
    """
    # TODO: ~8 行
    # 提示：
    # rets = df['close'].pct_change()
    # position_change = signal.diff().abs().fillna(signal.iloc[0])
    # cost_today = position_change * cost_bps / 10000
    # nav = ((1 + rets * signal.shift(1) - cost_today).cumprod())





    return pd.Series(dtype=float)


def least_correlated_with(target_code: str = "002594",
                          candidates: list[str] = None) -> tuple[str, float]:
    """找出和 target_code 相关性最低的股票。

    Returns:
        (code, correlation) 二元组
    """
    # TODO: ~8 行
    if candidates is None:
        candidates = ["002602", "002624", "600519", "300750"]




    return ("", 0.0)


def run_all() -> None:
    print("=" * 60); print("题 1：风险指标"); print("=" * 60)
    byd = get_stock_data('002594').set_index('date')
    m = risk_metrics(byd)
    for k, v in m.items():
        print(f"  {k}: {v:.4f}")

    print(); print("=" * 60); print("题 2：含成本回测"); print("=" * 60)
    # 简单信号：MA20 上方持 1，下方持 0
    ma20 = byd['close'].rolling(20).mean()
    signal = (byd['close'] > ma20).astype(int)
    nav = backtest_with_cost(byd.reset_index(), signal.reset_index(drop=True))
    print(f"含成本净值: {nav.iloc[-1]:.3f}  总收益 {(nav.iloc[-1]-1)*100:.2f}%")

    print(); print("=" * 60); print("题 3：最低相关"); print("=" * 60)
    print(least_correlated_with())


if __name__ == "__main__":
    run_all()
