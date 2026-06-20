"""回测引擎：向量化计算策略净值（含交易成本扣除）。"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .metrics import compute_metrics
from .strategies import Strategy


@dataclass
class BacktestResult:
    """单次回测结果。"""
    strategy_name: str
    params: dict
    signal: pd.Series
    nav: pd.Series
    benchmark_nav: pd.Series
    metrics: dict
    n_trades: int = 0


class BacktestEngine:
    """向量化回测引擎。

    commission: 单边费率（默认 0.1%），每次仓位变化扣除 turnover * commission。
    """

    def __init__(self, commission: float = 0.001):
        self.commission = commission

    def run(self, df: pd.DataFrame, strategy: Strategy) -> BacktestResult:
        work = df.set_index("date") if "date" in df.columns else df.copy()

        signal = strategy.generate_signals(work)
        daily_ret = work["close"].pct_change().fillna(0.0)

        gross_ret = signal * daily_ret
        turnover = signal.diff().abs().fillna(0.0)
        net_ret = gross_ret - turnover * self.commission

        nav = pd.Series((1.0 + net_ret).cumprod(), index=work.index, name="nav")
        benchmark_nav = pd.Series(
            (1.0 + daily_ret).cumprod(), index=work.index, name="bench"
        )

        metrics = compute_metrics(net_ret, nav, daily_ret)
        n_trades = int((signal.diff().abs() > 1e-6).sum())

        return BacktestResult(
            strategy_name=strategy.name,
            params=dict(strategy.params),
            signal=signal,
            nav=nav,
            benchmark_nav=benchmark_nav,
            metrics=metrics,
            n_trades=n_trades,
        )
