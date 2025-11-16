"""
Configuration settings for StockSense AI Backend
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Environment
    ENV: str = os.getenv("ENV", "development")

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@postgres-db:5432/stocksense"

    # Redis Cache
    REDIS_URL: str = "redis://redis-cache:6379/0"
    REDIS_ENABLED: bool = True

    # API Keys (optional, for premium features)
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    FINNHUB_API_KEY: Optional[str] = None
    NEWS_API_KEY: Optional[str] = None

    # AWS Settings
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    BEDROCK_MODEL_ID: str = "amazon.titan-text-lite-v1"

    # Application
    APP_NAME: str = "StockSense AI"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # Security
    SECRET_KEY: str = "dev-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"

    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://127.0.0.1:3000", "http://frontend:3000"]

    # Cache settings (in seconds)
    CACHE_STOCK_DATA_TTL: int = 900  # 15 minutes
    CACHE_STOCK_HISTORY_TTL: int = 1800  # 30 minutes
    CACHE_NEWS_TTL: int = 600  # 10 minutes

    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60

    # Email (optional, for alerts)
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: Optional[str] = None

    # Production settings
    MAX_WORKERS: int = 4

    class Config:
        env_file = ".env"
        case_sensitive = True

    @property
    def is_production(self) -> bool:
        return self.ENV == "production"

    @property
    def is_development(self) -> bool:
        return self.ENV == "development"


settings = Settings()
