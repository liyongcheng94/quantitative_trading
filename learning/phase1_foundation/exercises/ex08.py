"""L08 课后练习：PE 估值与行业对比。"""
from __future__ import annotations
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd


def pe_percentile(pe_series: pd.Series, lookback_days: int = 252 * 5) -> float:
    """PE 历史分位数（带 lookback）。

    Args:
        pe_series: 时间序列 PE（index=date, value=PE）
        lookback_days: 向前看多少个交易日，默认 5 年

    Returns:
        当前 PE 在过去 lookback_days 内的分位数（0~1）
    """
    # TODO: ~5 行



    return 0.0


def industry_rank(stocks_df: pd.DataFrame, by: str = 'pe_ttm') -> pd.DataFrame:
    """在每个行业内部按 by 列排名。

    Args:
        stocks_df: 至少含 ['industry', by] 两列
        by: 排名依据列名

    Returns:
        原 DataFrame 加 'rank_in_industry' 和 'pct_in_industry' 两列
    """
    # TODO: ~4 行



    return stocks_df


def value_categories(pe_series: pd.Series,
                     bins: list[float] = None,
                     labels: list[str] = None) -> pd.Series:
    """按分位数把 PE 分箱到估值类别。

    默认 bins=[0, 0.2, 0.8, 1], labels=['低估', '合理', '高估']
    """
    if bins is None:
        bins = [0, 0.2, 0.8, 1.0001]
    if labels is None:
        labels = ['低估', '合理', '高估']
    # TODO: ~3 行
    # 提示：先算每只股票的 pct 分位，再 pd.cut()



    return pd.Series(dtype=str)


def run_all() -> None:
    # 复用 L08 的多行业数据
    data = pd.DataFrame({
        'code': ['002594', '600104', '601633', '600519', '000858',
                 '002624', '300413', '300251'],
        'name':  ['比亚迪', '上汽集团', '长城汽车', '贵州茅台', '五粮液',
                  '完美世界', '芒果超媒', '光线传媒'],
        'industry': ['汽车','汽车','汽车','食品饮料','食品饮料','传媒','传媒','传媒'],
        'pe_ttm': [28.5, 8.2, 22.1, 30.5, 22.1, 28.5, 22.1, 40.3],
    })

    print("=" * 60); print("题 2：行业内排名"); print("=" * 60)
    print(industry_rank(data).sort_values(['industry', 'pct_in_industry']))

    print(); print("=" * 60); print("题 3：估值分类"); print("=" * 60)
    # 用一个示例 PE 序列测分位
    rng = np.random.default_rng(42)
    sample_pe = pd.Series(rng.uniform(10, 50, 100))
    cats = value_categories(sample_pe)
    print(cats.value_counts())


if __name__ == "__main__":
    run_all()
