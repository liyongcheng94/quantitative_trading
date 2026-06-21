"""L14 课后练习：多股选股。"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2].parent / 'phase1_foundation'))

import numpy as np
import pandas as pd
from _data import get_stock_data


def momentum_factor(panel: pd.DataFrame, lookback: int = 126) -> pd.Series:
    """动量因子：每只股票过去 lookback 日的累计收益。

    Returns:
        Series index=code, value=累计收益
    """
    # TODO: ~3 行


    return pd.Series(dtype=float)


def rank_composite(factors: dict[str, pd.Series],
                   weights: dict[str, float]) -> pd.Series:
    """多因子 rank 融合：先对每个因子做 pct rank，再加权求和。

    Args:
        factors: {'momentum': Series, 'low_vol': Series, ...}
        weights: {'momentum': 0.4, 'low_vol': 0.3, ...}

    Returns:
        Series，综合得分（0~1）
    """
    # TODO: ~5 行




    return pd.Series(dtype=float)


def quintile_returns(rets: pd.DataFrame, factor: pd.Series,
                     n_groups: int = 5) -> pd.DataFrame:
    """按因子分 n_groups 组，返回每组等权组合的累计净值。

    Returns:
        DataFrame index=date, columns=[f'Q{i}' for i in 1..n_groups]
    """
    # TODO: ~8 行






    return pd.DataFrame()


def run_all() -> None:
    codes = ['002594', '600519', '002624', '300750', '000001',
             '002602', '600104', '601633', '000858', '300251']
    frames = {c: get_stock_data(c).set_index('date')['close'] for c in codes}
    panel = pd.DataFrame(frames).sort_index().ffill()
    rets = panel.pct_change().dropna()

    print("题 1：动量因子")
    mom = momentum_factor(panel)
    print(mom.sort_values(ascending=False).round(3))

    print("\n题 2：综合得分")
    factors = {
        'momentum': mom,
        'low_vol': -rets.std() * np.sqrt(252),
    }
    composite = rank_composite(factors, {'momentum': 0.6, 'low_vol': 0.4})
    print(composite.sort_values(ascending=False).round(3))

    print("\n题 3：分位回测（简化版，n=2 组）")
    q_navs = quintile_returns(rets, mom, n_groups=2)
    print(q_navs.tail())


if __name__ == "__main__":
    run_all()
