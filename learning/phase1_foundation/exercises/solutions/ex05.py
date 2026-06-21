"""L05 课后练习参考答案：收益率与涨停识别。

运行：
    .venv/Scripts/python.exe -m learning.phase1_foundation.exercises.solutions.ex05
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_P1 = _HERE.parents[2]
if str(_P1) not in sys.path:
    sys.path.insert(0, str(_P1))

import numpy as np
import pandas as pd

from _data import get_stock_data


# ---------- 题 1 ----------
def find_one_word_limit_ups(
    df: pd.DataFrame,
    threshold: float = 0.099,
    eps: float = 0.001,
) -> list[pd.Timestamp]:
    """返回一字涨停日日期列表。

    一字板条件：
        - chg_pct >= threshold（涨幅达涨停）
        - |open - high| < eps * close
        - |high - low| < eps * close
        - |low - close| < eps * close
    （开盘/最高/最低/收盘几乎相等，全天封死涨停）
    """
    work = df.copy()
    close = work["close"]
    chg = work["close"].pct_change()

    cond_chg = chg >= threshold
    cond_oh = (work["open"] - work["high"]).abs() < eps * close
    cond_hl = (work["high"] - work["low"]).abs() < eps * close
    cond_lc = (work["low"] - close).abs() < eps * close

    mask = cond_chg & cond_oh & cond_hl & cond_lc
    return list(work.index[mask.fillna(False)])


# ---------- 题 2 ----------
def annualized_return_with_costs(df: pd.DataFrame, cost_bps: int = 10) -> float:
    """扣交易成本后的年化收益率。

    cost_bps: 单边交易成本（佣金+印花税+滑点），单位万分之一（10 = 0.1%）
    假设：每月调仓 1 次（22 交易日），每次全仓切换。
    年成本 = 2 * cost_bps/10000 * 12  (买卖双向)
    """
    work = df.copy()
    if "date" in work.columns:
        work = work.set_index("date")
    rets = work["close"].pct_change().dropna()
    n = len(rets)

    # 不含成本的年化
    total_ret = (1 + rets).prod() - 1
    ann_no_cost = (1 + total_ret) ** (252 / n) - 1 if n > 0 else 0.0

    # 假设每月 1 次全仓切换：年化成本率
    annual_cost_ratio = 2 * cost_bps / 10000 * 12

    return ann_no_cost - annual_cost_ratio


# ---------- 题 3 ----------
def yearly_limit_up_pivot(codes: list[tuple[str, str]]) -> pd.DataFrame:
    """三股每年涨停日数 + 年化收益率。

    Args:
        codes: [(code, name), ...]

    Returns:
        DataFrame index=multiindex(code, year),
        columns=['limit_ups', 'annual_return']
    """
    rows = []
    for code, _name in codes:
        df = get_stock_data(code)
        work = df.copy()
        if "date" in work.columns:
            work["date"] = pd.to_datetime(work["date"])
            work = work.set_index("date")
        chg = work["close"].pct_change()

        for year, year_df in work.groupby(work.index.year):
            year_chg = chg.reindex(year_df.index).dropna()
            limit_ups = int((year_chg >= 0.099).sum())
            n = len(year_chg)
            if n > 0:
                total_ret = (1 + year_chg).prod() - 1
                ann_ret = (1 + total_ret) ** (252 / n) - 1
            else:
                ann_ret = float("nan")
            rows.append({
                "code": code,
                "year": year,
                "limit_ups": limit_ups,
                "annual_return": ann_ret,
            })

    return pd.DataFrame(rows).set_index(["code", "year"])


def run_all() -> None:
    print("=" * 60); print("题 1：一字涨停"); print("=" * 60)
    for code, name in [("002594", "比亚迪"), ("002602", "世纪华通"), ("002624", "完美世界")]:
        df = get_stock_data(code).set_index("date")
        yz = find_one_word_limit_ups(df)
        print(f"{name:<8} 一字涨停 {len(yz)} 次")

    print(); print("=" * 60); print("题 2：含成本年化"); print("=" * 60)
    for code, name in [("002594", "比亚迪"), ("002602", "世纪华通"), ("002624", "完美世界")]:
        df = get_stock_data(code).set_index("date")
        r = annualized_return_with_costs(df, cost_bps=15)
        print(f"{name:<8} 含成本年化: {r*100:>7.2f}%")

    print(); print("=" * 60); print("题 3：年度透视"); print("=" * 60)
    codes = [("002594", "比亚迪"), ("002602", "世纪华通"), ("002624", "完美世界")]
    print(yearly_limit_up_pivot(codes))


if __name__ == "__main__":
    run_all()
