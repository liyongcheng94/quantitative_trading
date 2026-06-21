"""数据层：A股日线数据获取（新浪源主、东财源备，带 parquet 缓存）。"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    import akshare as ak
except ImportError as e:
    raise ImportError(
        "未检测到 akshare，请执行: pip install akshare pandas numpy matplotlib"
    ) from e

from .cache import cache_path, load_cache, save_cache


def _to_sina_symbol(code: str) -> str:
    """纯数字股票代码转新浪格式：6/9 → sh，4/8 → bj，其余 → sz。"""
    code = str(code).strip().lower()
    if code.startswith(("sh", "sz", "bj")):
        return code
    if code.startswith(("6", "9")):
        return f"sh{code}"
    if code.startswith(("4", "8")):
        return f"bj{code}"
    return f"sz{code}"


def fetch_data(
    code: str,
    start: str,
    end: str,
    use_cache: bool = True,
    cache_dir: Path | None = None,
) -> pd.DataFrame:
    """下载 A股前复权日线，返回列：date / open / high / low / close / volume。

    Args:
        code: 股票代码（纯数字或带 sh/sz/bj 前缀）
        start: 起始日期 YYYY-MM-DD
        end: 结束日期 YYYY-MM-DD
        use_cache: 是否启用 parquet 本地缓存（默认 True）
        cache_dir: 自定义缓存目录，默认 ~/.qtrader_cache
    """
    if use_cache:
        path = cache_path(code, start, end, "qfq", cache_dir)
        cached = load_cache(path)
        if cached is not None:
            return cached

    df = _fetch_raw(code, start, end)

    if use_cache:
        save_cache(df, path)  # type: ignore[possibly-undefined]
    return df


def _fetch_raw(code: str, start: str, end: str) -> pd.DataFrame:
    """实际联网抓取（不含缓存逻辑）。"""
    errors: list[str] = []

    try:
        sina_symbol = _to_sina_symbol(code)
        df = ak.stock_zh_a_daily(
            symbol=sina_symbol,
            start_date=start.replace("-", ""),
            end_date=end.replace("-", ""),
            adjust="qfq",
        )
        if df is not None and len(df) > 0:
            df["date"] = pd.to_datetime(df["date"])
            df = df[["date", "open", "high", "low", "close", "volume"]].copy()
            df = df.sort_values("date").reset_index(drop=True)
            df = df[(df["date"] >= start) & (df["date"] <= end)].reset_index(drop=True)
            if len(df) > 0:
                return df
            errors.append("sina: empty after date filter")
        else:
            errors.append("sina: empty response")
    except Exception as e:
        errors.append(f"sina: {type(e).__name__}: {e}")

    try:
        df = ak.stock_zh_a_hist(
            symbol=code,
            period="daily",
            start_date=start.replace("-", ""),
            end_date=end.replace("-", ""),
            adjust="qfq",
        )
        if df is None or len(df) == 0:
            raise RuntimeError("东财源返回空")
        df = df.rename(columns={
            "日期": "date", "开盘": "open", "收盘": "close",
            "最高": "high", "最低": "low", "成交量": "volume",
        })
        df["date"] = pd.to_datetime(df["date"])
        df = df[["date", "open", "high", "low", "close", "volume"]].copy()
        df = df.sort_values("date").reset_index(drop=True)
        df = df[(df["date"] >= start) & (df["date"] <= end)].reset_index(drop=True)
        return df
    except Exception as e:
        errors.append(f"em: {type(e).__name__}: {e}")

    raise RuntimeError(
        "所有数据源均失败：" + " | ".join(errors) +
        "。建议：1) 检查股票代码；2) 排查网络/代理；3) 稍后重试。"
    )
