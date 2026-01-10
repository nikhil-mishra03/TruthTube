"""
Application configuration using Pydantic Settings.
Loads environment variables from .env file.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Keys
    openai_api_key: str = ""
    youtube_api_key: Optional[str] = None
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/truthtube"
    
    # Environment
    environment: str = "development"
    
    # Logging
    log_level: str = "INFO"
    
    # App settings
    app_name: str = "TruthTube"
    app_version: str = "0.1.0"
    
    # Analysis settings
    max_videos_per_request: int = 5
    min_videos_per_request: int = 1
    openai_model: str = "gpt-4o-mini"
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
