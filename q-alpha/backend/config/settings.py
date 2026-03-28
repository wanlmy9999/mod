"""
Q-Alpha Configuration & API Key Management
All API keys loaded from environment variables or config file.
Never hardcoded.
"""

import os
import json
import logging
from pathlib import Path

logger = logging.getLogger("q-alpha.config")

CONFIG_PATH = Path(__file__).parent / "api_keys.json"


def load_api_keys() -> dict:
    """Load API keys from environment or config file."""
    keys = {
        "yahoo": "",
        "finnhub": "",
        "alpha_vantage": "",
        "reddit_client_id": "",
        "reddit_client_secret": "",
        "google_trends": "",
        "sec": "",
        "opensecrets": "",
        "usaspending": "",
        "eulerpool": "",
    }

    # Load from config file if exists
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH) as f:
                file_keys = json.load(f)
                keys.update(file_keys)
        except Exception as e:
            logger.warning(f"Could not load api_keys.json: {e}")

    # Environment variables override config file
    env_map = {
        "YAHOO_API_KEY": "yahoo",
        "FINNHUB_API_KEY": "finnhub",
        "ALPHA_VANTAGE_API_KEY": "alpha_vantage",
        "REDDIT_CLIENT_ID": "reddit_client_id",
        "REDDIT_CLIENT_SECRET": "reddit_client_secret",
        "SEC_API_KEY": "sec",
        "OPENSECRETS_API_KEY": "opensecrets",
        "USASPENDING_API_KEY": "usaspending",
        "EULERPOOL_API_KEY": "eulerpool",
    }

    for env_var, key_name in env_map.items():
        val = os.getenv(env_var)
        if val:
            keys[key_name] = val

    return keys


class Settings:
    # App
    APP_NAME = "Q-Alpha"
    VERSION = "1.0.0"
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"

    # Redis
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_ENABLED = os.getenv("REDIS_ENABLED", "true").lower() == "true"

    # Database
    DATABASE_URL = os.getenv(
        "DATABASE_URL", "postgresql://qalpha:qalpha@localhost:5432/qalpha"
    )

    # Cache TTLs (seconds)
    CACHE_TTL_STOCK = 15
    CACHE_TTL_INSIDER = 3600        # 1 hour
    CACHE_TTL_WHALE = 3600          # 1 hour
    CACHE_TTL_TRENDS = 21600        # 6 hours
    CACHE_TTL_POLITICIANS = 3600    # 1 hour
    CACHE_TTL_DAILY = 86400         # 24 hours
    CACHE_TTL_AI = 300              # 5 min

    # Rate limiting
    RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT", "60"))

    # API Keys
    API_KEYS = load_api_keys()

    @classmethod
    def has_key(cls, key_name: str) -> bool:
        return bool(cls.API_KEYS.get(key_name))


settings = Settings()
