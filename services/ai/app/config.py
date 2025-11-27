"""
AI Service Configuration
"""
import os
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    SERVICE_NAME: str = "ai-service"
    SERVICE_PORT: int = 8009
    DEBUG: bool = True
    
    DATABASE_URL: str = os.environ.get('DATABASE_URL', '')
    
    IDENTITY_SERVICE_URL: str = "http://localhost:8001"
    SALES_SERVICE_URL: str = "http://localhost:8002"
    FINANCE_SERVICE_URL: str = "http://localhost:8003"
    INVENTORY_SERVICE_URL: str = "http://localhost:8004"
    HR_SERVICE_URL: str = "http://localhost:8005"
    COMPLIANCE_SERVICE_URL: str = "http://localhost:8006"
    PROJECT_SERVICE_URL: str = "http://localhost:8007"
    
    REDIS_URL: str = "redis://localhost:6379/8"
    
    MODEL_CACHE_TTL: int = 3600
    PREDICTION_CACHE_TTL: int = 300
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()
