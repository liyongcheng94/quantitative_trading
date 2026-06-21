"""参数优化：网格搜索 + Walk-Forward 验证（防过拟合）。

设计原则：
- 零依赖（仅 itertools + pandas/numpy）
- 不引入 sklearn
- grid_search 返回全参数组合的指标排序
- walk_forward 强制 in-sample/out-of-sample 切分，让学习者直观看到过拟合
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Callable

import pandas as pd

from .engine import BacktestEngine
from .strategies import Strategy


def _expand_grid(param_grid: dict[str, list]) -> list[dict]:
    """{'short':[5,10], 'long':[20,30]} -> [{short:5,long:20}, ...]"""
    if not param_grid:
        return [{}]
    keys = list(param_grid.keys())
    values = [param_grid[k] for k in keys]
    return [dict(zip(keys, combo)) for combo in product(*values)]


def grid_search(
    engine: BacktestEngine,
    df: pd.DataFrame,
    strategy_cls: type[Strategy],
    param_grid: dict[str, list],
    metric: str = "sharpe",
    top_n: int | None = None,
) -> pd.DataFrame:
    """网格搜索：遍历所有参数组合，返回按 metric 排序的 DataFrame。

    Args:
        engine: 已配置 CostModel 的 BacktestEngine
        df: OHLCV 数据
        strategy_cls: 策略类（如 DualMAStrategy）
        param_grid: {'param_name': [val1, val2, ...]}
        metric: 排序指标，默认 'sharpe'。可选 sharpe/sortino/calmar/ann_return/...
        top_n: 只返回前 N 条；None 返回全部

    Returns:
        DataFrame，每行一组参数 + n_trades + 各项指标。按 metric 降序。
    """
    combos = _expand_grid(param_grid)
    rows: list[dict] = []
    for params in combos:
        try:
            strategy = strategy_cls(**params)
            result = engine.run(df, strategy)
            row = {"n_trades": result.n_trades, **params}
            row.update(result.metrics)
            rows.append(row)
        except Exception as e:
            # 参数不合法或回测异常，跳过但保留 None 记录便于排查
            rows.append({**params, "n_trades": 0, "error": str(e)})

    out = pd.DataFrame(rows)
    if metric not in out.columns:
        raise ValueError(
            f"metric='{metric}' 不在结果列中。可选: {[c for c in out.columns if c not in ('n_trades',)]}"
        )
    out = out.sort_values(metric, ascending=False, na_position="last").reset_index(drop=True)
    if top_n is not None:
        out = out.head(top_n)
    return out


@dataclass
class WalkForwardResult:
    """Walk-Forward 验证结果。"""
    best_params: dict
    train_metric: float
    test_metric: float
    overfit_gap: float  # train - test；越大越过拟合
    train_full: pd.DataFrame  # 训练段全参数 grid 结果
    test_metrics: dict  # 测试段上 best_params 的完整指标


def walk_forward(
    engine: BacktestEngine,
    df: pd.DataFrame,
    strategy_cls: type[Strategy],
    param_grid: dict[str, list],
    train_ratio: float = 0.7,
    metric: str = "sharpe",
) -> WalkForwardResult:
    """单次切分 Walk-Forward：训练段选最优参数，测试段评估。

    Args:
        engine: BacktestEngine
        df: 完整 OHLCV 数据
        strategy_cls: 策略类
        param_grid: 参数网格
        train_ratio: 训练段占比，默认 0.7
        metric: 评价指标，默认 'sharpe'

    Returns:
        WalkForwardResult，含 train/test 指标与 overfit_gap
    """
    if not 0.1 < train_ratio < 0.95:
        raise ValueError(f"train_ratio 应在 (0.1, 0.95)，当前 {train_ratio}")

    n = len(df)
    split = int(n * train_ratio)
    train_df = df.iloc[:split].reset_index(drop=True)
    test_df = df.iloc[split:].reset_index(drop=True)

    # 训练段：grid search 选最优
    train_grid = grid_search(engine, train_df, strategy_cls, param_grid, metric=metric)
    if train_grid.empty or metric not in train_grid.columns:
        raise RuntimeError("训练段 grid_search 无有效结果")

    # 取 top-1 参数（排除有 error 列的行）
    valid = train_grid[~train_grid.get("error", pd.Series(dtype=str)).notna()] \
        if "error" in train_grid.columns else train_grid
    if valid.empty:
        raise RuntimeError("所有参数组合在训练段均失败")

    best_row = valid.iloc[0]
    param_cols = [k for k in param_grid.keys()]
    best_params = {k: best_row[k] for k in param_cols}
    # JSON-able 转换（numpy int -> int）
    best_params = {k: (int(v) if hasattr(v, "item") else v) for k, v in best_params.items()}
    train_metric = float(best_row[metric]) if pd.notna(best_row[metric]) else float("nan")

    # 测试段：用最优参数评估
    strategy = strategy_cls(**best_params)
    test_result = engine.run(test_df, strategy)
    test_metric = float(test_result.metrics.get(metric, float("nan")))

    overfit_gap = train_metric - test_metric if pd.notna(train_metric) and pd.notna(test_metric) else float("nan")

    return WalkForwardResult(
        best_params=best_params,
        train_metric=train_metric,
        test_metric=test_metric,
        overfit_gap=overfit_gap,
        train_full=train_grid,
        test_metrics=test_result.metrics,
    )
