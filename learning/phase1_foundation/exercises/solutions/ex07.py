"""L07 课后练习参考答案：技术指标。

运行：
    .venv/Scripts/python.exe -m learning.phase1_foundation.exercises.solutions.ex07
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
def compute_macd(
    prices: pd.Series,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:
    """计算 MACD。

    Returns:
        DataFrame 列 [dif, dea, hist]
        - dif  = EMA_fast - EMA_slow
        - dea  = EMA_signal(dif)
        - hist = 2 * (dif - dea)  （A 股习惯 2 倍柱）
    """
    ema_fast = prices.ewm(span=fast, adjust=False).mean()
    ema_slow = prices.ewm(span=slow, adjust=False).mean()
    dif = ema_fast - ema_slow
    dea = dif.ewm(span=signal, adjust=False).mean()
    hist = 2 * (dif - dea)
    return pd.DataFrame({"dif": dif, "dea": dea, "hist": hist})


# ---------- 题 2 ----------
def rsi_signal(
    prices: pd.Series,
    period: int = 14,
    oversold: int = 30,
    overbought: int = 70,
) -> pd.Series:
    """RSI 信号：超卖 +1，超买 -1，中性 0。"""
    delta = prices.diff()
    gain = delta.where(delta > 0, 0.0).rolling(period).mean()
    loss = (-delta.where(delta < 0, 0.0)).rolling(period).mean()
    rs = gain / loss
    rsi = 100 - 100 / (1 + rs)

    signal = pd.Series(0, index=prices.index, dtype=int)
    signal[rsi < oversold] = 1
    signal[rsi > overbought] = -1
    return signal.fillna(0)


# ---------- 题 3 ----------
def best_ma_params(
    df: pd.DataFrame,
    params: list[tuple[int, int]] | None = None,
) -> tuple[tuple[int, int], float]:
    """搜索最优 MA 参数组合（按夏普）。

    Returns:
        ((short, long), sharpe)
    """
    if params is None:
        params = [(5, 20), (10, 30), (5, 60), (20, 60)]

    work = df.copy()
    if "date" in work.columns:
        work = work.set_index("date")
    rets = work["close"].pct_change()

    best_pair: tuple[int, int] = (0, 0)
    best_sharpe = float("-inf")
    for short, long in params:
        ma_s = work["close"].rolling(short).mean()
        ma_l = work["close"].rolling(long).mean()
        signal = (ma_s > ma_l).astype(float).shift(1).fillna(0)
        strat_ret = signal * rets
        std = strat_ret.std()
        if std > 0:
            sharpe = float(strat_ret.mean() / std * np.sqrt(252))
        else:
            sharpe = float("nan")
        if sharpe > best_sharpe:
            best_sharpe = sharpe
            best_pair = (short, long)

    return best_pair, best_sharpe


def run_all() -> None:
    byd = get_stock_data("002594").set_index("date")

    print("=" * 60); print("题 1：MACD"); print("=" * 60)
    macd = compute_macd(byd["close"])
    print(macd.tail(3))

    print(); print("=" * 60); print("题 2：RSI 信号"); print("=" * 60)
    sig = rsi_signal(byd["close"])
    print(f"超卖信号 {int((sig==1).sum())} 次，超买信号 {int((sig==-1).sum())} 次")

    print(); print("=" * 60); print("题 3：最优 MA 参数"); print("=" * 60)
    best, sharpe = best_ma_params(byd)
    print(f"最优参数: {best}, 夏普: {sharpe:.2f}")


if __name__ == "__main__":
    run_all()
