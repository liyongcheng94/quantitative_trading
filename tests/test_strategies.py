"""策略信号生成的单元测试（使用合成数据，不联网）。"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from qtrader.strategies import (
    DualMAStrategy, TurtleStrategy, GridStrategy,
)


def _make_df(n: int = 60, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    close = 100 + np.cumsum(rng.normal(0, 1, n))
    high = close + rng.uniform(0.1, 0.5, n)
    low = close - rng.uniform(0.1, 0.5, n)
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    return pd.DataFrame({"date": dates, "open": close, "high": high,
                         "low": low, "close": close, "volume": 1000})


@pytest.mark.unit
def test_dual_ma_signal_range_and_first_day():
    df = _make_df()
    sig = DualMAStrategy(short=5, long=20).generate_signals(df)
    assert sig.between(0, 1).all()
    assert sig.iloc[0] == 0


@pytest.mark.unit
def test_dual_ma_ma5_above_ma20_gives_long():
    close = np.concatenate([np.linspace(10, 5, 25), np.linspace(5, 20, 25)])
    df = pd.DataFrame({"close": close})
    sig = DualMAStrategy(short=5, long=20).generate_signals(df)
    assert sig.iloc[-1] == 1.0


@pytest.mark.unit
def test_turtle_signal_range_and_first_day():
    df = _make_df(n=60)
    sig = TurtleStrategy(entry_n=20, exit_n=10).generate_signals(df)
    assert sig.between(0, 1).all()
    assert sig.iloc[0] == 0


@pytest.mark.unit
def test_turtle_breakout_triggers_long():
    close = np.concatenate([np.full(20, 10.0), [15.0], np.full(9, 12.0)])
    df = pd.DataFrame({"close": close, "high": close, "low": close})
    sig = TurtleStrategy(entry_n=20, exit_n=10).generate_signals(df)
    assert sig.iloc[-1] == 1.0


@pytest.mark.unit
def test_grid_signal_range_and_first_day():
    df = _make_df(n=80)
    sig = GridStrategy(grid_n=10, lookback=20).generate_signals(df)
    assert sig.between(0, 1).all()
    assert sig.iloc[0] == 0


@pytest.mark.unit
def test_grid_increases_position_on_dip():
    close = np.concatenate([
        np.full(20, 100.0),
        np.linspace(100, 60, 20),
        np.full(20, 60.0),
    ])
    df = pd.DataFrame({
        "close": close,
        "high": close + 0.1,
        "low": close - 0.1,
    })
    sig = GridStrategy(grid_n=10, lookback=20).generate_signals(df)
    assert sig.iloc[-1] >= sig.iloc[25]


# ---------- B-4 Turtle ATR 仓位管理 ----------


@pytest.mark.unit
def test_turtle_atr_backward_compat():
    """不传 atr_n 时退化为 [0,1] 二值信号（与旧行为一致）。"""
    df = _make_df(n=60)
    sig_new = TurtleStrategy(entry_n=20, exit_n=10).generate_signals(df)
    sig_old = TurtleStrategy(entry_n=20, exit_n=10, atr_n=None).generate_signals(df)
    pd.testing.assert_series_equal(sig_new, sig_old, check_names=False)
    assert sig_new.between(0, 1).all()


@pytest.mark.unit
def test_turtle_atr_scales_position_within_max_pos():
    """传 atr_n 后信号仍落在 [0, max_pos] 区间内。"""
    df = _make_df(n=60)
    sig = TurtleStrategy(
        entry_n=20, exit_n=10, atr_n=14,
        risk_per_trade=0.01, max_pos=1.0,
    ).generate_signals(df)
    assert sig.between(0, 1.0 + 1e-9).all()
    assert sig.iloc[0] == 0


@pytest.mark.unit
def test_turtle_atr_max_pos_caps_signal():
    """max_pos=0.5 时信号不超过 0.5。"""
    df = _make_df(n=80)
    sig = TurtleStrategy(
        entry_n=20, exit_n=10, atr_n=14,
        risk_per_trade=0.05, max_pos=0.5,
    ).generate_signals(df)
    assert sig.max() <= 0.5 + 1e-9


@pytest.mark.unit
def test_turtle_atr_zero_signal_when_flat():
    """非持仓状态下 ATR 仓位应为 0（不会因为 atr_pct 小而放大到持仓）。"""
    # 用平稳数据，确保不触发唐奇安突破 → 信号恒为 0
    close = np.full(60, 100.0)
    df = pd.DataFrame({
        "close": close, "high": close, "low": close,
    })
    sig = TurtleStrategy(
        entry_n=20, exit_n=10, atr_n=14,
        risk_per_trade=0.01, max_pos=1.0,
    ).generate_signals(df)
    assert (sig == 0).all()
