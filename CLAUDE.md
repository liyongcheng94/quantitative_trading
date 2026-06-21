# qtrader · A股量化回测

## 项目概述
两个组件：
1. **qtrader** — 零依赖 A股量化回测框架：双均线 / 海龟 / 网格 三策略横向对比，向量化引擎，无 K线 for 循环
2. **learning** — 系统化学习教材：Phase 1「打地基」10 节互动 Jupyter 课程（金融通识 + Pandas/NumPy + 向量化）

## 环境约定
- **Python 解释器**：始终使用 `.venv/Scripts/python.exe`（不要用系统 python）
- **工作目录**：`D:/project/quantitative_trading`
- **平台**：Windows 11 + bash shell（Unix 语法）

## 核心命令
- **运行测试**：`.venv/Scripts/python.exe -m pytest tests/ -v`
- **多策略回测**：`.venv/Scripts/python.exe -m scripts.run_backtest --code 002594 --save outputs/comparison_byd.png`
- **单策略（双均线）**：`.venv/Scripts/python.exe -m scripts.run_dual_ma --code 002594 --save outputs/byd.png`
- **HTML 报告**：`.venv/Scripts/python.exe -m scripts.build_report`
- **启动 Jupyter 学习环境**：`.venv/Scripts/python.exe -m jupyter lab`
- **重生成 Phase 1 全部 notebook**：`.venv/Scripts/python.exe learning/phase1_foundation/_build_notebooks.py && .venv/Scripts/python.exe learning/phase1_foundation/_build_remaining.py`
- **安装依赖**：`.venv/Scripts/python.exe -m pip install -r requirements.txt`

## 代码地图
- `qtrader/` — 回测主包
  - `data.py` — akshare 数据层（新浪源主、东财源备）
  - `strategies.py` — `Strategy` 基类 + `DualMA` / `Turtle` / `GridStrategy`
  - `engine.py` — `BacktestEngine` + `BacktestResult`（含交易成本扣除）
  - `metrics.py` — `compute_metrics`（总收益/年化/最大回撤/夏普/Calmar/波动率）
  - `plotting.py` — `print_comparison_table` + `plot_comparison`
- `scripts/` — CLI 入口（`run_backtest` / `run_dual_ma` / `build_report`）
- `tests/` — pytest 单元测试（11 tests，合成数据，不联网）
- `outputs/` — 回测产物 PNG / HTML（gitignored）
- `docs/` — 路线图（`roadmap.html` 故事版 + `roadmap2.html` 速览版）
- `learning/` — 系统化学习教材
  - `README.md` / `INDEX.md` / `progress.md` — 课程总览、目录、进度日志
  - `phase1_foundation/` — 阶段一（1.5–2 周，10 节 notebook）
    - `00_setup.ipynb` ~ `10_capstone_stock_analysis.ipynb` — 10 节互动课
    - `exercises/exNN.py` — 9 份课后练习（L10 综合项目无）
    - `_data.py` — 数据缓存 helper（akshare 主、合成数据兜底，parquet 缓存）
    - `_style.py` — Matplotlib 中文字体 + A 股配色
    - `_build_notebooks.py` / `_build_remaining.py` — notebook 生成器（改内容后重跑）

## 关键约定（务必遵守）
1. **向量化优先**：策略层严禁 K线级别 for 循环；网格策略的 grid_n 循环属于可接受的"网格线循环"
2. **避免未来函数**：所有信号 `shift(1).fillna(0)` 后再用于收益计算
3. **新增策略**：继承 `qtrader.strategies.Strategy`，实现 `generate_signals(df) -> pd.Series`，返回 `[0,1]` 目标仓位
4. **新增入口脚本**：放 `scripts/`，首行加 `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))` 以便 `from qtrader import ...`
5. **测试**：用合成 DataFrame，标记 `@pytest.mark.unit`，不联网
6. **输出位置**：所有 PNG/HTML 写入 `outputs/`（已在 `.gitignore`）
7. **改 notebook 内容**：编辑 `_build_*.py` 生成器脚本后重跑，**不要直接编辑 .ipynb**（会被下次重生成覆盖）
8. **notebook sys.path 自检**：notebook 首格已写自动定位 phase1_foundation 目录，兼容"从项目根启动 jupyter lab"和"从 phase1_foundation 启动"两种 CWD
9. **费率/规则类硬事实**：2026 已核实仍准确（印花税 0.05%、过户费 0.001%、涨跌停板）；2026 已更新（佣金万 2.1 免 5、无风险利率 rf=1.75%、量化高频监管）

## 已知工程问题与解决
- **akshare 东方财富源被反爬**：Python requests 的 TLS 指纹被识别，连接被 reset（curl 能成功）。已在 `qtrader/data.py` 切换到新浪源 `stock_zh_a_daily` 为主路径，东财源作为回退。
- **A股代码前缀转换**：纯数字代码自动转新浪格式（`6/9 → sh`、`4/8 → bj`、其余 `sz`），见 `_to_sina_symbol`。
- **pandas 2.1+ 废弃 `fillna(method='ffill')`**：learning/phase1_foundation 统一用 `.ffill()`。
- **GateGuard 钩子拖慢批量文件创建**：在 `.claude/settings.local.json` 的 `ECC_DISABLED_HOOKS` 已加 `pre:edit-write:gateguard-fact-force`。新 session 想禁用成本警告可加 `posttooluse:ecc:cost-tracking`。

## 学习路径
**系统化课程（推荐入口）**：
- [learning/README.md](learning/README.md) — 课程总览与使用说明
- [learning/INDEX.md](learning/INDEX.md) — 10 节课目录与进度
- [learning/phase1_foundation/00_setup.ipynb](learning/phase1_foundation/00_setup.ipynb) — 第一节课（环境自检）

**路线图与心得**：
- [docs/roadmap.html](docs/roadmap.html) — 量化学习四阶段路线图（故事版）
- [docs/roadmap2.html](docs/roadmap2.html) — 路线图速览版（4 列横向）
- 双均线三股对比心得 — 本地运行 `scripts.build_report` 生成 `outputs/report.html`（产物 gitignored，GitHub 上无此文件）

## 免责声明
仅学习交流，不构成投资建议。
