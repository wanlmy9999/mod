"""
Q-Alpha Financial AI Platform - Backend Entry Point
FastAPI application with CORS, Redis caching, and all route mounting.
"""

import os
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from api.market import router as market_router
from api.politicians import router as politicians_router
from api.financial import router as financial_router
from api.ai_analysis import router as ai_router
from api.reports import router as reports_router
from scheduler.tasks import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("q-alpha")

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown lifecycle."""
    logger.info("🚀 Q-Alpha starting up...")
    start_scheduler()
    yield
    logger.info("🛑 Q-Alpha shutting down...")
    stop_scheduler()


app = FastAPI(
    title="Q-Alpha Financial AI API",
    description="Quantitative financial analysis & AI decision platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(market_router, prefix="/api/market", tags=["Market"])
app.include_router(politicians_router, prefix="/api", tags=["Politicians & Government"])
app.include_router(financial_router, prefix="/api", tags=["Financial & Corporate"])
app.include_router(ai_router, prefix="/api", tags=["AI Analysis"])
app.include_router(reports_router, prefix="/api/report", tags=["Reports"])


@app.get("/")
async def root():
    return {
        "name": "Q-Alpha API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "q-alpha-backend"}


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
