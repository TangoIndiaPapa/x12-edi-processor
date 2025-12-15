"""Configuration management using Pydantic Settings.

This module provides application-wide configuration management using environment
variables and Pydantic validation. Settings are cached for performance.

Callers:
    - src.handlers.lambda_handler: Uses get_settings() for AWS configuration
    - src.input.local_input: Uses get_settings() for file size limits
    - src.input.s3_input: Uses get_settings() for AWS region and file size
    - src.input.upload_input: Uses get_settings() for file size validation
    - main.py: Uses get_settings() for environment display

Callees:
    - pydantic.BaseSettings: Configuration validation framework
    - functools.lru_cache: Settings instance caching

Environment Variables:
    ENVIRONMENT: Application environment (development/staging/production)
    AWS_REGION: AWS region for S3 and Lambda operations
    AWS_S3_BUCKET: Default S3 bucket for file storage
    AWS_LAMBDA_FUNCTION_NAME: Lambda function identifier
    LOG_LEVEL: Logging verbosity (DEBUG/INFO/WARNING/ERROR/CRITICAL)
    MAX_FILE_SIZE_MB: Maximum file size in megabytes
    ENABLE_VALIDATION: Enable X12 validation checks
    STRICT_MODE: Fail on validation errors when True
"""

from functools import lru_cache
from typing import Literal

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables.
    
    Uses Pydantic BaseSettings for automatic environment variable loading,
    type validation, and default value assignment. Settings are immutable
    once loaded.
    
    Attributes:
        ENVIRONMENT: Runtime environment identifier
        AWS_REGION: AWS region for service calls
        AWS_S3_BUCKET: Default S3 bucket name
        AWS_LAMBDA_FUNCTION_NAME: Lambda function name
        LOG_LEVEL: Logging level string
        MAX_FILE_SIZE_MB: Maximum allowed file size in MB
        ENABLE_VALIDATION: Whether to validate X12 documents
        STRICT_MODE: Whether to fail on validation errors
    """

    # Environment
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # AWS Configuration
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: str = ""
    AWS_LAMBDA_FUNCTION_NAME: str = "x12-edi-processor"

    # Application Settings
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    MAX_FILE_SIZE_MB: int = 50

    # Processing Options
    ENABLE_VALIDATION: bool = True
    STRICT_MODE: bool = False

    @property
    def max_file_size_bytes(self) -> int:
        """Convert max file size from MB to bytes.
        
        Returns:
            int: Maximum file size in bytes (MB * 1024 * 1024)
            
        Example:
            >>> settings = Settings(MAX_FILE_SIZE_MB=50)
            >>> settings.max_file_size_bytes
            52428800
        """
        return self.MAX_FILE_SIZE_MB * 1024 * 1024

    @property
    def is_production(self) -> bool:
        """Check if running in production environment.
        
        Returns:
            bool: True if ENVIRONMENT == 'production', False otherwise
            
        Example:
            >>> settings = Settings(ENVIRONMENT='production')
            >>> settings.is_production
            True
        """
        return self.ENVIRONMENT == "production"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.
    
    Returns a singleton Settings instance using LRU cache. The settings
    object is created once and reused across the application lifecycle.
    This improves performance and ensures consistency.
    
    Returns:
        Settings: Cached application settings instance
        
    Called by:
        - Lambda handlers for AWS configuration
        - Input handlers for validation limits
        - Parsers for processing options
        
    Example:
        >>> settings = get_settings()
        >>> settings.AWS_REGION
        'us-east-1'
    """
    return Settings()

