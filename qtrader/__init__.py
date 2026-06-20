"""qtrader — 零依赖 A股量化回测包。"""
from .data import fetch_data
from .strategies import (
    Strategy, DualMAStrategy, TurtleStrategy, GridStrategy, ALL_STRATEGIES,
)
from .engine import BacktestEngine, BacktestResult
from .metrics import compute_metrics
from .plotting import print_comparison_table, plot_comparison

__all__ = [
    "fetch_data",
    "Strategy", "DualMAStrategy", "TurtleStrategy", "GridStrategy", "ALL_STRATEGIES",
    "BacktestEngine", "BacktestResult",
    "compute_metrics",
    "print_comparison_table", "plot_comparison",
]
__version__ = "0.1.0"
