import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # Encryption
    encryption_key: str = Field(..., env="ENCRYPTION_KEY")
    
    # Master Admin
    master_admin_secret: str = Field(default="change-me", env="MASTER_ADMIN_SECRET")
    
    # Google Cloud TTS
    google_cloud_project_id: Optional[str] = Field(default=None, env="GOOGLE_CLOUD_PROJECT_ID")
    google_application_credentials: Optional[str] = Field(default=None, env="GOOGLE_APPLICATION_CREDENTIALS")
    default_voice: str = Field(default="en-US-Neural2-F", env="DEFAULT_VOICE")
    
    # Service Configuration
    api_timeout: int = Field(default=60, env="API_TIMEOUT")
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

settings = Settings()
