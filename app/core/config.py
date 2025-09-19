# app/core/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API Settings
    api_key: str = "your-secure-api-key"
    
    # MongoDB Atlas
    mongodb_url: str = "mongodb+srv://happyrobot123:happyrobot123@happyrobot.ssvmps4.mongodb.net/?retryWrites=true&w=majority&appName=happyrobot"
    
    # External APIs
    fmcsa_api_key: str = "cdc33e44d693a3a58451898d4ec9df862c65b954"
    
    # Redis (optional for caching)
    redis_url: Optional[str] = "redis://localhost:6379"
    
    # HappyRobot Webhook Settings
    happyrobot_webhook_secret: Optional[str] = None
    
    # Environment
    environment: str = "development"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()