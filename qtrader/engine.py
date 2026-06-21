"""回测引擎：向量化计算策略净值（含 A 股交易成本扣除）。"""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .metrics import compute_metrics
from .strategies import Strategy


@dataclass(frozen=True)
class CostModel:
    """A 股交易成本模型（2026 现行费率）。

    佣金双向，最低 min_commission 元（部分券商已"免 5"）。
    印花税仅在卖出时征收（2023.8.28 起降为 0.05%）。
    过户费 2022.4.29 起沪深统一为 0.001%（双向）。
    滑点 slippage_bps（默认 5bps）按换手率线性扣除——简化模型，
    精细版（成交量比例/涨跌停拒单/TWAP/VWAP）留到 Phase 2。

    Args:
        commission_rate: 双向佣金费率（默认万 2.1 = 0.00021）
        stamp_duty_rate: 卖方印花税费率（默认 0.05% = 0.0005）
        transfer_fee_rate: 双向过户费率（默认 0.001% = 0.00001）
        min_commission: 单笔最低佣金（元）。回测中按 1.0 标准化资金，
            实盘需按真实资金规模换算。默认 0 关闭（教学场景假设"免 5"）。
        slippage_bps: 固定滑点（basis points），默认 5 bps = 0.05%。
            对实盘盈利影响重大，Phase 1 用固定值教学，精细版留 Phase 2。
    """
    commission_rate: float = 0.00021
    stamp_duty_rate: float = 0.0005
    transfer_fee_rate: float = 0.00001
    min_commission: float = 0.0
    slippage_bps: float = 5.0

    def buy_rate(self) -> float:
        """买入单边总费率（佣金 + 过户费 + 滑点）。"""
        return (
            self.commission_rate
            + self.transfer_fee_rate
            + self.slippage_bps / 10000
        )

    def sell_rate(self) -> float:
        """卖出单边总费率（佣金 + 印花税 + 过户费 + 滑点）。"""
        return (
            self.commission_rate
            + self.stamp_duty_rate
            + self.transfer_fee_rate
            + self.slippage_bps / 10000
        )

    def total_round_trip_rate(self) -> float:
        """双边总费率（买 + 卖）。"""
        return self.buy_rate() + self.sell_rate()


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
    """向量化回测引擎（含 A 股 2026 真实交易成本）。

    成本模型区分买入与卖出方向：
    - 仓位增加部分（turnover > 0）按 buy_rate 扣除
    - 仓位减少部分（turnover < 0）按 sell_rate 扣除（含印花税）

    向后兼容：传入 commission（float）时，转为单向费率 CostModel，
    佣金 = commission / 2（买卖各半），与旧行为近似一致。
    """

    def __init__(
        self,
        commission: float | None = None,
        cost_model: CostModel | None = None,
    ):
        if cost_model is not None and commission is not None:
            raise ValueError("commission 与 cost_model 二选一，不要同时传")
        if cost_model is not None:
            self.cost_model = cost_model
        elif commission is not None:
            # 向后兼容：commission 作为双边总费率，平摊到买卖两端
            half = commission / 2
            self.cost_model = CostModel(
                commission_rate=half,
                stamp_duty_rate=0.0,
                transfer_fee_rate=0.0,
                min_commission=0.0,
            )
        else:
            # 默认 A 股 2026 费率
            self.cost_model = CostModel()

    def run(self, df: pd.DataFrame, strategy: Strategy) -> BacktestResult:
        work = df.set_index("date") if "date" in df.columns else df.copy()

        signal = strategy.generate_signals(work)
        daily_ret = work["close"].pct_change().fillna(0.0)

        gross_ret = signal * daily_ret
        signal_prev = signal.shift(1).fillna(0.0)
        delta = signal - signal_prev  # 正 = 加仓，负 = 减仓
        buy_turnover = delta.clip(lower=0.0).abs()
        sell_turnover = delta.clip(upper=0.0).abs()

        cm = self.cost_model
        cost = (
            buy_turnover * cm.buy_rate()
            + sell_turnover * cm.sell_rate()
        )
        net_ret = gross_ret - cost

        nav = pd.Series((1.0 + net_ret).cumprod(), index=work.index, name="nav")
        benchmark_nav = pd.Series(
            (1.0 + daily_ret).cumprod(), index=work.index, name="bench"
        )

        metrics = compute_metrics(net_ret, nav, daily_ret, signal=signal)
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
