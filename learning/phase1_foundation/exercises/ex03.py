"""L03 课后练习：量价关系与聚合。"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from _data import get_stock_data


def monthly_stats(df: pd.DataFrame) -> pd.DataFrame:
    """月度 OHLCV + 涨跌幅。

    Returns:
        DataFrame index=月末日期，列 open/high/low/close/volume/chg_pct
    """
    # TODO: ~8 行





    return pd.DataFrame()


def rolling_sharpe(df: pd.DataFrame, window: int = 20) -> pd.Series:
    """滚动夏普比率（简化版，无风险利率=0）。

    公式：每日收益的 rolling mean / rolling std × sqrt(252)
    """
    # TODO: ~5 行




    return pd.Series(dtype=float)


def find_crossings(df: pd.DataFrame, short: int = 20, long: int = 60) -> dict:
    """找金叉/死叉日期。

    Returns:
        {'golden': [pd.Timestamp...], 'death': [pd.Timestamp...]}
        golden = ma_short 从下方上穿 ma_long
        death  = ma_short 从上方下穿 ma_long
    """
    # TODO: ~8 行
    # 提示：
    # ma_short = df['close'].rolling(short).mean()
    # ma_long  = df['close'].rolling(long).mean()
    # diff = (ma_short - ma_long).shift(1)  # 前一日差
    # diff_today = ma_short - ma_long
    # 金叉：diff < 0 且 diff_today > 0





    return {"golden": [], "death": []}


def run_all() -> None:
    byd = get_stock_data('002594')

    print("=" * 60); print("题 1：月度统计"); print("=" * 60)
    print(monthly_stats(byd).tail(6))

    print(); print("=" * 60); print("题 2：滚动夏普（最后 5 个值）"); print("=" * 60)
    print(rolling_sharpe(byd).tail())

    print(); print("=" * 60); print("题 3：金叉死叉"); print("=" * 60)
    c = find_crossings(byd)
    print(f"比亚迪 2022 至今：金叉 {len(c['golden'])} 次，死叉 {len(c['death'])} 次")
    print("金叉日期：", [d.date() for d in c['golden'][:5]])


if __name__ == "__main__":
    run_all()
