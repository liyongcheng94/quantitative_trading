"""L01 课后练习：股票数据基础。

每题完成后，在终端运行：
    .venv/Scripts/python.exe -m learning.phase1_foundation.exercises.ex01

或在 notebook 里 from exercises import ex01; ex01.run_all()
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd
from _data import get_stock_data


# ---------- 题 1 ----------
def moutai_summary() -> dict:
    """拉取 600519 贵州茅台最近 1 年数据，返回统计字典。

    Returns:
        dict 包含 high (float) / low (float) / avg_volume (float)
        high/low 是期间最高/最低"收盘价"（不是 high/low 列）
        avg_volume 是平均"日成交量"
    """
    # TODO: 你的代码（约 5 行）






    return {"high": 0.0, "low": 0.0, "avg_volume": 0.0}


# ---------- 题 2 ----------
def count_limit_up(df: pd.DataFrame, threshold: float = 0.099) -> int:
    """统计 DataFrame 中涨停日的数量。

    Args:
        df: 必须含 close 列的 DataFrame
        threshold: 涨幅阈值，主板默认 0.099 (9.9%)，创/科可传 0.199

    Returns:
        涨停日数（int）

    注意:
        - 第一行的 prev_close 为 NaN，不能计入
        - 用 shift(1) 取前一日收盘
    """
    # TODO: 你的代码（约 4 行）




    return 0


# ---------- 题 3 ----------
def compare_three_stocks() -> pd.DataFrame:
    """对三只股票最近一年做对比表。

    Returns:
        DataFrame，index 为股票名，列为 ['涨停日数', '平均日成交量', '年化波动率(%)']
        股票名：比亚迪/世纪华通/完美世界
        代码：002594 / 002602 / 002624
        年化波动率 = chg_pct.std() * sqrt(252) * 100
    """
    # TODO: 你的代码（约 10 行）






    return pd.DataFrame()


def run_all() -> None:
    print("=" * 60)
    print("题 1：贵州茅台最近 1 年统计")
    print("=" * 60)
    r = moutai_summary()
    print(f"最高收盘价: {r['high']:.2f}")
    print(f"最低收盘价: {r['low']:.2f}")
    print(f"平均日成交量: {r['avg_volume']:,.0f}")

    print()
    print("=" * 60)
    print("题 2：涨停日数函数测试")
    print("=" * 60)
    byd = get_stock_data("002594")
    print(f"比亚迪涨停日数: {count_limit_up(byd)}")
    print(f"比亚迪涨停日数(20% 阈值，应为 0): {count_limit_up(byd, 0.199)}")

    print()
    print("=" * 60)
    print("题 3：三股最近一年对比表")
    print("=" * 60)
    print(compare_three_stocks())


if __name__ == "__main__":
    run_all()
