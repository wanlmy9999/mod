#!/usr/bin/env bash
# Q-Alpha API Test Suite
# Usage: bash test_api.sh [BASE_URL]
# Default BASE_URL: http://localhost:8000

BASE="${1:-http://localhost:8000}"
PASS=0
FAIL=0
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

check() {
  local label="$1"
  local url="$2"
  local method="${3:-GET}"
  local data="$4"

  if [ "$method" = "POST" ]; then
    resp=$(curl -s -o /dev/null -w "%{http_code}" -X POST \
      -H "Content-Type: application/json" \
      -d "$data" "$url" 2>/dev/null)
  else
    resp=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
  fi

  if [ "$resp" = "200" ]; then
    echo -e "  ${GREEN}✅ PASS${NC} [$resp] $label"
    ((PASS++))
  else
    echo -e "  ${RED}❌ FAIL${NC} [$resp] $label"
    ((FAIL++))
  fi
}

echo -e "${CYAN}"
echo "╔══════════════════════════════════════════╗"
echo "║        Q-Alpha API Test Suite            ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"
echo "Target: $BASE"
echo ""

# ── Health ─────────────────────────────────────────────────────
echo "── Core ──────────────────────────────────"
check "Health check"              "$BASE/api/health"
check "API root"                  "$BASE/"
check "OpenAPI docs"              "$BASE/docs"

# ── Stock & Market ──────────────────────────────────────────────
echo ""
echo "── Stock & Market ────────────────────────"
check "Stock price (AAPL)"        "$BASE/api/stock/price?ticker=AAPL"
check "Stock price (TSLA)"        "$BASE/api/stock/price?ticker=TSLA"
check "Stock candles 3mo"         "$BASE/api/stock/candles?ticker=NVDA&timeframe=3mo"
check "Stock candles 1y"          "$BASE/api/stock/candles?ticker=MSFT&timeframe=1y"
check "Stock info"                "$BASE/api/stock/info?ticker=AAPL"
check "Market popular"            "$BASE/api/market/popular"
check "Market news"               "$BASE/api/market/news"

# ── AI Analysis ────────────────────────────────────────────────
echo ""
echo "── AI Analysis ───────────────────────────"
check "AI analyze GET (AAPL)"     "$BASE/api/ai/analyze?ticker=AAPL"
check "AI analyze GET (TSLA)"     "$BASE/api/ai/analyze?ticker=TSLA"
check "AI analyze POST"           "$BASE/api/ai/analyze" "POST" '{"ticker":"NVDA"}'
check "Famous portfolio (Pelosi)" "$BASE/api/portfolio/famous?celebrity_name=Nancy+Pelosi"
check "Famous portfolio (Buffett)" "$BASE/api/portfolio/famous?celebrity_name=Warren+Buffett"

# ── Reports ───────────────────────────────────────────────────
echo ""
echo "── Reports ───────────────────────────────"
check "Report HTML"               "$BASE/api/report/download?ticker=AAPL&format=html"
check "Report Markdown"           "$BASE/api/report/download?ticker=TSLA&format=markdown"
check "Report JSON"               "$BASE/api/report/download?ticker=NVDA&format=json"

# ── Financial & Corporate ──────────────────────────────────────
echo ""
echo "── Financial & Corporate ─────────────────"
check "Insider trading (AAPL)"    "$BASE/api/insider?ticker=AAPL"
check "Whale moves (NVDA)"        "$BASE/api/whales?ticker=NVDA"
check "Institutional (MSFT)"      "$BASE/api/institutional?ticker=MSFT"
check "Analyst ratings (TSLA)"    "$BASE/api/analyst?ticker=TSLA"
check "SEC filings (AAPL)"        "$BASE/api/sec?ticker=AAPL"
check "Revenue breakdown (AAPL)"  "$BASE/api/revenue?ticker=AAPL"
check "Risk factors (TSLA)"       "$BASE/api/risk?ticker=TSLA"
check "ETF holdings (SPY)"        "$BASE/api/etf?ticker=SPY"
check "Stock splits (AAPL)"       "$BASE/api/splits?ticker=AAPL"
check "Google Trends"             "$BASE/api/trends?keyword=AI+stocks"
check "Consumer interest"         "$BASE/api/consumer?keyword=NVDA"
check "Patents (Apple)"           "$BASE/api/patents?company_name=Apple"
check "CNBC picks"                "$BASE/api/media/cnbc"
check "Cramer tracker"            "$BASE/api/media/cramer"
check "App ratings"               "$BASE/api/app-ratings?app_name=Twitter"

# ── Politicians & Government ───────────────────────────────────
echo ""
echo "── Government & Political ────────────────"
check "Politician search"         "$BASE/api/politician/search?name=Pelosi"
check "Congress trading (all)"    "$BASE/api/gov/congress-trading"
check "Congress trading (member)" "$BASE/api/gov/congress-trading?member_name=Nancy+Pelosi"
check "Net worth"                 "$BASE/api/gov/networth?member_name=Nancy+Pelosi"
check "DC Insider Score"          "$BASE/api/gov/insider-score?member_name=Tommy+Tuberville"
check "Lobbying"                  "$BASE/api/gov/lobbying?company_name=Apple"
check "Gov contracts"             "$BASE/api/gov/contracts"
check "Gov spending"              "$BASE/api/gov/spending"
check "Elections"                 "$BASE/api/gov/elections"
check "Fundraising"               "$BASE/api/gov/fundraising?politician_name=Nancy+Pelosi"
check "Corporate donations"       "$BASE/api/gov/corporate-donations?company_name=Google"

# ── Summary ────────────────────────────────────────────────────
echo ""
echo "══════════════════════════════════════════"
echo -e "  Results: ${GREEN}${PASS} passed${NC}  ${RED}${FAIL} failed${NC}  (total $((PASS+FAIL)))"
echo "══════════════════════════════════════════"
echo ""

if [ "$FAIL" -gt 0 ]; then
  echo "⚠️  Some tests failed. Make sure the backend is running:"
  echo "   cd backend && uvicorn main:app --reload --port 8000"
  exit 1
else
  echo "🎉 All tests passed!"
fi
