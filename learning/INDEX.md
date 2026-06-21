# 量化学习课程目录

状态图例：⚪ 未开始 / 🟡 进行中 / ✅ 已完成

## 阶段一 · 打地基（Phase 1 Foundation）

| # | 课题 | 时长 | 状态 |
|---|------|------|------|
| 00 | [环境自检](phase1_foundation/00_setup.ipynb) | 20 min | ⚪ |
| 01 | [股票基础 + A 股规则](phase1_foundation/01_stock_etf_a_share_rules.ipynb) | 60 min | ⚪ |
| 02 | [K 线读图 + DataFrame](phase1_foundation/02_kline_dataframe.ipynb) | 60 min | ⚪ |
| 03 | [量价关系 + 聚合](phase1_foundation/03_volume_aggregation.ipynb) | 60 min | ⚪ |
| 04 | [数据清洗 + 复权 + 多股对齐](phase1_foundation/04_data_cleaning_adjust_align.ipynb) | 75–90 min | ⚪ |
| 05 | [收益率 + 涨停识别](phase1_foundation/05_returns_limit_identification.ipynb) | 60 min | ⚪ |
| 06 | [统计基础 + 交易成本](phase1_foundation/06_statistics_trading_costs.ipynb) | 60 min | ⚪ |
| 07 | [技术指标入门](phase1_foundation/07_technical_indicators.ipynb) | 60 min | ⚪ |
| 08 | [PE 估值 + 行业对比](phase1_foundation/08_pe_valuation_industry.ipynb) | 60 min | ⚪ |
| 09 | [向量化核心习惯](phase1_foundation/09_vectorization.ipynb) | 60 min | ⚪ |
| 10 | [综合项目：股票分析报告](phase1_foundation/10_capstone_stock_analysis.ipynb) | 90–120 min | ⚪ |

**练习答案参考**：[phase1_foundation/exercises/solutions/](phase1_foundation/exercises/solutions/) — ex01~ex09 共 9 份 UTF-8 可独立运行的参考答案。

## 阶段二 · 策略与组合（Phase 2 Strategies）

三大策略原理（DualMA / Turtle / Grid）+ 多股选股 + 组合构建，补齐 Phase 1 最大盲区。

| # | 课题 | 时长 | 状态 |
|---|------|------|------|
| 11 | [双均线择时（DualMA）](phase2_strategies/11_dual_ma_timing.ipynb) | 75 min | ⚪ |
| 12 | [海龟策略（唐奇安通道 + ATR 仓位）](phase2_strategies/12_turtle_donchian_atr.ipynb) | 90 min | ⚪ |
| 13 | [网格策略（Grid Trading）](phase2_strategies/13_grid_strategy.ipynb) | 75 min | ⚪ |
| 14 | [多股选股（价值/动量/低波动因子）](phase2_strategies/14_multi_stock_selection.ipynb) | 90 min | ⚪ |
| 15 | [组合构建（等权/反向波动/Markowitz）](phase2_strategies/15_portfolio_construction.ipynb) | 90 min | ⚪ |

**练习**：[ex14.py](phase2_strategies/exercises/ex14.py) · [ex15.py](phase2_strategies/exercises/ex15.py)

## 学习节奏建议

- 每周 4–5 节，留 1–2 天复习/补练习
- 每节课后练习必须独立完成（可查文档、问 Claude，但不直接抄答案）
- 每 3 节课一次 15 分钟串讲复习

## 依赖关系

```
Phase 1:
00 → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10

Phase 2（前置：Phase 1 全部）:
10 → 11 → 12 → 13 → 14 → 15
        (L11-L13 择时三巨头)   (L14-L15 选股+组合)
```

## 未来阶段（Phase 3+ 路线图占位）

以下主题本课程暂不覆盖，留待后续阶段或用户自学：
- **机器学习 Alpha 因子**：LightGBM、强化学习交易代理
- **事件驱动回测**：限价单、涨跌停拒单、订单簿模拟
- **实盘对接**：券商 API、CTP 期货、低延迟执行
- **A 股衍生品**：可转债打新、股指期货基差套利、期权 Vega 策略
- **精细滑点模型**：成交量比例滑点、TWAP/VWAP 执行
- **多资产组合引擎**：N×T 仓位矩阵、行业中性、风险平价

L04（数据清洗）是 L05/L06/L10 的硬前置，不要跳。
