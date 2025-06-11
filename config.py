"""Production-grade configuration management."""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from pathlib import Path


class SecuritySettings(BaseSettings):
    """Security configuration."""
    
    secret_key: str = Field(default="dev-secret-key-change-in-production", env="SECRET_KEY")
    jwt_secret: str = Field(default="dev-jwt-secret-change-in-production", env="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=30, env="JWT_EXPIRE_MINUTES")
    bcrypt_rounds: int = Field(default=12, env="BCRYPT_ROUNDS")
    
    # Rate limiting
    rate_limit_per_minute: int = Field(default=60, env="RATE_LIMIT_PER_MINUTE")
    rate_limit_burst: int = Field(default=100, env="RATE_LIMIT_BURST")
    
    # CORS
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "https://localhost:3000"],
        env="CORS_ORIGINS"
    )
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v


class DatabaseSettings(BaseSettings):
    """Database configuration."""
    
    # Redis
    redis_host: str = Field(default="redis", env="REDIS_HOST")
    redis_port: int = Field(default=6379, env="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    redis_db: int = Field(default=0, env="REDIS_DB")
    redis_max_connections: int = Field(default=20, env="REDIS_MAX_CONNECTIONS")
    
    # Neo4j (optional)
    neo4j_uri: Optional[str] = Field(default=None, env="NEO4J_URI")
    neo4j_user: Optional[str] = Field(default=None, env="NEO4J_USER")
    neo4j_password: Optional[str] = Field(default=None, env="NEO4J_PASSWORD")
    neo4j_max_connection_lifetime: int = Field(default=300, env="NEO4J_MAX_CONNECTION_LIFETIME")
    neo4j_max_connection_pool_size: int = Field(default=50, env="NEO4J_MAX_CONNECTION_POOL_SIZE")


class APISettings(BaseSettings):
    """API service configuration."""
    
    # LLM APIs (optional for demo)
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    
    # API behavior
    default_timeout: int = Field(default=30, env="DEFAULT_TIMEOUT")
    max_retries: int = Field(default=3, env="MAX_RETRIES")
    retry_delay: float = Field(default=1.0, env="RETRY_DELAY")


class AppSettings(BaseSettings):
    """Application configuration."""
    
    # App info
    app_name: str = Field(default="NSAI Orchestrator MCP", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    app_description: str = Field(
        default="Production-grade multi-agent orchestration platform",
        env="APP_DESCRIPTION"
    )
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Server
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    workers: int = Field(default=1, env="WORKERS")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Performance
    enable_gzip: bool = Field(default=True, env="ENABLE_GZIP")
    max_request_size: int = Field(default=16777216, env="MAX_REQUEST_SIZE")  # 16MB
    
    # Memory settings
    memory_ttl_seconds: int = Field(default=3600, env="MEMORY_TTL_SECONDS")
    memory_max_entries: int = Field(default=10000, env="MEMORY_MAX_ENTRIES")
    
    # WebSocket settings
    websocket_ping_interval: int = Field(default=20, env="WEBSOCKET_PING_INTERVAL")
    websocket_ping_timeout: int = Field(default=10, env="WEBSOCKET_PING_TIMEOUT")
    
    @validator("environment")
    def validate_environment(cls, v):
        if v not in ["development", "staging", "production"]:
            raise ValueError("Environment must be development, staging, or production")
        return v


class Settings(BaseSettings):
    """Combined application settings."""
    
    security: SecuritySettings = SecuritySettings()
    database: DatabaseSettings = DatabaseSettings()
    api: APISettings = APISettings()
    app: AppSettings = AppSettings()
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings