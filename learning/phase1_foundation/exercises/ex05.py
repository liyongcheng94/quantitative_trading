"""L05 课后练习：收益率与涨停识别。"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from _data import get_stock_data


def find_one_word_limit_ups(df: pd.DataFrame, threshold: float = 0.099,
                             eps: float = 0.001) -> list[pd.Timestamp]:
    """返回一字涨停日日期列表。

    一字板条件：
        - chg_pct >= threshold（涨幅达涨停）
        - |open - high| < eps * close
        - |high - low| < eps * close
        - |low - close| < eps * close
    """
    # TODO: ~8 行






    return []


def annualized_return_with_costs(df: pd.DataFrame, cost_bps: int = 10) -> float:
    """扣交易成本后的年化收益率。

    cost_bps: 单边交易成本（佣金+印花税+滑点），单位万分之一（10 = 0.1%）
    假设：每月调仓 1 次（22 交易日），每次全仓切换。
    年成本 = 2 * cost_bps/10000 * 12  (买卖双向)
    """
    # TODO: ~6 行




    return 0.0


def yearly_limit_up_pivot(codes: list[tuple[str, str]]) -> pd.DataFrame:
    """三股每年涨停日数 + 年化收益率。

    Args:
        codes: [(code, name), ...]

    Returns:
        DataFrame index=multiindex(code, year),
        columns=['limit_ups', 'annual_return']
    """
    # TODO: ~12 行






    return pd.DataFrame()


def run_all() -> None:
    print("=" * 60); print("题 1：一字涨停"); print("=" * 60)
    for code, name in [("002594", "比亚迪"), ("002602", "世纪华通"), ("002624", "完美世界")]:
        df = get_stock_data(code).set_index('date')
        yz = find_one_word_limit_ups(df)
        print(f"{name:<8} 一字涨停 {len(yz)} 次")

    print(); print("=" * 60); print("题 2：含成本年化"); print("=" * 60)
    for code, name in [("002594", "比亚迪"), ("002602", "世纪华通"), ("002624", "完美世界")]:
        df = get_stock_data(code).set_index('date')
        r = annualized_return_with_costs(df, cost_bps=15)
        print(f"{name:<8} 含成本年化: {r*100:>7.2f}%")

    print(); print("=" * 60); print("题 3：年度透视"); print("=" * 60)
    codes = [("002594", "比亚迪"), ("002602", "世纪华通"), ("002624", "完美世界")]
    print(yearly_limit_up_pivot(codes))


if __name__ == "__main__":
    run_all()
