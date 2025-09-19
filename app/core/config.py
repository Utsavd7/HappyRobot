# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings - loaded from environment
    api_key: str
    
    # MongoDB Atlas - loaded from environment
    mongodb_url: str
    
    # External APIs - loaded from environment
    fmcsa_api_key: str
    
    # Redis (optional for caching)
    redis_url: Optional[str] = "redis://localhost:6379"
    
    # HappyRobot Webhook Settings
    happyrobot_webhook_secret: Optional[str] = None
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()