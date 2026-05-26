"""Configuration management for AI-Trader.

Loads and validates environment variables from .env file,
providing a centralized config object used throughout the application.
"""

import os
from dataclasses import dataclass, field
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


@dataclass
class LLMConfig:
    """Configuration for the Language Model backend."""
    provider: str          # e.g. 'openai', 'anthropic', 'deepseek'
    model: str             # e.g. 'gpt-4o', 'claude-3-5-sonnet'
    api_key: str
    base_url: Optional[str] = None
    temperature: float = 0.0
    max_tokens: int = 4096


@dataclass
class MarketDataConfig:
    """Configuration for market data sources."""
    finnhub_api_key: Optional[str] = None
    alpha_vantage_api_key: Optional[str] = None
    polygon_api_key: Optional[str] = None
    # Default data source priority order
    sources: list = field(default_factory=lambda: ["finnhub", "alpha_vantage", "polygon"])


@dataclass
class TradingConfig:
    """Configuration for trading parameters."""
    initial_cash: float = 100_000.0
    max_position_size: float = 0.2      # Max 20% of portfolio per position
    stop_loss_pct: float = 0.05         # 5% stop loss
    take_profit_pct: float = 0.15       # 15% take profit
    trading_fee_pct: float = 0.001      # 0.1% per trade
    allow_short: bool = False


@dataclass
class AppConfig:
    """Top-level application configuration."""
    llm: LLMConfig
    market_data: MarketDataConfig
    trading: TradingConfig
    log_level: str = "INFO"
    data_dir: str = "./data"
    results_dir: str = "./results"


def _require_env(key: str) -> str:
    """Retrieve a required environment variable or raise an error."""
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(
            f"Required environment variable '{key}' is not set. "
            f"Please check your .env file against .env.example."
        )
    return value


def load_config() -> AppConfig:
    """Build and return the application configuration from environment variables."""

    llm_config = LLMConfig(
        provider=os.getenv("LLM_PROVIDER", "openai"),
        model=os.getenv("LLM_MODEL", "gpt-4o"),
        api_key=_require_env("LLM_API_KEY"),
        base_url=os.getenv("LLM_BASE_URL"),  # Optional custom endpoint
        temperature=float(os.getenv("LLM_TEMPERATURE", "0.0")),
        max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4096")),
    )

    market_data_config = MarketDataConfig(
        finnhub_api_key=os.getenv("FINNHUB_API_KEY"),
        alpha_vantage_api_key=os.getenv("ALPHA_VANTAGE_API_KEY"),
        polygon_api_key=os.getenv("POLYGON_API_KEY"),
    )

    trading_config = TradingConfig(
        initial_cash=float(os.getenv("INITIAL_CASH", "100000.0")),
        max_position_size=float(os.getenv("MAX_POSITION_SIZE", "0.2")),
        stop_loss_pct=float(os.getenv("STOP_LOSS_PCT", "0.05")),
        take_profit_pct=float(os.getenv("TAKE_PROFIT_PCT", "0.15")),
        trading_fee_pct=float(os.getenv("TRADING_FEE_PCT", "0.001")),
        allow_short=os.getenv("ALLOW_SHORT", "false").lower() == "true",
    )

    return AppConfig(
        llm=llm_config,
        market_data=market_data_config,
        trading=trading_config,
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        data_dir=os.getenv("DATA_DIR", "./data"),
        results_dir=os.getenv("RESULTS_DIR", "./results"),
    )


# Module-level singleton — import `config` directly in other modules
config: AppConfig = load_config()
