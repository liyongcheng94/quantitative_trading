"""参数网格搜索 + Walk-Forward 验证 CLI。

运行示例：
    python -m scripts.run_gridsearch --code 002594 --strategy dual_ma
    python -m scripts.run_gridsearch --code 002594 --strategy turtle --walk-forward
"""
from __future__ import annotations

import argparse
import sys
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from qtrader import (
    BacktestEngine, CostModel,
    DualMAStrategy, TurtleStrategy, GridStrategy,
    fetch_data,
)
from qtrader.optimize import grid_search, walk_forward


STRATEGY_REGISTRY = {
    "dual_ma": (DualMAStrategy, {"short": [3, 5, 10], "long": [20, 30, 60]}),
    "turtle": (TurtleStrategy, {"entry_n": [10, 20, 55], "exit_n": [5, 10]}),
    "grid": (GridStrategy, {"grid_n": [5, 10, 20], "lookback": [30, 60, 120]}),
}


def main() -> int:
    parser = argparse.ArgumentParser(description="参数网格搜索 + Walk-Forward 验证")
    parser.add_argument("--code", default="000001", help="股票代码")
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument("--end", default="2026-06-18")
    parser.add_argument(
        "--strategy", choices=list(STRATEGY_REGISTRY.keys()), default="dual_ma",
        help="策略名（决定参数网格）",
    )
    parser.add_argument("--metric", default="sharpe", help="评价指标")
    parser.add_argument("--top-n", type=int, default=10, help="显示前 N 条")
    parser.add_argument("--walk-forward", action="store_true", help="启用 walk-forward 验证")
    parser.add_argument("--train-ratio", type=float, default=0.7)
    parser.add_argument("--no-cache", action="store_true")
    args = parser.parse_args()

    strategy_cls, param_grid = STRATEGY_REGISTRY[args.strategy]
    total_combos = 1
    for v in param_grid.values():
        total_combos *= len(v)
    print(f"[策略] {strategy_cls.__name__}，参数网格 {param_grid}，共 {total_combos} 组合")

    try:
        df = fetch_data(args.code, args.start, args.end, use_cache=not args.no_cache)
        print(f"[数据] {len(df)} 个交易日")

        engine = BacktestEngine(cost_model=CostModel())

        print(f"\n===== Grid Search（{args.metric}）=====")
        top = grid_search(engine, df, strategy_cls, param_grid, metric=args.metric, top_n=args.top_n)
        param_cols = list(param_grid.keys())
        metric_cols = [args.metric, "total_return", "max_drawdown", "n_trades"]
        show_cols = [c for c in param_cols + metric_cols if c in top.columns]
        print(top[show_cols].to_string(index=False))

        if args.walk_forward:
            print(f"\n===== Walk-Forward (train_ratio={args.train_ratio}) =====")
            wf = walk_forward(
                engine, df, strategy_cls, param_grid,
                train_ratio=args.train_ratio, metric=args.metric,
            )
            print(f"训练段最优参数: {wf.best_params}")
            print(f"训练段 {args.metric}: {wf.train_metric:.3f}")
            print(f"测试段 {args.metric}: {wf.test_metric:.3f}")
            print(f"过拟合差距 (train - test): {wf.overfit_gap:+.3f}")
            if wf.overfit_gap > 0.5:
                print("⚠️ 警告：训练-测试差距过大，存在过拟合风险")
            elif wf.overfit_gap < 0:
                print("✓ 测试段反而更好，参数稳健性较好")
            else:
                print("○ 训练-测试差距合理")

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
