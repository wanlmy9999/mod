"""
Q-Alpha 全流程烟雾测试
- 自动拉起后端
- 依次调用主要页面/按钮对应 API
- 统计来源 meta（API/爬虫/mock）
- 输出 Markdown 报告
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests


ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = ROOT / "reports" / "smoke_test_report.md"
BASE_URL = "http://127.0.0.1:8020"


@dataclass
class CheckResult:
    name: str
    method: str
    path: str
    ok: bool
    status_code: int
    selected_source: str
    message: str
    elapsed_ms: int


CHECKS = [
    ("健康检查", "GET", "/api/health"),
    ("热门股票", "GET", "/api/market/popular"),
    ("市场新闻", "GET", "/api/market/news"),
    ("股票价格", "GET", "/api/stock/price?ticker=AAPL"),
    ("股票信息", "GET", "/api/stock/info?ticker=AAPL"),
    ("股票K线", "GET", "/api/stock/candles?ticker=AAPL&timeframe=3mo"),
    ("AI分析POST", "POST", "/api/ai/analyze"),
    ("AI分析GET", "GET", "/api/ai/analyze?ticker=NVDA"),
    ("内幕交易", "GET", "/api/insider?ticker=NVDA"),
    ("大资金", "GET", "/api/whales?ticker=AAPL"),
    ("机构持仓", "GET", "/api/institutional?ticker=MSFT"),
    ("分析师评级", "GET", "/api/analyst?ticker=TSLA"),
    ("SEC文件", "GET", "/api/sec?ticker=AAPL"),
    ("风险因素", "GET", "/api/risk?ticker=AAPL"),
    ("营收拆分", "GET", "/api/revenue?ticker=AAPL"),
    ("ETF持仓", "GET", "/api/etf?ticker=QQQ"),
    ("拆股记录", "GET", "/api/splits?ticker=AAPL"),
    ("趋势代理", "GET", "/api/trends?keyword=AI+stocks"),
    ("消费者热度", "GET", "/api/consumer?keyword=tesla"),
    ("国会交易", "GET", "/api/gov/congress-trading?member_name=Pelosi"),
    ("政治人物搜索", "GET", "/api/politician/search?name=Pelosi"),
    ("游说数据", "GET", "/api/gov/lobbying?company_name=Apple"),
    ("政府支出", "GET", "/api/gov/spending?agency_name=DoD"),
    ("选举数据", "GET", "/api/gov/elections?year=2026"),
    ("募资数据", "GET", "/api/gov/fundraising?politician_name=Nancy+Pelosi"),
    ("公司捐赠", "GET", "/api/gov/corporate-donations?company_name=Apple"),
    ("名人组合", "GET", "/api/portfolio/famous?celebrity_name=Warren+Buffett"),
]


def _start_server() -> subprocess.Popen:
    env = os.environ.copy()
    env["REDIS_ENABLED"] = "false"
    proc = subprocess.Popen(
        ["python", "-m", "uvicorn", "main:app", "--port", "8020"],
        cwd=str(ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return proc


def _wait_until_ready(timeout_sec: int = 60) -> None:
    start = time.time()
    while time.time() - start < timeout_sec:
        try:
            r = requests.get(f"{BASE_URL}/api/health", timeout=2)
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError("Backend did not become ready in time.")


def _extract_source(payload: Any) -> str:
    if isinstance(payload, dict):
        meta = payload.get("meta", {})
        if isinstance(meta, dict):
            s = meta.get("selected_source")
            if s:
                return str(s)
    return "unknown"


def _run_check(name: str, method: str, path: str) -> CheckResult:
    url = f"{BASE_URL}{path}"
    start = time.perf_counter()
    try:
        if method == "GET":
            resp = requests.get(url, timeout=25)
        else:
            resp = requests.post(url, json={"ticker": "AAPL"}, timeout=25)
        elapsed = int((time.perf_counter() - start) * 1000)
        if resp.headers.get("content-type", "").startswith("application/json"):
            payload = resp.json()
        else:
            payload = {"raw": resp.text[:200]}
        source = _extract_source(payload)
        ok = resp.status_code == 200 and ("data" in payload or path.endswith("/api/health"))
        msg = "ok" if ok else f"unexpected response: {str(payload)[:140]}"
        return CheckResult(name, method, path, ok, resp.status_code, source, msg, elapsed)
    except Exception as e:
        elapsed = int((time.perf_counter() - start) * 1000)
        return CheckResult(name, method, path, False, 0, "error", str(e), elapsed)


def _write_report(results: list[CheckResult], source_counter: Counter) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    total = len(results)
    passed = sum(1 for r in results if r.ok)
    lines = [
        "# Q-Alpha 全流程烟雾测试报告",
        "",
        f"- 生成时间(UTC): `{now}`",
        f"- 测试总数: **{total}**",
        f"- 通过: **{passed}**",
        f"- 失败: **{total - passed}**",
        "",
        "## 来源分布",
        "",
    ]
    for src, c in source_counter.most_common():
        lines.append(f"- `{src}`: {c}")
    lines += ["", "## 明细", "", "| 用例 | 方法 | 路径 | 状态 | 来源 | 耗时(ms) | 说明 |", "|---|---|---|---|---|---:|---|"]
    for r in results:
        state = "✅" if r.ok else "❌"
        lines.append(
            f"| {r.name} | {r.method} | `{r.path}` | {state} {r.status_code} | `{r.selected_source}` | {r.elapsed_ms} | {r.message} |"
        )
    REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    proc = _start_server()
    try:
        _wait_until_ready()
        results: list[CheckResult] = []
        sources = Counter()
        for item in CHECKS:
            r = _run_check(*item)
            results.append(r)
            sources[r.selected_source] += 1
        _write_report(results, sources)
        print(f"[OK] Report written: {REPORT_PATH}")
        print(json.dumps({"total": len(results), "passed": sum(1 for x in results if x.ok)}, ensure_ascii=False))
        return 0 if all(r.ok for r in results) else 1
    finally:
        if proc.poll() is None:
            proc.send_signal(signal.SIGINT)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
