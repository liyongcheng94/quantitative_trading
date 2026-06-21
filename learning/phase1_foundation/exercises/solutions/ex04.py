"""L04 课后练习参考答案：数据清洗、复权与多股对齐。

运行：
    .venv/Scripts/python.exe -m learning.phase1_foundation.exercises.solutions.ex04
"""
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_P1 = _HERE.parents[2]  # solutions/ -> exercises/ -> phase1_foundation/
if str(_P1) not in sys.path:
    sys.path.insert(0, str(_P1))

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

from _data import get_stock_data


# ---------- 题 1 ----------
def build_panel(codes: list[str], adjust: str = "qfq") -> pd.DataFrame:
    """构建对齐的 wide-format close DataFrame。

    Args:
        codes: 股票代码列表
        adjust: 'qfq' / 'hfq' / ''

    Returns:
        DataFrame index=date, columns=code, values=close
        停牌日 ffill 填充；首日 NaN 不填充
    """
    frames = {}
    for code in codes:
        df = get_stock_data(code, adjust=adjust)
        df = df.set_index("date") if "date" in df.columns else df
        frames[code] = df["close"]
    panel = pd.DataFrame(frames).sort_index()
    return panel.ffill()


# ---------- 题 2 ----------
def detect_suspicious_gap(codes: list[str], threshold: float = 0.15) -> list[tuple]:
    """用不复权数据检测疑似除权日。

    条件：当日 pct_change < -threshold 且 > -0.11（排除真实跌停）

    Returns:
        [(date, code, pct_change), ...] 按日期升序
    """
    results = []
    for code in codes:
        df = get_stock_data(code, adjust="")  # 不复权
        df = df.set_index("date") if "date" in df.columns else df
        chg = df["close"].pct_change()
        # -threshold < chg < -0.11 排除正常跌停（A股 10% 限制）
        mask = (chg < -threshold) & (chg > -0.11)
        for date, pct in chg[mask].items():
            results.append((date, code, float(pct)))
    return sorted(results, key=lambda x: x[0])


# ---------- 题 3 ----------
def corr_heatmap(codes: list[str]) -> pd.DataFrame:
    """画 5 股相关矩阵热力图，返回相关矩阵。"""
    panel = build_panel(codes)
    rets = panel.pct_change().dropna()
    corr = rets.corr()

    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(
        corr, annot=True, cmap="RdYlGn_r", vmin=-1, vmax=1,
        square=True, ax=ax, fmt=".2f",
    )
    ax.set_title(f"{len(codes)} 股日收益率相关矩阵")
    plt.tight_layout()
    plt.show()
    return corr


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

    print(); print("=" * 60); print("题 3：相关矩阵（不展示图）"); print("=" * 60)
    import matplotlib
    matplotlib.use("Agg")  # 非交互模式，避免阻塞
    panel = build_panel(codes)
    print(panel.pct_change().dropna().corr().round(3))


if __name__ == "__main__":
    run_all()
