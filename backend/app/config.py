"""
Configuration settings for Loglytics AI
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional, List
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "allow"
    }
    
    # Application
    APP_NAME: str = Field(default="Loglytics AI", env="APP_NAME")
    APP_VERSION: str = Field(default="1.0.0", env="APP_VERSION")
    DEBUG: bool = Field(default=False, env="DEBUG")

    # PostgreSQL Database Configuration
    POSTGRES_USER: str = Field(default="postgres", env="POSTGRES_USER")
    POSTGRES_PASSWORD: str = Field(default="Rashan12", env="POSTGRES_PASSWORD")
    POSTGRES_HOST: str = Field(default="localhost", env="POSTGRES_HOST")
    POSTGRES_PORT: int = Field(default=5432, env="POSTGRES_PORT")
    POSTGRES_DB: str = Field(default="loglytics_ai", env="POSTGRES_DB")

    # Database URL (will be constructed from PostgreSQL settings if not provided)
    DATABASE_URL: Optional[str] = Field(default=None, env="DATABASE_URL")
    DATABASE_POOL_SIZE: int = Field(default=20, env="DATABASE_POOL_SIZE")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, env="DATABASE_MAX_OVERFLOW")
    DATABASE_POOL_TIMEOUT: int = Field(default=30, env="DATABASE_POOL_TIMEOUT")
    DATABASE_POOL_RECYCLE: int = Field(default=3600, env="DATABASE_POOL_RECYCLE")

    def model_post_init(self, __context):
        """Build DATABASE_URL and Celery URLs if not provided"""
        if not self.DATABASE_URL:
            self.DATABASE_URL = f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

        # Set Celery broker and result backend to Redis if not provided
        if not self.CELERY_BROKER_URL:
            self.CELERY_BROKER_URL = self.REDIS_URL
        if not self.CELERY_RESULT_BACKEND:
            self.CELERY_RESULT_BACKEND = self.REDIS_URL
    
    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    REDIS_PASSWORD: Optional[str] = Field(default=None, env="REDIS_PASSWORD")
    
    # Security
    SECRET_KEY: str = Field(default="your-secret-key-change-this-in-production", env="SECRET_KEY")
    JWT_SECRET_KEY: str = Field(default="your-jwt-secret-key-change-this-in-production", env="JWT_SECRET_KEY")
    ENCRYPTION_MASTER_KEY: str = Field(default="change-this-in-production-min-32-chars-required", env="ENCRYPTION_MASTER_KEY")
    ALGORITHM: str = Field(default="HS256", env="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    
    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    ALLOWED_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    ALLOWED_HEADERS: List[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    # File Upload
    MAX_FILE_SIZE: int = 100 * 1024 * 1024  # 100MB
    ALLOWED_FILE_TYPES: List[str] = [".log", ".txt", ".json", ".csv"]
    UPLOAD_DIR: str = "uploads"
    
    # LLM Configuration
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    DEFAULT_LLM_MODEL: str = "llama3.2:3b"
    
    # Email Configuration
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_USE_TLS: bool = True
    FROM_EMAIL: str = "noreply@loglytics.ai"
    
    # S3 Configuration
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Optional[str] = None
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090

    # Celery Configuration
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True
    CELERY_TASK_TRACK_STARTED: bool = True
    CELERY_TASK_TIME_LIMIT: int = 600  # 10 minutes
    CELERY_TASK_SOFT_TIME_LIMIT: int = 540  # 9 minutes
    CELERY_WORKER_PREFETCH_MULTIPLIER: int = 4
    CELERY_WORKER_MAX_TASKS_PER_CHILD: int = 1000
    CELERY_RESULT_EXPIRES: int = 86400  # 24 hours
    CELERY_TASK_ACKS_LATE: bool = True
    CELERY_WORKER_CONCURRENCY: int = 4

    # Celery Queue Configuration
    CELERY_DEFAULT_QUEUE: str = "default"
    CELERY_HIGH_PRIORITY_QUEUE: str = "high-priority"
    CELERY_LOW_PRIORITY_QUEUE: str = "low-priority"

    # Task Retry Configuration
    CELERY_TASK_MAX_RETRIES: int = 3
    CELERY_TASK_DEFAULT_RETRY_DELAY: int = 60  # 1 minute

    # Notification Services
    SENDGRID_API_KEY: Optional[str] = None
    SLACK_WEBHOOK_URL: Optional[str] = None
    JIRA_URL: Optional[str] = None
    JIRA_USERNAME: Optional[str] = None
    JIRA_API_TOKEN: Optional[str] = None

    # Feature Flags
    ENABLE_REGISTRATION: bool = True
    ENABLE_PASSWORD_RESET: bool = True
    ENABLE_API_KEYS: bool = True
    ENABLE_LIVE_LOGS: bool = True
    ENABLE_ANALYTICS: bool = True
    
    # Subscription Limits
    FREE_TIER_LIMITS: dict = {
        "max_projects": 3,
        "max_log_files": 100,
        "max_log_entries": 10000,
        "max_storage_mb": 1000,
        "max_api_calls_per_day": 1000,
        "max_llm_tokens_per_month": 100000
    }
    
    PRO_TIER_LIMITS: dict = {
        "max_projects": 50,
        "max_log_files": 1000,
        "max_log_entries": 1000000,
        "max_storage_mb": 10000,
        "max_api_calls_per_day": 10000,
        "max_llm_tokens_per_month": 1000000
    }
    
# Create settings instance
settings = Settings()

# Validate required settings
if settings.SECRET_KEY == "your-secret-key-change-this-in-production":
    import warnings
    warnings.warn(
        "SECRET_KEY is set to default value. Please change it in production!",
        UserWarning
    )

# Database URL validation
if settings.DATABASE_URL and not settings.DATABASE_URL.startswith(("postgresql://", "postgresql+asyncpg://", "sqlite://", "sqlite+aiosqlite://")):
    raise ValueError("DATABASE_URL must be a PostgreSQL or SQLite connection string")

# Redis URL validation
if not settings.REDIS_URL.startswith("redis://"):
    raise ValueError("REDIS_URL must be a Redis connection string")