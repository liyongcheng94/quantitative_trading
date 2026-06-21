"""qtrader.cache 缓存层单元测试（使用临时目录，不联网）。"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from qtrader.cache import cache_path, load_cache, save_cache, load, clear_cache


def _make_df(n: int = 5) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    return pd.DataFrame({
        "date": dates,
        "open": 100.0, "high": 101.0, "low": 99.0,
        "close": 100.0, "volume": 1_000_000,
    })


@pytest.mark.unit
def test_cache_path_naming(tmp_path: Path):
    p = cache_path("002594", "2024-01-01", "2024-12-31", "qfq", tmp_path)
    assert p.name == "002594_2024-01-01_2024-12-31_qfq.parquet"
    assert p.parent == tmp_path


@pytest.mark.unit
def test_save_and_load_roundtrip(tmp_path: Path):
    df = _make_df(5)
    p = cache_path("002594", "2024-01-01", "2024-12-31", "qfq", tmp_path)
    save_cache(df, p)
    assert p.exists()
    loaded = load_cache(p)
    assert loaded is not None
    assert list(loaded.columns) == ["date", "open", "high", "low", "close", "volume"]
    pd.testing.assert_frame_equal(
        loaded.reset_index(drop=True),
        df.reset_index(drop=True),
        check_dtype=False,
    )


@pytest.mark.unit
def test_load_cache_returns_none_on_missing(tmp_path: Path):
    p = tmp_path / "nonexistent.parquet"
    assert load_cache(p) is None


@pytest.mark.unit
def test_load_cache_returns_none_on_corrupt(tmp_path: Path):
    p = tmp_path / "bad.parquet"
    p.write_bytes(b"not a parquet file")
    assert load_cache(p) is None


@pytest.mark.unit
def test_load_hits_cache_without_refetch(tmp_path: Path):
    """缓存命中时不应调用 refetch_fn。"""
    df = _make_df(3)
    p = cache_path("002594", "2024-01-01", "2024-12-31", "qfq", tmp_path)
    save_cache(df, p)

    def refetch_fn(*args, **kwargs):
        raise AssertionError("不应调用 refetch_fn（缓存命中）")

    result = load("002594", "2024-01-01", "2024-12-31",
                  adjust="qfq", cache_dir=tmp_path, refetch_fn=refetch_fn)
    assert len(result) == 3


@pytest.mark.unit
def test_load_misses_cache_calls_refetch_and_writes(tmp_path: Path):
    """缓存未命中时调用 refetch_fn，并回写缓存文件。"""
    fetch_calls: list[tuple] = []

    def refetch_fn(code, start, end):
        fetch_calls.append((code, start, end))
        return _make_df(7)

    p = cache_path("600519", "2024-01-01", "2024-12-31", "qfq", tmp_path)
    assert not p.exists()

    result = load("600519", "2024-01-01", "2024-12-31",
                  adjust="qfq", cache_dir=tmp_path, refetch_fn=refetch_fn)
    assert len(result) == 7
    assert len(fetch_calls) == 1
    # 回写
    assert p.exists()


@pytest.mark.unit
def test_load_without_refetch_raises_on_miss(tmp_path: Path):
    with pytest.raises(RuntimeError, match="未提供 refetch_fn"):
        load("000001", "2024-01-01", "2024-12-31",
             adjust="qfq", cache_dir=tmp_path)


@pytest.mark.unit
def test_clear_cache_removes_files(tmp_path: Path):
    df = _make_df(2)
    for code in ["002594", "600519", "000001"]:
        save_cache(df, cache_path(code, "2024-01-01", "2024-12-31", "qfq", tmp_path))
    assert len(list(tmp_path.glob("*.parquet"))) == 3

    n_removed = clear_cache("002594", tmp_path)
    assert n_removed == 1
    remaining = sorted(p.name.split("_")[0] for p in tmp_path.glob("*.parquet"))
    assert remaining == ["000001", "600519"]

    n_all = clear_cache(cache_dir=tmp_path)
    assert n_all == 2
    assert len(list(tmp_path.glob("*.parquet"))) == 0


@pytest.mark.unit
def test_clear_cache_on_missing_dir(tmp_path: Path):
    """目录不存在时返回 0，不报错。"""
    empty = tmp_path / "nonexistent"
    assert clear_cache(cache_dir=empty) == 0
