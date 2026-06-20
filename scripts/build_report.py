"""生成双均线策略学习心得的 HTML 报告（单文件，图片 base64 内嵌）。

运行：python -m scripts.build_report
"""
from __future__ import annotations

import base64
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"


def embed_png(path: Path) -> str:
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{data}"


HTML = r"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>双均线策略实验 — 量化学习笔记</title>
<style>
:root{
  --bg:#0d1117; --surface:#161b22; --surface-2:#1c2330;
  --border:#2d3441; --text:#e6edf3; --text-muted:#8b949e;
  --gold:#d4a056; --gold-bright:#f0c674;
  --green:#4ade80; --red:#f87171;
}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg); color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,"PingFang SC","Microsoft YaHei",system-ui,sans-serif;
  line-height:1.75; font-size:16px; padding:40px 20px;}
.container{max-width:920px; margin:0 auto}
.hero{padding:80px 0 60px; border-bottom:1px solid var(--border); margin-bottom:60px}
.hero .eyebrow{font-family:"JetBrains Mono",Consolas,monospace; font-size:12px;
  letter-spacing:0.2em; text-transform:uppercase; color:var(--gold); margin-bottom:20px}
.hero h1{font-family:Georgia,serif; font-size:clamp(34px,5vw,56px); line-height:1.2;
  font-weight:700; margin-bottom:24px}
.hero .subtitle{font-size:19px; color:var(--text-muted); margin-bottom:40px; max-width:680px}
.hero .meta{display:flex; gap:32px; font-family:monospace; font-size:13px;
  color:var(--text-muted); flex-wrap:wrap}
.hero .meta strong{color:var(--text); font-weight:500}
section{padding:48px 0; border-bottom:1px solid var(--border)}
.section-number{font-family:monospace; font-size:12px; color:var(--gold);
  letter-spacing:0.1em; margin-bottom:10px}
h2{font-family:Georgia,serif; font-size:32px; font-weight:700; margin-bottom:24px}
p{margin-bottom:16px}
.quote{border-left:3px solid var(--gold); padding:16px 24px; margin:24px 0;
  font-style:italic; font-size:18px;
  background:linear-gradient(90deg,rgba(212,160,86,0.06) 0%, transparent 100%);}
.stock-card{background:var(--surface); border:1px solid var(--border);
  border-radius:12px; padding:32px; margin:32px 0}
.stock-card.win{border-left:4px solid var(--green)}
.stock-card.lose{border-left:4px solid var(--red)}
.stock-card.neutral{border-left:4px solid var(--gold)}
.stock-card .stock-name{font-size:24px; font-weight:700}
.stock-card img{width:100%; border-radius:6px; margin:16px 0; background:white; display:block}
.truth{text-align:center; padding:60px 24px; margin:40px 0;
  background:linear-gradient(180deg,var(--surface) 0%,var(--bg) 100%);
  border-radius:16px; border:1px solid var(--border)}
.truth .big{font-family:Georgia,serif; font-size:clamp(22px,3vw,32px); line-height:1.5;
  max-width:720px; margin:0 auto}
.truth .highlight{color:var(--gold-bright); font-style:italic}
footer{text-align:center; padding:60px 0 20px; color:var(--text-muted); font-size:13px}
footer p{margin-bottom:8px}
</style>
</head>
<body>
<div class="container">

<div class="hero">
  <div class="eyebrow">Quant Learning · Experiment 01</div>
  <h1>双均线策略实验<br>—— 三只股票里的量化真相</h1>
  <p class="subtitle">一个量化新手用 Claude Code 搭建回测系统，在比亚迪、世纪华通、完美世界上跑了同一个策略，意外发现：同一个"金叉/死叉"，在三种股票上演绎出三种截然不同的结局。</p>
  <div class="meta">
    <div><strong>时间</strong> · 2020-01-02 ~ 2026-06-18</div>
    <div><strong>策略</strong> · MA5 / MA20 双均线</div>
    <div><strong>交易日</strong> · 1564</div>
  </div>
</div>

<section>
  <div class="section-number">01 · 起点与洞察</div>
  <h2>从一个朴素的问题开始</h2>
  <p>"5 日均线上穿 20 日均线就买入，下穿就卖出" —— 这是每一本量化入门书都会讲的<strong>双均线策略</strong>。听起来简单，但能不能真的赚钱？在什么股票上管用？又为什么？</p>
  <div class="quote">
    双均线策略不是"万能赚钱机器"，而是一个"择时工具"。<br>
    它的价值不取决于策略本身，而取决于<strong>标的价格行为模式</strong>。
  </div>
  <p>选股比择时更重要，识别市场状态比预测价格更重要。</p>
</section>

<section>
  <div class="section-number">02 · 三只股票三种命运</div>
  <h2>实验结果</h2>

  <div class="stock-card neutral">
    <div class="stock-name">比亚迪 · 002594</div>
    <div style="color:var(--text-muted); font-size:14px; margin:6px 0 12px;">长期牛市 · 策略跑输（+254% vs B&amp;H +466%）</div>
    <img src="__BYD_IMG__" alt="比亚迪">
  </div>

  <div class="stock-card win">
    <div class="stock-name">世纪华通 · 002602</div>
    <div style="color:var(--text-muted); font-size:14px; margin:6px 0 12px;">高波动 · 教科书级胜利（+340% vs B&amp;H +28%）</div>
    <img src="__SHJT_IMG__" alt="世纪华通">
  </div>

  <div class="stock-card lose">
    <div class="stock-name">完美世界 · 002624</div>
    <div style="color:var(--text-muted); font-size:14px; margin:6px 0 12px;">长期下行 · 策略减亏（-27% vs B&amp;H -55%）</div>
    <img src="__WMSJ_IMG__" alt="完美世界">
  </div>
</section>

<div class="truth">
  <p class="big">
    双均线策略不是 <span class="highlight">"万能赚钱机器"</span>，<br>
    而是一个 <span class="highlight">"择时工具"</span>。
  </p>
</div>

<footer>
  <p>双均线策略实验 · 量化学习笔记 #01</p>
  <p>2026 年 6 月 · 使用 Claude Code 辅助完成</p>
  <p style="margin-top:18px; font-size:11px; opacity:0.6;">本报告仅为学习与交流用途，不构成任何投资建议。</p>
</footer>

</div>
</body>
</html>
"""


def main() -> int:
    images = {
        "__BYD_IMG__": "backtest_byd.png",
        "__SHJT_IMG__": "backtest_shjt.png",
        "__WMSJ_IMG__": "backtest_wmsj.png",
    }
    html = HTML
    for placeholder, filename in images.items():
        path = OUTPUTS / filename
        if not path.exists():
            print(f"[错误] 缺少图片: {path}")
            return 1
        html = html.replace(placeholder, embed_png(path))
        print(f"[图片] 已嵌入 {filename}")

    output = OUTPUTS / "report.html"
    output.write_text(html, encoding="utf-8")
    size_kb = len(html.encode("utf-8")) / 1024
    print(f"[完成] 已生成 {output} ({size_kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
