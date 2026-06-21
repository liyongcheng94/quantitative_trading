"""L02 课后练习参考答案：K 线读图 + DataFrame 索引。

运行：
    .venv/Scripts/python.exe -m learning.phase1_foundation.exercises.solutions.ex02
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_P1 = _HERE.parents[2]  # solutions/ -> exercises/ -> phase1_foundation/
if str(_P1) not in sys.path:
    sys.path.insert(0, str(_P1))

import pandas as pd
import matplotlib.pyplot as plt
import mplfinance as mpf

import _style  # noqa: F401  # 注册中文字体 + A 股配色
from _data import get_stock_data


# ---------- 题 1 ----------
def find_doji(df: pd.DataFrame, tol: float = 0.005) -> list[pd.Timestamp]:
    """找出十字星日期（open 和 close 几乎相等）。

    Args:
        df: OHLC DataFrame，含 date/open/high/low/close
        tol: |open - close| / open < tol 视为十字星，默认 0.5%

    Returns:
        pd.Timestamp 列表（升序）
    """
    open_ = df["open"]
    close = df["close"]
    body_ratio = (open_ - close).abs() / open_
    mask = body_ratio < tol
    # 把 date 列转 datetime 再筛选
    if "date" in df.columns:
        dates = pd.to_datetime(df.loc[mask, "date"])
    else:
        dates = df.index[mask]
        if not pd.api.types.is_datetime64_any_dtype(dates):
            dates = pd.to_datetime(dates)
    return list(dates)


# ---------- 题 2 ----------
def plot_byd_2024(save_path: str = "data/byd_2024.png") -> str:
    """画比亚迪 2024 全年 K 线 + 20 日均线 + 成交量。

    Returns:
        保存的文件路径
    """
    df = get_stock_data("002594").copy()
    df["date"] = pd.to_datetime(df["date"])
    df_2024 = df[df["date"].dt.year == 2024].set_index("date")

    # mplfinance 要求列名严格 OHLCV + DatetimeIndex
    mpf.plot(
        df_2024,
        type="candle",
        mav=20,
        volume=True,
        title="比亚迪 2024 K 线 + MA20",
        style="charles",  # mplfinance 内置样式，中文标题字体由 _style 处理
        savefig=save_path,
    )
    plt.close("all")
    return save_path


# ---------- 题 3 ----------
def monthly_big_up_count(df: pd.DataFrame, threshold: float = 0.05) -> pd.Series:
    """统计每月"大涨"天数（日涨幅 ≥ threshold）。

    Args:
        df: OHLC DataFrame，需含 date 和 close
        threshold: 涨幅阈值，默认 5%

    Returns:
        pd.Series，index 为月末日期（'M' 频），值为当月大涨天数
    """
    work = df.copy()
    work["date"] = pd.to_datetime(work["date"])
    work = work.set_index("date")
    chg = work["close"].pct_change()
    is_big_up = (chg >= threshold).astype(int)
    # resample('ME') 是 pandas 2.2+ 写法，旧版用 'M'
    try:
        return is_big_up.resample("ME").sum()
    except ValueError:
        return is_big_up.resample("M").sum()


def run_all() -> None:
    print("=" * 60)
    print("题 1：十字星")
    print("=" * 60)
    byd = get_stock_data("002594")
    dojis = find_doji(byd)
    print(f"比亚迪 2022-2024 共 {len(dojis)} 个十字星")
    print("前 5 个日期：", [d.date() for d in dojis[:5]])

    print()
    print("=" * 60)
    print("题 2：2024 K 线图")
    print("=" * 60)
    path = plot_byd_2024()
    print(f"已保存: {path}")

    print()
    print("=" * 60)
    print("题 3：月度大涨天数（近 12 个月）")
    print("=" * 60)
    print(monthly_big_up_count(byd).tail(12))


if __name__ == "__main__":
    run_all()
