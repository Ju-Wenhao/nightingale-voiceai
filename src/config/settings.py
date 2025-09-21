"""
Configuration settings for Nightingale VoiceAI system
"""

from typing import Optional
from pydantic import BaseModel


class Settings(BaseModel):
    """Application settings with environment variable support"""
    
    # API Configuration
    app_name: str = "Nightingale VoiceAI"
    debug: bool = False
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Security
    secret_key: str = "nightingale_jwt_secret_key_change_in_production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    
    # Database
    database_url: str = "sqlite:///./nightingale.db"
    
    # External API Keys (set via environment variables)
    openai_api_key: Optional[str] = None
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/nightingale.log"
    
    # PHI Redaction
    phi_redaction_enabled: bool = True
    phi_confidence_threshold: float = 0.8
    
    # Audio Processing  
    audio_chunk_size: int = 30  # seconds
    transcription_model: str = "whisper-base"
    
    # Summary Generation
    max_summary_length: int = 500
    include_provenance: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()