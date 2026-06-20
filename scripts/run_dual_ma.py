"""单策略入口（双均线）— 基于 qtrader 包。

运行示例：
    python -m scripts.run_dual_ma
    python -m scripts.run_dual_ma --code 002594 --save outputs/byd_dual_ma.png
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from qtrader import BacktestEngine, DualMAStrategy, fetch_data

plt.rcParams["font.sans-serif"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False


def _plot(df, result, code: str, short: int, long: int, save_path):
    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(12, 8), sharex=True,
        gridspec_kw={"height_ratios": [2, 1]},
    )
    work = df.set_index("date")
    date_idx = result.nav.index

    ax1.plot(date_idx, work["close"], color="#333333",
             label="收盘价", linewidth=1.0)
    ax1.plot(date_idx, work["close"].rolling(short).mean(),
             color="#e8a33d", label=f"MA{short}", linewidth=1.0)
    ax1.plot(date_idx, work["close"].rolling(long).mean(),
             color="#2e86de", label=f"MA{long}", linewidth=1.0)

    sig = result.signal
    buys = sig[sig.diff() > 0]
    sells = sig[sig.diff() < 0]
    ax1.scatter(buys.index, work["close"].reindex(buys.index), marker="^", s=80,
                color="#27ae60", label="买入", zorder=5,
                edgecolors="white", linewidths=0.5)
    ax1.scatter(sells.index, work["close"].reindex(sells.index), marker="v", s=80,
                color="#e74c3c", label="卖出", zorder=5,
                edgecolors="white", linewidths=0.5)
    ax1.set_title(f"{code} 双均线策略 (MA{short}/MA{long})")
    ax1.set_ylabel("价格")
    ax1.legend(loc="best", fontsize=9)
    ax1.grid(True, alpha=0.3)

    ax2.plot(date_idx, result.nav, color="#c0392b",
             label="策略净值", linewidth=1.2)
    ax2.plot(date_idx, result.benchmark_nav, color="#2c3e50",
             label="买入持有", linewidth=1.0, alpha=0.8)
    ax2.axhline(1.0, color="gray", linestyle="--", linewidth=0.7)
    ax2.set_title("策略净值 vs 买入持有")
    ax2.set_ylabel("净值")
    ax2.set_xlabel("日期")
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


def main() -> int:
    parser = argparse.ArgumentParser(description="A股双均线策略回测（单策略）")
    parser.add_argument("--code", default="000001")
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument("--end", default="2026-06-18")
    parser.add_argument("--short", type=int, default=5)
    parser.add_argument("--long", type=int, default=20)
    parser.add_argument("--save", default=None)
    args = parser.parse_args()

    if args.short >= args.long:
        print("[参数错误] 短期均线必须小于长期均线")
        return 2

    try:
        df = fetch_data(args.code, args.start, args.end)
        print(f"[数据] 共获取 {len(df)} 个交易日，范围 "
              f"{df['date'].iloc[0].strftime('%Y-%m-%d')} ~ "
              f"{df['date'].iloc[-1].strftime('%Y-%m-%d')}")

        engine = BacktestEngine()
        strategy = DualMAStrategy(short=args.short, long=args.long)
        result = engine.run(df, strategy)
        m = result.metrics

        print("\n" + "=" * 60)
        print(f" 双均线策略回测报告  | 股票: {args.code} | MA{args.short}/{args.long}")
        print("=" * 60)
        print(f"  交易日数          : {m['n_days']}")
        print(f"  交易次数          : {result.n_trades}")
        print(f"  策略总收益率      : {m['total_return']:.2%}")
        print(f"  策略年化收益率    : {m['ann_return']:.2%}")
        print(f"  买入持有总收益率  : {m['bench_total_return']:.2%}")
        print(f"  最大回撤          : {m['max_drawdown']:.2%}")
        print(f"  最大回撤时间      : {m['max_dd_date'].strftime('%Y-%m-%d')}")
        print(f"  夏普比率 (rf=3%)  : {m['sharpe']:.4f}")
        print(f"  Calmar            : {m['calmar']:.4f}")
        print("=" * 60 + "\n")

        save_path = args.save
        if save_path and not Path(save_path).is_absolute():
            Path("outputs").mkdir(exist_ok=True)
            save_path = str(Path("outputs") / save_path)

        _plot(df, result, args.code, args.short, args.long, save_path)
        return 0

    except KeyboardInterrupt:
        print("\n[中断] 用户取消")
        return 130
    except Exception as e:
        print(f"\n[错误] {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
