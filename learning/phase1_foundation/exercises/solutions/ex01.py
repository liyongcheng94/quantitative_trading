"""L01 课后练习参考答案：股票数据基础。

运行：
    .venv/Scripts/python.exe -m learning.phase1_foundation.exercises.solutions.ex01
"""
from __future__ import annotations

import sys
from pathlib import Path

# 自动定位 phase1_foundation 目录，兼容两种启动位置
_HERE = Path(__file__).resolve()
_P1 = _HERE.parents[2]  # solutions/ -> exercises/ -> phase1_foundation/
if str(_P1) not in sys.path:
    sys.path.insert(0, str(_P1))

import pandas as pd

from _data import get_stock_data


# ---------- 题 1 ----------
def moutai_summary(code: str = "600519") -> dict:
    """获取贵州茅台近 1 年数据，返回 high/low/avg_volume 统计字典。

    Args:
        code: 股票代码，默认 600519（贵州茅台）

    Returns:
        {"high": 最高收盘价, "low": 最低收盘价, "avg_volume": 平均日成交量}
    """
    df = get_stock_data(code)
    # 把最近 252 个交易日近似为"近 1 年"（A 股年交易日约 244）
    recent = df.tail(252)
    return {
        "high": float(recent["close"].max()),
        "low": float(recent["close"].min()),
        "avg_volume": float(recent["volume"].mean()),
    }


# ---------- 题 2 ----------
def count_limit_up(df: pd.DataFrame, threshold: float = 0.099) -> int:
    """统计 DataFrame 中涨停的天数。

    Args:
        df: 必须含 close 列
        threshold: 涨幅阈值，默认 9.9%（主板）。科创板/创业板改为 0.199

    Returns:
        涨停天数（int）

    Notes:
        - 第一行的 prev_close 为 NaN，不计入
        - 涨幅 = (close - prev_close) / prev_close，用 pct_change + shift(1)
    """
    prev_close = df["close"].shift(1)
    chg_pct = (df["close"] - prev_close) / prev_close
    # dropna 去掉首行 NaN；再统计超阈值
    return int((chg_pct.dropna() >= threshold).sum())


# ---------- 题 3 ----------
def compare_three_stocks(
    codes: list[str] | None = None,
    names: list[str] | None = None,
) -> pd.DataFrame:
    """三只股票最近一年对比表。

    Args:
        codes: 默认 002594 / 002602 / 002624
        names: 对应名称（比亚迪 / 中公教育 / 完美世界）

    Returns:
        DataFrame，index 为名称，列为：
        ['涨停天数', '平均日成交量', '年化波动率(%)']
        年化波动率 = chg_pct.std() * sqrt(252) * 100
    """
    if codes is None:
        codes = ["002594", "002602", "002624"]
    if names is None:
        names = ["比亚迪", "中公教育", "完美世界"]

    rows = []
    for code in codes:
        df = get_stock_data(code)
        # 只保留最近一年（动态取 max year）
        df_dt = df.copy()
        if "date" in df_dt.columns:
            df_dt["date"] = pd.to_datetime(df_dt["date"])
            latest_year = df_dt["date"].dt.year.max()
            df_recent = df_dt[df_dt["date"].dt.year == latest_year]
        else:
            df_recent = df_dt

        chg = df_recent["close"].pct_change().dropna()
        rows.append({
            "涨停天数": count_limit_up(df_recent),
            "平均日成交量": float(df_recent["volume"].mean()),
            "年化波动率(%)": float(chg.std() * (252 ** 0.5) * 100),
        })

    return pd.DataFrame(rows, index=names)


def run_all() -> None:
    print("=" * 60)
    print("题 1：贵州茅台近 1 年统计")
    print("=" * 60)
    r = moutai_summary()
    print(f"最高收盘价: {r['high']:.2f}")
    print(f"最低收盘价: {r['low']:.2f}")
    print(f"平均日成交量: {r['avg_volume']:,.0f}")

    print()
    print("=" * 60)
    print("题 2：涨停天数（阈值 9.9%）")
    print("=" * 60)
    byd = get_stock_data("002594")
    print(f"比亚迪涨停天数: {count_limit_up(byd)}")
    print(f"比亚迪涨停天数（20% 阈值应 = 0）: {count_limit_up(byd, 0.199)}")

    print()
    print("=" * 60)
    print("题 3：三股最近一年对比表")
    print("=" * 60)
    print(compare_three_stocks())


if __name__ == "__main__":
    run_all()
