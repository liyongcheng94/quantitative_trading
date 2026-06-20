"""L07 课后练习：技术指标。"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from _data import get_stock_data


def compute_macd(prices: pd.Series, fast: int = 12, slow: int = 26,
                 signal: int = 9) -> pd.DataFrame:
    """计算 MACD。

    Returns:
        DataFrame 列 [dif, dea, hist]
    """
    # TODO: ~5 行




    return pd.DataFrame()


def rsi_signal(prices: pd.Series, period: int = 14,
               oversold: int = 30, overbought: int = 70) -> pd.Series:
    """RSI 信号：超卖 +1，超买 -1，中性 0。"""
    # TODO: ~6 行



    return pd.Series(dtype=int)


def best_ma_params(df: pd.DataFrame,
                   params: list[tuple[int, int]] = None) -> tuple[tuple[int, int], float]:
    """搜索最优 MA 参数组合（按夏普）。

    Returns:
        ((short, long), sharpe)
    """
    if params is None:
        params = [(5, 20), (10, 30), (5, 60), (20, 60)]
    # TODO: ~12 行
    # 提示：
    # rets = df['close'].pct_change()
    # for short, long in params:
    #   signal = (df['close'].rolling(short).mean() > df['close'].rolling(long).mean()).astype(int).shift(1).fillna(0)
    #   strat_ret = signal * rets
    #   sharpe = strat_ret.mean() / strat_ret.std() * np.sqrt(252)




    return ((0, 0), 0.0)


def run_all() -> None:
    byd = get_stock_data('002594').set_index('date')

    print("=" * 60); print("题 1：MACD"); print("=" * 60)
    macd = compute_macd(byd['close'])
    print(macd.tail(3))

    print(); print("=" * 60); print("题 2：RSI 信号"); print("=" * 60)
    sig = rsi_signal(byd['close'])
    print(f"超卖信号 {len(sig[sig==1])} 次，超买信号 {len(sig[sig==-1])} 次")

    print(); print("=" * 60); print("题 3：最优 MA 参数"); print("=" * 60)
    best, sharpe = best_ma_params(byd)
    print(f"最优参数: {best}, 夏普: {sharpe:.2f}")


if __name__ == "__main__":
    run_all()
