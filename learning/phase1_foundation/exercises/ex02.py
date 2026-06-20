"""L02 课后练习：K 线读图与 DataFrame 索引。"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf
import _style
from _data import get_stock_data


# ---------- 题 1 ----------
def find_doji(df: pd.DataFrame, tol: float = 0.005) -> list[pd.Timestamp]:
    """找出十字星日期。

    Args:
        df: OHLC DataFrame（列 date/open/high/low/close）
        tol: open 与 close 的相对差异阈值，默认 0.5%

    Returns:
        十字星日的日期列表（pd.Timestamp 列表），按日期升序
    """
    # TODO: ~3 行




    return []


# ---------- 题 2 ----------
def plot_byd_2024(save_path: str = "data/byd_2024.png") -> str:
    """画比亚迪 2024 全年 K 线 + 20 日均线 + 成交量。

    Returns:
        保存的文件路径
    """
    # TODO: ~8 行
    # 提示：mpf.plot(df_2024, type='candle', mav=20, volume=True, savefig=save_path)





    return save_path


# ---------- 题 3 ----------
def monthly_big_up_count(df: pd.DataFrame, threshold: float = 0.05) -> pd.Series:
    """统计每月"大阳线"出现次数。

    Args:
        df: OHLC DataFrame
        threshold: 涨幅阈值，默认 5%

    Returns:
        pd.Series，index 为月末日期（'M' 频率），值为该月大阳线次数
    """
    # TODO: ~5 行
    # 提示：df.set_index('date') 后用 resample('M') 分组



    return pd.Series(dtype=int)


def run_all() -> None:
    byd = get_stock_data("002594")

    print("=" * 60); print("题 1：十字星"); print("=" * 60)
    dojis = find_doji(byd)
    print(f"比亚迪 2022-2024 共 {len(dojis)} 个十字星")
    print("前 5 个日期：", [d.date() for d in dojis[:5]])

    print(); print("=" * 60); print("题 2：2024 K 线图"); print("=" * 60)
    path = plot_byd_2024()
    print(f"已保存: {path}")

    print(); print("=" * 60); print("题 3：月度大阳线次数"); print("=" * 60)
    print(monthly_big_up_count(byd).tail(12))


if __name__ == "__main__":
    run_all()
