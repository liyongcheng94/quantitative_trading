"""L09 课后练习：向量化。"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd


def rsi_vectorized(prices: pd.Series, period: int = 14) -> pd.Series:
    """向量化 RSI。

    提示：
        - delta = prices.diff()
        - gain = delta.where(delta > 0, 0).rolling(period).mean()
        - loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
        - rsi = 100 - 100 / (1 + gain/loss)
    """
    # TODO: ~4 行（与 L07 不同的是这里必须全部向量化，不能 apply）



    return pd.Series(dtype=float)


def batch_cumulative_nav(rets_matrix: np.ndarray) -> np.ndarray:
    """批量累计净值。

    Args:
        rets_matrix: shape (N_days, N_stocks)

    Returns:
        shape 同输入，每列累计净值从 1.0 开始
    """
    # TODO: 1 行



    return np.array([])


def n_largest_drawdowns(nav: pd.Series, n: int = 5) -> pd.DataFrame:
    """找出历史最大 N 次回撤（向量化实现）。

    Returns:
        DataFrame 列 [peak_date, trough_date, drawdown]
    """
    # TODO: ~6 行
    # 提示：
    #   running_max = nav.cummax()
    #   dd = nav / running_max - 1
    #   找出每次"连续 < 0" 段的 min，按深度排序取 top n




    return pd.DataFrame()


def run_all() -> None:
    from _data import get_stock_data

    print("=" * 60); print("题 1：RSI 向量化"); print("=" * 60)
    byd = get_stock_data('002594').set_index('date')
    rsi = rsi_vectorized(byd['close'])
    print(f"比亚迪 RSI 末值: {rsi.iloc[-1]:.2f}")

    print(); print("=" * 60); print("题 2：批量净值"); print("=" * 60)
    rng = np.random.default_rng(42)
    rets = rng.normal(0.0005, 0.02, size=(2520, 5))
    navs = batch_cumulative_nav(rets)
    print(f"shape: {navs.shape}, 末值: {navs[-1].round(3)}")

    print(); print("=" * 60); print("题 3：Top 5 回撤"); print("=" * 60)
    nav = (1 + byd['close'].pct_change().fillna(0)).cumprod()
    print(n_largest_drawdowns(nav, n=5))


if __name__ == "__main__":
    run_all()
