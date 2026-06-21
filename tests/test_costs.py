"""交易成本模型（B-1）单元测试。"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from qtrader.engine import BacktestEngine, CostModel
from qtrader.strategies import Strategy


class _FlatSignal(Strategy):
    """可控信号策略：按 day_step 切换仓位。"""
    name = "TestFlat"

    def __init__(self, signal_values: list[float]):
        self.params = {"signal_values": signal_values}
        self._signal_values = signal_values

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        return pd.Series(self._signal_values, index=df.index, dtype=float)


def _make_df(n: int) -> pd.DataFrame:
    """flat price = 100，daily_ret = 0（剔除市场影响，纯看成本）。"""
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    return pd.DataFrame({
        "date": dates,
        "open": 100.0, "high": 100.0, "low": 100.0,
        "close": 100.0, "volume": 1000,
    })


@pytest.mark.unit
def test_cost_model_buy_sell_rates():
    """CostModel 的 buy_rate / sell_rate / round_trip 计算正确（含默认 5bps 滑点）。"""
    cm = CostModel()  # 默认 A 股 2026
    slip = 5.0 / 10000  # 0.0005
    # 买：佣金 0.00021 + 过户 0.00001 + 滑点 0.0005
    assert abs(cm.buy_rate() - (0.00021 + 0.00001 + slip)) < 1e-9
    # 卖：佣金 + 印花 0.0005 + 过户 + 滑点
    assert abs(cm.sell_rate() - (0.00021 + 0.0005 + 0.00001 + slip)) < 1e-9


@pytest.mark.unit
def test_cost_model_zero_slippage_matches_legacy():
    """slippage_bps=0 时，buy/sell rate 回到无滑点版本。"""
    cm = CostModel(slippage_bps=0.0)
    assert abs(cm.buy_rate() - 0.00022) < 1e-9
    assert abs(cm.sell_rate() - 0.00072) < 1e-9


@pytest.mark.unit
def test_buy_only_incurs_no_stamp_duty():
    """加仓阶段只扣 buy_rate（佣金 + 过户费），不扣印花税。"""
    # 信号：第 0 天空仓 → 第 1 天全仓（一次买入）
    #   buy_turnover[1] = 1.0
    #   cost[1] = 1.0 * 0.00022 = 0.00022
    #   net_ret[1] = 0 - 0.00022 = -0.00022
    df = _make_df(3)
    sig = [0.0, 1.0, 1.0]
    result = BacktestEngine().run(df, _FlatSignal(sig))
    # 第 1 天的 net_ret 应等于 -buy_rate
    expected = -CostModel().buy_rate()
    assert abs(result.nav.pct_change().iloc[1] - expected) < 1e-9


@pytest.mark.unit
def test_sell_incurs_stamp_duty():
    """减仓阶段扣 sell_rate（含印花税）。"""
    # 信号：第 0 天全仓 → 第 1 天空仓（一次卖出）
    #   sell_turnover[1] = 1.0
    #   cost[1] = 1.0 * 0.00072 = 0.00072
    df = _make_df(3)
    sig = [1.0, 0.0, 0.0]
    result = BacktestEngine().run(df, _FlatSignal(sig))
    expected = -CostModel().sell_rate()
    assert abs(result.nav.pct_change().iloc[1] - expected) < 1e-9


@pytest.mark.unit
def test_round_trip_costs_match_buy_plus_sell():
    """完整买卖一次的累计成本 = buy_rate + sell_rate。"""
    # 4 天：空→全→全→空
    df = _make_df(4)
    sig = [0.0, 1.0, 1.0, 0.0]
    result = BacktestEngine().run(df, _FlatSignal(sig))
    # 日净收益：day0=0, day1=-buy_rate, day2=0, day3=-sell_rate
    # 累计净值 = (1-buy_rate) * (1-sell_rate)
    cm = CostModel()
    expected_nav = (1 - cm.buy_rate()) * (1 - cm.sell_rate())
    assert abs(result.nav.iloc[-1] - expected_nav) < 1e-9


@pytest.mark.unit
def test_backward_compatible_with_legacy_commission():
    """传 commission（float）保持向后兼容：转为 CostModel（半费率）。"""
    engine = BacktestEngine(commission=0.002)
    cm = engine.cost_model
    assert cm.commission_rate == 0.001   # 0.002 / 2
    assert cm.stamp_duty_rate == 0.0
    assert cm.transfer_fee_rate == 0.0


@pytest.mark.unit
def test_rejects_both_commission_and_cost_model():
    """同时传 commission 和 cost_model 应报错。"""
    with pytest.raises(ValueError, match="二选一"):
        BacktestEngine(commission=0.001, cost_model=CostModel())


@pytest.mark.unit
def test_zero_cost_model_matches_no_cost():
    """CostModel 全 0 时等价于无成本回测。"""
    zero_cm = CostModel(
        commission_rate=0.0, stamp_duty_rate=0.0,
        transfer_fee_rate=0.0, min_commission=0.0, slippage_bps=0.0,
    )
    df = _make_df(4)
    sig = [0.0, 1.0, 1.0, 0.0]
    result = BacktestEngine(cost_model=zero_cm).run(df, _FlatSignal(sig))
    # 无成本 → 全部 net_ret = 0 → 终值 = 1.0
    assert abs(result.nav.iloc[-1] - 1.0) < 1e-12


@pytest.mark.unit
def test_default_cost_lower_nav_than_zero_cost():
    """真实成本下净值应低于零成本净值（A 股默认费率为正）。"""
    df = _make_df(4)
    sig = [0.0, 1.0, 1.0, 0.0]
    zero_nav = BacktestEngine(
        cost_model=CostModel(0, 0, 0, 0, 0.0)
    ).run(df, _FlatSignal(sig)).nav.iloc[-1]
    real_nav = BacktestEngine().run(df, _FlatSignal(sig)).nav.iloc[-1]
    assert real_nav < zero_nav
