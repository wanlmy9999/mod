"""
Q-Alpha 详细报告生成系统 — HTML / Markdown / JSON
报告包含：综合评分、技术分析、内幕交易、机构持仓、分析师评级、风险因素、收入结构、投资逻辑
"""

import json, logging
from datetime import datetime
from fastapi import APIRouter, Query, Request
from fastapi.responses import Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from data_sources.provider import get_provider
from ai_engine.analyzer import get_analyzer
from config.settings import settings

logger = logging.getLogger("q-alpha.reports")
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


def _stars(score: float) -> str:
    filled = round(score / 20)
    return "★" * filled + "☆" * (5 - filled)


def _rating_zh(rating: str) -> str:
    return {"BUY": "强烈买入", "HOLD": "持有观望", "SELL": "建议卖出"}.get(rating, rating)


def _risk_level(score: float) -> str:
    if score >= 75: return "低风险"
    if score >= 55: return "中等风险"
    return "较高风险"


def _build_html_report(ticker, analysis, price, info, insider, whales, analyst, revenue, risk_factors) -> str:
    score = analysis.get("score", 0)
    rating = analysis.get("rating", "HOLD")
    rating_zh = _rating_zh(rating)
    color_map = {"BUY": "#00ff88", "HOLD": "#f59e0b", "SELL": "#ff3366"}
    rc = color_map.get(rating, "#8892a4")
    sub = analysis.get("sub_scores", {})
    ind = analysis.get("indicators", {})
    signals = analysis.get("signals", {})
    risks = analysis.get("risks", [])
    mas = ind.get("moving_averages", {})
    macd = ind.get("macd", {})
    now = datetime.now()

    def pct_bar(val):
        c = "#00ff88" if val >= 70 else "#f59e0b" if val >= 50 else "#ff3366"
        return f'<div style="background:#1a2a4a;border-radius:4px;height:6px;overflow:hidden;margin-top:4px"><div style="height:100%;border-radius:4px;background:{c};width:{val}%"></div></div>'

    analyst_rows = "".join(
        f'<tr><td style="padding:6px 8px;color:#c4ccdc;font-size:12px">{a.get("firm","")}</td>'
        f'<td style="padding:6px 8px"><span style="padding:2px 8px;border-radius:4px;font-size:10px;font-weight:700;'
        f'background:{"rgba(0,255,136,0.12)" if "Buy" in a.get("rating","") else "rgba(255,51,102,0.12)" if "Sell" in a.get("rating","") else "rgba(245,158,11,0.12)"};'
        f'color:{"#00ff88" if "Buy" in a.get("rating","") else "#ff3366" if "Sell" in a.get("rating","") else "#f59e0b"}">'
        f'{a.get("rating","")}</span></td>'
        f'<td style="padding:6px 8px;font-family:monospace;color:#c4ccdc;font-size:12px">${a.get("price_target","—")}</td>'
        f'<td style="padding:6px 8px;color:#8892a4;font-size:11px">{a.get("date","")}</td></tr>'
        for a in (analyst or [])[:8]
    )
    insider_rows = "".join(
        f'<tr><td style="padding:6px 8px;color:#c4ccdc;font-size:12px">{r.get("insider_name","")}</td>'
        f'<td style="padding:6px 8px;color:#8892a4;font-size:11px">{r.get("role","")}</td>'
        f'<td style="padding:6px 8px"><span style="padding:2px 7px;border-radius:4px;font-size:10px;font-weight:700;'
        f'background:{"rgba(0,255,136,0.12)" if r.get("action")=="Purchase" else "rgba(255,51,102,0.12)"};'
        f'color:{"#00ff88" if r.get("action")=="Purchase" else "#ff3366"}">'
        f'{"▲ 买入" if r.get("action")=="Purchase" else "▼ 卖出"}</span></td>'
        f'<td style="padding:6px 8px;font-family:monospace;color:#c4ccdc;font-size:12px">{r.get("amount","")}</td>'
        f'<td style="padding:6px 8px;color:#8892a4;font-size:11px">{r.get("date","")}</td></tr>'
        for r in (insider or [])[:8]
    )
    whale_rows = "".join(
        f'<tr><td style="padding:6px 8px;color:#c4ccdc;font-size:12px">{w.get("fund","")}</td>'
        f'<td style="padding:6px 8px;font-family:monospace;font-weight:600;color:#e2e8f0;font-size:12px">{w.get("value","")}</td>'
        f'<td style="padding:6px 8px;font-family:monospace;font-size:12px;color:{"#00ff88" if str(w.get("change","")).startswith("+") else "#ff3366"}">{w.get("change","")}</td>'
        f'<td style="padding:6px 8px;color:#8892a4;font-size:11px">{w.get("filing_date","")}</td></tr>'
        for w in (whales or [])[:6]
    )
    risk_rows = "".join(
        f'<li style="margin:6px 0;color:#c4ccdc;font-size:13px;line-height:1.6">⚠ {r.get("risk","")}'
        f' <span style="font-size:10px;padding:1px 6px;border-radius:3px;background:rgba(245,158,11,0.12);color:#f59e0b;margin-left:6px">{r.get("category","")}</span></li>'
        for r in (risk_factors or [])
    )
    revenue_rows = ""
    if revenue and revenue.get("segments"):
        for seg in revenue["segments"]:
            revenue_rows += f'<div style="margin-bottom:12px"><div style="display:flex;justify-content:space-between;font-size:12px;margin-bottom:4px"><span style="color:#c4ccdc">{seg.get("segment","")}</span><span style="color:#8892a4;font-family:monospace">${seg.get("revenue",0)}B · {seg.get("pct",0)}%</span></div>{pct_bar(seg.get("pct",0))}</div>'

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Q-Alpha 投资研究报告 — ${ticker}</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600;700;800&family=IBM+Plex+Mono:wght@400;500;600&family=Noto+Sans+SC:wght@400;500;700&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{background:#030712;color:#e2e8f0;font-family:"Noto Sans SC","Space Grotesk",sans-serif;padding:0}}
.page{{max-width:900px;margin:0 auto;padding:40px 32px}}
.header{{border-bottom:2px solid #1a2a4a;padding-bottom:28px;margin-bottom:36px;display:flex;justify-content:space-between;align-items:flex-start}}
.logo{{font-size:14px;font-weight:800;color:#00d4ff;letter-spacing:3px}}
.logo span{{color:#00ff88}}
.meta{{text-align:right;font-size:11px;color:#8892a4;font-family:"IBM Plex Mono",monospace;line-height:1.8}}
.ticker{{font-size:56px;font-weight:900;color:#fff;line-height:1;margin:4px 0;font-family:"Space Grotesk",sans-serif}}
.company{{font-size:16px;color:#8892a4;margin-top:4px}}
.score-hero{{display:flex;align-items:center;gap:32px;margin:28px 0;padding:24px;background:#0d1526;border:1px solid #1a2a4a;border-radius:14px}}
.score-num{{font-size:80px;font-weight:900;line-height:1;font-family:"IBM Plex Mono",monospace}}
.rating-badge{{font-size:36px;font-weight:800;font-family:"Space Grotesk",sans-serif}}
.section{{margin-bottom:32px}}
.section-title{{font-size:13px;font-weight:700;color:#00d4ff;letter-spacing:2px;text-transform:uppercase;margin-bottom:14px;padding-bottom:8px;border-bottom:1px solid #1a2a4a;display:flex;align-items:center;gap:8px}}
.grid-2{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.grid-3{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}}
.card{{background:#0d1526;border:1px solid #1a2a4a;border-radius:10px;padding:16px}}
.metric-label{{font-size:10px;color:#8892a4;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:6px}}
.metric-value{{font-size:20px;font-weight:700;font-family:"IBM Plex Mono",monospace}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
th{{font-size:9px;letter-spacing:1.5px;text-transform:uppercase;color:#8892a4;padding:8px;text-align:left;border-bottom:1px solid rgba(26,42,74,0.5)}}
td{{border-bottom:1px solid rgba(26,42,74,0.2)}}
tr:last-child td{{border-bottom:none}}
.explain{{background:#0d1526;border-left:3px solid #00d4ff;border-radius:0 10px 10px 0;padding:16px 20px;margin:16px 0;line-height:1.8;color:#c4ccdc;font-size:13px}}
.explain strong{{color:#00d4ff}}
.risk-list{{background:#0d1526;border-radius:10px;padding:16px;list-style:none}}
.ind-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}}
.ind-box{{background:#0a0f1e;border-radius:8px;padding:12px;text-align:center}}
.ind-label{{font-size:9px;color:#8892a4;letter-spacing:1px;text-transform:uppercase;margin-bottom:6px}}
.ind-val{{font-size:16px;font-weight:700;font-family:"IBM Plex Mono",monospace}}
.footer{{margin-top:48px;padding-top:20px;border-top:1px solid #1a2a4a;color:#8892a4;font-size:11px;line-height:1.8}}
@media print{{body{{background:#fff;color:#000}}.page{{padding:20px}}}}
</style>
</head>
<body>
<div class="page">

<!-- 页眉 -->
<div class="header">
  <div>
    <div class="logo">Q<span>-Alpha</span> 量化智能平台</div>
    <div class="ticker">${ticker}</div>
    <div class="company">{info.get("name", ticker)} · {info.get("sector", "")} · {info.get("industry", "")}</div>
  </div>
  <div class="meta">
    <div>报告类型：个股综合分析报告</div>
    <div>生成时间：{now.strftime("%Y年%m月%d日 %H:%M")}</div>
    <div>数据来源：Yahoo Finance · SEC EDGAR · Finnhub</div>
    <div>报告版本：Q-Alpha v{settings.VERSION}</div>
  </div>
</div>

<!-- 核心评分 -->
<div class="section">
  <div class="section-title">🎯 综合评分与投资建议</div>
  <div class="score-hero">
    <div>
      <div class="score-num" style="color:{rc}">{score}</div>
      <div style="font-size:11px;color:#8892a4;margin-top:4px;font-family:monospace">满分 100 分</div>
    </div>
    <div>
      <div class="rating-badge" style="color:{rc}">{rating_zh}</div>
      <div style="font-size:13px;color:#8892a4;margin-top:6px">风险等级：{_risk_level(score)}</div>
      <div style="font-size:20px;margin-top:6px;letter-spacing:2px" title="综合评级星数">{_stars(score)}</div>
    </div>
    <div style="flex:1;border-left:1px solid #1a2a4a;padding-left:28px">
      <div style="font-size:11px;color:#8892a4;margin-bottom:12px;letter-spacing:1px;text-transform:uppercase">分项评分明细</div>
      {"".join(f'<div style="margin-bottom:10px"><div style="display:flex;justify-content:space-between;font-size:12px"><span style="color:#c4ccdc">{k}</span><span style="font-family:monospace;color:{"#00ff88" if v>=70 else "#f59e0b" if v>=50 else "#ff3366"}">{v}/100</span></div>{pct_bar(v)}</div>' for k, v in sub.items())}
    </div>
  </div>
</div>

<!-- 当前价格 -->
<div class="section">
  <div class="section-title">📈 当前市场数据</div>
  <div class="grid-3">
    {"".join(f'<div class="card"><div class="metric-label">{l}</div><div class="metric-value" style="color:{c}">{v}</div></div>' for l,v,c in [
      ("当前股价", f'${price.get("price","N/A")}', "#e2e8f0"),
      ("单日涨跌", f'{price.get("change_pct",0):+.2f}%', "#00ff88" if (price.get("change_pct") or 0)>=0 else "#ff3366"),
      ("成交量", f'{int(price.get("volume",0)/1e6+0.5)}M', "#8892a4"),
      ("市值", f'${round((info.get("market_cap") or 0)/1e9,1)}B', "#00d4ff"),
      ("市盈率 P/E", str(info.get("pe_ratio","N/A")), "#e2e8f0"),
      ("52周高点", f'${info.get("52w_high","N/A")}', "#00ff88"),
    ])}
    <div class="card"><div class="metric-label">52周低点</div><div class="metric-value" style="color:#ff3366">${info.get("52w_low","N/A")}</div></div>
    <div class="card"><div class="metric-label">Beta 系数</div><div class="metric-value">{info.get("beta","N/A")}</div></div>
    <div class="card"><div class="metric-label">股息率</div><div class="metric-value">{(info.get("dividend_yield") or 0):.2f}%</div></div>
  </div>
</div>

<!-- AI 分析说明 -->
<div class="section">
  <div class="section-title">🤖 AI 分析逻辑解读</div>
  <div class="explain">{analysis.get("explanation","暂无分析内容").replace("**","<strong>").replace("**","</strong>")}</div>
  <div class="grid-2" style="margin-top:16px">
    <div class="card">
      <div class="metric-label" style="margin-bottom:10px">市场信号汇总</div>
      {"".join(f'<div style="display:flex;justify-content:space-between;padding:5px 0;border-bottom:1px solid #1a2a4a22;font-size:12px"><span style="color:#8892a4">{k}</span><span style="color:#c4ccdc">{v}</span></div>' for k,v in signals.items())}
    </div>
    <div class="card">
      <div class="metric-label" style="margin-bottom:10px">风险提示</div>
      {"".join(f'<div style="display:flex;align-items:flex-start;gap:6px;padding:5px 0;border-bottom:1px solid #1a2a4a22;font-size:11px;color:#c4ccdc">{"⚠" if r.get("type")=="warning" else "✓" if r.get("type")=="opportunity" else "ℹ"} {r.get("message","")}</div>' for r in risks) or '<div style="color:#8892a4;font-size:12px">未检测到重大风险信号</div>'}
    </div>
  </div>
</div>

<!-- 技术指标 -->
<div class="section">
  <div class="section-title">📊 技术指标详解</div>
  <div class="ind-grid">
    {"".join(f'<div class="ind-box"><div class="ind-label">{l}</div><div class="ind-val" style="color:{c}">{v}</div><div style="font-size:9px;color:#8892a4;margin-top:4px">{desc}</div></div>' for l,v,c,desc in [
      ("RSI（14）", ind.get("rsi","N/A"), "#f59e0b" if (ind.get("rsi") or 50) > 70 else "#00ff88" if (ind.get("rsi") or 50) < 30 else "#e2e8f0", "超买>70 超卖<30"),
      ("MACD", macd.get("macd","N/A"), "#00ff88" if (macd.get("histogram") or 0)>0 else "#ff3366", "正值看涨 负值看跌"),
      ("MACD 柱", f'{macd.get("histogram","N/A")}', "#00ff88" if (macd.get("histogram") or 0)>0 else "#ff3366", "动能方向指示"),
      ("成交量评分", ind.get("volume_score","N/A"), "#e2e8f0", "相对成交量强度"),
      ("MA20", f'${mas.get("ma20","N/A")}', "#00d4ff", "20日均线"),
      ("MA50", f'${mas.get("ma50","N/A")}', "#a855f7", "50日均线"),
      ("MA200", f'${mas.get("ma200","N/A")}', "#f59e0b", "200日均线"),
      ("当前价格", f'${mas.get("current","N/A")}', "#e2e8f0", "最新收盘价"),
      ("综合评分", score, rc, "AI 复合评分"),
    ])}
  </div>
</div>

<!-- 内幕交易 -->
<div class="section">
  <div class="section-title">🔒 内幕交易记录（SEC Form 4）</div>
  <p style="font-size:12px;color:#8892a4;margin-bottom:12px;line-height:1.7">
    以下为该公司高管、董事及持股5%以上股东在过去60天内向美国证券交易委员会（SEC）申报的交易记录。
    内幕人员大量买入往往被视为看涨信号，大规模卖出则需警惕。
  </p>
  <table>
    <thead><tr><th>内幕人员</th><th>职位</th><th>类型</th><th>金额</th><th>日期</th></tr></thead>
    <tbody>{insider_rows or '<tr><td colspan="5" style="padding:16px;color:#8892a4;text-align:center">暂无近期内幕交易数据</td></tr>'}</tbody>
  </table>
</div>

<!-- 机构持仓 -->
<div class="section">
  <div class="section-title">🐋 机构投资者持仓（13F 披露）</div>
  <p style="font-size:12px;color:#8892a4;margin-bottom:12px;line-height:1.7">
    以下为主要机构投资者根据 SEC 13F 规则披露的持仓情况及近期变动。持仓增加通常代表机构看好该股，持仓减少则需关注。
  </p>
  <table>
    <thead><tr><th>机构名称</th><th>持仓市值</th><th>仓位变动</th><th>申报日期</th></tr></thead>
    <tbody>{whale_rows or '<tr><td colspan="4" style="padding:16px;color:#8892a4;text-align:center">暂无机构持仓数据</td></tr>'}</tbody>
  </table>
</div>

<!-- 分析师评级 -->
<div class="section">
  <div class="section-title">⭐ 华尔街分析师评级</div>
  <p style="font-size:12px;color:#8892a4;margin-bottom:12px;line-height:1.7">
    汇总高盛、摩根士丹利、摩根大通等主要投行分析师对该股的评级与目标价。多数机构给出买入评级通常是正面信号。
  </p>
  <table>
    <thead><tr><th>机构</th><th>评级</th><th>目标价</th><th>日期</th></tr></thead>
    <tbody>{analyst_rows or '<tr><td colspan="4" style="padding:16px;color:#8892a4;text-align:center">暂无分析师评级数据</td></tr>'}</tbody>
  </table>
</div>

<!-- 收入结构 -->
{"" if not (revenue and revenue.get("segments")) else f'''
<div class="section">
  <div class="section-title">💰 营收结构分析（FY{revenue.get("fiscal_year","2024")}）</div>
  <p style="font-size:12px;color:#8892a4;margin-bottom:16px;line-height:1.7">
    该财年公司总营收约 ${revenue.get("total","N/A")}B，以下为各业务板块收入占比。
    了解收入多元化程度有助于判断公司抗风险能力。
  </p>
  {revenue_rows}
</div>
'''}

<!-- 风险因素 -->
{"" if not risk_factors else f'''
<div class="section">
  <div class="section-title">⚠ 主要风险因素（来源：SEC 年报）</div>
  <p style="font-size:12px;color:#8892a4;margin-bottom:12px;line-height:1.7">
    以下风险因素摘自公司最新 10-K 年报风险披露章节，投资者应充分知悉并评估这些潜在风险。
  </p>
  <ul class="risk-list">{risk_rows}</ul>
</div>
'''}

<!-- 公司简介 -->
{"" if not info.get("description") else f'''
<div class="section">
  <div class="section-title">🏢 公司基本情况</div>
  <div style="background:#0d1526;border-radius:10px;padding:16px">
    <div class="grid-2" style="margin-bottom:16px">
      {"".join(f'<div><span style="font-size:10px;color:#8892a4;display:block;margin-bottom:3px">{l}</span><span style="font-size:13px;color:#e2e8f0">{v}</span></div>' for l,v in [
        ("所属行业", info.get("sector","")),
        ("细分领域", info.get("industry","")),
        ("员工人数", f'{(info.get("employees") or 0):,}'),
        ("官方网站", info.get("website","")),
        ("每股收益 EPS", f'${info.get("eps","N/A")}'),
        ("资产负债率", "参见最新财报"),
      ])}
    </div>
    <p style="font-size:12px;color:#c4ccdc;line-height:1.8">{info.get("description","")[:600]}...</p>
  </div>
</div>
'''}

<!-- 投资结论 -->
<div class="section">
  <div class="section-title">📋 投资结论摘要</div>
  <div style="background:#0d1526;border:1px solid {rc}33;border-radius:12px;padding:20px">
    <div style="display:flex;align-items:center;gap:16px;margin-bottom:16px">
      <div style="font-size:48px;font-weight:900;color:{rc};font-family:monospace">{score}</div>
      <div>
        <div style="font-size:24px;font-weight:800;color:{rc};font-family:'Space Grotesk',sans-serif">{rating_zh}</div>
        <div style="font-size:12px;color:#8892a4;margin-top:4px">{_risk_level(score)} · 综合评分 {score}/100 分 · 评级星数 {_stars(score)}</div>
      </div>
    </div>
    <p style="font-size:13px;color:#c4ccdc;line-height:1.9">
      基于技术面（RSI {ind.get("rsi","N/A")}，MACD{"看涨" if (macd.get("histogram") or 0)>0 else "看跌"}），
      内幕信号（{signals.get("insider","中性")}），机构动向（{signals.get("whale","中性")}），
      华尔街评级共识（{signals.get("analyst","中性")}），Q-Alpha AI 引擎给出综合评分 <strong style="color:{rc}">{score}/100</strong>，
      建议操作方向为 <strong style="color:{rc}">{rating_zh}</strong>。
      投资者在作出决策前应结合自身风险承受能力、持仓结构及最新基本面信息进行综合判断。
    </p>
  </div>
</div>

<!-- 页脚 -->
<div class="footer">
  <strong style="color:#00d4ff">免责声明：</strong>
  本报告由 Q-Alpha 量化智能平台基于公开数据自动生成，仅供信息参考，不构成任何投资建议或要约。
  历史数据不代表未来表现，股票市场存在较大风险，投资者须独立判断并对自身投资决策负责。
  本平台不对任何因使用本报告而产生的损失承担责任。<br><br>
  数据来源：Yahoo Finance · SEC EDGAR · Finnhub · Alpha Vantage<br>
  生成时间：{now.isoformat()} · Q-Alpha v{settings.VERSION}
</div>

</div>
</body>
</html>"""


def _build_markdown_report(ticker, analysis, price, info, insider, whales, analyst) -> str:
    score = analysis.get("score", 0)
    rating = analysis.get("rating", "HOLD")
    rating_zh = _rating_zh(rating)
    sub = analysis.get("sub_scores", {})
    ind = analysis.get("indicators", {})
    signals = analysis.get("signals", {})
    risks = analysis.get("risks", [])
    macd = ind.get("macd", {})
    mas = ind.get("moving_averages", {})
    now = datetime.now()

    lines = [
        f"# Q-Alpha 投资研究报告：${ticker}",
        f"",
        f"> 生成时间：{now.strftime('%Y年%m月%d日 %H:%M')} | Q-Alpha v{settings.VERSION} | 数据来源：Yahoo Finance · SEC EDGAR · Finnhub",
        f"",
        f"---",
        f"",
        f"## 一、综合评分与投资建议",
        f"",
        f"| 项目 | 结果 |",
        f"|------|------|",
        f"| AI 综合评分 | **{score} / 100** {_stars(score)} |",
        f"| 投资建议 | **{rating_zh}** |",
        f"| 风险等级 | {_risk_level(score)} |",
        f"| 当前股价 | ${price.get('price','N/A')} |",
        f"| 单日涨跌 | {price.get('change_pct',0):+.2f}% |",
        f"| 市值 | ${round((info.get('market_cap') or 0)/1e9,1)}B |",
        f"",
        f"### 分项评分",
        f"",
        f"| 维度 | 评分 | 说明 |",
        f"|------|------|------|",
    ]
    desc_map = {"technical": "技术面 (RSI/MACD/均线)", "insider": "内幕交易信号", "whale": "机构持仓动向", "analyst": "分析师评级共识"}
    for k, v in sub.items():
        lines.append(f"| {desc_map.get(k, k)} | {v}/100 | {'看涨' if v>=70 else '中性' if v>=50 else '看跌'} |")

    lines += [
        f"",
        f"---",
        f"",
        f"## 二、AI 分析逻辑",
        f"",
        analysis.get("explanation", "暂无分析内容"),
        f"",
        f"---",
        f"",
        f"## 三、技术指标",
        f"",
        f"| 指标 | 数值 | 信号解读 |",
        f"|------|------|---------|",
        f"| RSI（14日） | {ind.get('rsi','N/A')} | {'超买，注意回调风险' if (ind.get('rsi') or 50)>70 else '超卖，关注反弹机会' if (ind.get('rsi') or 50)<30 else '中性区间'} |",
        f"| MACD | {macd.get('macd','N/A')} | {'柱状图为正，动能偏多' if (macd.get('histogram') or 0)>0 else '柱状图为负，动能偏空'} |",
        f"| 成交量评分 | {ind.get('volume_score','N/A')} | {'成交量异常放大，机构参与度高' if (ind.get('volume_score') or 0)>70 else '成交量正常'} |",
        f"| MA20 均线 | ${mas.get('ma20','N/A')} | {'价格高于20日均线，短期趋势向上' if (mas.get('current') or 0)>(mas.get('ma20') or 9999) else '价格低于20日均线'} |",
        f"| MA50 均线 | ${mas.get('ma50','N/A')} | {'中期趋势健康' if (mas.get('current') or 0)>(mas.get('ma50') or 9999) else '中期趋势需观察'} |",
        f"| MA200 均线 | ${mas.get('ma200','N/A')} | {'长期牛市结构完整' if (mas.get('current') or 0)>(mas.get('ma200') or 9999) else '长期趋势存疑'} |",
        f"",
        f"---",
        f"",
        f"## 四、市场信号",
        f"",
    ]
    for k, v in signals.items():
        lines.append(f"- **{k}**：{v}")

    lines += [
        f"",
        f"---",
        f"",
        f"## 五、内幕交易记录",
        f"",
        f"| 内幕人员 | 职位 | 交易类型 | 金额 | 日期 |",
        f"|----------|------|---------|------|------|",
    ]
    for r in (insider or [])[:8]:
        lines.append(f"| {r.get('insider_name','')} | {r.get('role','')} | {'买入' if r.get('action')=='Purchase' else '卖出'} | {r.get('amount','')} | {r.get('date','')} |")

    lines += [
        f"",
        f"---",
        f"",
        f"## 六、机构持仓动向",
        f"",
        f"| 机构 | 持仓市值 | 变动 | 申报日 |",
        f"|------|---------|------|--------|",
    ]
    for w in (whales or [])[:6]:
        lines.append(f"| {w.get('fund','')} | {w.get('value','')} | {w.get('change','')} | {w.get('filing_date','')} |")

    lines += [
        f"",
        f"---",
        f"",
        f"## 七、分析师评级",
        f"",
        f"| 机构 | 评级 | 目标价 | 日期 |",
        f"|------|------|--------|------|",
    ]
    for a in (analyst or [])[:8]:
        lines.append(f"| {a.get('firm','')} | {a.get('rating','')} | ${a.get('price_target','—')} | {a.get('date','')} |")

    lines += [
        f"",
        f"---",
        f"",
        f"## 八、风险提示",
        f"",
    ]
    for r in risks:
        lines.append(f"- **[{r.get('type','').upper()}]** {r.get('message','')}")
    if not risks:
        lines.append("- 未检测到重大风险信号")

    lines += [
        f"",
        f"---",
        f"",
        f"## 九、投资结论",
        f"",
        f"综合上述技术面、资金面及基本面分析，Q-Alpha AI 引擎给出综合评分 **{score}/100**，",
        f"建议操作方向为 **{rating_zh}**，风险等级为 **{_risk_level(score)}**。",
        f"",
        f"---",
        f"",
        f"*免责声明：本报告由 Q-Alpha 量化智能平台自动生成，仅供参考，不构成投资建议。投资有风险，入市需谨慎。*",
    ]
    return "\n".join(lines)


@router.get("/download")
@limiter.limit("5/minute")
async def download_report(
    request: Request,
    ticker: str = Query(...),
    format: str = Query("html", description="html|markdown|json"),
):
    """生成并下载投资分析报告 (HTML / Markdown / JSON)"""
    t = ticker.upper()
    provider = get_provider()
    analyzer = get_analyzer()

    # 并行获取所有数据
    import asyncio
    price_data  = provider.fetch("stock/price", {"ticker": t}, source_type="stock") or {}
    info_data   = provider.fetch("stock/info",  {"ticker": t}, source_type="stock") or {}
    candle_data = provider.fetch("stock/candles", {"ticker": t, "timeframe": "3mo"}, source_type="stock")
    insider_data = provider.fetch("insider",  {"ticker": t}, source_type="sec") or []
    whale_data   = provider.fetch("whales",   {"ticker": t}) or []
    analyst_data = provider.fetch("analyst",  {"ticker": t}) or []
    revenue_data = provider.fetch("revenue",  {"ticker": t}) or {}
    risk_data    = provider.fetch("risk",     {"ticker": t}) or []

    analysis = analyzer.analyze(
        ticker=t,
        candle_data=candle_data,
        insider_data=insider_data if isinstance(insider_data, list) else [],
        whale_data=whale_data if isinstance(whale_data, list) else [],
        analyst_data=analyst_data if isinstance(analyst_data, list) else [],
    )

    if format == "html":
        content = _build_html_report(t, analysis, price_data, info_data, insider_data, whale_data, analyst_data, revenue_data, risk_data)
        return Response(content=content, media_type="text/html",
            headers={"Content-Disposition": f"attachment; filename=qalpha_{t}_report.html"})
    elif format == "markdown":
        content = _build_markdown_report(t, analysis, price_data, info_data, insider_data, whale_data, analyst_data)
        return Response(content=content, media_type="text/markdown",
            headers={"Content-Disposition": f"attachment; filename=qalpha_{t}_report.md"})
    else:
        report = {
            "meta": {"ticker": t, "generated_at": datetime.now().isoformat(), "version": settings.VERSION},
            "price": price_data, "info": info_data, "analysis": analysis,
            "insider_trades": insider_data, "whale_positions": whale_data,
            "analyst_ratings": analyst_data, "revenue": revenue_data, "risk_factors": risk_data,
        }
        return Response(content=json.dumps(report, indent=2, default=str), media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=qalpha_{t}_report.json"})
