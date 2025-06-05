from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    secret_key: str = "your-secret-key-here-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    database_url: str = "sqlite:///./app.db"
    redis_url: str = "redis://localhost:6379/0"
    
    class Config:
        env_file = ".env"


settings = Settings() 