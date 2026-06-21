# qtrader · 零依赖 A股量化回测系统

> 配套量化学习四阶段路线图 · 阶段二「建系统」成果

## 是什么

一个零外部依赖（仅 Pandas / NumPy / Matplotlib + akshare）的 A股量化回测框架，支持多策略横向对比，采用向量化引擎避免 K线级别 for 循环。

## 目录结构

```
quantitative_trading/
├── qtrader/          # 主包：数据 / 策略 / 引擎 / 绩效 / 可视化
├── scripts/          # 可执行入口（多策略对比、单策略、HTML 报告）
├── tests/            # pytest 单元测试
├── outputs/          # 回测产物（PNG、HTML）
├── docs/             # 学习路线图（roadmap.html 故事版 + 速览版）
├── learning/         # 系统化课程教材（Phase 1：10 节互动 Jupyter 课）
│   ├── README.md     # 课程总览
│   ├── INDEX.md      # 10 课目录与进度
│   ├── progress.md   # 学习日志
│   └── phase1_foundation/  # 阶段一：金融通识 + Pandas/NumPy + 向量化
└── requirements.txt
```

## 快速开始

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 多策略对比（双均线 vs 海龟 vs 网格）
python -m scripts.run_backtest --code 002594 --save comparison_byd.png

# 3. 单策略（双均线）
python -m scripts.run_dual_ma --code 002594 --save byd.png

# 4. 生成 HTML 学习报告
python -m scripts.build_report

# 5. 跑单元测试
python -m pytest tests/ -v
```

## 三大经典策略

| 策略 | 思路 | 适用场景 |
|------|------|---------|
| **双均线** | MA5 > MA20 持仓 | 趋势市场（高波动优于单边牛） |
| **海龟（唐奇安通道）** | 突破 20 日最高买入，跌破 10 日最低卖出 | 强趋势突破 |
| **网格** | 价格区间等分 10 格，下穿买入上穿卖出 | 震荡区间市场 |

所有策略均：
- 向量化实现（无 K线 for 循环）
- `shift(1)` 避免未来函数
- 统一目标仓位接口（`generate_signals → [0,1]`）

## 如何扩展自定义策略

```python
from qtrader import Strategy, BacktestEngine, fetch_data

class MyStrategy(Strategy):
    name = "我的策略"
    def __init__(self):
        self.params = {}
    def generate_signals(self, df):
        # 返回 [0,1] 的目标仓位 Series
        ...

df = fetch_data("000001", "2020-01-01", "2026-06-18")
engine = BacktestEngine(commission=0.001)
result = engine.run(df, MyStrategy())
print(result.metrics)
```

## 绩效指标

每次回测返回：总收益、年化（252）、最大回撤 + 日期、夏普（rf=3%）、Calmar、年化波动率、买入持有对比。

## 学习路径

**系统化课程**（推荐入门顺序）：
- [learning/](learning/) — Phase 1「打地基」10 节互动 Jupyter 课程
- [learning/INDEX.md](learning/INDEX.md) — 课程目录与进度跟踪
- [learning/README.md](learning/README.md) — 课程使用说明

**路线图与心得**：
- [docs/roadmap.html](docs/roadmap.html) — 完整四阶段学习路线图（故事版）
- [docs/roadmap2.html](docs/roadmap2.html) — 路线图速览版（4 列横向）
- [outputs/report.html](outputs/report.html) — 双均线实验心得（三股对比）

## 免责声明

本仓库仅为学习与交流用途，不构成任何投资建议。量化不能保证盈利，A 股有风险。
