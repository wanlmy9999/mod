# Q-Alpha 全流程烟雾测试报告

- 生成时间(UTC): `2026-03-28T08:51:21.443030+00:00`
- 测试总数: **27**
- 通过: **27**
- 失败: **0**

## 来源分布

- `unknown`: 21
- `mock`: 2
- `composite`: 2
- `scraper-proxy`: 2

## 明细

| 用例 | 方法 | 路径 | 状态 | 来源 | 耗时(ms) | 说明 |
|---|---|---|---|---|---:|---|
| 健康检查 | GET | `/api/health` | ✅ 200 | `unknown` | 2 | ok |
| 热门股票 | GET | `/api/market/popular` | ✅ 200 | `mock` | 92 | ok |
| 市场新闻 | GET | `/api/market/news` | ✅ 200 | `unknown` | 820 | ok |
| 股票价格 | GET | `/api/stock/price?ticker=AAPL` | ✅ 200 | `mock` | 4 | ok |
| 股票信息 | GET | `/api/stock/info?ticker=AAPL` | ✅ 200 | `unknown` | 23 | ok |
| 股票K线 | GET | `/api/stock/candles?ticker=AAPL&timeframe=3mo` | ✅ 200 | `unknown` | 27 | ok |
| AI分析POST | POST | `/api/ai/analyze` | ✅ 200 | `composite` | 33 | ok |
| AI分析GET | GET | `/api/ai/analyze?ticker=NVDA` | ✅ 200 | `composite` | 40 | ok |
| 内幕交易 | GET | `/api/insider?ticker=NVDA` | ✅ 200 | `unknown` | 7 | ok |
| 大资金 | GET | `/api/whales?ticker=AAPL` | ✅ 200 | `unknown` | 2 | ok |
| 机构持仓 | GET | `/api/institutional?ticker=MSFT` | ✅ 200 | `unknown` | 809 | ok |
| 分析师评级 | GET | `/api/analyst?ticker=TSLA` | ✅ 200 | `unknown` | 8 | ok |
| SEC文件 | GET | `/api/sec?ticker=AAPL` | ✅ 200 | `unknown` | 2 | ok |
| 风险因素 | GET | `/api/risk?ticker=AAPL` | ✅ 200 | `unknown` | 2 | ok |
| 营收拆分 | GET | `/api/revenue?ticker=AAPL` | ✅ 200 | `unknown` | 2 | ok |
| ETF持仓 | GET | `/api/etf?ticker=QQQ` | ✅ 200 | `unknown` | 2 | ok |
| 拆股记录 | GET | `/api/splits?ticker=AAPL` | ✅ 200 | `unknown` | 8 | ok |
| 趋势代理 | GET | `/api/trends?keyword=AI+stocks` | ✅ 200 | `scraper-proxy` | 1616 | ok |
| 消费者热度 | GET | `/api/consumer?keyword=tesla` | ✅ 200 | `scraper-proxy` | 1619 | ok |
| 国会交易 | GET | `/api/gov/congress-trading?member_name=Pelosi` | ✅ 200 | `unknown` | 1618 | ok |
| 政治人物搜索 | GET | `/api/politician/search?name=Pelosi` | ✅ 200 | `unknown` | 3 | ok |
| 游说数据 | GET | `/api/gov/lobbying?company_name=Apple` | ✅ 200 | `unknown` | 809 | ok |
| 政府支出 | GET | `/api/gov/spending?agency_name=DoD` | ✅ 200 | `unknown` | 3 | ok |
| 选举数据 | GET | `/api/gov/elections?year=2026` | ✅ 200 | `unknown` | 2 | ok |
| 募资数据 | GET | `/api/gov/fundraising?politician_name=Nancy+Pelosi` | ✅ 200 | `unknown` | 2 | ok |
| 公司捐赠 | GET | `/api/gov/corporate-donations?company_name=Apple` | ✅ 200 | `unknown` | 2 | ok |
| 名人组合 | GET | `/api/portfolio/famous?celebrity_name=Warren+Buffett` | ✅ 200 | `unknown` | 3 | ok |