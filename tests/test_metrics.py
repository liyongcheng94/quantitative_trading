"""绩效指标单元测试。"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from qtrader.metrics import compute_metrics


def _metrics_from_nav(nav_values: list[float]) -> dict:
    idx = pd.date_range("2024-01-01", periods=len(nav_values), freq="B")
    nav = pd.Series(nav_values, index=idx, name="nav")
    strat_ret = nav.pct_change().fillna(0.0)
    bench_ret = strat_ret.copy()
    return compute_metrics(strat_ret, nav, bench_ret)


@pytest.mark.unit
def test_total_return_on_known_curve():
    m = _metrics_from_nav([1.0, 1.1, 1.21])
    assert abs(m["total_return"] - 0.21) < 1e-9


@pytest.mark.unit
def test_zero_drawdown_on_monotonic_up():
    m = _metrics_from_nav([1.0, 1.1, 1.2, 1.3])
    assert m["max_drawdown"] == 0.0
    assert np.isnan(m["calmar"])


@pytest.mark.unit
def test_known_drawdown_on_peak_trough():
    m = _metrics_from_nav([1.0, 1.2, 1.0, 1.1])
    assert abs(m["max_drawdown"] - (-1 / 6)) < 1e-6
    assert m["max_dd_date"] == pd.Timestamp("2024-01-03")


@pytest.mark.unit
def test_positive_sharpe_on_monotonic_up():
    m = _metrics_from_nav(list(np.linspace(1.0, 2.0, 50)))
    assert m["sharpe"] > 0


@pytest.mark.unit
def test_negative_sharpe_on_monotonic_down():
    m = _metrics_from_nav(list(np.linspace(1.0, 0.5, 50)))
    assert m["sharpe"] < 0


# ---------- B-2 新增指标测试 ----------


@pytest.mark.unit
def test_sortino_positive_when_monotonic_up():
    """单调上涨时（仅首日因 fillna(0) 扣 rf 有微小下行偏差）Sortino 应为大正数。"""
    m = _metrics_from_nav(list(np.linspace(1.0, 2.0, 50)))
    assert m["sortino"] > 0


@pytest.mark.unit
def test_sortino_negative_when_monotonic_down():
    """单调下跌时均值负、下行偏差正，Sortino 应为负。"""
    m = _metrics_from_nav(list(np.linspace(1.0, 0.5, 50)))
    assert m["sortino"] < 0


@pytest.mark.unit
def test_win_rate_on_alternating_returns():
    """交替涨跌的 nav，胜率应接近 0.5（忽略首日 0 收益）。"""
    nav_values = [1.0, 1.1, 1.0, 1.1, 1.0, 1.1, 1.0, 1.1, 1.0]
    m = _metrics_from_nav(nav_values)
    # pct_change: [NaN→0, +0.1, -0.0909, +0.1, -0.0909, +0.1, -0.0909, +0.1, -0.0909]
    # 正收益 4 次 / 9 总 = 4/9
    assert abs(m["win_rate"] - 4 / 9) < 1e-6


@pytest.mark.unit
def test_profit_factor_greater_than_one_on_winning_strategy():
    """盈利多于亏损时 profit_factor > 1。"""
    nav_values = [1.0, 1.1, 1.05, 1.15]
    m = _metrics_from_nav(nav_values)
    assert m["profit_factor"] > 1.0


@pytest.mark.unit
def test_profit_factor_nan_when_no_losses():
    """单调上涨无亏损日，profit_factor 应为 NaN。"""
    m = _metrics_from_nav(list(np.linspace(1.0, 2.0, 30)))
    assert np.isnan(m["profit_factor"])


@pytest.mark.unit
def test_exposure_time_full_when_always_in_market():
    """signal 全程为 1，exposure_time 应为 1.0。"""
    idx = pd.date_range("2024-01-01", periods=10, freq="B")
    nav = pd.Series(np.linspace(1.0, 1.1, 10), index=idx)
    strat_ret = nav.pct_change().fillna(0.0)
    bench_ret = strat_ret.copy()
    signal = pd.Series([1.0] * 10, index=idx)
    m = compute_metrics(strat_ret, nav, bench_ret, signal=signal)
    assert abs(m["exposure_time"] - 1.0) < 1e-9


@pytest.mark.unit
def test_exposure_time_zero_when_never_in_market():
    """signal 全程为 0，exposure_time 应为 0.0。"""
    idx = pd.date_range("2024-01-01", periods=10, freq="B")
    nav = pd.Series(np.linspace(1.0, 1.1, 10), index=idx)
    strat_ret = nav.pct_change().fillna(0.0)
    bench_ret = strat_ret.copy()
    signal = pd.Series([0.0] * 10, index=idx)
    m = compute_metrics(strat_ret, nav, bench_ret, signal=signal)
    assert abs(m["exposure_time"] - 0.0) < 1e-9


@pytest.mark.unit
def test_exposure_time_nan_when_signal_not_provided():
    """未传 signal 时 exposure_time 应为 NaN（向后兼容）。"""
    m = _metrics_from_nav([1.0, 1.1, 1.2])
    assert np.isnan(m["exposure_time"])


@pytest.mark.unit
def test_information_ratio_nan_when_tracking_benchmark_exactly():
    """策略收益与基准完全一致时，跟踪误差为 0，IR 应为 NaN。"""
    idx = pd.date_range("2024-01-01", periods=20, freq="B")
    strat_ret = pd.Series(np.linspace(0.001, 0.002, 20), index=idx)
    bench_ret = strat_ret.copy()
    nav = (1 + strat_ret).cumprod()
    m = compute_metrics(strat_ret, nav, bench_ret)
    assert np.isnan(m["information_ratio"])


@pytest.mark.unit
def test_information_ratio_positive_when_outperforming_benchmark():
    """策略稳定跑赢基准时 IR 应为正。"""
    idx = pd.date_range("2024-01-01", periods=50, freq="B")
    rng = np.random.default_rng(42)
    bench_ret = pd.Series(rng.normal(0.0, 0.01, 50), index=idx)
    strat_ret = bench_ret + 0.002  # 每日稳定 20bp 超额
    nav = (1 + strat_ret).cumprod()
    m = compute_metrics(strat_ret, nav, bench_ret)
    assert m["information_ratio"] > 0
