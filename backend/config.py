import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator

class Settings(BaseSettings):
    # API Keys
    openrouter_api_key: str = Field(..., env="OPENROUTER_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    jwt_secret: str = Field(..., env="JWT_SECRET")
    
    # Voice Model Configuration
    voice_model_id: str = Field(default="openai/gpt-4o-audio-preview", env="VOICE_MODEL_ID")
    voice_model_provider: str = Field(default="openrouter", env="VOICE_MODEL_PROVIDER")
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    client_id: str = Field(..., env="CLIENT_ID")
    
    # Service Configuration
    api_timeout: int = Field(default=60, env="API_TIMEOUT")
    max_audio_size_mb: int = Field(default=25, env="MAX_AUDIO_SIZE_MB")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_api_requests: bool = Field(default=False, env="LOG_API_REQUESTS")
    
    # Security
    cors_origins: str = Field(default="*", env="CORS_ORIGINS")
    
    @validator("openrouter_api_key")
    def validate_openrouter_key(cls, v):
        if not v or v.startswith("your-") or v == "":
            raise ValueError("OPENROUTER_API_KEY must be set to a valid API key")
        return v
    
    @validator("jwt_secret")
    def validate_jwt_secret(cls, v):
        if not v or len(v) < 16:
            raise ValueError("JWT_SECRET must be at least 16 characters")
        return v
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

def get_settings() -> Settings:
    """Load and validate settings from environment variables"""
    try:
        return Settings()
    except Exception as e:
        print(f"❌ Configuration Error: {str(e)}")
        print("\nRequired environment variables:")
        print("  - OPENROUTER_API_KEY")
        print("  - JWT_SECRET")
        print("  - DATABASE_URL")
        print("  - CLIENT_ID")
        raise SystemExit(1)

settings = get_settings()
