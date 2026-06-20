"""L04 课后练习：数据清洗、复权与多股对齐。"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from _data import get_stock_data


def build_panel(codes: list[str], adjust: str = "qfq") -> pd.DataFrame:
    """构建对齐的 wide-format close DataFrame。

    Args:
        codes: 股票代码列表，如 ['002594', '002602']
        adjust: 'qfq' / 'hfq' / ''

    Returns:
        DataFrame index=date, columns=code, values=close
        停牌日 ffill 填充；首日 NaN 不填充
    """
    # TODO: ~8 行




    return pd.DataFrame()


def detect_suspicious_gap(codes: list[str], threshold: float = 0.15) -> list[tuple]:
    """用不复权数据检测疑似除权日。

    条件：当日 pct_change < -threshold 且 > -0.11（排除真实跌停）

    Returns:
        [(date, code, pct_change), ...] 按日期升序
    """
    # TODO: ~10 行






    return []


def corr_heatmap(codes: list[str]) -> pd.DataFrame:
    """画 5 股相关矩阵热力图，返回相关矩阵。"""
    # TODO: ~5 行





    return pd.DataFrame()


def run_all() -> None:
    codes = ["002594", "002602", "002624", "600519", "300750"]

    print("=" * 60); print("题 1：5 股对齐 panel"); print("=" * 60)
    panel = build_panel(codes)
    print(f"shape: {panel.shape}")
    print(panel.tail(3))

    print(); print("=" * 60); print("题 2：可疑除权日"); print("=" * 60)
    gaps = detect_suspicious_gap(codes)
    print(f"找到 {len(gaps)} 个可疑除权日，前 5 个：")
    for d, c, p in gaps[:5]:
        print(f"  {d.date()} {c} {p*100:.2f}%")

    print(); print("=" * 60); print("题 3：相关矩阵"); print("=" * 60)
    print(corr_heatmap(codes))


if __name__ == "__main__":
    run_all()
