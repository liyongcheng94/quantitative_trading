"""多策略回测主入口：双均线 / 海龟 / 网格 横向对比。

运行示例：
    python -m scripts.run_backtest
    python -m scripts.run_backtest --code 002594 --save outputs/comparison_byd.png
    python -m scripts.run_backtest --code 000001 --commission 0.0005
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qtrader import (
    BacktestEngine, DualMAStrategy, TurtleStrategy, GridStrategy,
    fetch_data, print_comparison_table, plot_comparison,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="A股多策略回测（双均线 / 海龟 / 网格）")
    parser.add_argument("--code", default="000001", help="股票代码，默认 000001")
    parser.add_argument("--start", default="2020-01-01", help="开始日期 YYYY-MM-DD")
    parser.add_argument("--end", default="2026-06-18", help="结束日期 YYYY-MM-DD")
    parser.add_argument("--commission", type=float, default=0.001,
                        help="单边费率，默认 0.001 (0.1%%)")
    parser.add_argument("--no-cache", action="store_true",
                        help="禁用 parquet 本地缓存（默认启用）")
    parser.add_argument("--save", default=None,
                        help="图表保存路径（设置后不弹窗）")
    args = parser.parse_args()

    try:
        df = fetch_data(args.code, args.start, args.end, use_cache=not args.no_cache)
        print(f"[数据] {len(df)} 个交易日，范围 "
              f"{df['date'].iloc[0].strftime('%Y-%m-%d')} ~ "
              f"{df['date'].iloc[-1].strftime('%Y-%m-%d')}")

        strategies = [
            DualMAStrategy(short=5, long=20),
            TurtleStrategy(entry_n=20, exit_n=10),
            GridStrategy(grid_n=10, lookback=60),
        ]

        engine = BacktestEngine(commission=args.commission)
        results = [engine.run(df, s) for s in strategies]

        print_comparison_table(results, args.code)

        save_path = args.save
        if save_path and not Path(save_path).is_absolute():
            Path("outputs").mkdir(exist_ok=True)
            save_path = str(Path("outputs") / save_path)

        plot_comparison(results, args.code, save_path=save_path)
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
