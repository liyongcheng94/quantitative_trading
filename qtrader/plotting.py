"""可视化：终端对比表 + matplotlib 双子图（净值对比 + 回撤）。"""
from __future__ import annotations

from typing import Optional

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

from .engine import BacktestResult

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False

_COLORS = ["#e74c3c", "#9b59b6", "#27ae60", "#f39c12", "#3498db"]


def print_comparison_table(results: list[BacktestResult], code: str) -> None:
    print("\n" + "=" * 112)
    print(f" 多策略对比  | 股票: {code}")
    print("=" * 112)
    header = (
        f"{'策略':<14} {'总收益':>10} {'年化':>10} "
        f"{'最大回撤':>10} {'夏普':>8} {'Sortino':>8} "
        f"{'Calmar':>8} {'波动率':>8} {'胜率':>8} {'交易次数':>8}"
    )
    print(header)
    print("-" * 112)

    bench = results[0].metrics["bench_total_return"]
    print(
        f"{'买入持有':<14} {bench:>10.2%} {'':>10} {'':>10} "
        f"{'':>8} {'':>8} {'':>8} {'':>8} {'':>8} {'':>8}"
    )

    for r in results:
        m = r.metrics
        sortino_str = f"{m['sortino']:>8.3f}" if not np.isnan(m["sortino"]) else f"{'NaN':>8}"
        win_str = f"{m['win_rate']:>8.2%}" if not np.isnan(m["win_rate"]) else f"{'NaN':>8}"
        print(
            f"{r.strategy_name:<14} "
            f"{m['total_return']:>10.2%} {m['ann_return']:>10.2%} "
            f"{m['max_drawdown']:>10.2%} {m['sharpe']:>8.3f} "
            f"{sortino_str} {m['calmar']:>8.3f} {m['volatility']:>8.2%} "
            f"{win_str} {r.n_trades:>8}"
        )
    print("=" * 112 + "\n")


def plot_comparison(
    results: list[BacktestResult],
    code: str,
    save_path: Optional[str] = None,
) -> None:
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(13, 9), sharex=True,
        gridspec_kw={"height_ratios": [3, 1]},
    )

    ax1.plot(
        results[0].benchmark_nav.index, results[0].benchmark_nav.values,
        color="#7f8c8d", linewidth=1.6, label="买入持有", alpha=0.85,
    )
    for r, color in zip(results, _COLORS):
        ax1.plot(
            r.nav.index, r.nav.values,
            color=color, linewidth=1.4, label=r.strategy_name, alpha=0.92,
        )
    ax1.set_title(f"{code} 多策略对比 - 净值曲线", fontsize=14)
    ax1.set_ylabel("净值")
    ax1.legend(loc="best", fontsize=10)
    ax1.grid(True, alpha=0.3)

    for r, color in zip(results, _COLORS):
        cummax = r.nav.cummax()
        dd = r.nav / cummax - 1.0
        ax2.fill_between(
            dd.index, dd.values, 0,
            color=color, alpha=0.22, label=f"{r.strategy_name} 回撤",
        )
    ax2.set_title("策略回撤对比")
    ax2.set_ylabel("回撤")
    ax2.legend(loc="best", fontsize=9)
    ax2.grid(True, alpha=0.3)

    ax2.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    fig.autofmt_xdate()
    fig.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=150, bbox_inches="tight")
        print(f"[图表] 已保存至 {save_path}")
    else:
        plt.show()
    plt.close(fig)
