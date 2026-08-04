# backend/app/core/config.py
from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field, ValidationError
import os

class Settings(BaseSettings):
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # MongoDB
    MONGO_URI: str = Field(..., env="MONGO_URI")
    MONGO_DB_NAME: str = "twinflow"

    # Redis
    REDIS_URL: str = Field(..., env="REDIS_URL")

    # JWT
    SECRET_KEY: str = Field(..., env="SECRET_KEY", min_length=32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:80", "http://localhost"],
        env="CORS_ORIGINS",
    )

    # External APIs
    OPENWEATHER_API_KEY: str = Field(..., env="OPENWEATHER_API_KEY")
    TAVILY_API_KEY: str = Field(..., env="TAVILY_API_KEY")
    OPENAQ_API_KEY: str = Field(..., env="OPENAQ_API_KEY")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()