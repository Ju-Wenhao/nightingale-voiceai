"""
Nightingale VoiceAI Configuration Settings

Centralized configuration management with environment-based settings
for development, testing, and production deployments.
"""

from pydantic_settings import BaseSettings
from typing import Optional, List
import os


class Settings(BaseSettings):
    """Application configuration settings"""
    
    # Application settings
    app_name: str = "Nightingale VoiceAI"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    
    # Security settings
    secret_key: str = "nightingale_secret_change_in_production"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7
    
    # Database settings
    database_url: str = "sqlite:///./nightingale.db"
    database_echo: bool = False  # Set to True for SQL query logging
    
    # Encryption settings (for data at rest)
    encryption_key: Optional[str] = None
    
    # PHI Redaction settings
    phi_redaction_enabled: bool = True
    phi_confidence_threshold: float = 0.7
    phi_redaction_timeout: int = 5  # seconds
    
    # Audio processing settings
    audio_chunk_duration: int = 30  # seconds
    audio_sample_rate: int = 16000
    audio_max_file_size: int = 50 * 1024 * 1024  # 50MB
    
    # Speech-to-text settings
    whisper_model: str = "base"  # base, small, medium, large
    whisper_language: str = "en"
    whisper_device: str = "cpu"  # cpu or cuda
    
    # LLM settings for summary generation
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-3.5-turbo"
    openai_max_tokens: int = 1000
    openai_temperature: float = 0.3
    
    # Provenance settings
    provenance_enabled: bool = True
    provenance_granularity: str = "sentence"  # word, sentence, paragraph
    
    # Logging settings
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "logs/nightingale.log"
    
    # CORS settings
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    cors_allow_credentials: bool = True
    cors_allow_methods: List[str] = ["*"]
    cors_allow_headers: List[str] = ["*"]
    
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    # Healthcare compliance settings
    hipaa_mode: bool = True
    audit_logging: bool = True
    phi_logging_disabled: bool = True
    
    # Performance settings
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    
    # File storage settings
    upload_dir: str = "uploads"
    max_storage_days: int = 30
    
    # Email settings (for notifications)
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Monitoring and health check settings
    health_check_interval: int = 60  # seconds
    metrics_enabled: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


class DevelopmentSettings(Settings):
    """Development environment specific settings"""
    environment: str = "development"
    debug: bool = True
    database_echo: bool = True
    log_level: str = "DEBUG"
    
    # Development-specific overrides
    cors_origins: List[str] = ["*"]  # Allow all origins in development
    rate_limit_enabled: bool = False


class ProductionSettings(Settings):
    """Production environment specific settings"""
    environment: str = "production"
    debug: bool = False
    database_echo: bool = False
    log_level: str = "INFO"
    
    # Production security requirements
    secret_key: str  # Must be provided via environment variable
    openai_api_key: str  # Must be provided via environment variable
    encryption_key: str  # Must be provided via environment variable
    
    # Production database (example for PostgreSQL)
    database_url: str = "postgresql://user:password@localhost/nightingale"
    
    # Stricter CORS in production
    cors_origins: List[str] = ["https://nightingale.healthcare"]
    
    # Enhanced security
    rate_limit_requests: int = 50
    request_timeout: int = 10


class TestingSettings(Settings):
    """Testing environment specific settings"""
    environment: str = "testing"
    debug: bool = True
    database_url: str = "sqlite:///:memory:"
    
    # Disable external services during testing
    openai_api_key: str = "test_key"
    
    # Faster testing
    whisper_model: str = "tiny"
    phi_redaction_timeout: int = 1
    
    # Test-specific settings
    rate_limit_enabled: bool = False
    audit_logging: bool = False


def get_settings() -> Settings:
    """Get settings based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    if env == "production":
        return ProductionSettings()
    elif env == "testing":
        return TestingSettings()
    else:
        return DevelopmentSettings()


# Global settings instance
settings = get_settings()


# Environment-specific validation
def validate_production_settings():
    """Validate critical production settings"""
    if settings.environment == "production":
        required_vars = [
            "secret_key", "openai_api_key", "encryption_key"
        ]
        
        missing_vars = [
            var for var in required_vars 
            if not getattr(settings, var, None)
        ]
        
        if missing_vars:
            raise ValueError(
                f"Missing required production environment variables: {missing_vars}"
            )


# Healthcare compliance validation
def validate_hipaa_compliance():
    """Validate HIPAA compliance settings"""
    if settings.hipaa_mode:
        assert settings.phi_logging_disabled, "PHI logging must be disabled in HIPAA mode"
        assert settings.audit_logging, "Audit logging required for HIPAA compliance"
        assert settings.phi_redaction_enabled, "PHI redaction required for HIPAA compliance"
        
        if settings.environment == "production":
            assert settings.encryption_key, "Encryption key required for HIPAA compliance"


if __name__ == "__main__":
    # Configuration validation for deployment
    print(f"Environment: {settings.environment}")
    print(f"Debug mode: {settings.debug}")
    print(f"Database URL: {settings.database_url}")
    print(f"HIPAA mode: {settings.hipaa_mode}")
    
    try:
        validate_production_settings()
        validate_hipaa_compliance()
        print("✅ Configuration validation passed")
    except Exception as e:
        print(f"❌ Configuration validation failed: {e}")