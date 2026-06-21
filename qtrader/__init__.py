"""qtrader — 零依赖 A股量化回测包。"""
from .data import fetch_data
from .strategies import (
    Strategy, DualMAStrategy, TurtleStrategy, GridStrategy, ALL_STRATEGIES,
)
from .engine import BacktestEngine, BacktestResult, CostModel
from .metrics import compute_metrics
from .plotting import print_comparison_table, plot_comparison
from . import cache
from .cache import load as load_cached, clear_cache, cache_path

__all__ = [
    "fetch_data",
    "Strategy", "DualMAStrategy", "TurtleStrategy", "GridStrategy", "ALL_STRATEGIES",
    "BacktestEngine", "BacktestResult", "CostModel",
    "compute_metrics",
    "print_comparison_table", "plot_comparison",
    "cache", "load_cached", "clear_cache", "cache_path",
]
__version__ = "0.2.0"
