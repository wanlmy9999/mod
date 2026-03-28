# Q-Alpha — Financial AI Intelligence Platform

Bloomberg + TradingView aesthetics · AI-powered scoring · Multi-source data aggregation · Zero login required

---

## Overview

Q-Alpha is a full-stack quantitative financial analysis platform that aggregates data from 12+ sources, runs multi-factor AI scoring on any stock, and surfaces political, insider, and institutional intelligence — all within a premium dark-mode UI requiring no login or subscription.

**Design reference:** Quiver Quantitative (quiverquant.com)
**UI style:** Bloomberg Terminal × TradingView × Glassmorphism
**Stack:** Next.js 14 · FastAPI · Redis · APScheduler · ECharts · Framer Motion

---

## Quick Start (5 minutes)

Works immediately with zero API keys — rich mock data is automatically used as fallback.

### Without Docker

**Backend:**
```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend (new terminal):**
```bash
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000

### With Docker Compose

```bash
cp .env.example .env   # edit optional API keys
docker compose up -d
```

- Frontend  →  http://localhost:3000
- Backend   →  http://localhost:8000
- API Docs  →  http://localhost:8000/docs

---

## API Key Configuration

Add keys to `backend/config/api_keys.json` or set as environment variables. Leave any field blank to fall back to mock data for that source.

```json
{
  "finnhub":              "your_finnhub_key",
  "alpha_vantage":        "",
  "reddit_client_id":     "your_reddit_id",
  "reddit_client_secret": "your_reddit_secret",
  "opensecrets":          "your_opensecrets_key"
}
```

SEC EDGAR and Yahoo Finance (yfinance) require no keys.

---

## Project Structure

```
q-alpha/
├── backend/
│   ├── main.py                        # FastAPI entry point + lifespan
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings.py                # Config + key loading
│   │   └── api_keys.json              # ← Your API keys go here
│   ├── api/
│   │   ├── market.py                  # /api/market/*
│   │   ├── politicians.py             # /api/politician/*, /api/gov/*
│   │   ├── financial.py               # /api/insider, /api/whales, etc.
│   │   ├── ai_analysis.py             # /api/stock/*, /api/ai/analyze
│   │   └── reports.py                 # /api/report/download
│   ├── ai_engine/
│   │   └── analyzer.py                # RSI · MACD · Composite scoring
│   ├── data_sources/
│   │   ├── provider.py                # Orchestrator with fallback
│   │   ├── yahoo_provider.py          # Yahoo Finance (yfinance)
│   │   ├── sec_provider.py            # SEC EDGAR public API
│   │   └── mock_provider.py           # Rich mock data (always available)
│   ├── cache/
│   │   └── redis_cache.py             # Redis + in-memory fallback
│   └── scheduler/
│       └── tasks.py                   # APScheduler background refresh
│
├── frontend/
│   ├── pages/
│   │   ├── index.tsx                  # Dashboard
│   │   ├── search.tsx                 # Fuzzy search
│   │   ├── ai-analysis.tsx            # AI engine interface
│   │   ├── data.tsx                   # Data hub
│   │   ├── congress-trading.tsx       # Congress trading
│   │   ├── politicians.tsx            # Politician profiles
│   │   ├── insider.tsx                # Insider transactions
│   │   ├── whales.tsx                 # Institutional moves
│   │   ├── reports.tsx                # Report generator
│   │   └── stock/[ticker].tsx         # Stock detail (chart + tabs)
│   ├── components/
│   │   ├── layout/Layout.tsx          # Sidebar + top bar
│   │   ├── charts/CandlestickChart.tsx
│   │   ├── ai/AIScoreCard.tsx
│   │   ├── dashboard/TickerTape.tsx
│   │   └── common/StockSearch.tsx
│   ├── lib/
│   │   ├── api.ts                     # Typed API client
│   │   └── utils.ts                   # Formatters
│   └── styles/globals.css             # Design system (neon/glass)
│
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## Full API Reference

### Stock & Market

| Endpoint | Method | Params | Cache |
|---|---|---|---|
| `/api/stock/price` | GET | `ticker` | 15s |
| `/api/stock/candles` | GET | `ticker, timeframe` | 15s–5m |
| `/api/stock/info` | GET | `ticker` | 1h |
| `/api/market/popular` | GET | — | 15s |
| `/api/market/news` | GET | — | 5m |

### AI Analysis

| Endpoint | Method | Params |
|---|---|---|
| `/api/ai/analyze` | POST | `{"ticker":"AAPL"}` |
| `/api/ai/analyze` | GET | `ticker` |
| `/api/portfolio/famous` | GET | `celebrity_name` |
| `/api/report/download` | GET | `ticker, format` (html/markdown/json) |

### Government & Political

| Endpoint | Key Param |
|---|---|
| `/api/politician/search` | `name` |
| `/api/gov/congress-trading` | `member_name?` |
| `/api/gov/networth` | `member_name` |
| `/api/gov/insider-score` | `member_name` |
| `/api/gov/elections` | `year?` |
| `/api/gov/fundraising` | `politician_name` |
| `/api/gov/lobbying` | `company_name` |
| `/api/gov/contracts` | `agency_name?` |
| `/api/gov/spending` | `agency_name?` |
| `/api/gov/corporate-donations` | `company_name` |

### Financial & Corporate

`/api/insider` · `/api/whales` · `/api/institutional` · `/api/analyst` · `/api/sec` · `/api/revenue` · `/api/risk` · `/api/etf` · `/api/splits` · `/api/trends` · `/api/consumer` · `/api/patents` · `/api/media/cnbc` · `/api/media/cramer` · `/api/app-ratings`

All accept `ticker` or `keyword` / `company_name` as appropriate.

---

## API Test Commands

```bash
# Health
curl http://localhost:8000/api/health

# Stock price
curl "http://localhost:8000/api/stock/price?ticker=AAPL"

# Candlestick data
curl "http://localhost:8000/api/stock/candles?ticker=NVDA&timeframe=3mo"

# AI Analysis (POST)
curl -X POST http://localhost:8000/api/ai/analyze \
  -H "Content-Type: application/json" \
  -d '{"ticker":"TSLA"}'

# AI Analysis (GET)
curl "http://localhost:8000/api/ai/analyze?ticker=MSFT"

# Congress trading
curl "http://localhost:8000/api/gov/congress-trading"
curl "http://localhost:8000/api/gov/congress-trading?member_name=Nancy+Pelosi"

# DC Insider Score
curl "http://localhost:8000/api/gov/insider-score?member_name=Nancy+Pelosi"

# Politician search
curl "http://localhost:8000/api/politician/search?name=Pelosi"

# Insider trading
curl "http://localhost:8000/api/insider?ticker=NVDA"

# Whale moves
curl "http://localhost:8000/api/whales?ticker=AAPL"

# Google Trends
curl "http://localhost:8000/api/trends?keyword=AI+stocks"

# Famous portfolio
curl "http://localhost:8000/api/portfolio/famous?celebrity_name=Warren+Buffett"

# Download reports
curl "http://localhost:8000/api/report/download?ticker=AAPL&format=html"     -o aapl_report.html
curl "http://localhost:8000/api/report/download?ticker=TSLA&format=markdown" -o tsla_report.md
curl "http://localhost:8000/api/report/download?ticker=NVDA&format=json"     -o nvda_report.json
```

---

## AI Scoring Engine

The composite score (0–100) weights four signal categories:

```
Score = Technical (40%) + Insider (25%) + Whale (20%) + Analyst (15%)
```

**Technical** uses RSI (overbought/oversold), MACD histogram direction, and price relative to MA20/50/200. **Insider** maps buy/sell ratio from SEC Form 4 filings to a sentiment score. **Whale** detects institutional accumulation vs. distribution from 13F/13D position changes. **Analyst** converts consensus ratings (Strong Buy → Strong Sell) to a normalized score.

Scores ≥ 72 map to BUY, 50–71 to HOLD, and below 50 to SELL. Each analysis also returns a natural-language explanation and flagged risk conditions.

---

## Data Update Strategy

All user-facing endpoints read exclusively from cache. Background refresh jobs handle external API calls on a safe schedule that avoids rate limits and bans.

| Data Type | Scheduler Interval |
|---|---|
| Stock prices | 30 seconds |
| Insider / Whale | 1 hour |
| Congress trades | 1 hour |
| Google Trends | 6 hours |
| Revenue / Contracts | 24 hours |

---

## Adding a New Data Source

Create `backend/data_sources/my_provider.py` implementing `BaseProvider`, register it in `DataProvider.__init__`, add a scheduler job, and add an API route. The core application code is never modified.

---

## Deployment

**Vercel + Railway (recommended free tier):**
```bash
# Frontend → Vercel
cd frontend && npx vercel deploy
# Set NEXT_PUBLIC_API_URL=https://your-api.railway.app

# Backend → Railway
# Connect GitHub repo, set env vars, deploy
```

**Docker production:**
```bash
docker compose --profile production up -d
```

---

*Disclaimer: Q-Alpha is for informational and educational purposes only. Nothing on this platform constitutes financial advice. Always conduct your own due diligence.*
