"""批次 3+4 notebook 构建脚本（L02-L10 + ex02-ex09）。

设计原则：每节 = 元信息 + 概念 + 数据准备 + 3-5 演示 + 1-2 小练 + 习题说明 + tip。
内容保持精简但完整，重点突出"金融概念 × 数据技能"紧配对。
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
    EX_DIR.mkdir(exist_ok=True)
    (EX_DIR / "__init__.py").write_text("")
    (EX_DIR / filename).write_text(dedent(body).lstrip())


def common_imports() -> str:
    return """
        import sys
        from pathlib import Path

        # 自动定位 phase1_foundation 目录 + project root（兼容两种 jupyter 启动位置）
        _cwd = Path.cwd()
        _p1 = _cwd if (_cwd / '_data.py').exists() else (_cwd / 'learning' / 'phase1_foundation')
        sys.path.insert(0, str(_p1))
        _proj = _p1.parent.parent if _p1.name == 'phase1_foundation' else _p1
        if (_proj / 'qtrader' / '__init__.py').exists():
            sys.path.insert(0, str(_proj))

        import numpy as np
        import pandas as pd
        import matplotlib.pyplot as plt
        import _style
        from _data import get_stock_data
    """


# ============================================================
# L02 K 线读图 + DataFrame
# ============================================================
def build_l02() -> None:
    cells = [
        md("""
        # L02 · K 线读图 + DataFrame 索引

        **预计时长**：60 min | **难度**：⭐⭐ | **前置**：L01

        ## 本节目标
        1. 看懂 K 线 4 元素（OHLC）、阳线阴线、上下影、典型形态
        2. 用 mplfinance 画专业 K 线图（替代 L01 的纯数字表）
        3. 掌握 DataFrame 的 `.loc / .iloc` 索引切片
        4. 从 K 线上定位"最大涨/跌幅日"并理解为什么
        """),

        md("""
        ## 第 1 段：金融概念

        ### K 线构成（单根）
        ```
             最高 ───┐       ← 上影线
                     │
              ┌──────┴──────┐  ← 收盘价（阳线）
              │             │
              │   实体      │
              │             │
              └──────┬──────┘  ← 开盘价（阳线）
                     │
             最低 ───┘       ← 下影线
        ```
        - **阳线（红 / A 股惯例）**：close > open，看涨
        - **阴线（绿 / A 股惯例）**：close < open，看跌
        - **上影**：high - max(open, close)，代表"上方抛压"
        - **下影**：min(open, close) - low，代表"下方支撑"

        **注意**：A 股红涨绿跌，和美股相反！后续所有图按 A 股惯例。

        ### 典型形态（4 例）
        | 形态 | 特征 | 含义 |
        |------|------|------|
        | 大阳线 | 实体长、影线短 | 强势看涨 |
        | 十字星 | open≈close、有上下影 | 多空胶着，可能反转 |
        | 锤头线 | 下影长、实体小、无上影 | 底部反转信号 |
        | 一字板 | OHLC 全相等 | 涨/跌停封死（L01 见过） |
        """),

        code(common_imports()),

        code("""
        byd = get_stock_data("002594")
        byd.head()
        """),

        md("""
        ## 第 2 段：手画一根 K 线（理解本质）

        用 matplotlib 矩形 + 线段画一根 K 线，让你看清 mplfinance 背后做了什么。
        """),

        code("""
        # 选一天比亚迪的 K 线
        row = byd.iloc[100]  # 第 100 个交易日
        is_up = row['close'] >= row['open']
        color = 'red' if is_up else 'green'

        fig, ax = plt.subplots(figsize=(3, 6))
        # 上下影线
        ax.plot([0, 0], [row['low'], row['high']], color=color, linewidth=1.5)
        # 实体矩形
        body_low = min(row['open'], row['close'])
        body_high = max(row['open'], row['close'])
        ax.add_patch(plt.Rectangle((-0.3, body_low), 0.6, body_high - body_low,
                                    facecolor=color, edgecolor=color))
        ax.set_xlim(-1, 1)
        ax.set_title(f"比亚迪 {row['date'].date()} 单根 K 线")
        ax.set_xticks([])
        plt.show()
        """),

        md("""
        ## 第 3 段：mplfinance 专业 K 线图

        手画太累。`mplfinance` 一行画出几十根 K 线 + 均线 + 成交量。
        """),

        code("""
        import mplfinance as mpf

        # 自定义 A 股配色（红涨绿跌，与美股相反）
        a_share_style = mpf.make_mpf_style(
            base_mpf_style='charles',
            marketcolors=mpf.make_marketcolors(up='#e74c3c', down='#27ae60',
                                                edge='inherit', wick='inherit',
                                                volume='inherit'),
            rc={'font.sans-serif': ['Microsoft YaHei']},
        )

        # mplfinance 要求 DataFrame 的 index 是 DatetimeIndex，列名是 Open/High/Low/Close/Volume
        df = byd.set_index('date').rename(columns={
            'open': 'Open', 'high': 'High', 'low': 'Low',
            'close': 'Close', 'volume': 'Volume'
        })
        # 取最近 60 个交易日
        df_recent = df.tail(60)
        mpf.plot(df_recent, type='candle', style=a_share_style,
                 title='比亚迪 近 60 日 K 线（A 股配色：红涨绿跌）',
                 volume=True, mav=(5, 20))
        """),

        md("""
        **A 股配色**：红涨绿跌（与美股相反）。上面用 `mpf.make_marketcolors(up='#e74c3c', down='#27ae60')` 自定义。
        """),

        md("""
        ## 第 4 段：`.loc / .iloc` 索引切片

        - `.loc`：按**标签**（日期、列名）索引
        - `.iloc`：按**位置**（整数下标）索引
        """),

        code("""
        # 1. 用 .loc 选某一段日期（要用日期 index）
        byd_indexed = byd.set_index('date')
        slice1 = byd_indexed.loc['2024-01-01':'2024-03-31']
        print(f"2024 Q1 行数: {len(slice1)}")
        slice1.head()
        """),

        code("""
        # 2. 用 .loc 选某些列
        byd_indexed.loc['2024-01-01':'2024-01-05', ['close', 'volume']]
        """),

        code("""
        # 3. 用 .iloc 按位置取
        print("第 1 行：")
        print(byd.iloc[0])
        print("\\n第 10-12 行的 close 列：")
        print(byd.iloc[10:13, byd.columns.get_loc('close')])
        """),

        code("""
        # 4. 布尔索引（loc 的高级用法）
        # 找所有 close > open 且当日涨幅 > 5% 的日子
        byd['prev_close'] = byd['close'].shift(1)
        byd['chg_pct'] = byd['close'] / byd['prev_close'] - 1
        big_up = byd[(byd['close'] > byd['open']) & (byd['chg_pct'] > 0.05)]
        print(f"比亚迪涨幅>5% 且阳线的日子共 {len(big_up)} 天")
        big_up[['date', 'open', 'close', 'chg_pct']].head()
        """),

        md("""
        ## 第 5 段：随堂小练

        ### 小练：找比亚迪 2024 年最大单日涨幅日的 K 线
        用 mplfinance 画出那一天 ±10 个交易日的 K 线图（共 21 根），观察"最大涨幅日"长什么样。
        """),

        code("""
        # TODO: 你的代码（约 5 行）
        # 提示：
        # 1) 筛出 2024 年的 byd 子集
        # 2) idx = sub['chg_pct'].idxmax() 找到最大涨幅日的行号
        # 3) 用 .iloc 取 ±10 范围
        # 4) 转 mplfinance 格式后画图



        """),

        md("""
        ## 第 6 段：课后练习 + 下节预告

        ### 📝 `exercises/ex02.py`
        1. 写函数 `find_doji(df, tol=0.005)`：找出"十字星"（open 与 close 差异 < tol × close）的日期列表
        2. 用 mplfinance 画比亚迪 2024 全年 K 线 + 20 日均线 + 成交量，保存为 PNG
        3. 统计比亚迪 2022-2024 每月"大阳线（涨幅>5%）"出现次数，画月度柱状图

        ### 🔮 下节 L03：量价关系 + 聚合
        成交量是 K 线之外的另一根主线。学 `resample` / `rolling` / 双轴图 + 换手率概念。
        """),

        md("""
        ## 第 7 段：Jupyter tip 🔧
        - `Shift + Tab`（在函数名后按）：弹窗显示文档
        - 连续按 `Tab` 两次：展开详细文档
        - `Esc + Z`：撤销单元格删除（救命数据的神技）
        - 命令行 `%matplotlib widget`：让图可交互缩放（需装 ipympl）
        """),
    ]
    write_nb(cells, "02_kline_dataframe.ipynb")


def build_ex02() -> None:
    write_ex("ex02.py", """
        \"\"\"L02 课后练习：K 线读图与 DataFrame 索引。\"\"\"
        from __future__ import annotations
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

        import pandas as pd
        import matplotlib.pyplot as plt
        import mplfinance as mpf
        import _style
        from _data import get_stock_data


        # ---------- 题 1 ----------
        def find_doji(df: pd.DataFrame, tol: float = 0.005) -> list[pd.Timestamp]:
            \"\"\"找出十字星日期。

            Args:
                df: OHLC DataFrame（列 date/open/high/low/close）
                tol: open 与 close 的相对差异阈值，默认 0.5%

            Returns:
                十字星日的日期列表（pd.Timestamp 列表），按日期升序
            \"\"\"
            # TODO: ~3 行




            return []


        # ---------- 题 2 ----------
        def plot_byd_2024(save_path: str = "data/byd_2024.png") -> str:
            \"\"\"画比亚迪 2024 全年 K 线 + 20 日均线 + 成交量。

            Returns:
                保存的文件路径
            \"\"\"
            # TODO: ~8 行
            # 提示：mpf.plot(df_2024, type='candle', mav=20, volume=True, savefig=save_path)





            return save_path


        # ---------- 题 3 ----------
        def monthly_big_up_count(df: pd.DataFrame, threshold: float = 0.05) -> pd.Series:
            \"\"\"统计每月"大阳线"出现次数。

            Args:
                df: OHLC DataFrame
                threshold: 涨幅阈值，默认 5%

            Returns:
                pd.Series，index 为月末日期（'M' 频率），值为该月大阳线次数
            \"\"\"
            # TODO: ~5 行
            # 提示：df.set_index('date') 后用 resample('M') 分组



            return pd.Series(dtype=int)


        def run_all() -> None:
            byd = get_stock_data("002594")

            print("=" * 60); print("题 1：十字星"); print("=" * 60)
            dojis = find_doji(byd)
            print(f"比亚迪 2022-2024 共 {len(dojis)} 个十字星")
            print("前 5 个日期：", [d.date() for d in dojis[:5]])

            print(); print("=" * 60); print("题 2：2024 K 线图"); print("=" * 60)
            path = plot_byd_2024()
            print(f"已保存: {path}")

            print(); print("=" * 60); print("题 3：月度大阳线次数"); print("=" * 60)
            print(monthly_big_up_count(byd).tail(12))


        if __name__ == "__main__":
            run_all()
    """)


# ============================================================
# L03 量价关系 + 聚合
# ============================================================
def build_l03() -> None:
    cells = [
        md("""
        # L03 · 量价关系 + 聚合

        **预计时长**：60 min | **难度**：⭐⭐ | **前置**：L02

        ## 本节目标
        1. 理解成交量、量价八法则、换手率
        2. matplotlib 双轴图（收盘价 + 成交量）
        3. `resample()` 按周/月聚合；`rolling()` 滚动均线
        4. 处理停牌日 NaN（fillna / interpolate）
        """),

        md("""
        ## 第 1 段：金融概念

        ### 成交量
        - 单位：**股数**（不是金额）。比亚迪 1 亿成交量 = 当天买卖了 1 亿股
        - 成交额 = volume × 平均价，akshare 默认不返回，自己算
        - 高成交量代表"分歧大"（有人大量买也有人大量卖）

        ### 量价八法则（核心 4 条）
        | 量价关系 | 含义 |
       ---------|------|
        | 量增价涨 | 健康上升，可持续 |
        | 量缩价涨 | 上升乏力，警惕 |
        | 量增价跌 | 抛压重，可能继续跌 |
        | 量缩价跌 | 抛压减弱，可能见底 |

        ### 换手率
        换手率 = 当日成交量 / 流通股本 × 100%
        - < 1%：低换手，盘面冷清
        - 1-5%：正常
        - 5-10%：活跃
        - > 10%：高度活跃（往往是热点题材或大单进出）
        - > 30%：极端（次新股、跌停封板出货常见）

        akshare 不直接给流通股本，要单独拉 `stock_individual_info_em`，本节略。
        """),

        code(common_imports()),
        code("byd = get_stock_data('002594')"),

        md("""
        ## 第 2 段：双轴图（价格 + 成交量）
        """),

        code("""
        df = byd.set_index('date').tail(120)

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True,
                                        gridspec_kw={'height_ratios': [3, 1]})
        ax1.plot(df.index, df['close'], color=_style.COLORS['price'], label='收盘价')
        ax1.set_ylabel('价格（元）')
        ax1.legend(loc='upper left')
        ax1.grid(alpha=0.3)

        ax2.bar(df.index, df['volume'], color=_style.COLORS['volume'], width=0.8)
        ax2.set_ylabel('成交量（股）')
        ax2.grid(alpha=0.3)

        plt.suptitle('比亚迪 价量双轴图（近 120 日）')
        plt.tight_layout()
        plt.show()
        """),

        md("""
        ## 第 3 段：`resample()` 按周/月聚合
        """),

        code("""
        # 必须 set_index('date') 才能 resample
        byd_idx = byd.set_index('date')

        # 周线：W = weekly；OHLC 用 ohlc() 聚合，volume 用 sum()
        weekly = byd_idx.resample('W').agg({
            'open': 'first', 'high': 'max', 'low': 'min',
            'close': 'last', 'volume': 'sum'
        })
        print(f"日线 {len(byd_idx)} 行 → 周线 {len(weekly)} 行")
        weekly.tail(5)
        """),

        code("""
        # 月线
        monthly = byd_idx.resample('M').agg({
            'open': 'first', 'high': 'max', 'low': 'min',
            'close': 'last', 'volume': 'sum'
        })
        monthly.tail(5)
        """),

        md("""
        ## 第 4 段：`rolling()` 滚动均线
        """),

        code("""
        byd_idx['ma5'] = byd_idx['close'].rolling(window=5).mean()
        byd_idx['ma20'] = byd_idx['close'].rolling(window=20).mean()
        byd_idx['ma60'] = byd_idx['close'].rolling(window=60).mean()

        df_plot = byd_idx.tail(180)
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(df_plot.index, df_plot['close'], label='收盘', color='black', alpha=0.6)
        ax.plot(df_plot.index, df_plot['ma5'],  label='MA5',  color=_style.COLORS['ma_short'])
        ax.plot(df_plot.index, df_plot['ma20'], label='MA20', color=_style.COLORS['ma_long'])
        ax.plot(df_plot.index, df_plot['ma60'], label='MA60', color='purple', alpha=0.6)
        ax.legend()
        ax.set_title('比亚迪 移动平均线')
        plt.show()
        """),

        md("""
        **新手陷阱**：rolling 的前 N-1 个值是 NaN（N = 窗口大小），plot 时 matplotlib 自动忽略 NaN。但做策略信号时要注意，这 N-1 天不能用。
        """),

        md("""
        ## 第 5 段：停牌日 NaN 处理

        A 股停牌日（公司公告、重大事件、临停）在 akshare 数据里有时表现为：
        - 完全没有这一天的行（最常见）
        - 行存在但 volume=0

        偶尔我们 resample 后会产生 NaN，要处理。
        """),

        code("""
        # 演示：人为造一段 NaN，练习 fillna / interpolate
        demo = byd_idx['close'].tail(30).copy()
        demo.iloc[10:13] = np.nan  # 模拟 3 天停牌

        fig, axes = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
        demo.plot(ax=axes[0], title='原始（含 NaN）', color='gray')
        demo.ffill().plot(ax=axes[1], title='ffill（用前一日填充）', color='blue')
        demo.interpolate().plot(ax=axes[2], title='interpolate（线性插值）', color='red')
        plt.tight_layout(); plt.show()
        """),

        md("""
        **何时用哪个？**
        - `fillna(0)`：成交量 0 是真实的（停牌没成交），用这个
        - `.ffill()`（forward fill）：价格停牌期间"沿用前一日"，回测常用
        - `interpolate()`：图形平滑用，**回测不能用**（会有未来函数嫌疑）
        - `dropna()`：直接删掉，适合"不关心这段"的统计分析
        """),

        md("""
        ## 第 6 段：随堂小练

        ### 小练：画"收盘价 + 20 日成交量均线"双轴图
        """),

        code("""
        # TODO: 你的代码（约 8 行）
        # 1) 算出 byd 的 volume_ma20
        # 2) 取最近 180 天
        # 3) 左轴画 close（蓝）、右轴画 volume + volume_ma20（橙/绿）
        # 提示：ax2 = ax1.twinx() 共享 x 轴



        """),

        md("""
        ## 第 7 段：课后练习 + 下节预告

        ### 📝 `exercises/ex03.py`
        1. 写 `monthly_stats(df)` 返回每月（open first / high max / low min / close last / volume sum / 涨跌幅 %）的 DataFrame
        2. 写 `rolling_sharpe(df, window=20)` 简单版夏普（每日收益 mean / std × sqrt(252)）的滚动序列
        3. 对比比亚迪 2024 年 MA20 上穿 MA60（金叉）与下穿（死叉）的次数，标出每次日期

        ### 🔮 下节 L04：数据清洗 + 复权 + 多股对齐
        本节最硬核（75-90 min）。你将理解为什么"不复权" K 线会有假跳空、为什么多股对比必须先对齐日期。
        """),

        md("""
        ## 第 8 段：Jupyter tip 🔧
        - `!pip list | grep pandas`：在 notebook 内跑 shell 命令（! 开头）
        - `%load` 一行魔法：把外部文件加载进 cell，例 `%load learning/phase1_foundation/_data.py`
        - `ax.xaxis.set_major_formatter()`：格式化日期轴，避免"2022-01-04 00:00:00" 这种丑陋显示
        """),
    ]
    write_nb(cells, "03_volume_aggregation.ipynb")


def build_ex03() -> None:
    write_ex("ex03.py", """
        \"\"\"L03 课后练习：量价关系与聚合。\"\"\"
        from __future__ import annotations
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

        import numpy as np
        import pandas as pd
        from _data import get_stock_data


        def monthly_stats(df: pd.DataFrame) -> pd.DataFrame:
            \"\"\"月度 OHLCV + 涨跌幅。

            Returns:
                DataFrame index=月末日期，列 open/high/low/close/volume/chg_pct
            \"\"\"
            # TODO: ~8 行





            return pd.DataFrame()


        def rolling_sharpe(df: pd.DataFrame, window: int = 20) -> pd.Series:
            \"\"\"滚动夏普比率（简化版，无风险利率=0）。

            公式：每日收益的 rolling mean / rolling std × sqrt(252)
            \"\"\"
            # TODO: ~5 行




            return pd.Series(dtype=float)


        def find_crossings(df: pd.DataFrame, short: int = 20, long: int = 60) -> dict:
            \"\"\"找金叉/死叉日期。

            Returns:
                {'golden': [pd.Timestamp...], 'death': [pd.Timestamp...]}
                golden = ma_short 从下方上穿 ma_long
                death  = ma_short 从上方下穿 ma_long
            \"\"\"
            # TODO: ~8 行
            # 提示：
            # ma_short = df['close'].rolling(short).mean()
            # ma_long  = df['close'].rolling(long).mean()
            # diff = (ma_short - ma_long).shift(1)  # 前一日差
            # diff_today = ma_short - ma_long
            # 金叉：diff < 0 且 diff_today > 0





            return {"golden": [], "death": []}


        def run_all() -> None:
            byd = get_stock_data('002594')

            print("=" * 60); print("题 1：月度统计"); print("=" * 60)
            print(monthly_stats(byd).tail(6))

            print(); print("=" * 60); print("题 2：滚动夏普（最后 5 个值）"); print("=" * 60)
            print(rolling_sharpe(byd).tail())

            print(); print("=" * 60); print("题 3：金叉死叉"); print("=" * 60)
            c = find_crossings(byd)
            print(f"比亚迪 2022-2024：金叉 {len(c['golden'])} 次，死叉 {len(c['death'])} 次")
            print("金叉日期：", [d.date() for d in c['golden'][:5]])


        if __name__ == "__main__":
            run_all()
    """)


# ============================================================
# L04 数据清洗 + 复权 + 多股对齐（最重）
# ============================================================
def build_l04() -> None:
    cells = [
        md("""
        # L04 · 数据清洗 + 复权 + 多股对齐

        **预计时长**：75–90 min | **难度**：⭐⭐⭐⭐ | **前置**：L03

        ## 本节目标
        1. 理解除权除息（送股 / 转股 / 分红）对 K 线的影响
        2. 区分前复权（qfq）/ 后复权（hfq）/ 不复权（""）
        3. 多股数据对齐：`pd.concat` / `reindex` / 交易日历
        4. 写出能复用的 panel 数据生成函数，缓存到 parquet 供 L05+ 使用

        > ⚠️ 这是 Phase 1 最硬核的一节。L05/L06/L10 全部依赖本节产出的对齐数据。
        """),

        md("""
        ## 第 1 段：金融概念

        ### 除权除息（简称"除权"）
        公司分红送股那天，股价会**人为下调**。例：
        - 比亚迪分红 10 派 10 元（每股分 1 元）
        - 股权登记日收盘价 250 元
        - 除权日开盘价自动变成 249 元（250 - 1）

        如果你用**不复权**数据算收益率，除权日会显示"-0.4%"，但股东实际没亏（收到 1 元现金）。

        ### 前复权 vs 后复权 vs 不复权
        | 类型 | akshare 参数 | 特征 | 用途 |
        |------|-------------|------|------|
        | 不复权 | `adjust=""` | 真实成交价，有跳空 | 看"当时真实价格" |
        | 前复权 | `adjust="qfq"` | 以**最新价**为基准，往历史扣减 | 量化**最常用**，看历史涨跌"平滑" |
        | 后复权 | `adjust="hfq"` | 以**最早价**为基准，往后累加 | 长期持有收益率计算 |

        **新手陷阱**：所有量化策略回测都用 **qfq**，否则除权日会触发虚假信号。
        """),

        code(common_imports()),

        md("""
        ## 第 2 段：用比亚迪实测复权差异

        同时拉三份不同 adjust 的比亚迪数据，看除权日的跳空差异。
        """),

        code("""
        # 拉三种复权方式
        byd_raw  = get_stock_data("002594", adjust="",   force_refresh=False)
        byd_qfq  = get_stock_data("002594", adjust="qfq", force_refresh=False)
        byd_hfq  = get_stock_data("002594", adjust="hfq", force_refresh=False)

        # 找一个明显的除权日：不复权当日 close 与前一日 close 差距大，
        # 但前复权差距小
        raw_chg = byd_raw['close'].pct_change()
        # 涨幅 < -5% 但不是跌停（A股有跌停规则）
        candidates = byd_raw[(raw_chg < -0.05) & (raw_chg > -0.11)]
        print(f"找到疑似除权日 {len(candidates)} 个，第一个：")
        print(candidates[['date', 'close']].head(1))
        """),

        code("""
        # 看那个日期三种复权方式的对比
        if len(candidates) > 0:
            ex_date = candidates['date'].iloc[0]
            print(f"除权日 {ex_date.date()} 三种复权对比：")
            print(f"  不复权 close: {byd_raw[byd_raw['date']==ex_date]['close'].iloc[0]:.2f}")
            print(f"  前复权 close: {byd_qfq[byd_qfq['date']==ex_date]['close'].iloc[0]:.2f}")
            print(f"  后复权 close: {byd_hfq[byd_hfq['date']==ex_date]['close'].iloc[0]:.2f}")
        """),

        md("""
        ## 第 3 段：多股纵向合并 `pd.concat`

        把三只股票的日线**纵向**堆起来（行变多），加 code 列区分。
        """),

        code("""
        stocks = [("002594", "比亚迪"), ("002602", "世纪华通"), ("002624", "完美世界")]
        frames = []
        for code, name in stocks:
            df = get_stock_data(code)
            df = df.copy()
            df['code'] = code
            df['name'] = name
            frames.append(df)

        long_df = pd.concat(frames, ignore_index=True)
        print(f"三股纵向合并：{len(long_df)} 行 × {len(long_df.columns)} 列")
        long_df.head()
        """),

        md("""
        ## 第 4 段：多股横向对齐 `pivot` + `reindex`

        把 close 列**横向**铺开，每只股票一列，日期为 index。
        **关键**：日期必须对齐（停牌日要补齐）。
        """),

        code("""
        # pivot 成 wide format
        wide_close = long_df.pivot(index='date', columns='code', values='close')
        print(f"对齐前 shape: {wide_close.shape}")
        print(f"NaN 总数（说明有日期错位）: {wide_close.isna().sum().sum()}")
        wide_close.head()
        """),

        code("""
        # 用交易日历 reindex（用三股的并集作为完整日历）
        full_dates = wide_close.index  # pd.concat 已隐式对齐
        # 如果某只股票某天缺数据（停牌），用 ffill 填充
        wide_close_filled = wide_close.sort_index().ffill()
        print(f"填充后 NaN 总数: {wide_close_filled.isna().sum().sum()}")
        wide_close_filled.head()
        """),

        md("""
        ## 第 5 段：保存 panel 数据到 parquet

        把对齐好的 wide format 存起来，L05+ 直接读用。
        """),

        code("""
        from pathlib import Path
        panel_path = Path("data/panel_three_stocks.parquet")
        wide_close_filled.to_parquet(panel_path)
        print(f"已保存：{panel_path} ({panel_path.stat().st_size // 1024} KB)")

        # 验证读回
        read_back = pd.read_parquet(panel_path)
        print(f"读回 shape: {read_back.shape}")
        read_back.head()
        """),

        md("""
        ## 第 6 段：随堂小练

        ### 小练：5 股对齐 panel
        拉取 5 只代码（比亚迪、世纪华通、完美世界、贵州茅台 600519、宁德时代 300750），
        对齐成 wide format，存为 `data/panel_five_stocks.parquet`。
        """),

        code("""
        # TODO: 你的代码（约 10 行）




        """),

        md("""
        ## 第 7 段：课后练习 + 下节预告

        ### 📝 `exercises/ex04.py`
        1. 写 `build_panel(codes: list[str], adjust='qfq') -> pd.DataFrame`，输入代码列表，返回对齐后的 wide close DataFrame
        2. 写 `detect_suspicious_gap(df, threshold=0.15) -> list[tuple]`，检测不复权数据里"单日跌幅 > threshold 但不是跌停"的可疑除权日（return [(date, code, pct_change), ...]）
        3. 对 5 股 panel 计算两两相关矩阵，用 seaborn 画热力图

        ### 🔮 下节 L05：收益率 + 涨停识别
        本节的对齐 panel 是 L05 的输入。下节学 `pct_change / shift / diff / cumprod`，并真正识别"一字涨停"。
        """),

        md("""
        ## 第 8 段：Jupyter tip 🔧
        - `%time wide_close.corr()`：测整段代码（多行用 `%%time`）
        - `df.info(memory_usage='deep')`：看真实内存占用
        - `pd.set_option('display.max_rows', 100)`：调整显示行数
        - 处理大表前先 `df = df.convert_dtypes()` 或手动 `astype('float32')` 降精度省内存
        """),
    ]
    write_nb(cells, "04_data_cleaning_adjust_align.ipynb")


def build_ex04() -> None:
    write_ex("ex04.py", """
        \"\"\"L04 课后练习：数据清洗、复权与多股对齐。\"\"\"
        from __future__ import annotations
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

        import numpy as np
        import pandas as pd
        import seaborn as sns
        import matplotlib.pyplot as plt
        from _data import get_stock_data


        def build_panel(codes: list[str], adjust: str = "qfq") -> pd.DataFrame:
            \"\"\"构建对齐的 wide-format close DataFrame。

            Args:
                codes: 股票代码列表，如 ['002594', '002602']
                adjust: 'qfq' / 'hfq' / ''

            Returns:
                DataFrame index=date, columns=code, values=close
                停牌日 ffill 填充；首日 NaN 不填充
            \"\"\"
            # TODO: ~8 行




            return pd.DataFrame()


        def detect_suspicious_gap(codes: list[str], threshold: float = 0.15) -> list[tuple]:
            \"\"\"用不复权数据检测疑似除权日。

            条件：当日 pct_change < -threshold 且 > -0.11（排除真实跌停）

            Returns:
                [(date, code, pct_change), ...] 按日期升序
            \"\"\"
            # TODO: ~10 行






            return []


        def corr_heatmap(codes: list[str]) -> pd.DataFrame:
            \"\"\"画 5 股相关矩阵热力图，返回相关矩阵。\"\"\"
            # TODO: ~5 行





            return pd.DataFrame()


        def run_all() -> None:
            codes = ["002594", "002602", "002624", "600519", "300750"]

            print("=" * 60); print("题 1：5 股对齐 panel"); print("=" * 60)
            panel = build_panel(codes)
            print(f"shape: {panel.shape}")
            print(panel.tail(3))

            print(); print("=" * 60); print("题 2：可疑除权日"); print("=" * 60)
            gaps = detect_suspicious_gap(codes)
            print(f"找到 {len(gaps)} 个可疑除权日，前 5 个：")
            for d, c, p in gaps[:5]:
                print(f"  {d.date()} {c} {p*100:.2f}%")

            print(); print("=" * 60); print("题 3：相关矩阵"); print("=" * 60)
            print(corr_heatmap(codes))


        if __name__ == "__main__":
            run_all()
    """)


# ============================================================
# L05 收益率 + 涨停识别
# ============================================================
def build_l05() -> None:
    cells = [
        md("""
        # L05 · 收益率 + 涨停识别

        **预计时长**：60 min | **难度**：⭐⭐⭐ | **前置**：L04

        ## 本节目标
        1. 彻底搞清 `shift / diff / pct_change` 三者关系
        2. 日收益率、累计收益率、年化收益率（252 交易日/年）
        3. 代码识别涨停日（含一字涨停）
        4. 复利 vs 算术累加的区别
        """),

        md("""
        ## 第 1 段：金融概念

        ### 三种"收益率"
        | 类型 | 公式 | 用途 |
        |------|------|------|
        | 单日收益率 | (close - prev_close) / prev_close | 日度分析 |
        | 累计收益率 | (final_close - initial_close) / initial_close | 简单区间统计 |
        | 复利累计 | ∏(1 + r_t) - 1 | **正确**做法 |
        | 年化收益率 | (1 + 累计) ** (252/N) - 1 | 跨期比较 |

        ### 复利 vs 算术累加（新手陷阱）
        - ❌ 累计 = sum(日收益率) — 错的！会低估
        - ✅ 累计 = prod(1 + 日收益率) - 1 — 正确

        ### 涨停识别（L01 深化版）
        - **普通涨停**：chg_pct >= 9.9%（主板）
        - **一字涨停**：open == high == low == close 且 chg_pct >= 9.9%（最强势）
        - **秒板**：开盘即涨停，但日内可能有波动（数据上看就是 open == close）

        一字涨停是**最强信号**，意味着开盘瞬间就封板，没人能买到（除非早上挂单）。
        """),

        code(common_imports()),

        code("""
        byd = get_stock_data('002594')
        byd = byd.set_index('date')
        byd.head(3)
        """),

        md("""
        ## 第 2 段：`shift / diff / pct_change` 三剑客
        """),

        code("""
        # shift: 整列平移
        byd['prev_close'] = byd['close'].shift(1)        # 前一日
        byd['next_close'] = byd['close'].shift(-1)       # 后一日（小心未来函数！）

        # diff: 一阶差分（当前 - 前一）
        byd['abs_change'] = byd['close'].diff(1)         # close - prev_close

        # pct_change: 百分比变化
        byd['ret'] = byd['close'].pct_change(1)          # = (close - prev_close) / prev_close

        byd[['close', 'prev_close', 'abs_change', 'ret']].head()
        """),

        code("""
        # 三者关系：
        # diff(1)   = close - shift(1)
        # pct_change(1) = diff(1) / shift(1)
        # pct_change 是最常用的，因为收益率本身是无量纲的（百分比）
        """),

        md("""
        ## 第 3 段：累计收益率 `cumprod`
        """),

        code("""
        # 复利累计收益 = ∏(1 + r_t) - 1
        byd['cum_ret'] = (1 + byd['ret']).cumprod() - 1

        # 对比算术累加（错的！）
        byd['cum_ret_wrong'] = byd['ret'].cumsum()

        fig, ax = plt.subplots(figsize=(12, 5))
        byd['cum_ret'].plot(ax=ax, label='复利（正确）', linewidth=2)
        byd['cum_ret_wrong'].plot(ax=ax, label='算术累加（错）', linestyle='--')
        ax.axhline(0, color='black', alpha=0.3)
        ax.legend()
        ax.set_title('比亚迪 累计收益率：复利 vs 算术累加')
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f'{x*100:.0f}%'))
        plt.show()
        """),

        md("""
        ## 第 4 段：年化收益率（252 交易日/年）
        """),

        code("""
        def annualized_return(df: pd.DataFrame, col: str = 'close') -> float:
            \"\"\"计算年化收益率。

            公式：(final/initial) ** (252/N) - 1
            \"\"\"
            n_days = len(df)
            initial = df[col].iloc[0]
            final = df[col].iloc[-1]
            return (final / initial) ** (252 / n_days) - 1

        for code, name in [("002594", "比亚迪"), ("002602", "世纪华通"), ("002624", "完美世界")]:
            df = get_stock_data(code).set_index('date')
            ann = annualized_return(df)
            cum = (df['close'].iloc[-1] / df['close'].iloc[0]) - 1
            print(f"{name:<8} {code}  累计 {cum*100:>7.2f}%  年化 {ann*100:>7.2f}%")
        """),

        md("""
        ## 第 5 段：代码识别涨停日（含一字板）
        """),

        code("""
        def find_limit_ups(df: pd.DataFrame, threshold: float = 0.099) -> pd.DataFrame:
            \"\"\"识别涨停日 + 一字板。

            ⚠️ 严格涨停识别应用「不复权」数据（raw）。本函数用 qfq 数据，
            除权日可能轻微误判（qfq 会把除权日"缺口"补回去，导致 chg_pct
            虚高）。教学场景可接受，实战回测请传 adjust="" 的数据。

            Returns:
                DataFrame index=date，列 [close, prev_close, chg_pct, is_yizi]
                is_yizi=True 表示一字涨停（开盘=最高=最低=收盘）
            \"\"\"
            d = df.copy()
            d['prev_close'] = d['close'].shift(1)
            d['chg_pct'] = d['close'] / d['prev_close'] - 1
            limit_up = d[d['chg_pct'] >= threshold].copy()
            # 一字板判定：4 价几乎相等
            eps = 0.001  # 千分之一容差
            limit_up['is_yizi'] = (
                (abs(limit_up['open'] - limit_up['high']) < eps * limit_up['close']) &
                (abs(limit_up['high'] - limit_up['low']) < eps * limit_up['close']) &
                (abs(limit_up['low'] - limit_up['close']) < eps * limit_up['close'])
            )
            return limit_up

        byd_lu = find_limit_ups(get_stock_data('002594').set_index('date'))
        print(f"比亚迪涨停 {len(byd_lu)} 次，其中一字板 {byd_lu['is_yizi'].sum()} 次")
        byd_lu[byd_lu['is_yizi']].head()
        """),

        md("""
        ## 第 6 段：随堂小练

        ### 小练：三股累计收益率排名
        """),

        code("""
        # TODO: 你的代码（约 6 行）
        # 对 002594 / 002602 / 002624 三只股票
        # 用 (1+ret).cumprod()-1 算 2024 全年累计收益率
        # 按收益从高到低排名打印



        """),

        md("""
        ## 第 7 段：小测（5 题）

        在 notebook 里直接答，答完告诉我答案：
        1. `shift(1)` 和 `shift(-1)` 哪个有"未来函数"风险？
        2. `pct_change()` 和 `diff() / shift(1)` 哪个返回值无量纲？
        3. 主板涨停阈值是 9.9% 还是 10%？为什么不是整数？
        4. 一字涨停的判定条件用 `open == high == low == close` 对吗？为什么实际代码要加 `eps`？
        5. 252 这个数字怎么来的？

        答完我给反馈。
        """),

        md("""
        ## 第 8 段：课后练习 + 下节预告

        ### 📝 `exercises/ex05.py`
        1. 写 `find_one_word_limit_ups(df, threshold=0.099, eps=0.001)` 返回一字涨停日列表
        2. 写 `annualized_return_with_costs(df, cost_bps=10)`：扣除每笔交易成本（L06 讲）后的年化
        3. 对三股计算 2022-2024 每年"涨停日数 + 年化收益率"，做一张 3×3 的透视表

        ### 🔮 下节 L06：统计基础 + 交易成本
        量化必备的"风险度量"：均值、方差、标准差、相关系数。同时讲清交易成本如何拖垮策略。
        """),

        md("""
        ## 第 9 段：Jupyter tip 🔧
        - `Series.clip(lower=-0.11, upper=0.11)`：把涨跌幅限制在 ±11%（防涨停日异常）
        - `pd.Timedelta(days=1)`：时间差，比手写 `86400` 秒清晰
        - `df.rolling(20).apply(my_func)`：自定义滚动函数（但慢，能用向量化就别用 apply）
        """),
    ]
    write_nb(cells, "05_returns_limit_identification.ipynb")


def build_ex05() -> None:
    write_ex("ex05.py", """
        \"\"\"L05 课后练习：收益率与涨停识别。\"\"\"
        from __future__ import annotations
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

        import numpy as np
        import pandas as pd
        from _data import get_stock_data


        def find_one_word_limit_ups(df: pd.DataFrame, threshold: float = 0.099,
                                     eps: float = 0.001) -> list[pd.Timestamp]:
            \"\"\"返回一字涨停日日期列表。

            一字板条件：
                - chg_pct >= threshold（涨幅达涨停）
                - |open - high| < eps * close
                - |high - low| < eps * close
                - |low - close| < eps * close
            \"\"\"
            # TODO: ~8 行






            return []


        def annualized_return_with_costs(df: pd.DataFrame, cost_bps: int = 10) -> float:
            \"\"\"扣交易成本后的年化收益率。

            cost_bps: 单边交易成本（佣金+印花税+滑点），单位万分之一（10 = 0.1%）
            假设：每月调仓 1 次（22 交易日），每次全仓切换。
            年成本 = 2 * cost_bps/10000 * 12  (买卖双向)
            \"\"\"
            # TODO: ~6 行




            return 0.0


        def yearly_limit_up_pivot(codes: list[tuple[str, str]]) -> pd.DataFrame:
            \"\"\"三股每年涨停日数 + 年化收益率。

            Args:
                codes: [(code, name), ...]

            Returns:
                DataFrame index=multiindex(code, year),
                columns=['limit_ups', 'annual_return']
            \"\"\"
            # TODO: ~12 行






            return pd.DataFrame()


        def run_all() -> None:
            print("=" * 60); print("题 1：一字涨停"); print("=" * 60)
            for code, name in [("002594", "比亚迪"), ("002602", "世纪华通"), ("002624", "完美世界")]:
                df = get_stock_data(code).set_index('date')
                yz = find_one_word_limit_ups(df)
                print(f"{name:<8} 一字涨停 {len(yz)} 次")

            print(); print("=" * 60); print("题 2：含成本年化"); print("=" * 60)
            for code, name in [("002594", "比亚迪"), ("002602", "世纪华通"), ("002624", "完美世界")]:
                df = get_stock_data(code).set_index('date')
                r = annualized_return_with_costs(df, cost_bps=15)
                print(f"{name:<8} 含成本年化: {r*100:>7.2f}%")

            print(); print("=" * 60); print("题 3：年度透视"); print("=" * 60)
            codes = [("002594", "比亚迪"), ("002602", "世纪华通"), ("002624", "完美世界")]
            print(yearly_limit_up_pivot(codes))


        if __name__ == "__main__":
            run_all()
    """)


# ============================================================
# L06 统计基础 + 交易成本
# ============================================================
def build_l06() -> None:
    cells = [
        md("""
        # L06 · 统计基础 + 交易成本

        **预计时长**：60 min | **难度**：⭐⭐⭐ | **前置**：L05

        ## 本节目标
        1. 均值 / 方差 / 标准差 / 相关系数 的金融含义
        2. A 股交易成本三件套：佣金 / 印花税 / 过户费
        3. 写一个 `apply_trading_cost` 函数，回测必备
        4. seaborn 相关矩阵热力图
        """),

        md("""
        ## 第 1 段：金融概念

        ### 基础统计的金融含义
        | 统计量 | 公式 | 金融含义 |
        |-------|------|---------|
        | 均值 μ | Σx / N | 平均日收益（"赚钱能力"） |
        | 方差 σ² | Σ(x-μ)² / N | 收益波动幅度 |
        | 标准差 σ | √方差 | **风险**的量化 |
        | 相关系数 ρ | cov(x,y) / (σx·σy) | 两资产同向度（-1 到 +1） |
        | 协方差 | E[(x-μx)(y-μy)] | 相关系数的分子 |

        ### 关键概念：风险与收益的权衡
        - **夏普比率 = (μ - rf) / σ**：单位风险的超额回报（rf = 无风险利率，A 股常用 3%）
        - 夏普 > 1：不错；> 2：优秀；> 3：可疑（要排查未来函数）

        ### A 股交易成本三件套（2026 现行）
        | 项目 | 费率 | 收费方 | 双向？ |
        |------|------|-------|--------|
        | 佣金 | 行业平均 **万 2.1**（券商可谈到 **万 1 免 5**） | 券商 | 双向 |
        | 印花税 | **卖**方 0.05%（2023.8.28 起） | 国家 | 仅卖出 |
        | 过户费 | 0.001%（沪深统一，2022.4.29 起） | 中登公司 | 双向 |
        | ~~最低佣金 5 元~~ | 部分券商已"免 5"（不足 5 元按实际收） | 券商 | 双向 |

        ### 滑点（slippage）
        你下单时看到的价格 ≠ 实际成交价。原因：盘口变化、流动性不足。
        - 大盘股：滑点极小（< 0.05%）
        - 小盘股：滑点可能 0.1–0.3%
        - 涨停封板：你可能根本买不到（"一字板"）

        回测一般保守按 **0.1% 滑点** 额外扣除。

        ### 单边 vs 双边总成本（关键数字，以万 2.5 佣金为保守估计）
        - **买入单边**：佣金 0.025% + 过户费 0.001% + 滑点 0.1% = **约 0.13%**
        - **卖出单边**：上面 + 印花税 0.05% = **约 0.18%**（卖出多一道税）
        - **双边来回**：0.13% + 0.18% = **约 0.31%**
        - 高频策略每多 1 次调仓，先扣 0.31% 再算收益。**这是策略亏钱的常见原因**。
        - 若你的券商给到"万 1 免 5"（2026 主流），单边佣金可降到 0.01%，双边总成本降到 **约 0.25%**。
        - `apply_trading_cost` 默认用万 2.5 + 最低 5 元（保守），未实现"免 5"实际。
        """),

        code(common_imports()),

        md("""
        ## 第 2 段：基础统计量计算
        """),

        code("""
        byd = get_stock_data('002594').set_index('date')
        rets = byd['close'].pct_change().dropna()

        print("比亚迪日收益率基础统计：")
        print(f"  均值（日均）:   {rets.mean()*100:>7.3f}%")
        print(f"  标准差（日波动）: {rets.std()*100:>7.3f}%")
        print(f"  方差:           {rets.var()*1e6:>7.1f}（×1e6）")
        print(f"  年化均值:       {rets.mean()*252*100:>7.2f}%")
        print(f"  年化波动:       {rets.std()*np.sqrt(252)*100:>7.2f}%")
        # 2026 年中国 10 年期国债 ~1.75%，老教材常用 3% 偏高
        rf = 0.0175
        print(f"  夏普（rf={rf*100:.2f}%）:  {(rets.mean()*252 - rf) / (rets.std()*np.sqrt(252)):>7.2f}")
        """),

        md("""
        ## 第 3 段：相关矩阵 + 热力图
        """),

        code("""
        import seaborn as sns

        # 三股对齐的收益率（用 L04 的 panel）
        from pathlib import Path
        panel_path = Path("data/panel_three_stocks.parquet")
        if panel_path.exists():
            wide = pd.read_parquet(panel_path)
        else:
            # 兜底：现场对齐
            frames = {c: get_stock_data(c).set_index('date')['close'] for c in ['002594','002602','002624']}
            wide = pd.DataFrame(frames).sort_index().ffill()

        rets_wide = wide.pct_change().dropna()
        corr = rets_wide.corr()
        print("相关矩阵：")
        print(corr.round(3))
        """),

        code("""
        fig, ax = plt.subplots(figsize=(5, 4))
        sns.heatmap(corr, annot=True, cmap='RdYlGn_r', vmin=-1, vmax=1,
                    square=True, ax=ax, fmt='.2f')
        ax.set_title("三股日收益率相关矩阵")
        plt.tight_layout(); plt.show()
        """),

        md("""
        **解读**：
        - 相关系数接近 1：两股高度同向（行业相近、大盘股）
        - 接近 0：相互独立
        - 接近 -1：反向（很少见，可能套利对）
        - 三只消费/游戏股彼此相关系数通常 0.4–0.7
        """),

        md("""
        ## 第 4 段：交易成本函数
        """),

        code("""
        def apply_trading_cost(turnover_ratio: float, capital: float,
                               commission_bps: float = 2.5,
                               stamp_duty_bps: float = 5,
                               transfer_fee_bps: float = 0.1,
                               slippage_bps: float = 10) -> float:
            \"\"\"计算单期交易成本（人民币）。

            Args:
                turnover_ratio: 换手率（0~1 之间，1 = 全仓切换）
                capital: 当期总资金
                *_bps: 各项费率，单位万分之一（bps = basis points）

            Returns:
                本期交易成本（元）
            \"\"\"
            traded_value = capital * turnover_ratio
            # 买入：佣金 + 过户费 + 滑点
            # 卖出：佣金 + 过户费 + 印花税 + 滑点
            # 双边总费率（万分之）
            total_bps = (commission_bps + transfer_fee_bps + slippage_bps) * 2 \\
                        + stamp_duty_bps
            return traded_value * total_bps / 10000

        # 示例：10 万资金，本期换手 50%（半仓切换）
        cost = apply_trading_cost(turnover_ratio=0.5, capital=100_000)
        print(f"10 万资金半仓切换成本: {cost:.2f} 元 ({cost/100_000*100:.3f}%)")
        """),

        md("""
        ## 第 5 段：含成本 vs 不含成本对比
        """),

        code("""
        # 简单策略：每月调仓一次（22 交易日），全仓持有比亚迪
        byd = get_stock_data('002594').set_index('date')
        byd['ret'] = byd['close'].pct_change()
        byd['cum_no_cost'] = (1 + byd['ret']).cumprod()

        # 每月扣一次成本
        capital = 1.0
        capitals = []
        for i, r in enumerate(byd['ret']):
            capital *= (1 + r)
            if i > 0 and i % 22 == 0:  # 每月
                cost = apply_trading_cost(turnover_ratio=1.0, capital=capital)
                capital -= cost
            capitals.append(capital)
        byd['cum_with_cost'] = capitals

        fig, ax = plt.subplots(figsize=(12, 5))
        byd['cum_no_cost'].plot(ax=ax, label='不含成本', linewidth=2)
        byd['cum_with_cost'].plot(ax=ax, label='含成本', linestyle='--')
        ax.legend()
        ax.set_title('比亚迪 月调仓：成本对净值曲线的影响')
        plt.show()

        final_no = byd['cum_no_cost'].iloc[-1]
        final_yes = byd['cum_with_cost'].iloc[-1]
        print(f"终值 不含成本: {final_no:.3f}  含成本: {final_yes:.3f}  成本吃掉: {(final_no-final_yes)/final_no*100:.2f}%")
        """),

        md("""
        ## 第 6 段：随堂小练

        ### 小练：模拟一次完整买卖扣费
        100 万资金，100 元买入 5000 股比亚迪，250 元全部卖出。算实际盈利和收益率（含所有成本）。
        """),

        code("""
        # TODO: 你的代码（约 8 行）
        # 1) 买入：100 * 5000 = 50万 成交额，扣 commission + transfer + slippage
        # 2) 卖出：250 * 5000 = 125万 成交额，扣 commission + transfer + stamp + slippage
        # 3) 净利 = 卖出所得 - 买入花费 - 总成本
        # 4) 对比"理想"收益（不含成本）和"实际"收益



        """),

        md("""
        ## 第 7 段：课后练习 + 下节预告

        ### 📝 `exercises/ex06.py`
        1. 写 `risk_metrics(df, rf=0.03)` 返回 dict 含 mean/std/sharpe/max_drawdown
        2. 写 `backtest_with_cost(df, signal, cost_bps=15)` 返回含成本的净值曲线
        3. 对三股 + 上证指数（000001）算相关矩阵，找出"和比亚迪相关性最低的"

        ### 🔮 下节 L07：技术指标入门
        MA / EMA / MACD / RSI 原理与实现，并用 `np.where` 生成信号——为 Phase 2 的策略回测铺路。
        """),

        md("""
        ## 第 8 段：Jupyter tip 🔧
        - `np.log(1 + rets)`：对数收益率，加性变可加，统计建模常用
        - `pd.Timedelta`、`pd.Timestamp`：比 datetime 模块好用
        - `np.sqrt(252)`：年化因子。252 是美股 ADR；A 股实际 244 左右，但学界惯例 252
        - `ax.yaxis.set_major_formatter(plt.FuncFormatter(...))`：自定义坐标轴格式（如百分号）
        """),
    ]
    write_nb(cells, "06_statistics_trading_costs.ipynb")


def build_ex06() -> None:
    write_ex("ex06.py", """
        \"\"\"L06 课后练习：统计基础与交易成本。\"\"\"
        from __future__ import annotations
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

        import numpy as np
        import pandas as pd
        from _data import get_stock_data


        def risk_metrics(df: pd.DataFrame, rf: float = 0.03) -> dict:
            \"\"\"计算风险指标。

            Args:
                df: OHLC DataFrame
                rf: 无风险年利率，默认 3%

            Returns:
                {
                    'mean_daily': 日均收益率
                    'std_daily': 日波动
                    'mean_annual': 年化收益
                    'std_annual': 年化波动
                    'sharpe': 夏普比率
                    'max_drawdown': 最大回撤（负数，如 -0.35）
                }
            \"\"\"
            # TODO: ~10 行






            return {}


        def backtest_with_cost(df: pd.DataFrame, signal: pd.Series,
                               cost_bps: int = 15) -> pd.Series:
            \"\"\"含交易成本的策略回测。

            Args:
                df: OHLC DataFrame
                signal: 目标仓位 Series（0~1），index 与 df 对齐
                cost_bps: 每次调仓的总成本（双边，单位万分之一），默认 15

            Returns:
                净值 Series（从 1.0 开始）
            \"\"\"
            # TODO: ~8 行
            # 提示：
            # rets = df['close'].pct_change()
            # position_change = signal.diff().abs().fillna(signal.iloc[0])
            # cost_today = position_change * cost_bps / 10000
            # nav = ((1 + rets * signal.shift(1) - cost_today).cumprod())





            return pd.Series(dtype=float)


        def least_correlated_with(target_code: str = "002594",
                                  candidates: list[str] = None) -> tuple[str, float]:
            \"\"\"找出和 target_code 相关性最低的股票。

            Returns:
                (code, correlation) 二元组
            \"\"\"
            # TODO: ~8 行
            if candidates is None:
                candidates = ["002602", "002624", "600519", "300750"]




            return ("", 0.0)


        def run_all() -> None:
            print("=" * 60); print("题 1：风险指标"); print("=" * 60)
            byd = get_stock_data('002594').set_index('date')
            m = risk_metrics(byd)
            for k, v in m.items():
                print(f"  {k}: {v:.4f}")

            print(); print("=" * 60); print("题 2：含成本回测"); print("=" * 60)
            # 简单信号：MA20 上方持 1，下方持 0
            ma20 = byd['close'].rolling(20).mean()
            signal = (byd['close'] > ma20).astype(int)
            nav = backtest_with_cost(byd.reset_index(), signal.reset_index(drop=True))
            print(f"含成本净值: {nav.iloc[-1]:.3f}  总收益 {(nav.iloc[-1]-1)*100:.2f}%")

            print(); print("=" * 60); print("题 3：最低相关"); print("=" * 60)
            print(least_correlated_with())


        if __name__ == "__main__":
            run_all()
    """)


# ============================================================
# L07 技术指标入门
# ============================================================
def build_l07() -> None:
    cells = [
        md("""
        # L07 · 技术指标入门

        **预计时长**：60 min | **难度**：⭐⭐⭐ | **前置**：L06

        ## 本节目标
        1. 理解趋势类（MA/EMA）与震荡类（MACD/RSI）指标的本质
        2. 用 pandas 实现 MA / EMA / MACD / RSI
        3. `np.where` 生成交易信号
        4. 对比 qtrader.strategies.DualMAStrategy 的实现
        """),

        md("""
        ## 第 1 段：金融概念

        ### 趋势类 vs 震荡类
        | 类型 | 代表 | 适合行情 | 缺点 |
        |------|------|---------|------|
        | 趋势类 | MA / EMA / MACD | 单边行情 | 震荡市频繁假信号 |
        | 震荡类 | RSI / KDJ | 震荡行情 | 单边行情"钝化"失效 |

        ### MA（简单移动平均）
        MA_N = 过去 N 日收盘价的算术平均。**等权重**。
        - MA5 / MA20 / MA60：短期 / 中期 / 长期
        - 金叉（短上穿长）：买入信号
        - 死叉（短下穿长）：卖出信号

        ### EMA（指数移动平均）
        EMA_N = 越近的日子权重越大（指数衰减）。
        - 比反应迟缓的 MA 更敏感
        - 公式：EMA_today = α × price + (1-α) × EMA_yesterday，α = 2/(N+1)

        ### MACD（Moving Average Convergence Divergence）
        - DIF = EMA12 - EMA26（"快线减慢线"）
        - DEA = EMA9(DIF)（DIF 的 9 日 EMA，"信号线"）
        - Histogram = 2 × (DIF - DEA)（柱状图，红绿）
        - 信号：DIF 上穿 DEA → 买；下穿 → 卖

        ### RSI（Relative Strength Index，相对强弱）
        RSI_N = 100 - 100/(1 + RS)，RS = N 日平均涨幅 / N 日平均跌幅
        - 取值 0-100
        - > 70：超买（可能要跌）
        - < 30：超卖（可能要涨）
        - N 常用 6 / 12 / 14
        """),

        code(common_imports()),
        code("byd = get_stock_data('002594').set_index('date')"),

        md("""
        ## 第 2 段：MA 与 EMA
        """),

        code("""
        # pandas 内置 rolling 实现MA
        byd['ma5']  = byd['close'].rolling(5).mean()
        byd['ma20'] = byd['close'].rolling(20).mean()

        # ewm 实现 EMA（adjust=False 表示用递推公式）
        byd['ema12'] = byd['close'].ewm(span=12, adjust=False).mean()
        byd['ema26'] = byd['close'].ewm(span=26, adjust=False).mean()

        df_plot = byd.tail(180)
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(df_plot.index, df_plot['close'], label='close', color='black', alpha=0.6)
        ax.plot(df_plot.index, df_plot['ma5'],   label='MA5',  color=_style.COLORS['ma_short'])
        ax.plot(df_plot.index, df_plot['ma20'],  label='MA20', color=_style.COLORS['ma_long'])
        ax.plot(df_plot.index, df_plot['ema12'], label='EMA12', linestyle='--')
        ax.legend()
        plt.show()
        """),

        md("""
        ## 第 3 段：MACD
        """),

        code("""
        byd['dif'] = byd['ema12'] - byd['ema26']
        byd['dea'] = byd['dif'].ewm(span=9, adjust=False).mean()
        byd['hist'] = 2 * (byd['dif'] - byd['dea'])

        df_plot = byd.tail(180)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True,
                                        gridspec_kw={'height_ratios': [2, 1]})
        ax1.plot(df_plot.index, df_plot['close'], color='black', alpha=0.6, label='close')
        ax1.plot(df_plot.index, df_plot['dif'], label='DIF', color='blue')
        ax1.plot(df_plot.index, df_plot['dea'], label='DEA', color='orange')
        ax1.legend()

        colors = ['red' if v > 0 else 'green' for v in df_plot['hist']]
        ax2.bar(df_plot.index, df_plot['hist'], color=colors, width=0.8)
        ax2.axhline(0, color='black', alpha=0.3)
        ax2.set_title('MACD Histogram')

        plt.tight_layout(); plt.show()
        """),

        md("""
        ## 第 4 段：RSI
        """),

        code("""
        def compute_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
            \"\"\"RSI 实现（SMA 简化版）。

            注意：通达信/同花顺默认用 Wilder's RSI（用 EMA-like 递推平滑），
            数值上与本函数略有差异。教学版用 SMA 已足够；实战对照行情软件
            时记得这个口径差。
            \"\"\"
            delta = prices.diff()
            gain = delta.where(delta > 0, 0).rolling(period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
            rs = gain / loss
            return 100 - 100 / (1 + rs)

        byd['rsi14'] = compute_rsi(byd['close'], 14)

        df_plot = byd.tail(180)
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 6), sharex=True,
                                        gridspec_kw={'height_ratios': [2, 1]})
        ax1.plot(df_plot.index, df_plot['close'], color='black')
        ax2.plot(df_plot.index, df_plot['rsi14'], color='purple')
        ax2.axhline(70, color='red', linestyle='--', alpha=0.5, label='超买 70')
        ax2.axhline(30, color='green', linestyle='--', alpha=0.5, label='超卖 30')
        ax2.set_ylim(0, 100); ax2.legend()
        plt.tight_layout(); plt.show()
        """),

        md("""
        ## 第 5 段：`np.where` 生成信号
        """),

        code("""
        # 双均线信号：MA5 > MA20 持仓 1，否则 0
        byd['signal'] = np.where(byd['ma5'] > byd['ma20'], 1, 0)
        # 关键：shift(1) 避免未来函数
        byd['signal_used'] = byd['signal'].shift(1).fillna(0)

        byd['strategy_ret'] = byd['signal_used'] * byd['close'].pct_change()
        byd['strategy_nav'] = (1 + byd['strategy_ret']).cumprod()
        byd['buy_hold_nav'] = byd['close'] / byd['close'].iloc[0]

        fig, ax = plt.subplots(figsize=(12, 5))
        byd['strategy_nav'].plot(ax=ax, label='MA 双均线策略')
        byd['buy_hold_nav'].plot(ax=ax, label='买入持有', alpha=0.6)
        ax.legend()
        ax.set_title('比亚迪 双均线 vs 买入持有')
        plt.show()

        # 胜率统计
        trade_rets = byd.loc[byd['signal_used'].diff() == 1, 'strategy_ret']
        print(f"开仓次数: {len(trade_rets)}, 平均持仓期收益: {trade_rets.sum()/max(len(trade_rets),1)*100:.2f}%")
        """),

        md("""
        ## 第 6 段：对比 qtrader 框架
        """),

        code("""
        # qtrader 已实现的 DualMA 策略（common_imports 已把 project root 加入 sys.path）
        from qtrader.strategies import DualMAStrategy
        from qtrader.engine import BacktestEngine

        df_qt = get_stock_data('002594')
        result = BacktestEngine().run(df_qt, DualMAStrategy(short=5, long=20))
        print(f"qtrader DualMA(5,20) 总收益: {result.metrics['total_return']*100:.2f}%")
        print(f"策略净值末值: {result.nav.iloc[-1]:.3f}")
        """),

        md("""
        看一下 `qtrader/strategies.py` 里 `DualMAStrategy.generate_signals` 的实现——你会发现它就是用 `rolling().mean()` + 比较，**和上面手写的一模一样**。这就是 Phase 2 的入口：你已经会写策略了。
        """),

        md("""
        ## 第 7 段：随堂小练

        ### 小练：实现 EMA 交叉策略
        用 EMA12 上穿 EMA26 作为买入信号，下穿作为卖出，跑比亚迪 2022-2024 的回测。
        """),

        code("""
        # TODO: 你的代码（约 6 行）



        """),

        md("""
        ## 第 8 段：课后练习 + 下节预告

        ### 📝 `exercises/ex07.py`
        1. 写 `compute_macd(prices, fast=12, slow=26, signal=9)` 返回 DataFrame（dif/dea/hist 三列）
        2. 写 `rsi_signal(prices, period=14, oversold=30, overbought=70)` 返回信号 Series（超卖+1，超买-1，中性 0）
        3. 双均线参数搜索：在 (short, long) ∈ {(5,20), (10,30), (5,60), (20,60)} 中找比亚迪最优组合（按夏普）

        ### 🔮 下节 L08：PE 估值 + 行业对比
        价格类指标（MA/MACD）只看"价格本身"，**估值指标（PE）**告诉你"价格相对价值是贵还是便宜"。
        """),

        md("""
        ## 第 9 段：Jupyter tip 🔧
        - `?DualMAStrategy` 查类文档；`??DualMAStrategy` 查源码（双问号）
        - `%run my_script.py` 在 notebook 里跑外部脚本，变量自动注入
        - `np.where(cond, a, b)` vs `pd.Series.where(cond, other)`：方向相反，注意！
        """),
    ]
    write_nb(cells, "07_technical_indicators.ipynb")


def build_ex07() -> None:
    write_ex("ex07.py", """
        \"\"\"L07 课后练习：技术指标。\"\"\"
        from __future__ import annotations
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

        import numpy as np
        import pandas as pd
        from _data import get_stock_data


        def compute_macd(prices: pd.Series, fast: int = 12, slow: int = 26,
                         signal: int = 9) -> pd.DataFrame:
            \"\"\"计算 MACD。

            Returns:
                DataFrame 列 [dif, dea, hist]
            \"\"\"
            # TODO: ~5 行




            return pd.DataFrame()


        def rsi_signal(prices: pd.Series, period: int = 14,
                       oversold: int = 30, overbought: int = 70) -> pd.Series:
            \"\"\"RSI 信号：超卖 +1，超买 -1，中性 0。\"\"\"
            # TODO: ~6 行



            return pd.Series(dtype=int)


        def best_ma_params(df: pd.DataFrame,
                           params: list[tuple[int, int]] = None) -> tuple[tuple[int, int], float]:
            \"\"\"搜索最优 MA 参数组合（按夏普）。

            Returns:
                ((short, long), sharpe)
            \"\"\"
            if params is None:
                params = [(5, 20), (10, 30), (5, 60), (20, 60)]
            # TODO: ~12 行
            # 提示：
            # rets = df['close'].pct_change()
            # for short, long in params:
            #   signal = (df['close'].rolling(short).mean() > df['close'].rolling(long).mean()).astype(int).shift(1).fillna(0)
            #   strat_ret = signal * rets
            #   sharpe = strat_ret.mean() / strat_ret.std() * np.sqrt(252)




            return ((0, 0), 0.0)


        def run_all() -> None:
            byd = get_stock_data('002594').set_index('date')

            print("=" * 60); print("题 1：MACD"); print("=" * 60)
            macd = compute_macd(byd['close'])
            print(macd.tail(3))

            print(); print("=" * 60); print("题 2：RSI 信号"); print("=" * 60)
            sig = rsi_signal(byd['close'])
            print(f"超卖信号 {len(sig[sig==1])} 次，超买信号 {len(sig[sig==-1])} 次")

            print(); print("=" * 60); print("题 3：最优 MA 参数"); print("=" * 60)
            best, sharpe = best_ma_params(byd)
            print(f"最优参数: {best}, 夏普: {sharpe:.2f}")


        if __name__ == "__main__":
            run_all()
    """)


# ============================================================
# L08 PE 估值 + 行业对比
# ============================================================
def build_l08() -> None:
    cells = [
        md("""
        # L08 · PE 估值 + 行业对比

        **预计时长**：60 min | **难度**：⭐⭐⭐ | **前置**：L07

        ## 本节目标
        1. PE / PB / PS 三大估值指标的含义与适用范围
        2. PE 历史分位数（"现在的 PE 比过去 X% 时间低"）
        3. 申万一级行业分类
        4. `groupby / rank / quantile / cut / qcut` 用法

        > ⚠️ akshare 的 PE 数据接口偶尔不稳，本节用一份静态备份的 PE 数据集演示。
        """),

        md("""
        ## 第 1 段：金融概念

        ### 三大估值指标
        | 指标 | 公式 | 适用 | 缺点 |
        |------|------|------|------|
        | **PE** (市盈率) | 股价 / 每股收益 | 盈利稳定的公司 | 亏损公司无意义 |
        | **PB** (市净率) | 股价 / 每股净资产 | 重资产行业（银行、地产） | 无形资产多的公司失真 |
        | **PS** (市销率) | 股价 / 每股营收 | 高增长未盈利公司（电商、SaaS） | 不反映盈利能力 |

        ### PE 的几种口径
        - **静态 PE** (LYR)：用上一年度净利润
        - **滚动 PE** (TTM)：用最近 4 个季度净利润（**最常用**）
        - **动态 PE** (Forward)：用分析师预测的今年净利润

        ### PE 分位数（核心概念）
        "比亚迪当前 PE 30，处于过去 5 年的 65% 分位" = 过去 5 年有 65% 的时间 PE ≤ 30。
        - 分位数 < 20%：**低估**（历史上 80% 时间更贵）
        - 20-80%：**合理区间**
        - > 80%：**高估**

        ### 申万行业分类（SW）
        A 股最权威的行业分类，分一级（31 个）、二级、三级。例：
        - 一级"汽车"含比亚迪、长城汽车、上汽集团
        - 一级"传媒"含完美世界、世纪华通
        - 一级"食品饮料"含贵州茅台、五粮液

        **对比逻辑**：同行业内比 PE 才有意义。茅台 PE 30 不算贵（行业均值 25），但放到银行（行业均值 5）就天价。
        """),

        code(common_imports()),
        code("byd = get_stock_data('002594').set_index('date')"),

        md("""
        ## 第 2 段：从价格反推"伪 PE"

        真实 PE 需要"每股收益（EPS）"数据。akshare 的 `stock_a_pe_em` 能拉到，但接口不稳定。
        本节用**简化教学版**：给三只股票一个假设的 EPS，算 PE。
        """),

        code("""
        # 假设的 EPS（实际项目应从 akshare.stock_financial_abstract 拉）
        EPS = {
            "002594": 5.20,   # 比亚迪
            "002602": 0.18,   # 世纪华通
            "002624": 0.45,   # 完美世界
        }

        # 用三股对齐的 close 价格
        from pathlib import Path
        panel_path = Path("data/panel_three_stocks.parquet")
        if panel_path.exists():
            wide = pd.read_parquet(panel_path)
        else:
            frames = {c: get_stock_data(c).set_index('date')['close'] for c in EPS}
            wide = pd.DataFrame(frames).sort_index().ffill()

        # 算 PE
        pe = wide.copy()
        for code, eps in EPS.items():
            pe[code] = wide[code] / eps
        pe.tail(3)
        """),

        md("""
        ## 第 3 段：PE 历史分位数
        """),

        code("""
        def pe_percentile(pe_series: pd.Series, today: pd.Timestamp = None) -> float:
            \"\"\"计算 PE 在历史区间内的分位数（0~1）。\"\"\"
            if today is None:
                today = pe_series.index[-1]
            current = pe_series.loc[:today].iloc[-1]
            history = pe_series.loc[:today].dropna()
            return (history <= current).sum() / len(history)

        # 对三股算当前 PE 分位数
        for code in pe.columns:
            pct = pe_percentile(pe[code])
            current_pe = pe[code].iloc[-1]
            print(f"{code} 当前 PE {current_pe:>6.2f}, 历史 {pct*100:>5.1f}% 分位")
        """),

        code("""
        # 画比亚迪 PE 历史曲线 + 分位线
        fig, ax = plt.subplots(figsize=(12, 4))
        pe['002594'].plot(ax=ax, color='steelblue', label='比亚迪 PE')
        ax.axhline(pe['002594'].quantile(0.2), color='green', linestyle='--', label='20% 分位（低估）')
        ax.axhline(pe['002594'].quantile(0.8), color='red', linestyle='--', label='80% 分位（高估）')
        ax.legend()
        ax.set_title('比亚迪 PE 历史区间')
        plt.show()
        """),

        md("""
        ## 第 4 段：构造行业 PE 对比数据

        模拟一个 10 只股票的"汽车行业" PE 表，演示 `groupby / rank / qcut`。
        """),

        code("""
        # 构造静态示例数据（实战中从 akshare.stock_industry_pe_ratio_cninfo 拉）
        auto_industry = pd.DataFrame({
            'code': ['002594', '600104', '600006', '601633', '000625',
                     '601238', '600686', '000800', '600178', '000927'],
            'name':  ['比亚迪', '上汽集团', '东风汽车', '长城汽车', '长安汽车',
                      '广汽集团', '金龙汽车', '一汽解放', '安凯客车', '中国重汽'],
            'industry': ['汽车'] * 10,
            'pe_ttm':  [28.5, 8.2, 15.3, 22.1, 12.7, 9.8, 18.4, 11.5, 25.6, 10.2],
            'pb':      [4.1, 0.8, 1.5, 2.3, 1.1, 0.9, 1.8, 1.2, 2.8, 1.0],
        })
        auto_industry
        """),

        code("""
        # rank：在同行业里排名
        auto_industry['pe_rank'] = auto_industry['pe_ttm'].rank(ascending=True)  # 小=便宜
        auto_industry['pe_pct'] = auto_industry['pe_ttm'].rank(pct=True)
        auto_industry = auto_industry.sort_values('pe_pct')
        auto_industry[['code', 'name', 'pe_ttm', 'pe_rank', 'pe_pct']]
        """),

        code("""
        # qcut：按分位分箱（如 3 档：便宜/合理/贵）
        auto_industry['pe_band'] = pd.qcut(auto_industry['pe_ttm'], q=3,
                                            labels=['低估', '合理', '高估'])
        auto_industry[['code', 'name', 'pe_ttm', 'pe_band']]
        """),

        md("""
        ## 第 5 段：多行业 groupby 聚合
        """),

        code("""
        # 模拟多行业数据
        multi = pd.concat([
            auto_industry,
            pd.DataFrame({
                'code': ['600519', '000858', '000568', '002304'],
                'name':  ['贵州茅台', '五粮液', '泸州老窖', '洋河股份'],
                'industry': ['食品饮料'] * 4,
                'pe_ttm':  [30.5, 22.1, 25.3, 18.7],
                'pb':      [11.2, 6.5, 7.8, 4.9],
            }),
            pd.DataFrame({
                'code': ['002602', '002624', '300413', '300251'],
                'name':  ['世纪华通', '完美世界', '芒果超媒', '光线传媒'],
                'industry': ['传媒'] * 4,
                'pe_ttm':  [35.2, 28.5, 22.1, 40.3],
                'pb':      [3.2, 2.5, 3.8, 4.1],
            }),
        ], ignore_index=True)

        # 按行业算 PE 均值/中位数/分位
        summary = multi.groupby('industry').agg(
            pe_mean=('pe_ttm', 'mean'),
            pe_median=('pe_ttm', 'median'),
            pb_mean=('pb', 'mean'),
            count=('code', 'count'),
        ).round(2)
        summary
        """),

        code("""
        # 每只股票在自己行业里的 PE 分位
        multi['pe_pct_in_industry'] = multi.groupby('industry')['pe_ttm'].rank(pct=True)
        multi.sort_values(['industry', 'pe_pct_in_industry'])
        """),

        md("""
        ## 第 6 段：随堂小练

        ### 小练：找出"行业里最便宜"的股票
        用 `multi` 数据，每个行业挑 PE 分位 < 0.3 的股票（同行业内低估）。
        """),

        code("""
        # TODO: 你的代码（约 2 行）


        """),

        md("""
        ## 第 7 段：课后练习 + 下节预告

        ### 📝 `exercises/ex08.py`
        1. 写 `pe_percentile(pe_series, lookback_days=252*5)` 带 lookback 参数（默认 5 年）
        2. 写 `industry_rank(stocks_df, by='pe_ttm')` 返回带 `rank_in_industry` 列的 DataFrame
        3. 写 `value_categories(pe_series, bins=[0, 0.2, 0.8, 1])` 返回每个股票的估值类别（低估/合理/高估）

        ### 🔮 下节 L09：向量化核心习惯
        量化最重要的"心法"。用 `%timeit` 对比 for 循环 vs 向量化，让"100 倍速度差"刻进肌肉记忆。
        """),

        md("""
        ## 第 8 段：Jupyter tip 🔧
        - `pd.qcut(s, q=10)` 分十等分（十分位）—— 量化常用
        - `pd.cut(s, bins=[0, 30, 70, 100])` 按自定义区间分箱
        - `df.style.background_gradient(cmap='RdYlGn_r')` 给 DataFrame 加渐变背景（看 PE 排名很直观）
        """),
    ]
    write_nb(cells, "08_pe_valuation_industry.ipynb")


def build_ex08() -> None:
    write_ex("ex08.py", """
        \"\"\"L08 课后练习：PE 估值与行业对比。\"\"\"
        from __future__ import annotations
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

        import numpy as np
        import pandas as pd


        def pe_percentile(pe_series: pd.Series, lookback_days: int = 252 * 5) -> float:
            \"\"\"PE 历史分位数（带 lookback）。

            Args:
                pe_series: 时间序列 PE（index=date, value=PE）
                lookback_days: 向前看多少个交易日，默认 5 年

            Returns:
                当前 PE 在过去 lookback_days 内的分位数（0~1）
            \"\"\"
            # TODO: ~5 行



            return 0.0


        def industry_rank(stocks_df: pd.DataFrame, by: str = 'pe_ttm') -> pd.DataFrame:
            \"\"\"在每个行业内部按 by 列排名。

            Args:
                stocks_df: 至少含 ['industry', by] 两列
                by: 排名依据列名

            Returns:
                原 DataFrame 加 'rank_in_industry' 和 'pct_in_industry' 两列
            \"\"\"
            # TODO: ~4 行



            return stocks_df


        def value_categories(pe_series: pd.Series,
                             bins: list[float] = None,
                             labels: list[str] = None) -> pd.Series:
            \"\"\"按分位数把 PE 分箱到估值类别。

            默认 bins=[0, 0.2, 0.8, 1], labels=['低估', '合理', '高估']
            \"\"\"
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
    """)


# ============================================================
# L09 向量化（核心习惯）
# ============================================================
def build_l09() -> None:
    cells = [
        md("""
        # L09 · 向量化核心习惯

        **预计时长**：60 min | **难度**：⭐⭐⭐⭐ | **前置**：L08

        ## 本节目标
        1. 理解为什么量化必须向量化（速度差 100 倍）
        2. NumPy ndarray 基础 + 广播机制
        3. `np.where` 替代 if-else 循环
        4. **apply / map / itertuples 的边界**（什么时候 NOT 用）
        5. 性能基准测试 `%timeit`
        """),

        md("""
        ## 第 1 段：为什么量化必须向量化

        量化场景下，你要处理的不是"一个数字"，而是：
        - 1000 只股票 × 10 年 × 250 交易日 = **250 万个数据点**
        - 用 for 循环逐个处理 → 几分钟到几小时
        - 用向量化 → 几秒到几十秒

        **Python 慢的本质**：每个操作都要经过解释器、类型检查、动态分发。NumPy 用 C 实现，绕过这些开销。

        ### ⚠️ 监管提示（2025.7.7 起）
        中国证监会《程序化交易管理实施细则》已正式实施：每秒申报 ≥ 300 笔或单日笔数较高的，认定为**高频交易**，监管对其收取差异化收费、加强监测。**向量化提速用于研究与回测没问题**，但真要上实盘"刷单"，请先确认符合监管要求。Phase 1 的内容全部限于研究与回测范畴。

        ### 核心原则
        > **永远优先使用 Pandas/NumPy 的"整列运算"，不要 for 循环遍历行。**

        L01-L08 你已经在用（`.rolling()`、`.shift()`、`.cumprod()` 等都是向量化），本节让你**意识到**这个习惯，并测出速度差。
        """),

        code(common_imports()),

        md("""
        ## 第 2 段：NumPy ndarray 基础
        """),

        code("""
        # NumPy 的核心数据结构：ndarray（n 维数组）
        a = np.array([1, 2, 3, 4, 5], dtype='float64')
        b = np.array([10, 20, 30, 40, 50])

        # 整数组运算：自动逐元素
        print("a + b =", a + b)
        print("a * 2 =", a * 2)  # 标量广播
        print("a > 3 =", a > 3)  # 布尔数组
        print("a[a > 3] =", a[a > 3])  # 布尔索引

        # 和 list 对比
        py_list = [1, 2, 3, 4, 5]
        # py_list + py_list  # 这是拼接 [1,2,3,4,5,1,2,3,4,5]，不是逐元素加！
        print("list + list =", py_list + py_list)
        """),

        md("""
        ## 第 3 段：广播机制（broadcasting）
        """),

        code("""
        # 形状不同的数组相加，NumPy 会"广播"成相同形状
        matrix = np.array([[1, 2, 3],
                           [4, 5, 6],
                           [7, 8, 9]])  # shape (3, 3)
        row = np.array([10, 20, 30])  # shape (3,)

        # row 被广播成 (3, 3)：每行都加 [10,20,30]
        print("matrix + row =\\n", matrix + row)

        col = np.array([[100], [200], [300]])  # shape (3, 1)
        print("\\nmatrix + col =\\n", matrix + col)
        """),

        code("""
        # 实战：1000 只股票 10 年日收益，每个股票累乘
        rng = np.random.default_rng(42)
        rets = rng.normal(0.0005, 0.02, size=(2520, 1000))  # 2520 日 × 1000 股
        print(f"数据 shape: {rets.shape}")

        # 每只股票的累计收益（沿 axis=0 累乘）
        cum = np.cumprod(1 + rets, axis=0) - 1
        print(f"末值 shape: {cum[-1].shape}")
        print(f"前 5 只末值: {cum[-1, :5]}")
        """),

        md("""
        ## 第 4 段：`np.where` 替代 if-else 循环
        """),

        code("""
        # 任务：把 rets 中 > 0 的标 1，<= 0 的标 0
        # ❌ 错误做法：双层 for
        # ✅ 正确做法：np.where

        signals = np.where(rets > 0, 1, 0)
        print(f"信号 shape: {signals.shape}, 均值（即胜率）: {signals.mean():.4f}")

        # 多条件组合：np.select
        conditions = [rets > 0.01, rets < -0.01]
        choices = [2, -2]  # 大涨标 2，大跌标 -2
        multi_signal = np.select(conditions, choices, default=0)
        print("信号分布：", np.unique(multi_signal, return_counts=True))
        """),

        md("""
        ## 第 5 段：for 循环 vs 向量化 速度对比

        用 `%timeit` 实测。这个对比你应该**亲眼看到**，让肌肉记忆刻进去。
        """),

        code("""
        # 准备数据：单只股票 2520 日收益率
        byd = get_stock_data('002594').set_index('date')
        rets = byd['close'].pct_change().dropna().values  # 转 ndarray
        print(f"数据点数: {len(rets)}")
        """),

        code("""
        # 任务：算每个时间点的累计收益率
        # 版本 A：for 循环
        def cum_with_loop(rets: np.ndarray) -> np.ndarray:
            result = np.empty_like(rets)
            cum = 1.0
            for i, r in enumerate(rets):
                cum *= (1 + r)
                result[i] = cum
            return result

        # 版本 B：向量化（np.cumprod）
        def cum_vectorized(rets: np.ndarray) -> np.ndarray:
            return np.cumprod(1 + rets, axis=0)

        # 验证两者结果一致
        a = cum_with_loop(rets)
        b = cum_vectorized(rets)
        assert np.allclose(a, b), "结果不一致！"
        print("✓ 两版本结果一致")
        """),

        code("""
        # 速度对比
        import timeit
        n_loop = 1000

        t_loop = timeit.timeit(lambda: cum_with_loop(rets), number=n_loop)
        t_vec  = timeit.timeit(lambda: cum_vectorized(rets), number=n_loop)
        print(f"for 循环:    {t_loop*1000:>8.1f} ms / {n_loop} 次 = {t_loop/n_loop*1000:.3f} ms/次")
        print(f"向量化:      {t_vec*1000:>8.1f} ms / {n_loop} 次 = {t_vec/n_loop*1000:.3f} ms/次")
        print(f"加速比:      {t_loop/t_vec:>8.1f} ×")
        """),

        code("""
        # 用 magic 命令更简洁（仅 notebook 可用）
        %timeit cum_with_loop(rets)
        %timeit cum_vectorized(rets)
        """),

        md("""
        ## 第 6 段：apply / map / itertuples 的边界

        Pandas 的 `apply` 很方便，但**慢**。原则：

        | 场景 | 用什么 | 速度 |
        |------|-------|------|
        | 单列变换（如 abs） | `.abs()` / `.astype()` 内置方法 | 最快 |
        | 多列组合运算 | 整列算术 + np.where | 最快 |
        | 复杂自定义函数 | `.apply()` / `.map()` | 中等 |
        | 必须逐行依赖前一行 | `for` 循环 / `itertuples()` | 最慢（但有时不可避免） |

        **判断标准**：能用整列算术就别用 apply。apply 里再套循环就是灾难。
        """),

        code("""
        df = pd.DataFrame({'a': np.random.randn(10000), 'b': np.random.randn(10000)})

        # 任务：算 a^2 + b^2
        def f(row):
            return row['a']**2 + row['b']**2

        # 三种写法（取消注释逐个 %timeit）
        %timeit df.apply(f, axis=1)              # ❌ 最慢
        %timeit df['a']**2 + df['b']**2          # ✅ 最快

        # 典型输出（数字因机器而异）：
        # apply:      ~150 ms
        # 整列算术:   ~0.5 ms
        # 加速比:     ~300×
        """),

        md("""
        ## 第 7 段：随堂小练

        ### 小练：把给定 for 循环改写成向量化

        下面这个函数计算"过去 N 日中上涨日数"（用于 RSI 等指标）。把它改写成向量化版本，并用 %timeit 对比。
        """),

        code("""
        # 原版：for 循环
        def up_days_loop(rets: np.ndarray, window: int = 10) -> np.ndarray:
            result = np.full(len(rets), np.nan)
            for i in range(window, len(rets)):
                result[i] = (rets[i-window:i] > 0).sum()
            return result

        # TODO: 你的向量化版本（约 2 行）
        def up_days_vec(rets: np.ndarray, window: int = 10) -> np.ndarray:
            pass



        # 验证 + 测速
        rng = np.random.default_rng(0)
        test_rets = rng.normal(0, 0.02, 1000)
        a = up_days_loop(test_rets)
        b = up_days_vec(test_rets)
        # assert np.allclose(a[10:], b[10:], equal_nan=True)  # 取消注释验证
        """),

        md("""
        ## 第 8 段：课后练习 + 下节预告

        ### 📝 `exercises/ex09.py`
        1. 把"计算 RSI"的 for 循环版改成纯向量化（用 `np.where` + `rolling`）
        2. 写 `batch_cumulative_nav(rets_matrix)`：输入 (N_days, N_stocks) 矩阵，返回每股票累计净值（一条向量化语句搞定）
        3. 找出 qtrader 代码里一处可以用向量化优化的地方，写优化前后两版

        ### 🔮 下节 L10：综合项目（毕业考核）
        用前面所有技能（数据/清洗/复权/统计/指标/向量化）产出一份完整的股票分析 HTML 报告。
        """),

        md("""
        ## 第 9 段：Jupyter tip 🔧
        - `%timeit` 自动多次取平均；`%%timeit` 测整 cell
        - `%prun my_func()` 行级性能分析（找出最慢的那行）
        - `%load_ext line_profiler` + `%lprun -f my_func my_func()` 更细
        - NumPy 大数组运算前用 `np.ascontiguousarray` 整理内存布局，可再快 1.5×
        """),
    ]
    write_nb(cells, "09_vectorization.ipynb")


def build_ex09() -> None:
    write_ex("ex09.py", """
        \"\"\"L09 课后练习：向量化。\"\"\"
        from __future__ import annotations
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

        import numpy as np
        import pandas as pd


        def rsi_vectorized(prices: pd.Series, period: int = 14) -> pd.Series:
            \"\"\"向量化 RSI。

            提示：
                - delta = prices.diff()
                - gain = delta.where(delta > 0, 0).rolling(period).mean()
                - loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
                - rsi = 100 - 100 / (1 + gain/loss)
            \"\"\"
            # TODO: ~4 行（与 L07 不同的是这里必须全部向量化，不能 apply）



            return pd.Series(dtype=float)


        def batch_cumulative_nav(rets_matrix: np.ndarray) -> np.ndarray:
            \"\"\"批量累计净值。

            Args:
                rets_matrix: shape (N_days, N_stocks)

            Returns:
                shape 同输入，每列累计净值从 1.0 开始
            \"\"\"
            # TODO: 1 行



            return np.array([])


        def n_largest_drawdowns(nav: pd.Series, n: int = 5) -> pd.DataFrame:
            \"\"\"找出历史最大 N 次回撤（向量化实现）。

            Returns:
                DataFrame 列 [peak_date, trough_date, drawdown]
            \"\"\"
            # TODO: ~6 行
            # 提示：
            #   running_max = nav.cummax()
            #   dd = nav / running_max - 1
            #   找出每次"连续 < 0" 段的 min，按深度排序取 top n




            return pd.DataFrame()


        def run_all() -> None:
            from _data import get_stock_data

            print("=" * 60); print("题 1：RSI 向量化"); print("=" * 60)
            byd = get_stock_data('002594').set_index('date')
            rsi = rsi_vectorized(byd['close'])
            print(f"比亚迪 RSI 末值: {rsi.iloc[-1]:.2f}")

            print(); print("=" * 60); print("题 2：批量净值"); print("=" * 60)
            rng = np.random.default_rng(42)
            rets = rng.normal(0.0005, 0.02, size=(2520, 5))
            navs = batch_cumulative_nav(rets)
            print(f"shape: {navs.shape}, 末值: {navs[-1].round(3)}")

            print(); print("=" * 60); print("题 3：Top 5 回撤"); print("=" * 60)
            nav = (1 + byd['close'].pct_change().fillna(0)).cumprod()
            print(n_largest_drawdowns(nav, n=5))


        if __name__ == "__main__":
            run_all()
    """)


# ============================================================
# L10 综合项目（毕业考核）
# ============================================================
def build_l10() -> None:
    cells = [
        md("""
        # L10 · 综合项目：股票分析报告（毕业考核）

        **预计时长**：90–120 min | **难度**：⭐⭐⭐⭐⭐ | **前置**：L00–L09 全部

        ## 项目目标

        自选一只 A 股，产出一份完整的 HTML 分析报告。报告中每一个数字、每一张图都必须能解释清楚。

        ### 报告必含 7 个 section
        1. **基本信息卡片**：股票名/代码/行业/当前价/总市值（可省）
        2. **K 线图**：mplfinance 近 1 年 K 线 + MA20 + 成交量
        3. **量价分析**：价格 + 成交量双轴图 + 量价关系点评
        4. **涨跌停统计**：2024 年涨停日数、一字板数、最大单日涨幅
        5. **收益率曲线**：累计收益 vs 买入持有 + 年化 + 最大回撤
        6. **PE 历史**：PE 曲线 + 分位线 + 当前估值结论
        7. **简单回测**：调 qtrader DualMA 策略 + 三组参数对比

        ### 输出
        - 文件：`learning/phase1_foundation/capstone_<自选代码>.html`
        - 提交给我审阅 ⭐⭐⭐（按完整性 + 代码质量 + 金融理解打分）

        ### 推荐自选股
        - 三选一：比亚迪 002594、世纪华通 002602、完美世界 002624（数据已缓存）
        - 或自选任一 A 股（需自行缓存）
        """),

        md("""
        ## 任务清单

        本 notebook 是**项目模板**。按下面 7 个 cell 顺序填充代码，最后导出 HTML。
        """),

        code(common_imports()),
        code("import mplfinance as mpf"),

        code("""
        # ====== 项目参数（自选）======
        TARGET_CODE = "002594"   # 改成你要分析的股票
        TARGET_NAME = "比亚迪"
        REPORT_YEAR = 2024
        OUTPUT_HTML = f"capstone_{TARGET_CODE}.html"

        # 拉数据（已在 L01 缓存）
        df = get_stock_data(TARGET_CODE)
        df = df.set_index('date')
        print(f"数据范围: {df.index.min().date()} ~ {df.index.max().date()}, {len(df)} 行")
        """),

        md("""
        ### Section 1：基本信息卡片
        """),

        code("""
        # TODO: 打印一张基本信息表
        # 含：股票名/代码、数据起止、当前收盘价、最高/最低、平均成交量、年化波动率
        # 提示：用 f-string + 表格化打印，约 15 行
        """),

        md("""
        ### Section 2：K 线图（mplfinance）
        """),

        code("""
        # TODO: 画近 1 年 K 线 + MA20 + 成交量
        # 提示：
        # df_mp = df.tail(252).rename(columns={'open':'Open', ...})
        # mpf.plot(df_mp, type='candle', mav=20, volume=True, style='charles')
        """),

        md("""
        ### Section 3：量价分析
        """),

        code("""
        # TODO: 双轴图（close + volume）+ 20 日量均线
        # + 文字点评（5 行）：当前量价关系属于哪一类（量增价涨/量缩价涨/...）
        """),

        md("""
        ### Section 4：涨跌停统计
        """),

        code("""
        # TODO: 复用 L05 的 find_limit_ups 函数
        # 统计 2024 年涨停日数 + 一字板数 + 最大单日涨幅日（日期、涨幅、K 线形态）
        """),

        md("""
        ### Section 5：收益率曲线
        """),

        code("""
        # TODO: 画累计收益曲线
        # + 算年化收益率、年化波动率、夏普、最大回撤
        # + 与"买入持有"对比（其实策略 = 买入持有，但为 L07 留接口）
        """),

        md("""
        ### Section 6：PE 历史（用假设 EPS）
        """),

        code("""
        # TODO: 给一个合理 EPS 估值，画 PE 历史曲线 + 20%/80% 分位线
        # + 文字结论："当前 PE X，历史分位 Y%，估值 低估/合理/高估"
        """),

        md("""
        ### Section 7：简单回测（调 qtrader）
        """),

        code("""
        # TODO: 调用 qtrader.strategies.DualMAStrategy 跑三组参数
        # (5, 20) / (10, 30) / (20, 60)
        # 用 qtrader.metrics.compute_metrics 输出对比表
        # 提示：
        #   from qtrader.strategies import DualMAStrategy
        #   from qtrader.engine import BacktestEngine
        #   engine = BacktestEngine()
        #   results = [engine.run(df.reset_index(), DualMAStrategy(s, l)) for s, l in params]
        """),

        md("""
        ### 导出 HTML

        完成所有 Section 后：
        1. 菜单 `File → Export Notebook As... → HTML`
        2. 保存为 `capstone_<TARGET_CODE>.html`
        3. 把 HTML 文件路径发我，我审阅打分

        ### 毕业标准（⭐⭐⭐）
        - ✅ 7 个 Section 全部填充完整（不留 TODO）
        - ✅ 每张图有标题、轴标签、单位
        - ✅ 每段文字结论**有数字支撑**（不能只写"涨得不错"）
        - ✅ 能口头解释 PE 分位、夏普比率、最大回撤的计算逻辑
        - ✅ 代码可一键运行（Restart Kernel 后从头跑通）

        ### 下一阶段
        L10 通过 = Phase 1「打地基」毕业，进入 Phase 2「建系统：回测框架与经典策略」。
        参考 [docs/roadmap.html](../../docs/roadmap.html)。
        """),

        md("""
        ## Jupyter tip 🔧
        - `Kernel → Restart & Run All`：从零跑一遍，确认无遗漏 cell
        - 导出 HTML 前一定要 Restart & Run All，否则输出可能错乱
        - 大段解释写 Markdown cell（不是代码注释），导出 HTML 后更好看
        """),
    ]
    write_nb(cells, "10_capstone_stock_analysis.ipynb")


# ============================================================
# 主入口
# ============================================================
if __name__ == "__main__":
    build_l02(); build_ex02()
    build_l03(); build_ex03()
    build_l04(); build_ex04()
    build_l05(); build_ex05()
    build_l06(); build_ex06()
    build_l07(); build_ex07()
    build_l08(); build_ex08()
    build_l09(); build_ex09()
    build_l10()  # 综合项目，无独立 exercise
    print("OK: L02-L10 + ex02-ex09 created")
