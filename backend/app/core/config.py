import json
from typing import List, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # Application Settings
    PROJECT_NAME: str = "Prospect Digital Analyzer"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "default_secret_key_change_in_production"

    # CORS Settings
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if not v.startswith("["):
                return [i.strip() for i in v.split(",") if i.strip()]
            try:
                return json.loads(v)
            except Exception:
                return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    # Database Configuration (PostgreSQL)
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres_password"
    POSTGRES_DB: str = "prospect_analyzer_db"
    
    DATABASE_URL: Union[str, None] = None
    DATABASE_URL_SYNC: Union[str, None] = None

    @property
    def async_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def sync_database_url(self) -> str:
        if self.DATABASE_URL_SYNC:
            return self.DATABASE_URL_SYNC
        return (
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    # Redis & Celery Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_URL: Union[str, None] = None

    @property
    def redis_connection_url(self) -> str:
        if self.REDIS_URL:
            return self.REDIS_URL
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    CELERY_BROKER_URL: Union[str, None] = None
    CELERY_RESULT_BACKEND: Union[str, None] = None

    @property
    def celery_broker(self) -> str:
        return self.CELERY_BROKER_URL or self.redis_connection_url

    @property
    def celery_backend(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.redis_connection_url

    # External APIs
    PAGESPEED_API_KEY: str = ""
    SEMRUSH_API_KEY: str = ""
    HUNTER_API_KEY: str = ""
    HUBSPOT_ACCESS_TOKEN: str = ""

    # Internal Crawler Service Constants
    CRAWLER_CONCURRENT_REQUESTS_PER_DOMAIN: int = 2
    CRAWLER_DELAY_BETWEEN_REQUESTS_SECONDS: float = 1.5
    CRAWLER_CONCURRENT_DOMAINS_BATCH: int = 5
    CRAWLER_MAX_PAGES_PER_SITE: int = 20
    CRAWLER_MAX_DEPTH: int = 2
    CRAWLER_REQUEST_TIMEOUT_SECONDS: float = 10.0
    CRAWLER_TOTAL_SITE_TIMEOUT_SECONDS: float = 75.0
    CRAWLER_USER_AGENT: str = "ProspectDigitalAnalyzer/1.0 (+https://prospectanalyzer.io/bot)"
    CRAWLER_MAX_RETRIES: int = 1

    # Scoring Engine Weights
    WEIGHT_PERFORMANCE: float = 0.25
    WEIGHT_SEO: float = 0.25
    WEIGHT_LEAD_GEN: float = 0.25
    WEIGHT_UI_UX: float = 0.15
    WEIGHT_BROKEN_LINKS: float = 0.10

    # Content Appropriateness Heuristics
    CONTENT_MODERATION_ENABLED: bool = True


settings = Settings()
