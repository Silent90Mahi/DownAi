"""
Ooumph Configuration System
Environment-based configuration for production-ready deployment
"""
from pydantic_settings import BaseSettings
from typing import Optional
import re


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Create a .env file in the backend directory with these variables.
    """

    # ============= SECURITY =============
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # ============= API KEYS =============
    OPENAI_API_KEY: str
    ONDC_API_KEY: Optional[str] = None

    def validate_openai_key(self) -> None:
        """Validate OpenAI API key format."""
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required")
        pattern = r'^sk-proj-[A-Za-z0-9_-]{20,}$'
        if not re.match(pattern, self.OPENAI_API_KEY):
            raise ValueError(
                "Invalid OPENAI_API_KEY format. "
                "Key should start with 'sk-proj-' followed by alphanumeric characters."
            )
    GEM_API_KEY: Optional[str] = None
    ESARAS_API_KEY: Optional[str] = None
    RTGS_API_KEY: Optional[str] = None
    RAZORPAY_KEY_ID: Optional[str] = None
    RAZORPAY_KEY_SECRET: Optional[str] = None

    # ============= OPENAI MODELS =============
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_WHISPER_MODEL: str = "whisper-1"
    OPENAI_TTS_MODEL: str = "tts-1"
    OPENAI_TTS_VOICE: str = "alloy"

    # ============= DATABASE =============
    DATABASE_URL: str = "sqlite:///./ooumph.db"

    # ============= CORS =============
    FRONTEND_URL: str = "http://localhost:5173"

    # ============= REDIS =============
    REDIS_URL: str = "redis://localhost:6379"

    # ============= APPLICATION =============
    APP_NAME: str = "Ooumph SHG Ecosystem"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"  # development, staging, production

    # ============= LOGGING =============
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text

    # ============= RATE LIMITING =============
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # ============= FEATURES =============
    ENABLE_WEBSOCKET: bool = True
    ENABLE_CACHE: bool = True
    CACHE_TTL: int = 3600  # seconds
    ENABLE_VOICE_AGENT: bool = True
    ENABLE_TRUST_COINS: bool = True
    ENABLE_BULK_ORDERING: bool = True
    ENABLE_NEGOTIATION: bool = True

    # ============= FILE UPLOAD =============
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields in .env file


# Create global settings instance
settings = Settings()


# Configuration validation
def validate_settings() -> None:
    """
    Validate critical settings are set.
    Raises ValueError if critical settings are missing.
    """
    critical_settings = ["SECRET_KEY", "OPENAI_API_KEY"]

    missing = []
    for setting in critical_settings:
        value = getattr(settings, setting)
        if not value or value == f"CHANGE_{setting}":
            missing.append(setting)

    if missing:
        raise ValueError(
            f"Critical settings missing: {', '.join(missing)}. "
            f"Please set these in your .env file."
        )

    settings.validate_openai_key()

    if settings.SECRET_KEY == "ooumph_secret_key_change_in_production":
        if settings.ENVIRONMENT == "production":
            raise ValueError(
                "SECRET_KEY must be changed in production! "
                "Generate a secure key with: openssl rand -hex 32"
            )
        else:
            import warnings
            warnings.warn(
                "Using default SECRET_KEY. Change this before production deployment!"
            )


# Validate settings on import
try:
    validate_settings()
except ValueError as e:
    print(f"Configuration Error: {e}")
    raise
