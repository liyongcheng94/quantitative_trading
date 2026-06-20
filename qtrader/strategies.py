"""策略层：Strategy 基类 + 3 个经典策略实现（向量化，无未来函数）。"""
from __future__ import annotations

import numpy as np
import pandas as pd


class Strategy:
    """策略基类。子类需实现 generate_signals 返回 [0,1] 目标仓位序列。"""
    name: str = "Base"
    params: dict

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        raise NotImplementedError

    def __repr__(self) -> str:
        return f"{self.name}({self.params})"


class DualMAStrategy(Strategy):
    """双均线：MA_short > MA_long 时持仓。"""
    name = "双均线"

    def __init__(self, short: int = 5, long: int = 20):
        self.short = short
        self.long = long
        self.params = {"short": short, "long": long}

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        ma_s = df["close"].rolling(self.short).mean()
        ma_l = df["close"].rolling(self.long).mean()
        raw = (ma_s > ma_l).astype(int)
        return raw.shift(1).fillna(0).astype(float)


class TurtleStrategy(Strategy):
    """海龟（唐奇安通道）：突破 N 日最高买入，跌破 M 日最低卖出。"""
    name = "海龟"

    def __init__(self, entry_n: int = 20, exit_n: int = 10):
        self.entry_n = entry_n
        self.exit_n = exit_n
        self.params = {"entry_n": entry_n, "exit_n": exit_n}

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        upper = df["high"].rolling(self.entry_n).max().shift(1)
        lower = df["low"].rolling(self.exit_n).min().shift(1)
        buy = df["close"] > upper
        sell = df["close"] < lower
        raw = pd.Series(np.nan, index=df.index)
        raw[buy] = 1.0
        raw[sell] = 0.0
        filled = raw.ffill().fillna(0)
        return filled.shift(1).fillna(0).astype(float)


class GridStrategy(Strategy):
    """网格交易：在 lookback 期 high/low 区间等分 grid_n 格，
    每日统计穿越网格线次数（上穿+1，下穿-1），cumsum 得到目标仓位。"""
    name = "网格"

    def __init__(self, grid_n: int = 10, lookback: int = 60):
        self.grid_n = grid_n
        self.lookback = lookback
        self.params = {"grid_n": grid_n, "lookback": lookback}

    def generate_signals(self, df: pd.DataFrame) -> pd.Series:
        ref_high = df["close"].rolling(self.lookback).max().shift(1)
        ref_low = df["close"].rolling(self.lookback).min().shift(1)
        step = (ref_high - ref_low) / self.grid_n
        prev_close = df["close"].shift(1)

        position_change = pd.Series(0.0, index=df.index)
        for i in range(1, self.grid_n + 1):
            grid_line = ref_low + i * step
            cross_up = (prev_close < grid_line) & (df["close"] >= grid_line)
            cross_down = (prev_close > grid_line) & (df["close"] <= grid_line)
            position_change += cross_up.astype(float) - cross_down.astype(float)

        raw = position_change.cumsum().clip(0, self.grid_n) / self.grid_n
        return raw.shift(1).fillna(0).astype(float)


ALL_STRATEGIES = [DualMAStrategy, TurtleStrategy, GridStrategy]
