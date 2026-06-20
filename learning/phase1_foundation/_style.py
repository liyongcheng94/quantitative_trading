"""Matplotlib 中文字体 + 学习用配色。

notebook 首个代码格 `import _style` 即触发字体设置（import 副作用）。
"""
from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt

_FONT_STACK = ["Microsoft YaHei", "SimHei", "Arial Unicode MS"]

mpl.rcParams["font.sans-serif"] = _FONT_STACK
mpl.rcParams["axes.unicode_minus"] = False

COLORS = {
    "price": "#1f77b4",
    "volume": "#ff7f0e",
    "ma_short": "#d62728",
    "ma_long": "#2ca02c",
    "up": "#e74c3c",
    "down": "#27ae60",
    "benchmark": "#7f7f7f",
    "signal_buy": "#e74c3c",
    "signal_sell": "#27ae60",
}


def apply() -> None:
    """显式触发字体设置（等价于 import 副作用，便于教学演示）。"""
    plt.rcParams["font.sans-serif"] = _FONT_STACK
    plt.rcParams["axes.unicode_minus"] = False
