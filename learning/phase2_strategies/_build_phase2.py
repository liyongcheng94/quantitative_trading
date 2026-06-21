"""Phase 2 「策略与组合」notebook 构建脚本（L11-L15 + ex14/ex15）。

延续 Phase 1 的「金融概念 × 代码技能」紧配对风格，但聚焦：
- 把 qtrader 框架里的三大策略原理讲透（DualMA / Turtle / Grid）
- 补齐 Phase 1 最大盲区：多股选股 + 组合构建

设计原则：
- 每个策略 notebook 都让学生先「手写简化版」→ 再对比 qtrader 框架版
- 选股/组合章节复用 Phase 1 L04 的 panel_three_stocks.parquet
- 零依赖：不引 sklearn/scipy，Markowitz 用纯 numpy 解析解（等权/反向波动作为主要方案）
"""
from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import nbformat as nbf

OUT_DIR = Path(__file__).parent
EX_DIR = OUT_DIR / "exercises"


def md(src: str) -> dict:
    return nbf.v4.new_markdown_cell(dedent(src).strip())


def code(src: str) -> dict:
    return nbf.v4.new_code_cell(dedent(src).strip())


def write_nb(nb_cells: list, filename: str) -> None:
    nb = nbf.v4.new_notebook()
    nb.cells = nb_cells
    nb.metadata.kernelspec = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.metadata.language_info = {"name": "python"}
    nbf.write(nb, OUT_DIR / filename)


def write_ex(filename: str, body: str) -> None:
    EX_DIR.mkdir(exist_ok=True, parents=True)
    (EX_DIR / "__init__.py").write_text("")
    # UTF-8 写入（修复 phase1 exercises 的 GBK 编码 bug）
    (EX_DIR / filename).write_text(dedent(body).lstrip(), encoding="utf-8")


def common_imports() -> str:
    return """
        import sys
        from pathlib import Path

        # 自动定位 phase1_foundation（共享 _data/_style）+ project root
        _cwd = Path.cwd()
        _p1 = _cwd if (_cwd / '_data.py').exists() else (
            _cwd / 'learning' / 'phase1_foundation'
            if (_cwd / 'learning' / 'phase1_foundation' / '_data.py').exists()
            else _cwd.parent / 'phase1_foundation'
        )
        sys.path.insert(0, str(_p1))
        _proj = _p1.parent.parent if _p1.name == 'phase1_foundation' else _p1
        if (_proj / 'qtrader' / '__init__.py').exists():
            sys.path.insert(0, str(_proj))

        import numpy as np
        import pandas as pd
        import matplotlib.pyplot as plt
        import _style
        from _data import get_stock_data
        from qtrader import (
            BacktestEngine, CostModel,
            DualMAStrategy, TurtleStrategy, GridStrategy,
            print_comparison_table,
        )
    """


# ============================================================
# L11 双均线择时
# ============================================================
def build_l11() -> None:
    cells = [
        md("""
        # L11 · 双均线择时（DualMA）

        **预计时长**：75 min | **难度**：⭐⭐⭐ | **前置**：Phase 1 全部

        ## 本节目标
        1. 双均线策略的金融逻辑：金叉 / 死叉 / 长短周期博弈
        2. 手写向量化信号生成（无 for 循环）
        3. 回测并对比 qtrader 框架版的 `DualMAStrategy`
        4. 参数敏感性：short/long 组合对夏普的影响
        """),

        md("""
        ## 第 1 段：金融概念

        ### 双均线（Moving Average Crossover）核心逻辑
        | 信号 | 条件 | 含义 |
        |------|------|------|
        | **金叉** | MA_short 从下方上穿 MA_long | 短期上涨动能强于长期 → 买入 |
        | **死叉** | MA_short 从上方下穿 MA_long | 短期下跌动能强于长期 → 卖出 |
        | 震荡 | MA 交织反复 | 双均线失效区，常见于横盘 |

        ### 为什么有效（也为什么失效）
        - **有效**：趋势跟踪，能在持续上涨/下跌中捕捉大部分中段利润
        - **失效**：震荡市频繁假信号，每次假金叉都吃 0.3% 双边成本
        - **A 股适配**：T+1 制度下当日买入不能卖，所以信号必须 `shift(1)`——用昨日信号决定今日仓位

        ### 参数选择经验
        | 短/长 | 性格 | 适用场景 |
        |-------|------|---------|
        | 5/20 | 敏捷 | 短线，交易频繁 |
        | 10/30 | 平衡 | 中线主流 |
        | 20/60 | 保守 | 大波段，过滤噪音 |
        | 5/60 | 跨频 | 短长周期博弈，信号少但强 |
        """),

        code(common_imports()),

        md("""
        ## 第 2 段：手写双均线信号

        **关键技巧**：避免未来函数——信号用「昨日 MA 比较」决定「今日仓位」。
        """),

        code("""
        byd = get_stock_data('002594').set_index('date')

        def dual_ma_signal(close: pd.Series, short: int = 5, long: int = 20) -> pd.Series:
            \\\"\\\"\\\"手写双均线信号（向量化，无 for 循环）。

            返回 [0, 1] 目标仓位序列，index 与 close 对齐。
            \\\"\\\"\\\"
            ma_s = close.rolling(short).mean()
            ma_l = close.rolling(long).mean()
            # 金叉后持有，死叉后空仓；shift(1) 避免未来函数
            signal = (ma_s > ma_l).astype(int).shift(1).fillna(0)
            return signal

        sig = dual_ma_signal(byd['close'], short=5, long=20)
        print(f"持仓天数占比: {sig.mean():.2%}")
        print(f"信号切换次数: {(sig.diff().abs() > 1e-6).sum()}")

        # 可视化：价格 + 双均线 + 持仓阴影
        fig, ax = plt.subplots(figsize=(13, 5))
        byd['close'].plot(ax=ax, label='收盘价', alpha=0.7)
        byd['close'].rolling(5).mean().plot(ax=ax, label='MA5', linestyle='--')
        byd['close'].rolling(20).mean().plot(ax=ax, label='MA20', linestyle='--')
        ax.fill_between(sig.index, byd['close'].min(), byd['close'].max(),
                        where=(sig == 1), alpha=0.1, color='green', label='持仓区')
        ax.set_title('比亚迪 + 双均线 + 持仓区（5/20 参数）')
        ax.legend(loc='upper left')
        plt.tight_layout(); plt.show()
        """),

        md("""
        ## 第 3 段：向量化回测 + 对比 qtrader 框架版

        手写简化版回测 → 对比 `qtrader.DualMAStrategy`，应得到几乎一致的结果。
        """),

        code("""
        # 手写回测
        rets = byd['close'].pct_change().fillna(0)
        turnover = sig.diff().abs().fillna(0)
        cost_rate = 0.00094  # 双边总费率（佣金+印花+过户+滑点）
        strat_nav = (1 + sig.shift(1).fillna(0) * rets - turnover * cost_rate).cumprod()
        bench_nav = (1 + rets).cumprod()

        # qtrader 框架版（同样 5/20 参数 + 默认 CostModel）
        engine = BacktestEngine()  # 默认 A 股 2026 真实成本
        result = engine.run(byd.reset_index(), DualMAStrategy(short=5, long=20))

        fig, ax = plt.subplots(figsize=(13, 5))
        bench_nav.plot(ax=ax, label='买入持有', alpha=0.5)
        strat_nav.plot(ax=ax, label='手写双均线', linestyle='--')
        result.nav.plot(ax=ax, label='qtrader.DualMAStrategy', linewidth=1.5)
        ax.set_title('手写 vs 框架版（应几乎重合）')
        ax.legend()
        plt.tight_layout(); plt.show()

        print(f"手写版终值:  {strat_nav.iloc[-1]:.3f}")
        print(f"框架版终值:  {result.nav.iloc[-1]:.3f}")
        print(f"差异来源: 手写版用简化成本率 0.00094，框架版按买卖方向分别计征")
        """),

        md("""
        ## 第 4 段：参数敏感性

        哪个 short/long 组合最优？这正是「过拟合」最容易出现的场景——
        先跑一遍网格，再用 walk-forward 验证（下一段）。
        """),

        code("""
        from qtrader.optimize import grid_search, walk_forward

        param_grid = {'short': [3, 5, 10], 'long': [20, 30, 60]}
        top = grid_search(engine, byd.reset_index(), DualMAStrategy, param_grid,
                          metric='sharpe', top_n=5)
        print("Top 5 参数组合（按夏普降序）：")
        print(top[['short', 'long', 'sharpe', 'sortino', 'max_drawdown', 'n_trades']].to_string(index=False))
        """),

        md("""
        ## 第 5 段：Walk-Forward 验证（防过拟合）

        网格搜索选出来的「最优参数」在**未来**还成立吗？切分训练/测试段验证。
        """),

        code("""
        wf = walk_forward(engine, byd.reset_index(), DualMAStrategy,
                          param_grid, train_ratio=0.7, metric='sharpe')
        print(f"训练段最优参数: {wf.best_params}")
        print(f"训练段 Sharpe: {wf.train_metric:.3f}")
        print(f"测试段 Sharpe: {wf.test_metric:.3f}")
        print(f"过拟合差距:    {wf.overfit_gap:+.3f}")
        if wf.overfit_gap > 0.5:
            print("⚠️ 训练-测试差距 > 0.5，参数大概率过拟合")
        elif wf.overfit_gap < 0:
            print("✓ 测试段反而更好，参数稳健")
        else:
            print("○ 差距合理，参数有一定泛化能力")
        """),

        md("""
        ## 第 6 段：本节要点

        1. **双均线本质** = 趋势跟踪，震荡市失效
        2. **shift(1) 必须有**，否则未来函数 → 夏普虚高 3-10 倍
        3. **手写 vs 框架版** 应几乎重合，差异只在成本模型精细度
        4. **网格搜索 ≠ 真最优**，必须 walk-forward 验证泛化能力
        5. A 股 5/20 是主流短周期；20/60 适合大波段

        ### 🔮 下节 L12：海龟（唐奇安通道 + ATR 仓位）
        原版海龟用 ATR 动态调仓——这是 Phase 1 完全跳过的「仓位管理」入门。
        """),
    ]
    write_nb(cells, "11_dual_ma_timing.ipynb")


# ============================================================
# L12 海龟（唐奇安通道 + ATR 仓位）
# ============================================================
def build_l12() -> None:
    cells = [
        md("""
        # L12 · 海龟策略（唐奇安通道 + ATR 仓位）

        **预计时长**：90 min | **难度**：⭐⭐⭐⭐ | **前置**：L11

        ## 本节目标
        1. 唐奇安通道：N 日最高/最低突破系统
        2. ATR（Average True Range）：真实波动幅度，仓位管理的基石
        3. 原版海龟的仓位公式：`unit = risk_per_trade / (atr × point_value)`
        4. 对比 qtrader 的 TurtleStrategy（含 atr_n 参数版）
        """),

        md("""
        ## 第 1 段：金融概念

        ### 唐奇安通道（Donchian Channel）
        - 上轨 = 过去 N 日最高价
        - 下轨 = 过去 M 日最低价
        - **突破上轨 → 买入；跌破下轨 → 卖出**
        - N=20, M=10 是 1980 年代「海龟交易实验」原版参数

        ### ATR（Average True Range）
        当日「真实波幅」TR 取以下三者的最大值：
        1. 今日最高 - 今日最低
        2. |今日最高 - 昨日收盘|
        3. |今日最低 - 昨日收盘|

        ATR(N) = TR 的 N 日均值，衡量「日均波动金额」。

        ### 原版海龟仓位公式（核心创新）
        ```
        unit = (account × risk_per_trade) / (atr × dollar_per_point)
        ```
        - risk_per_trade：单次交易风险，通常 1%
        - 含义：价格波动 1 ATR 时，账户损失正好 = risk_per_trade
        - 让「单次亏损可控」成为第一性原则

        ### 为什么 A 股版要调整
        - 原版海龟做多也做空（期货思维）
        - A 股现货只能做多 → 仓位 ∈ [0, max_pos]
        - qtrader.TurtleStrategy 用 `atr_n=None` 时退化为 [0,1] 二值
        """),

        code(common_imports()),

        md("""
        ## 第 2 段：手写唐奇安通道信号
        """),

        code("""
        byd = get_stock_data('002594').set_index('date')

        def donchian_signal(df: pd.DataFrame, entry_n: int = 20, exit_n: int = 10) -> pd.Series:
            \\\"\\\"\\\"唐奇安通道突破信号（向量化）。\\\"\\\"\\\"
            upper = df['high'].rolling(entry_n).max().shift(1)  # 用昨日通道
            lower = df['low'].rolling(exit_n).min().shift(1)
            buy = df['close'] > upper
            sell = df['close'] < lower

            signal = pd.Series(np.nan, index=df.index)
            signal[buy] = 1.0
            signal[sell] = 0.0
            # fillna + shift(1)：避免未来函数
            return signal.ffill().fillna(0).shift(1).fillna(0)

        sig = donchian_signal(byd, entry_n=20, exit_n=10)
        print(f"持仓占比: {sig.mean():.2%}")
        print(f"信号切换次数: {(sig.diff().abs() > 1e-6).sum()}")
        """),

        md("""
        ## 第 3 段：ATR 计算与可视化
        """),

        code("""
        def compute_atr(df: pd.DataFrame, n: int = 20) -> pd.Series:
            \\\"\\\"\\\"计算 ATR（N 日均真实波幅）。\\\"\\\"\\\"
            prev_close = df['close'].shift(1)
            tr = pd.concat([
                df['high'] - df['low'],
                (df['high'] - prev_close).abs(),
                (df['low'] - prev_close).abs(),
            ], axis=1).max(axis=1)
            return tr.rolling(n).mean()

        atr = compute_atr(byd, n=20)
        atr_pct = (atr / byd['close']) * 100  # 转换为百分比

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 7), sharex=True,
                                       gridspec_kw={'height_ratios': [3, 1]})
        byd['close'].plot(ax=ax1, label='收盘价', alpha=0.7)
        byd['high'].rolling(20).max().shift(1).plot(ax=ax1, label='上轨 N=20', linestyle='--')
        byd['low'].rolling(10).min().shift(1).plot(ax=ax1, label='下轨 M=10', linestyle='--')
        ax1.set_title('比亚迪 + 唐奇安通道')
        ax1.legend()

        atr_pct.plot(ax=ax2, color='purple', label='ATR%')
        ax2.set_ylabel('日波动率(%)')
        ax2.legend()
        plt.tight_layout(); plt.show()

        print(f"ATR% 平均: {atr_pct.mean():.2f}%，最大: {atr_pct.max():.2f}%")
        """),

        md("""
        ## 第 4 段：ATR 仓位管理 + 对比框架版
        """),

        code("""
        # 手写 ATR 仓位
        risk_per_trade = 0.01  # 1% 单次风险
        max_pos = 1.0
        sized = (risk_per_trade / (atr_pct / 100).replace(0, np.nan)).clip(0, max_pos).fillna(0)
        position = sig * sized  # 仅持仓状态应用 ATR 仓位

        # qtrader 框架版
        engine = BacktestEngine()
        result_binary = engine.run(byd.reset_index(), TurtleStrategy(entry_n=20, exit_n=10))
        result_atr = engine.run(byd.reset_index(),
            TurtleStrategy(entry_n=20, exit_n=10, atr_n=20, risk_per_trade=0.01, max_pos=1.0))

        fig, ax = plt.subplots(figsize=(13, 5))
        (1 + byd['close'].pct_change().fillna(0)).cumprod().plot(ax=ax, label='买入持有', alpha=0.5)
        result_binary.nav.plot(ax=ax, label='Turtle 二值', linestyle='--')
        result_atr.nav.plot(ax=ax, label='Turtle + ATR', linewidth=1.5)
        ax.set_title('海龟二值 vs ATR 仓位版')
        ax.legend()
        plt.tight_layout(); plt.show()

        print(f"二值版夏普: {result_binary.metrics['sharpe']:.3f}")
        print(f"ATR 版夏普:  {result_atr.metrics['sharpe']:.3f}")
        print(f"ATR 版持仓时长: {result_atr.metrics['exposure_time']:.2%}")
        """),

        md("""
        ## 第 5 段：海龟策略的人性化解读

        - **纪律性**：突破就买，跌破就卖，不带感情——1980 年代实验证明规则化交易胜过直觉
        - **仓位智慧**：ATR 高（波动大）→ 减仓；ATR 低（平静）→ 加仓
        - **A 股实战注意**：
          - 涨停一字板无法买入，回测里的「突破买入」可能实盘做不到
          - 长期熊市（2010-2014、2021-2023）海龟会持续小亏，心理考验大
          - 必须搭配 ETF 或一篮子股票做分散，否则单股黑天鹅致命

        ### 🔮 下节 L13：网格策略
        与趋势跟踪相反，网格是「震荡市利器」，在 A 股的高波动环境有独特价值。
        """),
    ]
    write_nb(cells, "12_turtle_donchian_atr.ipynb")


# ============================================================
# L13 网格策略
# ============================================================
def build_l13() -> None:
    cells = [
        md("""
        # L13 · 网格策略（Grid Trading）

        **预计时长**：75 min | **难度**：⭐⭐⭐⭐ | **前置**：L12

        ## 本节目标
        1. 网格逻辑：震荡市的「低买高卖」自动化
        2. 向量化实现：cumsum 累加穿越次数 → 连续仓位
        3. 网格 vs 双均线 vs 海龟的适用场景对比
        4. qtrader.GridStrategy 源码精读
        """),

        md("""
        ## 第 1 段：金融概念

        ### 网格策略核心思想
        在一个价格区间内**等分若干网格**，每上穿一条线加 1 仓，每下穿一条线减 1 仓：
        ```
        价格轴（lookback 区间 low~high 等分 10 格）：
        ━━━━━━━━━━━━━━ high（ref）
        ─ ─ ─ ─ ─ ─ 网格 9
        ─ ─ ─ ─ ─ ─ 网格 8
        ...
        ─ ─ ─ ─ ─ ─ 网格 1
        ━━━━━━━━━━━━━━ low（ref）
        ```
        - **震荡市**：价格在区间内来回穿越，反复吃到 0.5%-1% 的小利润
        - **趋势上涨**：仓位逐渐加满 → 变成「满仓踏空上涨」
        - **趋势下跌**：仓位逐渐减到 0 → 至少不深套

        ### 与双均线/海龟的对比
        | 维度 | 双均线 / 海龟 | 网格 |
        |------|--------------|------|
        | 市场偏好 | 趋势市 | 震荡市 |
        | 信号触发 | 突破 | 穿越网格线 |
        | 仓位形态 | 0/1 二值（或 ATR 缩放） | 0 ~ max_pos 连续 |
        | 失效场景 | 频繁假突破 | 单边趋势（踏空或深套） |

        ### A 股适配
        - 适合**高波动但不深跌**的标的（ETF、蓝筹、可转债）
        - 不适合**单边趋势**（乐视网式崩盘）
        - 网格数 grid_n 通常 5-20，太少粗糙，太多交易成本吃光利润
        """),

        code(common_imports()),

        md("""
        ## 第 2 段：手写网格信号（向量化核心）
        """),

        code("""
        byd = get_stock_data('002594').set_index('date')

        def grid_signal(close: pd.Series, grid_n: int = 10, lookback: int = 60) -> pd.Series:
            \\\"\\\"\\\"手写网格信号（向量化，无 K 线级 for 循环）。

            关键技巧：
            - 网格线 = ref_low + i × step，i ∈ [1, grid_n]
            - 每日检查「是否上穿第 i 条线」+1，「是否下穿第 i 条线」-1
            - 累加 → 连续仓位
            \\\"\\\"\\\"
            ref_high = close.rolling(lookback).max().shift(1)
            ref_low = close.rolling(lookback).min().shift(1)
            step = (ref_high - ref_low) / grid_n
            prev_close = close.shift(1)

            position_change = pd.Series(0.0, index=close.index)
            for i in range(1, grid_n + 1):
                # 「网格线循环」是可接受例外（非 K 线循环）
                grid_line = ref_low + i * step
                cross_up = (prev_close < grid_line) & (close >= grid_line)
                cross_down = (prev_close > grid_line) & (close <= grid_line)
                position_change += cross_up.astype(float) - cross_down.astype(float)

            raw = position_change.cumsum().clip(0, grid_n) / grid_n
            return raw.shift(1).fillna(0)

        sig = grid_signal(byd['close'], grid_n=10, lookback=60)
        print(f"平均仓位: {sig.mean():.2%}")
        print(f"最大仓位: {sig.max():.2%}")
        print(f"调仓次数: {(sig.diff().abs() > 1e-6).sum()}")
        """),

        md("""
        ## 第 3 段：回测 + 对比 qtrader.GridStrategy
        """),

        code("""
        engine = BacktestEngine()
        result = engine.run(byd.reset_index(), GridStrategy(grid_n=10, lookback=60))

        fig, ax = plt.subplots(figsize=(13, 5))
        result.benchmark_nav.plot(ax=ax, label='买入持有', alpha=0.5)
        result.nav.plot(ax=ax, label='qtrader.GridStrategy', linewidth=1.5)
        ax.set_title('比亚迪 网格策略 vs 买入持有')
        ax.legend()
        plt.tight_layout(); plt.show()

        print(f"网格策略夏普: {result.metrics['sharpe']:.3f}")
        print(f"买入持有夏普:  (未计算，参考 nav.plot)")
        print(f"网格持仓时长: {result.metrics['exposure_time']:.2%}")
        """),

        md("""
        ## 第 4 段：网格参数敏感性

        - `grid_n`（网格数）：影响交易频率与单次利润
        - `lookback`（参考窗口）：影响区间宽度
        """),

        code("""
        from qtrader.optimize import grid_search

        # 注意：grid_n 越大不一定越好，因为交易成本累积
        top = grid_search(engine, byd.reset_index(), GridStrategy,
                          {'grid_n': [5, 10, 20], 'lookback': [30, 60, 120]},
                          metric='sharpe', top_n=5)
        print("Top 5 网格参数组合：")
        print(top[['grid_n', 'lookback', 'sharpe', 'n_trades', 'exposure_time']].to_string(index=False))
        """),

        md("""
        ## 第 5 段：何时用网格（实战指南）

        ✅ 适合：
        - ETF（沪深 300、中证 500、科创 50）：长期震荡向上
        - 高股息蓝筹（银行、公用事业）：股价「磨」
        - 可转债（下有债底、上有赎回）：天然区间

        ❌ 不适合：
        - 强趋势股（次新股、题材股）：要么踏空要么深套
        - 流动性差的股票：网格触发后无法成交
        - 涨跌停频繁的股票：一字板时网格失效

        ### 🔮 下节 L14：多股选股
        三个策略都是「择时」（何时买卖），下节转向「选股」（买什么）。
        """),
    ]
    write_nb(cells, "13_grid_strategy.ipynb")


# ============================================================
# L14 多股选股
# ============================================================
def build_l14() -> None:
    cells = [
        md("""
        # L14 · 多股选股（Stock Selection）

        **预计时长**：90 min | **难度**：⭐⭐⭐⭐ | **前置**：L04 panel 对齐、L08 PE 估值

        ## 本节目标
        1. 从「单股回测」跃迁到「多股选股 + 组合」
        2. 三大经典选股因子：价值（PE）/ 动量（Momentum）/ 波动率（Volatility）
        3. 多因子 rank 融合：每个因子打分 → 综合排名 → top-N 选股
        4. 分位回测（quintile backtest）：把股票按因子分 5 组，看 top 组 vs bottom 组
        """),

        md("""
        ## 第 1 段：金融概念

        ### 主动选股 vs 被动持有
        - **被动**（买入持有 ETF）：拿到市场平均 β 收益
        - **主动选股**：试图获取 α 超额收益——但这非常难

        ### 三大经典因子（Fama-French + 行为金融）
        | 因子 | 含义 | 历史 long-term 表现 |
        |------|------|-------------------|
        | **价值（PE/PB）** | 低估值股票便宜 | 价值溢价，但 2010-2020 美股失效 |
        | **动量（Momentum）** | 过去 6-12 月涨得多的继续涨 | 持续有效，但崩溃剧烈 |
        | **低波动（LowVol）** | 波动率低的股票长期更优 | 低波动异象，反 CAPM 直觉 |
        | 质量（Quality） | ROE 高、负债低 | 长期有效 |
        | 规模（Size） | 市值小 → 效率高 | A 股小盘股效应显著 |

        ### 多因子 rank 融合流程
        ```
        1. 每个股票每个因子 → 计算因子值 → 在全市场内 rank (0~1)
        2. 多因子加权：composite = 0.4*PE_rank + 0.3*MOM_rank + 0.3*LowVol_rank
        3. 选 composite 最高的 top-N（如 top 20%）
        ```

        ### A 股特性
        - 小盘股效应非常强（中证 1000 / 中证 2000 长期跑赢沪深 300）
        - 题材/概念驱动，价值因子在牛市失效、熊市有效
        - 财务造假风险 → 质量因子（剔除高应收/低现金流）尤其重要
        """),

        code(common_imports()),

        md("""
        ## 第 2 段：构建多股 panel

        复用 Phase 1 L04 的多股对齐能力。
        """),

        code("""
        # 5 只代表性股票跨行业
        codes_names = [
            ('002594', '比亚迪'),    # 汽车
            ('600519', '贵州茅台'),  # 食品饮料
            ('002624', '完美世界'),  # 传媒
            ('300750', '宁德时代'),  # 电池
            ('000001', '平安银行'),  # 银行
        ]
        codes = [c for c, _ in codes_names]
        names = [n for _, n in codes_names]

        frames = {}
        for code in codes:
            df = get_stock_data(code).set_index('date')
            frames[code] = df['close']
        panel = pd.DataFrame(frames).sort_index().ffill()
        print(f"panel shape: {panel.shape}")
        print(panel.tail(3))
        """),

        md("""
        ## 第 3 段：计算三大因子
        """),

        code("""
        rets_panel = panel.pct_change().dropna()

        # 因子 1: 动量（过去 6 个月累计收益）
        momentum = panel.pct_change(126).iloc[-1]  # 最近一日的 6 月动量
        print("动量（近 6 月涨幅）:")
        print(momentum.sort_values(ascending=False).round(3))

        # 因子 2: 波动率（过去 1 年日波动率年化）
        vol = rets_panel.std() * np.sqrt(252)
        print("\\n年化波动率:")
        print(vol.sort_values().round(3))

        # 因子 3: 价值（PE — 这里用代理指标：价格分位）
        # 真实 PE 需要财务数据，这里用「当前价在过去 1 年的分位」作为代理
        pe_proxy = panel.apply(lambda s: (s.iloc[-1] - s.min()) / (s.max() - s.min()))
        print("\\n价格分位（0 = 最低，1 = 最高）:")
        print(pe_proxy.sort_values().round(3))
        """),

        md("""
        ## 第 4 段：多因子 rank 融合

        关键：每个因子先 rank → 再加权，避免量纲不一致。
        """),

        code("""
        factors = pd.DataFrame({
            'momentum': momentum,
            'low_vol': -vol,      # 负号：波动低 = 好
            'value': -pe_proxy,   # 负号：价格分位低 = 便宜 = 好
        })

        # 在每列内 rank（0~1）
        ranked = factors.rank(pct=True)
        print("各因子分位排名（越大越好）:")
        print(ranked.round(3))

        # 加权融合
        weights = {'momentum': 0.4, 'low_vol': 0.3, 'value': 0.3}
        composite = (
            ranked['momentum'] * weights['momentum']
            + ranked['low_vol'] * weights['low_vol']
            + ranked['value'] * weights['value']
        )

        print("\\n综合排名（降序，前 2 名 = 推荐买入）:")
        top_n = 2
        top_codes = composite.sort_values(ascending=False).head(top_n)
        print(top_codes.round(3))

        # 加上股票名
        code_to_name = dict(codes_names)
        print("\\n推荐组合:")
        for code, score in top_codes.items():
            print(f"  {code} {code_to_name[code]:<6} 综合分: {score:.3f}")
        """),

        md("""
        ## 第 5 段：分位回测（Quintile Backtest）

        把股票按因子分 5 组，看 top 组是否长期跑赢 bottom 组。
        由于这里只有 5 只股票，分组意义有限——但流程对真实 300+ 股票池同样适用。
        """),

        code("""
        # 简化：按动量因子排序，top 组 vs bottom 组
        sorted_by_mom = momentum.sort_values(ascending=False)
        top_group = sorted_by_mom.head(2).index.tolist()
        bottom_group = sorted_by_mom.tail(2).index.tolist()

        # 等权组合净值
        top_nav = (1 + rets_panel[top_group].mean(axis=1)).cumprod()
        bottom_nav = (1 + rets_panel[bottom_group].mean(axis=1)).cumprod()

        fig, ax = plt.subplots(figsize=(13, 5))
        top_nav.plot(ax=ax, label=f'Top 动量 ({", ".join(top_group)})', linewidth=2)
        bottom_nav.plot(ax=ax, label=f'Bottom 动量 ({", ".join(bottom_group)})', linestyle='--')
        ax.set_title('动量因子分位回测：Top vs Bottom')
        ax.legend()
        plt.tight_layout(); plt.show()

        print(f"Top 组年化:    {(top_nav.iloc[-1] ** (252/len(top_nav)) - 1) * 100:.2f}%")
        print(f"Bottom 组年化: {(bottom_nav.iloc[-1] ** (252/len(bottom_nav)) - 1) * 100:.2f}%")
        print(f"多空收益:      {(top_nav.iloc[-1] / bottom_nav.iloc[-1] - 1) * 100:.2f}%")
        """),

        md("""
        ## 第 6 段：本节要点

        1. **选股 = 从 β 到 α 的跃迁**：被动持有拿 β，主动选股追求 α
        2. **三大因子**：价值、动量、低波动，每个都有学术与实战依据
        3. **多因子融合**：先 rank 再加权，避免量纲问题
        4. **分位回测**：是评估因子有效性的标准方法
        5. **A 股特性**：小盘效应强、题材驱动、财务造假风险——质量因子必备

        ### 🔮 下节 L15：组合构建
        选出 top-N 股票后，每只配置多少仓位？等权 / 反向波动加权 / Markowitz。
        """),
    ]
    write_nb(cells, "14_multi_stock_selection.ipynb")


# ============================================================
# L15 组合构建
# ============================================================
def build_l15() -> None:
    cells = [
        md("""
        # L15 · 组合构建（Portfolio Construction）

        **预计时长**：90 min | **难度**：⭐⭐⭐⭐⭐ | **前置**：L14

        ## 本节目标
        1. 从「选股」跃迁到「配置」：仓位权重如何决定
        2. 三大主流方案：等权 / 反向波动加权 / Markowitz 最小方差
        3. 组合再平衡（rebalance）：定期 vs 触发式
        4. 评估：组合层面的夏普 / 回撤 / 多样化收益
        """),

        md("""
        ## 第 1 段：金融概念

        ### 为什么权重重要
        选出 5 只好股票，但全仓押 1 只 → 仍是单股风险。
        权重决定了**组合的波动率、回撤、多样化效果**。

        ### 三大权重方案
        | 方案 | 公式 | 优点 | 缺点 |
        |------|------|------|------|
        | **等权** | w_i = 1/N | 最简单、稳健 | 忽略各股风险差异 |
        | **反向波动加权** | w_i ∝ 1/σ_i | 低波动股权重大 | 对 σ 估计敏感 |
        | **Markowitz 最小方差** | argmin w'Σw s.t. Σw=1 | 理论最优 | 对协方差矩阵敏感，过拟合 |

        ### Markowitz 现代组合理论（1952）
        - 核心：在给定收益下最小化风险，或给定风险下最大化收益
        - 有效前沿（Efficient Frontier）：风险-收益平面的上沿曲线
        - 局限：σ 和相关性估计误差被放大，过去 ≠ 未来

        ### A 股组合实战
        - **5-10 只股票足够**：分散边际收益递减
        - **跨行业**：避免行业暴雷全军覆没
        - **定期再平衡**（季度/半年）：让组合不偏离目标权重
        - **不要过度优化**：Markowitz 对噪声极度敏感
        """),

        code(common_imports()),

        md("""
        ## 第 2 段：复用 L14 的 panel
        """),

        code("""
        codes_names = [
            ('002594', '比亚迪'), ('600519', '贵州茅台'),
            ('002624', '完美世界'), ('300750', '宁德时代'),
            ('000001', '平安银行'),
        ]
        codes = [c for c, _ in codes_names]
        frames = {c: get_stock_data(c).set_index('date')['close'] for c in codes}
        panel = pd.DataFrame(frames).sort_index().ffill()
        rets = panel.pct_change().dropna()
        print(f"panel shape: {panel.shape}")
        """),

        md("""
        ## 第 3 段：三种权重方案
        """),

        code("""
        # 方案 1: 等权
        N = len(codes)
        w_equal = pd.Series(1/N, index=codes)

        # 方案 2: 反向波动加权
        vol = rets.std() * np.sqrt(252)
        w_inv_vol = (1 / vol) / (1 / vol).sum()

        # 方案 3: Markowitz 最小方差（解析解，无需 scipy）
        # min w'Σw s.t. Σw=1 的闭式解：w = Σ^(-1) 1 / (1' Σ^(-1) 1)
        cov = rets.cov() * 252  # 年化协方差
        inv_cov = np.linalg.pinv(cov.values)  # pseudo-inverse 防奇异
        ones = np.ones(N)
        w_mkv_values = inv_cov @ ones / (ones @ inv_cov @ ones)
        w_mkv = pd.Series(w_mkv_values, index=codes)

        weights = pd.DataFrame({
            '等权': w_equal, '反向波动': w_inv_vol, 'Markowitz': w_mkv
        })
        print("三种权重方案对比:")
        print(weights.round(3))
        print(f"\\n权重总和（应 = 1.0）:")
        print(weights.sum().round(6))
        """),

        md("""
        ## 第 4 段：组合回测 + 再平衡

        假设每月（22 交易日）再平衡一次。
        """),

        code("""
        def backtest_portfolio(rets: pd.DataFrame, weights: pd.Series,
                              rebalance_freq: int = 22) -> pd.Series:
            \\\"\\\"\\\"组合回测：定期再平衡到目标权重。\\\"\\\"\\\"
            nav = 1.0
            navs = []
            w = weights.copy()
            for i, (date, daily_rets) in enumerate(rets.iterrows()):
                # 当日组合收益
                port_ret = (w * daily_rets).sum()
                nav *= (1 + port_ret)
                navs.append(nav)
                # 权重随涨跌漂移
                w = w * (1 + daily_rets)
                w = w / w.sum()
                # 到再平衡日，重置回目标权重
                if (i + 1) % rebalance_freq == 0:
                    w = weights.copy()
            return pd.Series(navs, index=rets.index, name='nav')

        nav_equal = backtest_portfolio(rets, w_equal)
        nav_inv_vol = backtest_portfolio(rets, w_inv_vol)
        nav_mkv = backtest_portfolio(rets, w_mkv)
        nav_bench = (1 + rets.mean(axis=1)).cumprod()  # 等权基准作为对照

        fig, ax = plt.subplots(figsize=(13, 6))
        nav_equal.plot(ax=ax, label='等权', linewidth=2)
        nav_inv_vol.plot(ax=ax, label='反向波动', linestyle='--')
        nav_mkv.plot(ax=ax, label='Markowitz 最小方差', linestyle='-.')
        ax.set_title('三种组合构建方案净值对比')
        ax.legend()
        plt.tight_layout(); plt.show()
        """),

        md("""
        ## 第 5 段：组合绩效评估

        用 qtrader.metrics 的扩展指标评估三种方案。
        """),

        code("""
        from qtrader.metrics import compute_metrics

        results = {}
        for name, nav in [('等权', nav_equal), ('反向波动', nav_inv_vol), ('Markowitz', nav_mkv)]:
            strat_ret = nav.pct_change().fillna(0)
            # 传 nav 与 bench_ret（这里用等权作为基准对照）
            m = compute_metrics(strat_ret, nav, nav_equal.pct_change().fillna(0))
            results[name] = m

        import pandas as pd
        summary = pd.DataFrame({
            name: {k: v for k, v in m.items() if k in
                   ['total_return', 'ann_return', 'sharpe', 'sortino', 'calmar',
                    'max_drawdown', 'volatility', 'win_rate']}
            for name, m in results.items()
        }).T
        print("三种组合方案绩效对比:")
        print(summary.round(3))
        """),

        md("""
        ## 第 6 段：本节要点 + Phase 2 收官

        ### 组合构建要点
        1. **等权 > 你以为**：简单方案常常打败精巧的 Markowitz
        2. **反向波动是稳健中间路线**：考虑风险差异但不过度优化
        3. **Markowitz 对噪声敏感**：必须 shrinkage 协方差矩阵或用 Black-Litterman
        4. **再平衡是 alpha 来源**：定期「低买高卖」本质 = 逆向投资

        ### Phase 2 收官
        恭喜走完 L11-L15！现在你拥有了完整的量化基础栈：
        - **数据层**：akshare / 多股对齐 / 复权（Phase 1）
        - **指标层**：风险/收益/成本三件套（Phase 1 L06 + Phase 2 L11 metrics 扩展）
        - **策略层**：择时三巨头（DualMA/Turtle/Grid）+ 选股 + 组合（Phase 2）
        - **回测层**：向量化引擎 + CostModel + Walk-Forward（qtrader 框架）

        ### Phase 3 预告（未来阶段）
        - 机器学习 Alpha 因子（LightGBM、强化学习）
        - 事件驱动引擎（限价单、涨跌停拒单）
        - 实盘对接（券商 API、CTP）
        - 衍生品（可转债、股指期货）

        ### 📝 `exercises/ex14.py` / `ex15.py`
        本阶段配套 2 份课后练习，请独立完成。
        """),
    ]
    write_nb(cells, "15_portfolio_construction.ipynb")


# ============================================================
# Exercises
# ============================================================
def build_ex14() -> None:
    write_ex("ex14.py", '''
        """L14 课后练习：多股选股。"""
        from __future__ import annotations
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
        sys.path.insert(0, str(Path(__file__).resolve().parents[2].parent / 'phase1_foundation'))

        import numpy as np
        import pandas as pd
        from _data import get_stock_data


        def momentum_factor(panel: pd.DataFrame, lookback: int = 126) -> pd.Series:
            """动量因子：每只股票过去 lookback 日的累计收益。

            Returns:
                Series index=code, value=累计收益
            """
            # TODO: ~3 行


            return pd.Series(dtype=float)


        def rank_composite(factors: dict[str, pd.Series],
                           weights: dict[str, float]) -> pd.Series:
            """多因子 rank 融合：先对每个因子做 pct rank，再加权求和。

            Args:
                factors: {'momentum': Series, 'low_vol': Series, ...}
                weights: {'momentum': 0.4, 'low_vol': 0.3, ...}

            Returns:
                Series，综合得分（0~1）
            """
            # TODO: ~5 行




            return pd.Series(dtype=float)


        def quintile_returns(rets: pd.DataFrame, factor: pd.Series,
                             n_groups: int = 5) -> pd.DataFrame:
            """按因子分 n_groups 组，返回每组等权组合的累计净值。

            Returns:
                DataFrame index=date, columns=[f'Q{i}' for i in 1..n_groups]
            """
            # TODO: ~8 行






            return pd.DataFrame()


        def run_all() -> None:
            codes = ['002594', '600519', '002624', '300750', '000001',
                     '002602', '600104', '601633', '000858', '300251']
            frames = {c: get_stock_data(c).set_index('date')['close'] for c in codes}
            panel = pd.DataFrame(frames).sort_index().ffill()
            rets = panel.pct_change().dropna()

            print("题 1：动量因子")
            mom = momentum_factor(panel)
            print(mom.sort_values(ascending=False).round(3))

            print("\\n题 2：综合得分")
            factors = {
                'momentum': mom,
                'low_vol': -rets.std() * np.sqrt(252),
            }
            composite = rank_composite(factors, {'momentum': 0.6, 'low_vol': 0.4})
            print(composite.sort_values(ascending=False).round(3))

            print("\\n题 3：分位回测（简化版，n=2 组）")
            q_navs = quintile_returns(rets, mom, n_groups=2)
            print(q_navs.tail())


        if __name__ == "__main__":
            run_all()
    ''')


def build_ex15() -> None:
    write_ex("ex15.py", '''
        """L15 课后练习：组合构建。"""
        from __future__ import annotations
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
        sys.path.insert(0, str(Path(__file__).resolve().parents[2].parent / 'phase1_foundation'))

        import numpy as np
        import pandas as pd
        from _data import get_stock_data


        def equal_weight(codes: list[str]) -> pd.Series:
            """等权组合权重。"""
            # TODO: 1 行
            return pd.Series(dtype=float)


        def inverse_vol_weight(rets: pd.DataFrame) -> pd.Series:
            """反向波动加权：w_i ∝ 1/σ_i。"""
            # TODO: ~3 行



            return pd.Series(dtype=float)


        def min_variance_weights(rets: pd.DataFrame) -> pd.Series:
            """Markowitz 最小方差：w = Σ^(-1) 1 / (1' Σ^(-1) 1)。"""
            # TODO: ~5 行




            return pd.Series(dtype=float)


        def backtest_rebalanced(rets: pd.DataFrame, weights: pd.Series,
                                rebalance_freq: int = 22) -> pd.Series:
            """定期再平衡回测。"""
            # TODO: ~10 行






            return pd.Series(dtype=float)


        def run_all() -> None:
            codes = ['002594', '600519', '002624', '300750', '000001']
            frames = {c: get_stock_data(c).set_index('date')['close'] for c in codes}
            panel = pd.DataFrame(frames).sort_index().ffill()
            rets = panel.pct_change().dropna()

            print("题 1：三种权重对比")
            for name, w in [
                ('等权', equal_weight(codes)),
                ('反向波动', inverse_vol_weight(rets)),
                ('最小方差', min_variance_weights(rets)),
            ]:
                print(f"\\n[{name}]")
                print(w.round(3))

            print("\\n题 2：组合回测")
            navs = {}
            for name, w in [
                ('等权', equal_weight(codes)),
                ('反向波动', inverse_vol_weight(rets)),
                ('最小方差', min_variance_weights(rets)),
            ]:
                nav = backtest_rebalanced(rets, w, rebalance_freq=22)
                navs[name] = nav
                print(f"{name}: 终值 {nav.iloc[-1]:.3f}, 年化 {(nav.iloc[-1]**(252/len(nav))-1)*100:.2f}%")

            print("\\n题 3：最佳方案")
            best = max(navs.items(), key=lambda x: x[1].iloc[-1])
            print(f"最高终值: {best[0]} ({best[1].iloc[-1]:.3f})")


        if __name__ == "__main__":
            run_all()
    ''')


def main() -> None:
    build_l11()
    build_l12()
    build_l13()
    build_l14()
    build_l15()
    build_ex14()
    build_ex15()
    print(f"OK: L11-L15 + ex14/ex15 created in {OUT_DIR}")


if __name__ == "__main__":
    main()
