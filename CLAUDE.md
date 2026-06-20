# qtrader · A股量化回测

## 项目概述
零依赖 A股量化回测框架：双均线 / 海龟 / 网格 三策略横向对比，向量化引擎，无 K线 for 循环。

## 环境约定
- **Python 解释器**：始终使用 `.venv/Scripts/python.exe`（不要用系统 python）
- **工作目录**：`D:/project/quantitative_trading`
- **平台**：Windows 11 + bash shell（Unix 语法）

## 核心命令
- **运行测试**：`.venv/Scripts/python.exe -m pytest tests/ -v`
- **多策略回测**：`.venv/Scripts/python.exe -m scripts.run_backtest --code 002594 --save outputs/comparison_byd.png`
- **单策略（双均线）**：`.venv/Scripts/python.exe -m scripts.run_dual_ma --code 002594 --save outputs/byd.png`
- **HTML 报告**：`.venv/Scripts/python.exe -m scripts.build_report`
- **安装依赖**：`.venv/Scripts/python.exe -m pip install -r requirements.txt`

## 代码地图
- `qtrader/` — 主包
  - `data.py` — akshare 数据层（新浪源主、东财源备）
  - `strategies.py` — `Strategy` 基类 + `DualMA` / `Turtle` / `GridStrategy`
  - `engine.py` — `BacktestEngine` + `BacktestResult`（含交易成本扣除）
  - `metrics.py` — `compute_metrics`（总收益/年化/最大回撤/夏普/Calmar/波动率）
  - `plotting.py` — `print_comparison_table` + `plot_comparison`
- `scripts/` — CLI 入口（`run_backtest` / `run_dual_ma` / `build_report`）
- `tests/` — pytest 单元测试（11 tests，合成数据，不联网）
- `outputs/` — 回测产物 PNG / HTML（gitignored）
- `docs/` — 学习材料（`roadmap.html` 故事版 + `roadmap2.html` 速览版）

## 关键约定（务必遵守）
1. **向量化优先**：策略层严禁 K线级别 for 循环；网格策略的 grid_n 循环属于可接受的"网格线循环"
2. **避免未来函数**：所有信号 `shift(1).fillna(0)` 后再用于收益计算
3. **新增策略**：继承 `qtrader.strategies.Strategy`，实现 `generate_signals(df) -> pd.Series`，返回 `[0,1]` 目标仓位
4. **新增入口脚本**：放 `scripts/`，首行加 `sys.path.insert(0, str(Path(__file__).resolve().parents[1]))` 以便 `from qtrader import ...`
5. **测试**：用合成 DataFrame，标记 `@pytest.mark.unit`，不联网
6. **输出位置**：所有 PNG/HTML 写入 `outputs/`（已在 `.gitignore`）

## 已知工程问题与解决
- **akshare 东方财富源被反爬**：Python requests 的 TLS 指纹被识别，连接被 reset（curl 能成功）。已在 `qtrader/data.py` 切换到新浪源 `stock_zh_a_daily` 为主路径，东财源作为回退。
- **A股代码前缀转换**：纯数字代码自动转新浪格式（`6/9 → sh`、`4/8 → bj`、其余 `sz`），见 `_to_sina_symbol`。

## 学习路径
- [docs/roadmap.html](docs/roadmap.html) — 量化学习四阶段路线图（故事版）
- [docs/roadmap2.html](docs/roadmap2.html) — 路线图速览版（4 列横向）
- [outputs/report.html](outputs/report.html) — 双均线三股对比心得

## 免责声明
仅学习交流，不构成投资建议。
