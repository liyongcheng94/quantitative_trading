"""L15 课后练习：组合构建。"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[2].parent / 'phase1_foundation'))

import numpy as np
import pandas as pd
from _data import get_stock_data


def equal_weight(codes: list[str]) -> pd.Series:
    """等权组合权重。"""
    # TODO: 1 行
    return pd.Series(dtype=float)


def inverse_vol_weight(rets: pd.DataFrame) -> pd.Series:
    """反向波动加权：w_i ∝ 1/σ_i。"""
    # TODO: ~3 行



    return pd.Series(dtype=float)


def min_variance_weights(rets: pd.DataFrame) -> pd.Series:
    """Markowitz 最小方差：w = Σ^(-1) 1 / (1' Σ^(-1) 1)。"""
    # TODO: ~5 行




    return pd.Series(dtype=float)


def backtest_rebalanced(rets: pd.DataFrame, weights: pd.Series,
                        rebalance_freq: int = 22) -> pd.Series:
    """定期再平衡回测。"""
    # TODO: ~10 行






    return pd.Series(dtype=float)


def run_all() -> None:
    codes = ['002594', '600519', '002624', '300750', '000001']
    frames = {c: get_stock_data(c).set_index('date')['close'] for c in codes}
    panel = pd.DataFrame(frames).sort_index().ffill()
    rets = panel.pct_change().dropna()

    print("题 1：三种权重对比")
    for name, w in [
        ('等权', equal_weight(codes)),
        ('反向波动', inverse_vol_weight(rets)),
        ('最小方差', min_variance_weights(rets)),
    ]:
        print(f"\n[{name}]")
        print(w.round(3))

    print("\n题 2：组合回测")
    navs = {}
    for name, w in [
        ('等权', equal_weight(codes)),
        ('反向波动', inverse_vol_weight(rets)),
        ('最小方差', min_variance_weights(rets)),
    ]:
        nav = backtest_rebalanced(rets, w, rebalance_freq=22)
        navs[name] = nav
        print(f"{name}: 终值 {nav.iloc[-1]:.3f}, 年化 {(nav.iloc[-1]**(252/len(nav))-1)*100:.2f}%")

    print("\n题 3：最佳方案")
    best = max(navs.items(), key=lambda x: x[1].iloc[-1])
    print(f"最高终值: {best[0]} ({best[1].iloc[-1]:.3f})")


if __name__ == "__main__":
    run_all()
