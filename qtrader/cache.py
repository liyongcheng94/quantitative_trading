"""数据缓存层：parquet 本地缓存，避免每次重抓 akshare。

缓存路径：~/.qtrader_cache/{code}_{start}_{end}_{adjust}.parquet
命中策略：文件存在即用；文件缺失或损坏 → 联网抓 → 回写。
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

import pandas as pd

DEFAULT_CACHE_DIR: Path = Path.home() / ".qtrader_cache"


def cache_path(
    code: str,
    start: str,
    end: str,
    adjust: str = "qfq",
    cache_dir: Path | None = None,
) -> Path:
    """生成单股缓存文件路径。"""
    d = Path(cache_dir) if cache_dir is not None else DEFAULT_CACHE_DIR
    suffix = f"_{adjust}" if adjust else "_raw"
    safe_code = str(code).strip().lower().replace("/", "_")
    return d / f"{safe_code}_{start}_{end}{suffix}.parquet"


def load_cache(path: Path) -> pd.DataFrame | None:
    """命中返回 DataFrame；不命中或损坏返回 None。"""
    if not path.exists():
        return None
    try:
        df = pd.read_parquet(path)
        if len(df) == 0:
            return None
        if "date" in df.columns:
            df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception:
        return None


def save_cache(df: pd.DataFrame, path: Path) -> None:
    """写入缓存（自动创建父目录）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def load(
    code: str,
    start: str,
    end: str,
    adjust: str = "qfq",
    cache_dir: Path | None = None,
    refetch_fn: Callable[[str, str, str], pd.DataFrame] | None = None,
) -> pd.DataFrame:
    """高层 API：先查缓存，miss 时调用 refetch_fn 联网并回写。

    Args:
        code: 股票代码
        start: 起始日期 YYYY-MM-DD
        end: 结束日期 YYYY-MM-DD
        adjust: 复权类型 qfq/hfq/''
        cache_dir: 自定义缓存目录，默认 ~/.qtrader_cache
        refetch_fn: 缓存未命中时的联网函数，签名 (code, start, end) -> DataFrame

    Returns:
        OHLCV DataFrame（带 date 列）
    """
    path = cache_path(code, start, end, adjust, cache_dir)
    cached = load_cache(path)
    if cached is not None:
        return cached
    if refetch_fn is None:
        raise RuntimeError(f"缓存未命中且未提供 refetch_fn: {path}")
    df = refetch_fn(code, start, end)
    save_cache(df, path)
    return df


def clear_cache(
    code: str | None = None,
    cache_dir: Path | None = None,
) -> int:
    """清空缓存。返回删除的文件数。

    Args:
        code: 指定股票则只删该 code 的缓存；None 删全部
        cache_dir: 自定义目录
    """
    d = Path(cache_dir) if cache_dir is not None else DEFAULT_CACHE_DIR
    if not d.exists():
        return 0
    pattern = f"{code}*.parquet" if code else "*.parquet"
    files = list(d.glob(pattern))
    for f in files:
        f.unlink()
    return len(files)
