"""绩效指标：总收益、年化、最大回撤、夏普、Calmar、波动率。"""
from __future__ import annotations

import numpy as np
import pandas as pd


def compute_metrics(
    strat_ret: pd.Series,
    nav: pd.Series,
    bench_ret: pd.Series,
    rf_annual: float = 0.03,
) -> dict:
    """计算策略绩效指标。nav / strat_ret / bench_ret 共享 datetime index。"""
    n = len(nav)
    ann_factor = 252.0

    total_ret = nav.iloc[-1] - 1.0
    ann_ret = (1.0 + total_ret) ** (ann_factor / n) - 1.0 if n > 0 else np.nan

    cummax = nav.cummax()
    drawdown = nav / cummax - 1.0
    max_dd = drawdown.min()
    max_dd_date = drawdown.idxmin()

    rf_daily = rf_annual / ann_factor
    excess = strat_ret - rf_daily
    std = excess.std(ddof=0)
    sharpe = (excess.mean() / std) * np.sqrt(ann_factor) if std > 0 else np.nan

    vol = strat_ret.std(ddof=0) * np.sqrt(ann_factor)
    calmar = ann_ret / abs(max_dd) if max_dd < 0 else np.nan

    bench_nav = (1.0 + bench_ret).cumprod()
    bench_total = bench_nav.iloc[-1] - 1.0

    return {
        "n_days": n,
        "total_return": total_ret,
        "ann_return": ann_ret,
        "max_drawdown": max_dd,
        "max_dd_date": max_dd_date,
        "sharpe": sharpe,
        "calmar": calmar,
        "volatility": vol,
        "bench_total_return": bench_total,
        "final_nav": nav.iloc[-1],
    }
