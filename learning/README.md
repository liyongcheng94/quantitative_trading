# 量化学习路径

本目录是 `qtrader` 项目配套的系统化学习材料，按 roadmap 的四阶段推进。

## 阶段一：打地基（1.5–2 周）— 进行中

**目标**：理解 A 股市场基本规则，掌握 Pandas/NumPy 金融场景应用，养成向量化思维。

**载体**：10 节 Jupyter Notebook 互动课，每节 45–90 分钟。

**位置**：[phase1_foundation/](phase1_foundation/)

**课程目录与进度**：见 [INDEX.md](INDEX.md)

**你的学习日志**：[progress.md](progress.md)

## 如何上课

1. 打开当节 `.ipynb`，按 7 段结构往下走（元信息 → 概念 → 数据 → 演示 → 小练 → 习题 → tip）
2. 演示部分逐 cell 运行，遇到不懂的 API 立即问 Claude
3. 课后练习在 `exercises/exNN.py` 里独立完成，完成后请 Claude 审阅打分
4. 进度由 Claude 在 `progress.md` 维护

## 环境准备

首次使用前：

```bash
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m jupyter lab
```

然后打开 [phase1_foundation/00_setup.ipynb](phase1_foundation/00_setup.ipynb) 做环境自检。

## 免责

所有内容仅用于学习交流，不构成投资建议。
