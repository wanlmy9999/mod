"""
Q-Alpha Mock Data Provider
Provides realistic sample data when real API keys are not configured.
Ensures the UI is always populated and functional.
"""

import random
import logging
from datetime import datetime, timedelta
from typing import Any, Optional


logger = logging.getLogger("q-alpha.mock")

MOCK_STOCKS = {
    "AAPL": {"name": "Apple Inc.", "sector": "Technology", "base_price": 189.5},
    "TSLA": {"name": "Tesla, Inc.", "sector": "Automotive", "base_price": 248.3},
    "NVDA": {"name": "NVIDIA Corp", "sector": "Semiconductors", "base_price": 875.4},
    "MSFT": {"name": "Microsoft Corp", "sector": "Technology", "base_price": 415.2},
    "GOOGL": {"name": "Alphabet Inc.", "sector": "Technology", "base_price": 174.8},
    "AMZN": {"name": "Amazon.com Inc.", "sector": "E-Commerce", "base_price": 202.1},
    "META": {"name": "Meta Platforms", "sector": "Social Media", "base_price": 521.6},
    "AMD": {"name": "Advanced Micro Devices", "sector": "Semiconductors", "base_price": 162.3},
    "PLTR": {"name": "Palantir Technologies", "sector": "Software", "base_price": 24.8},
    "COIN": {"name": "Coinbase Global", "sector": "Fintech", "base_price": 243.7},
}

MOCK_POLITICIANS = [
    {"name": "Nancy Pelosi", "party": "Democrat", "chamber": "House", "state": "CA", "score": 94},
    {"name": "Marjorie Taylor Greene", "party": "Republican", "chamber": "House", "state": "GA", "score": 78},
    {"name": "J.D. Vance", "party": "Republican", "chamber": "Senate", "state": "OH", "score": 85},
    {"name": "Mark Warner", "party": "Democrat", "chamber": "Senate", "state": "VA", "score": 71},
    {"name": "Tommy Tuberville", "party": "Republican", "chamber": "Senate", "state": "AL", "score": 88},
    {"name": "Dan Goldman", "party": "Democrat", "chamber": "House", "state": "NY", "score": 65},
    {"name": "Ro Khanna", "party": "Democrat", "chamber": "House", "state": "CA", "score": 72},
    {"name": "Michael McCaul", "party": "Republican", "chamber": "House", "state": "TX", "score": 80},
]

MOCK_CONGRESS_TRADES = [
    {"politician": "Nancy Pelosi", "ticker": "NVDA", "action": "Purchase", "amount": "$500K-$1M", "date": "2024-01-15", "party": "Democrat"},
    {"politician": "Tommy Tuberville", "ticker": "TSLA", "action": "Purchase", "amount": "$1M-$5M", "date": "2024-01-22", "party": "Republican"},
    {"politician": "Marjorie Taylor Greene", "ticker": "AMZN", "action": "Sale", "amount": "$100K-$250K", "date": "2024-02-01", "party": "Republican"},
    {"politician": "Dan Goldman", "ticker": "AAPL", "action": "Purchase", "amount": "$250K-$500K", "date": "2024-02-08", "party": "Democrat"},
    {"politician": "Mark Warner", "ticker": "MSFT", "action": "Purchase", "amount": "$500K-$1M", "date": "2024-02-14", "party": "Democrat"},
    {"politician": "J.D. Vance", "ticker": "META", "action": "Purchase", "amount": "$100K-$250K", "date": "2024-02-20", "party": "Republican"},
    {"politician": "Ro Khanna", "ticker": "AMD", "action": "Purchase", "amount": "$50K-$100K", "date": "2024-03-01", "party": "Democrat"},
    {"politician": "Michael McCaul", "ticker": "PLTR", "action": "Sale", "amount": "$250K-$500K", "date": "2024-03-10", "party": "Republican"},
]

NEWS_FEED = [
    {"title": "Congress Trade: Representative Nancy Pelosi Just Disclosed New Stock Trades", "category": "Congress", "time": "2h ago", "ticker": "NVDA"},
    {"title": "Insider Purchase: CEO of $NVDA Buys 50,000 Shares Worth $43M", "category": "Insider", "time": "3h ago", "ticker": "NVDA"},
    {"title": "Whale Move: $1.2B Position in $MSFT Disclosed via 13D Filing", "category": "Whale", "time": "4h ago", "ticker": "MSFT"},
    {"title": "Lobbying Update: $3,200,000 of APPLE INC lobbying disclosed this quarter", "category": "Lobbying", "time": "5h ago", "ticker": "AAPL"},
    {"title": "Congress Trade: Senator Tommy Tuberville Buys TSLA Worth $1M-$5M", "category": "Congress", "time": "6h ago", "ticker": "TSLA"},
    {"title": "Analyst Upgrade: Goldman Sachs raises $NVDA to Strong Buy, PT $1100", "category": "Analyst", "time": "8h ago", "ticker": "NVDA"},
    {"title": "SEC Filing: $AMZN Revenue Breakdown Shows Cloud at 67% YoY Growth", "category": "SEC", "time": "1d ago", "ticker": "AMZN"},
    {"title": "Government Contract: $META awarded $450M DoD cloud contract", "category": "Contract", "time": "1d ago", "ticker": "META"},
]


class MockProvider:
    name = "mock"

    def is_available(self) -> bool:
        return True

    def fetch(self, endpoint: str, params: dict) -> Optional[Any]:
        ticker = params.get("ticker", "AAPL").upper()

        handlers = {
            "stock/price": lambda: self._price(ticker),
            "stock/candles": lambda: self._candles(ticker, params.get("timeframe", "3mo")),
            "stock/info": lambda: self._info(ticker),
            "market/popular": lambda: self._popular(),
            "market/news": lambda: NEWS_FEED,
            "insider": lambda: self._insider(ticker),
            "whales": lambda: self._whales(ticker),
            "institutional": lambda: self._institutional(ticker),
            "analyst": lambda: self._analyst(ticker),
            "sec": lambda: self._sec_filings(ticker),
            "etf": lambda: self._etf(ticker),
            "splits": lambda: self._splits(ticker),
            "risk": lambda: self._risk(ticker),
            "revenue": lambda: self._revenue(ticker),
            "trends": lambda: self._trends(params.get("keyword", ticker)),
            "consumer": lambda: self._trends(params.get("keyword", ticker)),
            "politician/search": lambda: self._politicians(params.get("name", "")),
            "gov/congress-trading": lambda: self._congress_trades(params.get("member_name", "")),
            "gov/networth": lambda: self._networth(params.get("member_name", "")),
            "gov/insider-score": lambda: self._insider_score(params.get("member_name", "")),
            "gov/lobbying": lambda: self._lobbying(params.get("company_name", ticker)),
            "gov/contracts": lambda: self._contracts(params.get("agency_name", "")),
            "gov/spending": lambda: self._spending(params.get("agency_name", "")),
            "gov/elections": lambda: self._elections(),
            "gov/fundraising": lambda: self._fundraising(params.get("politician_name", "")),
            "gov/corporate-donations": lambda: self._corp_donations(params.get("company_name", "")),
            "patents": lambda: self._patents(params.get("company_name", ticker)),
            "media/cnbc": lambda: self._cnbc_picks(),
            "media/cramer": lambda: self._cramer_picks(),
            "app-ratings": lambda: self._app_ratings(params.get("app_name", "")),
            "portfolio/famous": lambda: self._famous_portfolio(params.get("celebrity_name", "")),
        }

        handler = handlers.get(endpoint)
        if handler:
            return handler()
        return {"error": "Unknown endpoint", "endpoint": endpoint}

    def _price(self, ticker: str) -> dict:
        base = MOCK_STOCKS.get(ticker, {}).get("base_price", 100.0)
        change = round(random.uniform(-5, 8), 2)
        price = round(base + change, 2)
        return {
            "ticker": ticker,
            "name": MOCK_STOCKS.get(ticker, {}).get("name", ticker),
            "price": price,
            "change": change,
            "change_pct": round(change / base * 100, 2),
            "volume": random.randint(10_000_000, 80_000_000),
            "market_cap": int(base * random.randint(1_000_000_000, 10_000_000_000)),
            "day_high": round(price + random.uniform(0, 3), 2),
            "day_low": round(price - random.uniform(0, 3), 2),
            "source": "mock",
        }

    def _candles(self, ticker: str, timeframe: str) -> dict:
        days_map = {"1d": 1, "5d": 5, "1mo": 30, "3mo": 90, "6mo": 180, "1y": 365, "5y": 1825}
        days = days_map.get(timeframe, 90)
        base = MOCK_STOCKS.get(ticker, {}).get("base_price", 100.0)
        candles = []
        price = base * 0.85
        now = datetime.now()
        for i in range(days):
            date = now - timedelta(days=days - i)
            change_pct = random.uniform(-0.03, 0.035)
            open_p = round(price, 2)
            close_p = round(price * (1 + change_pct), 2)
            high_p = round(max(open_p, close_p) * (1 + random.uniform(0, 0.015)), 2)
            low_p = round(min(open_p, close_p) * (1 - random.uniform(0, 0.015)), 2)
            volume = random.randint(20_000_000, 100_000_000)
            candles.append({
                "time": int(date.timestamp() * 1000),
                "open": open_p,
                "high": high_p,
                "low": low_p,
                "close": close_p,
                "volume": volume,
            })
            price = close_p
        return {"ticker": ticker, "timeframe": timeframe, "candles": candles}

    def _info(self, ticker: str) -> dict:
        stock = MOCK_STOCKS.get(ticker, {"name": ticker, "sector": "Technology", "base_price": 100})
        return {
            "ticker": ticker,
            "name": stock["name"],
            "sector": stock["sector"],
            "industry": stock["sector"],
            "description": f"{stock['name']} is a leading company in the {stock['sector']} sector.",
            "employees": random.randint(10000, 200000),
            "website": f"https://www.{ticker.lower()}.com",
            "pe_ratio": round(random.uniform(15, 60), 1),
            "eps": round(random.uniform(2, 12), 2),
            "dividend_yield": round(random.uniform(0, 2.5), 2),
            "52w_high": round(stock["base_price"] * 1.35, 2),
            "52w_low": round(stock["base_price"] * 0.65, 2),
            "avg_volume": random.randint(30_000_000, 100_000_000),
            "beta": round(random.uniform(0.8, 2.2), 2),
            "market_cap": int(stock["base_price"] * random.randint(5_000_000_000, 20_000_000_000)),
        }

    def _popular(self) -> list:
        return [self._price(t) for t in list(MOCK_STOCKS.keys())[:8]]

    def _insider(self, ticker: str) -> list:
        names = ["Elon Musk", "Tim Cook", "Satya Nadella", "Jensen Huang", "Lisa Su"]
        roles = ["CEO", "CFO", "COO", "Director", "VP"]
        actions = ["Purchase", "Sale", "Exercise"]
        result = []
        for i in range(8):
            result.append({
                "ticker": ticker,
                "insider_name": random.choice(names),
                "role": random.choice(roles),
                "action": random.choice(actions),
                "shares": random.randint(1000, 100000),
                "price": round(random.uniform(80, 400), 2),
                "amount": f"${random.randint(100, 5000)}K",
                "date": str((datetime.now() - timedelta(days=random.randint(1, 60))).date()),
            })
        return result

    def _whales(self, ticker: str) -> list:
        funds = ["Vanguard Group", "BlackRock Inc", "Berkshire Hathaway", "State Street", "Fidelity"]
        result = []
        for f in funds:
            result.append({
                "ticker": ticker,
                "fund": f,
                "shares": random.randint(1_000_000, 100_000_000),
                "value": f"${round(random.uniform(100, 5000), 1)}M",
                "change": f"{random.choice(['+', '-'])}{round(random.uniform(0.5, 15), 1)}%",
                "filing_date": str((datetime.now() - timedelta(days=random.randint(1, 45))).date()),
            })
        return result

    def _institutional(self, ticker: str) -> list:
        return self._whales(ticker)

    def _analyst(self, ticker: str) -> list:
        firms = ["Goldman Sachs", "Morgan Stanley", "JPMorgan", "Bank of America", "Citi", "UBS"]
        ratings = ["Strong Buy", "Buy", "Neutral", "Sell"]
        result = []
        for firm in firms:
            result.append({
                "ticker": ticker,
                "firm": firm,
                "rating": random.choice(ratings),
                "price_target": round(random.uniform(100, 600), 0),
                "date": str((datetime.now() - timedelta(days=random.randint(1, 30))).date()),
            })
        return result

    def _sec_filings(self, ticker: str) -> list:
        forms = ["10-K", "10-Q", "8-K", "DEF 14A"]
        result = []
        for i in range(6):
            result.append({
                "ticker": ticker,
                "form": random.choice(forms),
                "date": str((datetime.now() - timedelta(days=i * 30)).date()),
                "description": f"Quarterly/Annual Report Filing",
                "url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={ticker}",
            })
        return result

    def _etf(self, ticker: str) -> dict:
        holdings = [
            {"symbol": "AAPL", "holding_percent": 7.8},
            {"symbol": "MSFT", "holding_percent": 7.2},
            {"symbol": "NVDA", "holding_percent": 5.1},
            {"symbol": "AMZN", "holding_percent": 4.9},
            {"symbol": "GOOGL", "holding_percent": 4.3},
        ]
        return {"ticker": ticker, "holdings": holdings, "total_assets": "$450B", "expense_ratio": "0.03%"}

    def _splits(self, ticker: str) -> list:
        return [
            {"date": "2020-08-31", "ratio": 4.0},
            {"date": "2014-06-09", "ratio": 7.0},
        ] if ticker == "AAPL" else []

    def _risk(self, ticker: str) -> list:
        risks = [
            "Competition from major technology companies may adversely affect revenue growth.",
            "Global supply chain disruptions could impact product availability and margins.",
            "Regulatory changes in key markets may impose additional operational constraints.",
            "Foreign currency fluctuations expose the company to exchange rate risk.",
            "Cybersecurity threats could compromise customer data and damage brand reputation.",
        ]
        return [{"risk": r, "category": random.choice(["Market", "Operational", "Regulatory", "Financial"])} for r in risks]

    def _revenue(self, ticker: str) -> dict:
        segments = {
            "AAPL": [
                {"segment": "iPhone", "revenue": 205.5, "pct": 52},
                {"segment": "Services", "revenue": 91.2, "pct": 23},
                {"segment": "Mac", "revenue": 29.4, "pct": 7},
                {"segment": "iPad", "revenue": 28.3, "pct": 7},
                {"segment": "Wearables", "revenue": 39.8, "pct": 10},
            ]
        }
        return {"ticker": ticker, "fiscal_year": "2024", "total": 395.0,
                "segments": segments.get(ticker, [{"segment": "Core Revenue", "revenue": 100, "pct": 100}])}

    def _trends(self, keyword: str) -> dict:
        data = []
        now = datetime.now()
        for i in range(52):
            date = now - timedelta(weeks=52 - i)
            data.append({
                "date": str(date.date()),
                "interest": random.randint(20, 100),
            })
        return {"keyword": keyword, "data": data, "peak": max(d["interest"] for d in data)}

    def _politicians(self, name: str) -> list:
        if name:
            filtered = [p for p in MOCK_POLITICIANS if name.lower() in p["name"].lower()]
            return filtered if filtered else MOCK_POLITICIANS[:3]
        return MOCK_POLITICIANS

    def _congress_trades(self, member_name: str) -> list:
        if member_name:
            return [t for t in MOCK_CONGRESS_TRADES if member_name.lower() in t["politician"].lower()]
        return MOCK_CONGRESS_TRADES

    def _networth(self, member_name: str) -> dict:
        base = random.uniform(500_000, 50_000_000)
        return {
            "politician": member_name or "Unknown",
            "estimated_net_worth": round(base, 0),
            "stock_holdings": round(base * 0.4, 0),
            "real_estate": round(base * 0.35, 0),
            "other_assets": round(base * 0.25, 0),
            "last_updated": str(datetime.now().date()),
        }

    def _insider_score(self, member_name: str) -> dict:
        score = random.randint(55, 98)
        politician = next((p for p in MOCK_POLITICIANS if member_name.lower() in p["name"].lower()), None)
        return {
            "politician": member_name,
            "dc_insider_score": score,
            "rank": random.randint(1, 535),
            "trading_performance": f"+{round(random.uniform(15, 120), 1)}%",
            "trades_count": random.randint(5, 80),
            "benchmark": "S&P 500",
            "alpha": round(random.uniform(5, 40), 1),
        }

    def _lobbying(self, company: str) -> list:
        issues = ["Technology Regulation", "Tax Policy", "Trade", "Healthcare", "Defense", "Environment"]
        return [{"company": company, "amount": f"${round(random.uniform(0.5, 10), 1)}M",
                 "issue": i, "year": 2024} for i in random.sample(issues, 3)]

    def _contracts(self, agency: str) -> list:
        agencies = ["DoD", "HHS", "NASA", "DHS", "DoE"]
        companies = ["Lockheed Martin", "Raytheon", "Boeing", "Northrop", "General Dynamics"]
        return [{"agency": random.choice(agencies), "company": random.choice(companies),
                 "amount": f"${round(random.uniform(10, 500), 0)}M",
                 "description": "Defense/Technology contract", "date": str((datetime.now() - timedelta(days=random.randint(1, 90))).date())}
                for _ in range(8)]

    def _spending(self, agency: str) -> list:
        return [{"agency": agency or "DoD", "amount": f"${round(random.uniform(100, 5000), 0)}M",
                 "category": c, "fiscal_year": 2024}
                for c in ["Personnel", "Operations", "Procurement", "R&D"]]

    def _elections(self) -> list:
        return [
            {"state": "PA", "race": "Senate", "candidate_d": "Bob Casey", "candidate_r": "Dave McCormick", "lean": "Tossup"},
            {"state": "AZ", "race": "Senate", "candidate_d": "Ruben Gallego", "candidate_r": "Kari Lake", "lean": "Lean D"},
            {"state": "OH", "race": "Senate", "candidate_d": "Sherrod Brown", "candidate_r": "Bernie Moreno", "lean": "Lean R"},
        ]

    def _fundraising(self, politician: str) -> dict:
        return {
            "politician": politician, "total_raised": f"${round(random.uniform(1, 50), 1)}M",
            "top_donors": ["Alphabet", "Microsoft", "Goldman Sachs", "JPMorgan"],
            "individual_contributions": f"${round(random.uniform(0.5, 20), 1)}M",
            "pac_contributions": f"${round(random.uniform(0.5, 10), 1)}M",
        }

    def _corp_donations(self, company: str) -> list:
        return [{"company": company, "recipient": p["name"], "amount": f"${random.randint(5000, 100000)}",
                 "party": p["party"], "year": 2024} for p in random.sample(MOCK_POLITICIANS, 4)]

    def _patents(self, company: str) -> list:
        return [{"patent_id": f"US{random.randint(10000000, 19999999)}", "title": f"Novel AI/ML Method {i}",
                 "company": company, "date": str((datetime.now() - timedelta(days=i * 30)).date()),
                 "status": "Granted"} for i in range(5)]

    def _cnbc_picks(self) -> list:
        return [{"show": "Mad Money", "ticker": t, "action": random.choice(["Buy", "Sell", "Hold"]),
                 "host": "Jim Cramer", "date": str((datetime.now() - timedelta(days=random.randint(0, 7))).date())}
                for t in ["AAPL", "NVDA", "TSLA", "MSFT", "META"]]

    def _cramer_picks(self) -> list:
        return self._cnbc_picks()

    def _app_ratings(self, app_name: str) -> dict:
        return {
            "app_name": app_name, "ios_rating": round(random.uniform(3.5, 4.9), 1),
            "android_rating": round(random.uniform(3.5, 4.9), 1),
            "ios_reviews": random.randint(100000, 5000000),
            "android_reviews": random.randint(100000, 10000000),
            "trend": random.choice(["improving", "stable", "declining"]),
        }

    def _famous_portfolio(self, celebrity: str) -> dict:
        celebs = {
            "nancy pelosi": {"name": "Nancy Pelosi", "holdings": [
                {"ticker": "NVDA", "shares": 50000, "value": "$43.7M", "return": "+156%"},
                {"ticker": "MSFT", "shares": 10000, "value": "$4.1M", "return": "+32%"},
                {"ticker": "AAPL", "shares": 25000, "value": "$4.7M", "return": "+18%"},
            ]},
            "warren buffett": {"name": "Warren Buffett", "holdings": [
                {"ticker": "AAPL", "shares": 905_560_000, "value": "$171B", "return": "+810%"},
                {"ticker": "BAC", "shares": 1_032_852_006, "value": "$35B", "return": "+52%"},
                {"ticker": "AXP", "shares": 151_610_700, "value": "$28B", "return": "+121%"},
            ]},
        }
        key = celebrity.lower()
        return celebs.get(key, {"name": celebrity, "holdings": [
            {"ticker": t, "shares": random.randint(1000, 100000), "value": f"${round(random.uniform(0.1, 50), 1)}M",
             "return": f"+{round(random.uniform(5, 200), 0)}%"}
            for t in ["AAPL", "NVDA", "MSFT"]
        ]})
