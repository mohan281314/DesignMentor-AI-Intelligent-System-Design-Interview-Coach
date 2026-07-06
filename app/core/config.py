"""
Application configuration using Pydantic Settings.
Loads from environment variables and .env file.
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    # Application
    app_name: str = "DesignMentor AI"
    app_version: str = "2.0.0"
    environment: Literal["development", "staging", "production", "test"] = "development"
    debug: bool = Field(default=True, description="Enable debug mode")
    
    # Server
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    
    # Database — defaults to SQLite so it works with zero setup.
    # Override with a full PostgreSQL URL in .env for production.
    database_url: str = Field(
        default="sqlite:///./designmentor.db",
        description="Database URL. SQLite by default, set to postgresql+psycopg2://... for production"
    )
    db_echo: bool = Field(default=False, description="Enable SQL query logging")
    
    # Redis
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )
    redis_cache_ttl: int = Field(default=3600, description="Default cache TTL in seconds")
    
    # Session Management
    session_ttl_seconds: int = Field(
        default=1800,  # 30 minutes
        description="Session timeout in seconds"
    )
    
    # Authentication & Security
    secret_key: str = Field(
        default="your-secret-key-change-this-in-production-min-32-chars",
        description="Secret key for JWT token signing (min 32 characters)"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7,
        description="Refresh token expiration time in days"
    )
    
    # OAuth2 Providers
    google_client_id: str = Field(default="", description="Google OAuth client ID")
    google_client_secret: str = Field(default="", description="Google OAuth client secret")
    github_client_id: str = Field(default="", description="GitHub OAuth client ID")
    github_client_secret: str = Field(default="", description="GitHub OAuth client secret")
    oauth_redirect_url: str = Field(
        default="http://localhost:8000/api/v1/auth/callback",
        description="OAuth callback URL"
    )
    
    # AI/LLM Configuration
    # Groq (default provider)
    groq_api_key: str = Field(default="", description="Groq API key")
    groq_model: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model name"
    )
    
    # OpenAI (fallback provider)
    openai_api_key: str = Field(default="", description="OpenAI API key")
    openai_model: str = Field(default="gpt-4-turbo-preview", description="OpenAI model name")
    
    # LLM Settings
    llm_provider: Literal["groq", "openai"] = Field(
        default="groq",
        description="Primary LLM provider"
    )
    llm_fallback_enabled: bool = Field(
        default=True,
        description="Enable fallback to secondary provider on error"
    )
    openai_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="LLM temperature"
    )
    openai_max_tokens: int = Field(
        default=4096,
        ge=1,
        le=32768,
        description="Maximum tokens for LLM completion"
    )
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests_per_minute: int = Field(
        default=60,
        description="API requests per minute per user"
    )
    rate_limit_burst: int = Field(
        default=10,
        description="Burst allowance for rate limiting"
    )
    
    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed CORS origins"
    )
    
    # File Storage
    upload_dir: str = Field(default="uploads", description="Directory for file uploads")
    max_upload_size_mb: int = Field(default=10, description="Max upload size in MB")
    
    # PDF Export
    pdf_export_enabled: bool = Field(default=True, description="Enable PDF export")
    pdf_temp_dir: str = Field(default="temp/pdfs", description="Temporary PDF directory")
    
    # Analytics
    analytics_enabled: bool = Field(default=True, description="Enable analytics tracking")
    analytics_retention_days: int = Field(
        default=90,
        description="Days to retain analytics data"
    )
    
    # Background Jobs (Celery - optional)
    celery_broker_url: str = Field(
        default="redis://localhost:6379/1",
        description="Celery broker URL"
    )
    celery_result_backend: str = Field(
        default="redis://localhost:6379/1",
        description="Celery result backend URL"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)"
    )
    log_format: str = Field(
        default="json",  # or "text"
        description="Log format (json or text)"
    )
    
    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Warn (don't crash) if secret key is too short in non-production."""
        import os
        env = os.getenv("ENVIRONMENT", "development")
        if env == "production" and len(v) < 32:
            raise ValueError("secret_key must be at least 32 characters in production")
        return v
    
    @property
    def database_url_async(self) -> str:
        """Get async database URL for asyncpg."""
        return self.database_url.replace("postgresql+psycopg2://", "postgresql+asyncpg://")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Use @lru_cache to avoid re-reading .env file on every call.
    """
    return Settings()
