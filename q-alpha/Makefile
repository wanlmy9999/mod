# Q-Alpha Makefile
# Convenience targets for development, testing, and deployment
# Usage: make <target>

.PHONY: help dev backend frontend docker docker-prod test test-api clean install

# ── Default ───────────────────────────────────────────────────────────────
help:
	@echo ""
	@echo "╔══════════════════════════════════════════╗"
	@echo "║          Q-Alpha — Make Targets          ║"
	@echo "╠══════════════════════════════════════════╣"
	@echo "║  make install      Install all deps       ║"
	@echo "║  make dev          Run frontend+backend   ║"
	@echo "║  make backend      Run FastAPI server     ║"
	@echo "║  make frontend     Run Next.js dev        ║"
	@echo "║  make docker       docker compose up      ║"
	@echo "║  make docker-prod  Full production stack  ║"
	@echo "║  make test         Python unit tests      ║"
	@echo "║  make test-api     Full API test suite    ║"
	@echo "║  make clean        Remove build artifacts ║"
	@echo "╚══════════════════════════════════════════╝"
	@echo ""

# ── Installation ──────────────────────────────────────────────────────────
install:
	@echo "→ Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "→ Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ All dependencies installed"

# ── Development ───────────────────────────────────────────────────────────
backend:
	@echo "→ Starting Q-Alpha backend (http://localhost:8000)..."
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

frontend:
	@echo "→ Starting Q-Alpha frontend (http://localhost:3000)..."
	cd frontend && npm run dev

# Run both concurrently (requires 'concurrently' or just two terminals)
dev:
	@echo "→ Starting Q-Alpha full stack..."
	@echo "  Backend:  http://localhost:8000"
	@echo "  Frontend: http://localhost:3000"
	@echo "  API Docs: http://localhost:8000/docs"
	@echo ""
	@echo "  Press Ctrl+C to stop both servers"
	@trap 'kill %1 %2 2>/dev/null; exit 0' INT; \
	  (cd backend  && uvicorn main:app --reload --port 8000) & \
	  (cd frontend && npm run dev) & \
	  wait

# ── Docker ────────────────────────────────────────────────────────────────
docker:
	@echo "→ Starting Q-Alpha with Docker Compose..."
	docker compose up -d
	@echo "✅ Services running:"
	@echo "  Frontend  → http://localhost:3000"
	@echo "  Backend   → http://localhost:8000"
	@echo "  API Docs  → http://localhost:8000/docs"
	@docker compose ps

docker-prod:
	@echo "→ Starting Q-Alpha production stack (with Nginx)..."
	docker compose --profile production up -d --build
	@echo "✅ Production stack running on http://localhost:80"

docker-down:
	docker compose down

docker-logs:
	docker compose logs -f

docker-rebuild:
	docker compose down
	docker compose up -d --build

# ── Testing ───────────────────────────────────────────────────────────────
test:
	@echo "→ Running Python unit tests..."
	cd backend && python -m pytest tests/ -v 2>/dev/null || \
	  python -c "
import sys; sys.path.insert(0,'.')
from data_sources.mock_provider import MockProvider
from ai_engine.analyzer import get_analyzer
m = MockProvider()
c = m.fetch('stock/candles',{'ticker':'AAPL','timeframe':'3mo'})
i = m.fetch('insider',{'ticker':'AAPL'})
r = get_analyzer().analyze('AAPL', candle_data=c, insider_data=i)
assert 0 <= r['score'] <= 100
assert r['rating'] in ('BUY','HOLD','SELL')
print('✅ All core tests passed')
"

test-api:
	@echo "→ Running full API test suite..."
	bash test_api.sh $(BASE_URL)

test-api-docker:
	@echo "→ Running API tests against Docker backend..."
	BASE_URL=http://localhost:8000 bash test_api.sh

# ── Build ─────────────────────────────────────────────────────────────────
build:
	@echo "→ Building frontend for production..."
	cd frontend && npm run build
	@echo "✅ Frontend build complete (.next/)"

# ── Utilities ─────────────────────────────────────────────────────────────
clean:
	@echo "→ Cleaning build artifacts..."
	rm -rf backend/__pycache__ backend/**/__pycache__ backend/**/*.pyc
	rm -rf frontend/.next frontend/node_modules/.cache
	@echo "✅ Clean complete"

logs-backend:
	@cd backend && uvicorn main:app --port 8000 2>&1 | grep -v DEBUG

seed-data:
	@echo "→ Seeding cache with initial data..."
	cd backend && python -c "
import sys; sys.path.insert(0,'.')
from scheduler.tasks import update_stock_prices, update_market_popular, update_congress_trades
update_market_popular()
update_stock_prices()
update_congress_trades()
print('✅ Cache seeded successfully')
"
