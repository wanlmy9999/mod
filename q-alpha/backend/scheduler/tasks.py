"""
Q-Alpha Scheduler - APScheduler background data refresh tasks.
All external API calls happen here; endpoints only read from cache.
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger("q-alpha.scheduler")
scheduler = BackgroundScheduler(timezone="UTC")

POPULAR_TICKERS = ["AAPL", "TSLA", "NVDA", "MSFT", "GOOGL", "AMZN", "META", "AMD", "PLTR", "COIN"]


# ─── Task Implementations ───────────────────────────────────────────────

def update_stock_prices():
    """Refresh stock prices every 15 seconds."""
    try:
        from data_sources.provider import get_provider
        from cache.redis_cache import cache_set
        from config.settings import settings

        provider = get_provider()
        for ticker in POPULAR_TICKERS:
            data = provider.fetch("stock/price", {"ticker": ticker}, source_type="stock")
            if data:
                cache_set(f"stock:price:{ticker}", data, ttl=settings.CACHE_TTL_STOCK)
        logger.debug("Stock prices refreshed")
    except Exception as e:
        logger.error(f"update_stock_prices error: {e}")


def update_insider_data():
    """Refresh insider trading data every hour."""
    try:
        from data_sources.provider import get_provider
        from cache.redis_cache import cache_set
        from config.settings import settings

        provider = get_provider()
        for ticker in POPULAR_TICKERS:
            data = provider.fetch("insider", {"ticker": ticker}, source_type="sec")
            if data:
                cache_set(f"insider:{ticker}", data, ttl=settings.CACHE_TTL_INSIDER)
        logger.info("Insider data refreshed")
    except Exception as e:
        logger.error(f"update_insider_data error: {e}")


def update_whale_data():
    """Refresh whale/institutional moves every hour."""
    try:
        from data_sources.provider import get_provider
        from cache.redis_cache import cache_set
        from config.settings import settings

        provider = get_provider()
        for ticker in POPULAR_TICKERS:
            data = provider.fetch("whales", {"ticker": ticker})
            if data:
                cache_set(f"whales:{ticker}", data, ttl=settings.CACHE_TTL_WHALE)
        logger.info("Whale data refreshed")
    except Exception as e:
        logger.error(f"update_whale_data error: {e}")


def update_trends_data():
    """Refresh Google Trends every 6 hours."""
    try:
        from data_sources.provider import get_provider
        from cache.redis_cache import cache_set
        from config.settings import settings

        provider = get_provider()
        for keyword in ["AI stocks", "semiconductor", "electric vehicles", "crypto", "NVDA"]:
            data = provider.fetch("trends", {"keyword": keyword})
            if data:
                cache_set(f"trends:{keyword}", data, ttl=settings.CACHE_TTL_TRENDS)
        logger.info("Trends data refreshed")
    except Exception as e:
        logger.error(f"update_trends_data error: {e}")


def update_congress_trades():
    """Refresh congress trading data every hour."""
    try:
        from data_sources.provider import get_provider
        from cache.redis_cache import cache_set
        from config.settings import settings

        provider = get_provider()
        data = provider.fetch("gov/congress-trading", {})
        if data:
            cache_set("gov:congress-trading", data, ttl=settings.CACHE_TTL_POLITICIANS)
        logger.info("Congress trades refreshed")
    except Exception as e:
        logger.error(f"update_congress_trades error: {e}")


def update_market_popular():
    """Refresh popular market tickers hourly."""
    try:
        from data_sources.provider import get_provider
        from cache.redis_cache import cache_set
        from config.settings import settings

        provider = get_provider()
        data = provider.fetch("market/popular", {}, source_type="stock")
        if data:
            cache_set("market:popular", data, ttl=settings.CACHE_TTL_STOCK)
        logger.info("Market popular refreshed")
    except Exception as e:
        logger.error(f"update_market_popular error: {e}")


def run_all_daily():
    """Full daily refresh of slower-updating data."""
    logger.info("Running daily data refresh...")
    update_insider_data()
    update_whale_data()
    update_congress_trades()
    update_trends_data()
    logger.info("Daily refresh complete.")


# ─── Scheduler Setup ────────────────────────────────────────────────────

def start_scheduler():
    """Register all jobs and start scheduler."""
    if scheduler.running:
        return

    # Stock prices: every 30 seconds (be gentle on Yahoo Finance)
    scheduler.add_job(
        update_stock_prices, IntervalTrigger(seconds=30),
        id="stock_prices", name="Stock Price Refresh", replace_existing=True
    )

    # Insider + Whale: every 1 hour
    scheduler.add_job(
        update_insider_data, IntervalTrigger(hours=1),
        id="insider_data", name="Insider Data Refresh", replace_existing=True
    )
    scheduler.add_job(
        update_whale_data, IntervalTrigger(hours=1),
        id="whale_data", name="Whale Data Refresh", replace_existing=True
    )

    # Congress trades: every hour
    scheduler.add_job(
        update_congress_trades, IntervalTrigger(hours=1),
        id="congress_trades", name="Congress Trades Refresh", replace_existing=True
    )

    # Google Trends: every 6 hours
    scheduler.add_job(
        update_trends_data, IntervalTrigger(hours=6),
        id="trends_data", name="Google Trends Refresh", replace_existing=True
    )

    # Full daily refresh at midnight UTC
    scheduler.add_job(
        run_all_daily, "cron", hour=0, minute=0,
        id="daily_refresh", name="Daily Full Refresh"
    )

    scheduler.start()
    logger.info("Scheduler started with all jobs registered")

    # Run initial data population on startup
    try:
        update_market_popular()
        update_stock_prices()
    except Exception as e:
        logger.warning(f"Initial data load error: {e}")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler stopped")
