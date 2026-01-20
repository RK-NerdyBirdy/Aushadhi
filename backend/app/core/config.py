from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    APP_NAME: str = "Aushadhi API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost:5432/aushadhi_db"
    DB_ECHO: bool = False
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # CORS
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # ML Service
    ML_SERVICE_URL: str = "http://localhost:8001"
    ML_SERVICE_API_KEY: str = "your-ml-service-api-key"
    
    # Alert Configuration
    ALERT_CHECK_INTERVAL_SECONDS: int = 3600
    EXPIRY_WARNING_DAYS: str = "90,60,30"
    
    # Pagination
    DEFAULT_SKIP: int = 0
    DEFAULT_LIMIT: int = 100
    MAX_LIMIT: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    @property
    def allowed_cors_origins(self) -> List[str]:
        """Parse CORS origins from string"""
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",")]

settings = Settings()
