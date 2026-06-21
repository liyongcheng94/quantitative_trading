"""绩效指标：总收益、年化、最大回撤、夏普、Sortino、Calmar、波动率、胜率、盈亏比等。"""
from __future__ import annotations

import numpy as np
import pandas as pd


def compute_metrics(
    strat_ret: pd.Series,
    nav: pd.Series,
    bench_ret: pd.Series,
    rf_annual: float = 0.03,
    signal: pd.Series | None = None,
) -> dict:
    """计算策略绩效指标。nav / strat_ret / bench_ret 共享 datetime index。

    新增指标（B-2 扩展）：
    - sortino: 下行风险版 Sharpe，仅用负超额收益计算下行偏差
    - win_rate: 正收益日占比
    - profit_factor: 总盈利 / 总亏损（绝对值），无亏损时为 NaN
    - exposure_time: 持仓时长占比（需传 signal，否则 NaN）
    - information_ratio: 超额收益 / 跟踪误差，基准为零时为 NaN
    """
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

    # Sortino: 下行偏差（downside deviation）= sqrt(mean(min(excess, 0)^2))
    downside = excess.clip(upper=0.0)
    downside_dev = np.sqrt((downside**2).mean()) if n > 0 else np.nan
    sortino = (
        (excess.mean() / downside_dev) * np.sqrt(ann_factor)
        if downside_dev and downside_dev > 0
        else np.nan
    )

    # Win rate: 正收益日占比
    win_rate = float((strat_ret > 0).sum()) / n if n > 0 else np.nan

    # Profit factor: 总盈利 / 总亏损
    gains = float(strat_ret[strat_ret > 0].sum())
    losses = float(-strat_ret[strat_ret < 0].sum())
    profit_factor = gains / losses if losses > 0 else np.nan

    # Exposure time: signal 非零占比（需调用方传 signal）
    if signal is not None and len(signal) > 0:
        exposure_time = float((signal.abs() > 1e-6).sum()) / len(signal)
    else:
        exposure_time = np.nan

    # Information ratio: (strat - bench).mean() / 跟踪误差
    active_return = strat_ret - bench_ret
    tracking_err = active_return.std(ddof=0)
    information_ratio = (
        (active_return.mean() / tracking_err) * np.sqrt(ann_factor)
        if tracking_err > 0
        else np.nan
    )

    return {
        "n_days": n,
        "total_return": total_ret,
        "ann_return": ann_ret,
        "max_drawdown": max_dd,
        "max_dd_date": max_dd_date,
        "sharpe": sharpe,
        "sortino": sortino,
        "calmar": calmar,
        "volatility": vol,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "exposure_time": exposure_time,
        "information_ratio": information_ratio,
        "bench_total_return": bench_total,
        "final_nav": nav.iloc[-1],
    }
