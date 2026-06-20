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
