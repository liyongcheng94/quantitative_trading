"""批次 2 notebook 构建脚本。

运行一次生成 L00 + L01 notebook + ex01.py 练习文件，然后可删除。
"""
from __future__ import annotations

import nbformat as nbf
from pathlib import Path
from textwrap import dedent

OUT_DIR = Path(__file__).parent


def md(src: str) -> dict:
    return nbf.v4.new_markdown_cell(dedent(src).strip())


def code(src: str) -> dict:
    return nbf.v4.new_code_cell(dedent(src).strip())


def build_l00() -> None:
    nb = nbf.v4.new_notebook()
    nb.cells = [
        md("""
        # L00 · 环境自检

        **预计时长**：20 min
        **难度**：⭐
        **前置**：无（第一节课）

        ## 本节目标

        1. 确认 Python 环境、必需库版本符合要求
        2. 确认 akshare 能拉到真实 A 股数据
        3. 确认 Matplotlib 中文显示正常（不会出方块字）
        4. 把比亚迪数据缓存到本地 parquet，后续课程秒级读取

        ## 学习方法提示

        - 每节 notebook 按 7 段结构组织：**元信息 → 概念 → 数据 → 演示 → 小练 → 习题 → Jupyter tip**
        - 代码格**逐个运行**（Shift+Enter），不要一次批量执行
        - 遇到不懂的 API 立即问 Claude
        - 课后练习独立完成，二次错才看答案
        """),

        md("""
        ## 第 1 段：版本检查

        需要的库与最低版本：

        | 库 | 用途 | 最低版本 |
        |----|------|---------|
        | python | 运行时 | 3.9 |
        | pandas | 表格处理 | 2.0 |
        | numpy | 数值计算 | 1.24 |
        | matplotlib | 绘图 | 3.7 |
        | akshare | A 股数据源 | 1.12 |
        | jupyterlab | notebook 环境 | 4.0 |
        | mplfinance | 专业 K 线图（L02 用） | 0.12 |
        | seaborn | 统计图（L06 用） | 0.13 |
        | pyarrow | parquet 读写 | 14.0 |
        """),

        code("""
        import sys
        import importlib

        REQUIRED = {
            "python": (3, 9),
            "pandas": (2, 0),
            "numpy": (1, 24),
            "matplotlib": (3, 7),
            "akshare": (1, 12),
            "jupyterlab": (4, 0),
            "mplfinance": (0, 12),
            "seaborn": (0, 13),
            "pyarrow": (14, 0),
        }

        def version_tuple(name: str) -> tuple[int, int]:
            if name == "python":
                return sys.version_info[:2]
            mod = importlib.import_module(name)
            v = getattr(mod, "__version__", "0.0")
            parts = v.split(".")[:2]
            try:
                return tuple(int(p) for p in parts)
            except ValueError:
                return (0, 0)

        results = []
        for name, min_v in REQUIRED.items():
            try:
                actual = version_tuple(name)
                ok = actual >= min_v
                results.append((name, ".".join(map(str, actual)), ".".join(map(str, min_v)), ok))
            except Exception as e:
                results.append((name, "MISSING", ".".join(map(str, min_v)), False))

        print(f"{'库':<14} {'当前':<12} {'最低':<10} {'状态'}")
        print("-" * 50)
        for name, cur, mn, ok in results:
            print(f"{name:<14} {cur:<12} {mn:<10} {'✅' if ok else '❌'}")
        """),

        md("""
        全部 ✅ 才能继续。如果有 ❌，在终端运行：

        ```bash
        .venv/Scripts/python.exe -m pip install -r requirements.txt
        ```
        """),

        md("""
        ## 第 2 段：模块导入 + 字体设置

        后面所有 notebook 的第一格都长这样。`import _style` 的副作用是设中文字体。
        """),

        code("""
        import sys
        from pathlib import Path

        # 自动定位 phase1_foundation 目录（无论 jupyter lab 从项目根还是从这里启动）
        _cwd = Path.cwd()
        _p1 = _cwd if (_cwd / '_data.py').exists() else (_cwd / 'learning' / 'phase1_foundation')
        sys.path.insert(0, str(_p1))

        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import _style  # 副作用：设中文字体
        from _data import get_stock_data
        """),

        md("""
        ## 第 3 段：中文字体测试

        如果方块字，说明系统没有 Microsoft YaHei，需要改 `_style.py` 的字体栈。
        """),

        code("""
        fig, ax = plt.subplots(figsize=(8, 3))
        ax.text(0.5, 0.7, "中文测试：股票、ETF、涨跌停板", ha='center', fontsize=20)
        ax.text(0.5, 0.3, "负号测试：-123.45 +789.00", ha='center', fontsize=16)
        ax.set_axis_off()
        plt.show()
        """),

        md("""
        ## 第 4 段：akshare 连通性 + 数据缓存

        第一次拉取会走网络（约 3–5 秒），后续读 parquet 缓存（毫秒级）。
        """),

        code("""
        # force_refresh=True 强制重新联网，验证 akshare 通畅
        df = get_stock_data("002594", force_refresh=True)
        print(f"行数: {len(df)}")
        print(f"日期范围: {df['date'].min().date()} ~ {df['date'].max().date()}")
        print(f"是否合成数据: {df.attrs.get('synthetic')}")
        df.head()
        """),

        code("""
        # 验证缓存文件已生成
        from pathlib import Path
        cache = Path("data/002594_qfq.parquet")
        print(f"缓存存在: {cache.exists()}, 大小: {cache.stat().st_size // 1024} KB")
        """),

        md("""
        ## 第 5 段：课程导览

        本阶段 10 节课，每节锁定 **1 个金融概念 × 1 个数据技能**：

        | # | 课题 | # | 课题 |
        |---|------|---|------|
        | 00 | 环境自检（本节） | 05 | 收益率 + 涨停识别 |
        | 01 | 股票基础 + A 股规则 | 06 | 统计基础 + 交易成本 |
        | 02 | K 线读图 + DataFrame | 07 | 技术指标入门 |
        | 03 | 量价关系 + 聚合 | 08 | PE 估值 + 行业对比 |
        | 04 | 数据清洗 + 复权 + 对齐 | 09 | 向量化核心习惯 |
        | | | 10 | 综合项目 |

        **核心目标**：L09 结束时，"向量化优先" 应该成为你的肌肉记忆；L10 结束时，你应该能独立产出一份股票分析报告。

        详细大纲见 `learning/INDEX.md`。
        """),

        md("""
        ## 第 6 段：Jupyter tip 🔧

        本节用到的 Jupyter 技巧：

        | 操作 | 作用 |
        |------|------|
        | `Shift + Enter` | 运行当前格并跳到下一格 |
        | `Ctrl + Enter` | 运行当前格但不跳转 |
        | `Esc` → `dd` | 删除当前格（先按 Esc 进入命令模式） |
        | `Esc` → `a` / `b` | 在上方/下方插入新格 |
        | `%timeit x = sum(range(1000))` | 测一行代码的执行时间（L09 会大量用到） |
        | `?print` | 查看函数文档 |
        | `??print` | 查看函数源码 |

        **最重要的习惯**：从 L01 开始，每运行完一个 cell，看一眼输出，确认它符合你的预期。看到奇怪的数字或图，**不要跳过**，立即问。
        """),

        md("""
        ## 收尾

        如果上面 4 段全部 ✅：恭喜，你已具备学习后续 9 节课的全部环境条件。

        **下一节 L01**：股票基础 + A 股规则（T+1、涨跌停板）。你会拉比亚迪/世纪华通/完美世界三只股票的数据，并在 K 线表里识别涨停日。

        **课后无练习**（环境课），直接进 L01。
        """),
    ]
    nb.metadata.kernelspec = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.metadata.language_info = {"name": "python"}
    nbf.write(nb, OUT_DIR / "00_setup.ipynb")


def build_l01() -> None:
    nb = nbf.v4.new_notebook()
    nb.cells = [
        md("""
        # L01 · 股票基础 + A 股规则

        **预计时长**：60 min
        **难度**：⭐⭐
        **前置**：L00 环境自检

        ## 本节目标

        1. 理解股票 / ETF / 指数的区别，看懂 A 股市场结构与代码规则
        2. **掌握 A 股两大特色规则**：T+1 交易制度、涨跌停板
        3. 会用 `ak.stock_zh_a_daily` 拉真实日线数据
        4. 会用 `head / tail / describe` 初步查看 DataFrame
        5. 肉眼从 K 线表里识别涨停日（深入识别在 L05）
        """),

        md("""
        ## 第 1 段：金融概念

        ### 1.1 股票、ETF、指数

        - **股票**：持有公司所有权的凭证。买 1 股 = 你是这家公司的股东之一
        - **ETF（Exchange-Traded Fund）**：一篮子股票的"打包产品"，像股票一样在交易所买卖。例：沪深300ETF = 一次性买进 300 只股票的迷你组合
        - **指数**：一组股票的加权平均价，反映市场整体或某板块走势。例：上证综指、创业板指

        | 品种 | 买的是什么 | 风险 | 适合谁 |
        |------|-----------|------|-------|
        | 个股 | 一家公司 | 高 | 想跑赢市场的人 |
        | ETF | 一篮子股票 | 中 | 想分散风险的人 |
        | 指数 | 不直接买，只跟踪 | — | 用来衡量市场 |

        ### 1.2 A 股市场结构

        ```
        中国 A 股
        ├── 上交所 (SH)  代码开头 6 / 9
        │   ├── 主板     600/601/603/605
        │   ├── 科创板   688     涨跌幅 ±20%
        │   └── B 股     900     (用美元交易，本课不涉及)
        ├── 深交所 (SZ)  代码开头 0 / 2 / 3
        │   ├── 主板     000/001/002
        │   ├── 中小板   002     (已并入主板，历史代码保留)
        │   ├── 创业板   300/301 涨跌幅 ±20%
        │   └── B 股     200     (用港币交易，本课不涉及)
        └── 北交所 (BJ)  代码开头 4 / 8     涨跌幅 ±30%
        ```

        **新手陷阱**：`002594 比亚迪` 是深交所主板（代码开头 002），`002602 世纪华通` 也是，`002624 完美世界` 也是。但 `688xxx` 是科创板（涨跌幅 ±20%），不是主板。

        ### 1.3 A 股两大特色规则（必背）

        #### 🇨🇳 T+1 制度
        今天买入的股票，**下一个交易日才能卖出**。T = Trade day，T+1 = 交易日的次日。
        - 今天上午买入 → 今天下午不能卖 → 明天才能卖
        - 周五买入 → 周一才能卖
        - 对比美股 / 港股：T+0（当天可买卖，但仍受资金 T+1 结算约束）

        **对策略的意义**：你不能日内"刷"一只股票，所有策略至少持有一天。回测时假设"T 日收盘买入、T+1 日开盘可卖"。

        #### 🇨🇳 涨跌停板
        每个交易日，单只股票相对**前一日收盘价**的最大涨跌幅被限制：

        | 板块 | 普通股 | ST 股（特别处理） | 新股首日 |
        |------|-------|-------------------|--------|
        | 主板（沪/深） | ±10% | ±5% | 前 5 日无限制（2023 注册制改革后；老规则 +44% 已废止） |
        | 创业板 / 科创板 | ±20% | ±20% | 前 5 日无限制 |
        | 北交所 | ±30% | ±30% | 无限制 |

        **新手陷阱**：
        - 涨停 = 收盘价 ≈ 前一日收盘 × 1.10（不是 1.11，不能四舍五入）
        - "一字涨停" = 开盘价 = 最高 = 最低 = 收盘价 = 涨停价（最强势）
        - "封死涨停" = 全天都停在涨停价，没人能买到（除非你早上挂单且运气好）
        - 跌停反之

        **为什么 A 股有这个规则？** 1996 年以前没有，出现过单日 ±50% 的极端波动；引入涨跌停是为了**冷却情绪**、降低杠杆爆仓的连锁反应。
        """),

        md("""
        ### 1.4 本节要拉的数据

        | 代码 | 名称 | 交易所 / 板块 |
        |------|------|--------------|
        | 002594 | 比亚迪 | 深交所主板 |
        | 002602 | 世纪华通 | 深交所主板 |
        | 002624 | 完美世界 | 深交所主板 |

        都是主板，涨跌幅都是 ±10%。下一节课我们用 mplfinance 画专业 K 线，本节先用表格看数据。
        """),

        md("""
        ## 第 2 段：数据准备

        L00 已经缓存了比亚迪，本节再缓存另外两只。
        """),

        code("""
        import sys
        from pathlib import Path

        # 自动定位 phase1_foundation 目录（无论 jupyter lab 从项目根还是从这里启动）
        _cwd = Path.cwd()
        _p1 = _cwd if (_cwd / '_data.py').exists() else (_cwd / 'learning' / 'phase1_foundation')
        sys.path.insert(0, str(_p1))

        import pandas as pd
        import numpy as np
        import matplotlib.pyplot as plt
        import _style
        from _data import get_stock_data
        """),

        code("""
        # 拉取三只股票数据（首次联网，约 10 秒；后续读缓存）
        byd      = get_stock_data("002594")  # 比亚迪
        zhckt    = get_stock_data("002602")  # 世纪华通
        wmworld  = get_stock_data("002624")  # 完美世界

        for name, df in [("比亚迪", byd), ("世纪华通", zhckt), ("完美世界", wmworld)]:
            print(f"{name}: {len(df)} 行, 日期 {df['date'].min().date()} ~ {df['date'].max().date()}, 合成={df.attrs.get('synthetic')}")
        """),

        md("""
        ## 第 3 段：代码演示

        ### 3.1 看懂 DataFrame 结构

        `get_stock_data` 返回 6 列 OHLCV：

        | 列 | 含义 | 类型 |
        |----|------|------|
        | date | 交易日 | datetime64 |
        | open | 开盘价（当日第一笔成交价） | float64 |
        | high | 当日最高价 | float64 |
        | low | 当日最低价 | float64 |
        | close | 收盘价（当日最后一笔成交价） | float64 |
        | volume | 成交量（股数，不是金额） | float64 |

        为什么没有"成交金额"列？因为金额 = volume × 平均价，可以自己算。akshare 接口如此约定。
        """),

        code("""
        # 看 DataFrame 前 5 行（head 默认就是 5）
        byd.head()
        """),

        code("""
        # 看后 5 行（tail）— 检查数据是否最新
        byd.tail()
        """),

        code("""
        # describe 看每列的统计摘要（count/mean/std/min/四分位/max）
        # 注意：date 列被自动跳过（因为不是数字）
        byd.describe()
        """),

        code("""
        # shape 看行列数：(行数, 列数)
        byd.shape

        # columns 看列名，dtype 看每列类型
        print(byd.columns.tolist())
        print(byd.dtypes)
        """),

        md("""
        ### 3.2 肉眼找涨停日

        T+1 规则要求我们**先算前一日收盘价**，再看当日是否涨停：
        - 涨停条件：`close / prev_close - 1 >= +9.9%`（用 9.9% 而不是 10%，因为四舍五入）
        - 跌停条件：`close / prev_close - 1 <= -9.9%`

        L05 会讲 `pct_change()` API，这里先用最朴素的方式：把 close 列整体除以它的"前一日"。
        """),

        code("""
        # 把 close 列往下"挪一格"（变成"前一日收盘"）
        byd["prev_close"] = byd["close"].shift(1)
        byd["chg_pct"] = byd["close"] / byd["prev_close"] - 1  # 当日涨跌幅
        byd["chg_pct_pct"] = (byd["chg_pct"] * 100).round(2).astype(str) + "%"

        # 找出涨幅 >= 9.9% 的日子（主板涨停）
        limit_up = byd[byd["chg_pct"] >= 0.099].copy()
        print(f"比亚迪 2022 至今共 {len(limit_up)} 个涨停日")
        limit_up[["date", "close", "prev_close", "chg_pct_pct"]]
        """),

        md("""
        **新手陷阱**：第一次接触 `shift(1)` 容易搞反方向。
        - `close.shift(1)` 把收盘价往下挪一行 → 第 N 行的 `shift(1)` 是第 N-1 日的收盘价（即"前一日收盘"）
        - `shift(-1)` 反过来，是"后一日"
        - 这是避免未来函数的核心操作，L05 会深入讲
        """),

        md("""
        ## 第 4 段：随堂小练

        ### 小练 1：找比亚迪最近一年最大单日涨幅日
        在下面 cell 里写代码，找出 `chg_pct` 最大的那一天，打印日期、收盘价、涨幅。
        """),

        code("""
        # TODO: 你的代码（约 3 行）
        # 提示：byd.sort_values('chg_pct', ascending=False).head(1)
        # 或者 byd.loc[byd['chg_pct'].idxmax()]



        """),

        md("""
        ### 小练 2：三只股票的涨停次数对比

        在下面 cell 给 zhckt 和 wmworld 也加上 `chg_pct` 列，然后统计三只股票各自涨停的次数。
        """),

        code("""
        # TODO: 你的代码（约 5 行）
        # 提示：可以用一个循环遍历 [('比亚迪', byd), ('世纪华通', zhckt), ('完美世界', wmworld)]
        # 对每个 df 算 chg_pct >= 0.099 的行数
        # 然后打印 f"{name}: {count} 次涨停"



        # 预期输出（数字仅供参考，实际取决于真实数据）：
        # 比亚迪: XX 次涨停
        # 世纪华通: XX 次涨停
        # 完美世界: XX 次涨停
        """),

        md("""
        ## 第 5 段：课后练习 + 下节预告

        ### 📝 课后练习：`exercises/ex01.py`

        打开 `exercises/ex01.py`，独立完成 3 道题：

        1. 拉取 `600519` 贵州茅台最近 1 年数据，计算期间最高价/最低价/平均成交量
        2. 写一个函数 `count_limit_up(df, threshold=0.099)`：输入任意股票 DataFrame，返回涨停日数（不要在函数里打印，return 一个 int）
        3. 给三只股票（比亚迪/世纪华通/完美世界）最近一年的"涨停日数 + 平均日成交量"做一张对比表（DataFrame）

        完成后让我审阅打分 ⭐⭐⭐。

        ### 🔮 下节预告：L02 K 线读图

        本节你只看了**数字表**。下节用 `mplfinance` 把 K 线画出来，你会立刻看清"涨停日长什么样"、"阴线阳线什么区别"。同时学 DataFrame 的 `.loc / .iloc` 索引切片。
        """),

        md("""
        ## 第 6 段：Jupyter tip 🔧

        - `%who` / `%whos`：查看当前所有变量（带类型）
        - `dir(df)`：列出 DataFrame 所有方法和属性（看到眼花但有用）
        - `df.<TAB>`：输入 `df.` 后按 Tab，弹出所有方法
        - 双击报错信息里的 `.ipy` / `.py` 路径：JupyterLab 支持直接跳转

        **本节最重要的心法**：金融数据是有"形状"的（时间序列 + OHLC + 成交量）。把它装进 DataFrame 后，**先 describe、再画图、再算指标**，是这个三段式让你避免绝大多数低级错误。
        """),
    ]
    nb.metadata.kernelspec = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.metadata.language_info = {"name": "python"}
    nbf.write(nb, OUT_DIR / "01_stock_etf_a_share_rules.ipynb")


def build_ex01() -> None:
    ex_dir = OUT_DIR / "exercises"
    ex_dir.mkdir(exist_ok=True)
    (ex_dir / "__init__.py").write_text("")
    (ex_dir / "ex01.py").write_text(dedent("""
        \"\"\"L01 课后练习：股票数据基础。

        每题完成后，在终端运行：
            .venv/Scripts/python.exe -m learning.phase1_foundation.exercises.ex01

        或在 notebook 里 from exercises import ex01; ex01.run_all()
        \"\"\"
        from __future__ import annotations

        import sys
        from pathlib import Path

        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

        import pandas as pd
        from _data import get_stock_data


        # ---------- 题 1 ----------
        def moutai_summary() -> dict:
            \"\"\"拉取 600519 贵州茅台最近 1 年数据，返回统计字典。

            Returns:
                dict 包含 high (float) / low (float) / avg_volume (float)
                high/low 是期间最高/最低"收盘价"（不是 high/low 列）
                avg_volume 是平均"日成交量"
            \"\"\"
            # TODO: 你的代码（约 5 行）






            return {"high": 0.0, "low": 0.0, "avg_volume": 0.0}


        # ---------- 题 2 ----------
        def count_limit_up(df: pd.DataFrame, threshold: float = 0.099) -> int:
            \"\"\"统计 DataFrame 中涨停日的数量。

            Args:
                df: 必须含 close 列的 DataFrame
                threshold: 涨幅阈值，主板默认 0.099 (9.9%)，创/科可传 0.199

            Returns:
                涨停日数（int）

            注意:
                - 第一行的 prev_close 为 NaN，不能计入
                - 用 shift(1) 取前一日收盘
            \"\"\"
            # TODO: 你的代码（约 4 行）




            return 0


        # ---------- 题 3 ----------
        def compare_three_stocks() -> pd.DataFrame:
            \"\"\"对三只股票最近一年做对比表。

            Returns:
                DataFrame，index 为股票名，列为 ['涨停日数', '平均日成交量', '年化波动率(%)']
                股票名：比亚迪/世纪华通/完美世界
                代码：002594 / 002602 / 002624
                年化波动率 = chg_pct.std() * sqrt(252) * 100
            \"\"\"
            # TODO: 你的代码（约 10 行）






            return pd.DataFrame()


        def run_all() -> None:
            print("=" * 60)
            print("题 1：贵州茅台最近 1 年统计")
            print("=" * 60)
            r = moutai_summary()
            print(f"最高收盘价: {r['high']:.2f}")
            print(f"最低收盘价: {r['low']:.2f}")
            print(f"平均日成交量: {r['avg_volume']:,.0f}")

            print()
            print("=" * 60)
            print("题 2：涨停日数函数测试")
            print("=" * 60)
            byd = get_stock_data("002594")
            print(f"比亚迪涨停日数: {count_limit_up(byd)}")
            print(f"比亚迪涨停日数(20% 阈值，应为 0): {count_limit_up(byd, 0.199)}")

            print()
            print("=" * 60)
            print("题 3：三股最近一年对比表")
            print("=" * 60)
            print(compare_three_stocks())


        if __name__ == "__main__":
            run_all()
        """).lstrip())


if __name__ == "__main__":
    build_l00()
    build_l01()
    build_ex01()
    print("OK: L00 + L01 + ex01.py created")
