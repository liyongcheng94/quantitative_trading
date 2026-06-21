"""阶段一学习用数据缓存 helper。

优先级：parquet 缓存 → akshare（新浪源主、东财源备）→ 合成数据。
合成数据保证离线也能上课，但会在 df.attrs['synthetic']=True 标记。
"""
from __future__ import annotations

import time
from datetime import date
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

DEFAULT_START = "2022-01-01"
DEFAULT_END = date.today().isoformat()  # 动态取今天，保证数据永远最新


def _cache_path(code: str, adjust: str) -> Path:
    suffix = adjust if adjust else "raw"
    return DATA_DIR / f"{code}_{suffix}.parquet"


def _to_sina_symbol(code: str) -> str:
    code = str(code).strip().lower()
    if code.startswith(("sh", "sz", "bj")):
        return code
    if code.startswith(("6", "9")):
        return f"sh{code}"
    if code.startswith(("4", "8")):
        return f"bj{code}"
    return f"sz{code}"


def _try_akshare(code: str, start: str, end: str, adjust: str) -> Optional[pd.DataFrame]:
    try:
        import akshare as ak
    except ImportError:
        return None

    try:
        time.sleep(1)
        df = ak.stock_zh_a_daily(
            symbol=_to_sina_symbol(code),
            start_date=start.replace("-", ""),
            end_date=end.replace("-", ""),
            adjust=adjust,
        )
        if df is not None and len(df) > 0:
            df["date"] = pd.to_datetime(df["date"])
            df = df[["date", "open", "high", "low", "close", "volume"]].copy()
            df = df.sort_values("date").reset_index(drop=True)
            df = df[(df["date"] >= start) & (df["date"] <= end)].reset_index(drop=True)
            if len(df) > 0:
                return df
    except Exception:
        pass

    try:
        time.sleep(1)
        df = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=start.replace("-", ""),
            end_date=end.replace("-", ""),
            adjust=adjust,
        )
        if df is not None and len(df) > 0:
            df = df.rename(columns={
                "日期": "date", "开盘": "open", "收盘": "close",
                "最高": "high", "最低": "low", "成交量": "volume",
            })
            df["date"] = pd.to_datetime(df["date"])
            df = df[["date", "open", "high", "low", "close", "volume"]].copy()
            df = df.sort_values("date").reset_index(drop=True)
            df = df[(df["date"] >= start) & (df["date"] <= end)].reset_index(drop=True)
            if len(df) > 0:
                return df
    except Exception:
        pass

    return None


def _synthetic(code: str, start: str, end: str) -> pd.DataFrame:
    rng = np.random.default_rng(seed=hash(code) % (2**32))
    dates = pd.bdate_range(start=start, end=end)
    n = len(dates)
    rets = rng.normal(0.0005, 0.02, size=n)
    close = 20.0 * np.exp(np.cumsum(rets))
    high = close * (1 + rng.uniform(0, 0.03, size=n))
    low = close * (1 - rng.uniform(0, 0.03, size=n))
    open_ = (high + low) / 2 * (1 + rng.normal(0, 0.005, size=n))
    volume = rng.integers(5_000_000, 50_000_000, size=n)
    return pd.DataFrame({
        "date": dates, "open": open_, "high": high,
        "low": low, "close": close, "volume": volume,
    })


def get_stock_data(
    code: str,
    start: str = DEFAULT_START,
    end: str = DEFAULT_END,
    adjust: str = "qfq",
    force_refresh: bool = False,
) -> pd.DataFrame:
    """获取 A 股日线：date/open/high/low/close/volume。

    adjust: 'qfq' 前复权 / 'hfq' 后复权 / '' 不复权。
    返回 df.attrs['synthetic'] 标记是否合成数据。
    """
    cache = _cache_path(code, adjust)
    if not force_refresh and cache.exists():
        df = pd.read_parquet(cache)
        if "synthetic" not in df.attrs:
            df.attrs["synthetic"] = False
        return df

    df = _try_akshare(code, start, end, adjust)
    if df is None or len(df) == 0:
        df = _synthetic(code, start, end)
        df.attrs["synthetic"] = True
    else:
        df.attrs["synthetic"] = False

    df.to_parquet(cache, index=False)
    return df
