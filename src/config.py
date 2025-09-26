"""
Configuration management for Smart Travel Optimizer.

This module handles all configuration settings with proper validation,
type safety, and security best practices.
"""

import os
import logging
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SMTPConfig:
    """SMTP configuration with validation."""
    host: str
    port: int
    username: str
    password: str
    from_name: str
    timeout: int = 30
    use_tls: bool = True
    
    def __post_init__(self):
        """Validate SMTP configuration."""
        if not self.host:
            raise ValueError("SMTP host is required")
        if not (1 <= self.port <= 65535):
            raise ValueError(f"Invalid SMTP port: {self.port}")
        if not self.username:
            raise ValueError("SMTP username is required")
        if not self.password:
            raise ValueError("SMTP password is required")
    
    @property
    def is_configured(self) -> bool:
        """Check if SMTP is properly configured."""
        return all([self.host, self.port, self.username, self.password])


@dataclass
class APIProviderConfig:
    """Base class for API provider configurations."""
    enabled: bool = False
    rate_limit: int = 100  # requests per minute
    timeout: int = 30  # seconds
    retry_attempts: int = 3
    
    @property
    def is_configured(self) -> bool:
        """Check if provider is properly configured."""
        return self.enabled


@dataclass  
class AmadeusConfig(APIProviderConfig):
    """Amadeus API configuration."""
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    base_url: str = "https://api.amadeus.com"
    
    def __post_init__(self):
        """Validate Amadeus configuration."""
        if self.api_key and self.api_secret:
            self.enabled = True
        elif self.api_key or self.api_secret:
            logger.warning("Amadeus: Both API key and secret are required")
    
    @property
    def is_configured(self) -> bool:
        """Check if Amadeus is properly configured."""
        return self.enabled and bool(self.api_key and self.api_secret)


@dataclass
class OmioConfig(APIProviderConfig):
    """Omio API configuration."""
    api_key: Optional[str] = None
    base_url: str = "https://api.omio.com"
    
    def __post_init__(self):
        """Validate Omio configuration."""
        if self.api_key:
            self.enabled = True
    
    @property
    def is_configured(self) -> bool:
        """Check if Omio is properly configured."""
        return self.enabled and bool(self.api_key)


@dataclass
class SecurityConfig:
    """Security-related configuration."""
    max_email_size_kb: int = 1024
    rate_limit_requests_per_minute: int = 60
    input_validation_enabled: bool = True
    sanitization_enabled: bool = True
    log_security_events: bool = True
    
    def __post_init__(self):
        """Validate security configuration."""
        if self.max_email_size_kb <= 0:
            raise ValueError("Max email size must be positive")
        if self.rate_limit_requests_per_minute <= 0:
            raise ValueError("Rate limit must be positive")


@dataclass
class ApplicationConfig:
    """Main application configuration."""
    smtp: SMTPConfig
    amadeus: AmadeusConfig
    omio: OmioConfig
    security: SecurityConfig
    debug: bool = False
    log_level: str = "INFO"
    
    @property
    def active_providers(self) -> Dict[str, bool]:
        """Get status of all providers."""
        return {
            "amadeus": self.amadeus.is_configured,
            "omio": self.omio.is_configured,
        }
    
    def validate(self) -> None:
        """Validate entire configuration."""
        if not any(self.active_providers.values()):
            logger.warning("No external providers configured - using mock data only")
        
        if self.smtp.is_configured:
            logger.info("SMTP configured for email notifications")
        else:
            logger.warning("SMTP not configured - email features disabled")


class ConfigurationManager:
    """Centralized configuration management."""
    
    def __init__(self, env_file: Optional[Path] = None):
        self.env_file = env_file or Path(".env")
        self._config: Optional[ApplicationConfig] = None
        self._load_environment()
    
    def _load_environment(self) -> None:
        """Load environment variables."""
        if self.env_file.exists():
            load_dotenv(self.env_file, override=True)
            logger.info(f"Loaded environment from {self.env_file}")
        else:
            logger.info("No .env file found, using system environment")
    
    def _get_env_value(self, key: str, default: Any = None, required: bool = False) -> Any:
        """Get environment variable with validation."""
        value = os.getenv(key, default)
        
        if required and value is None:
            raise ValueError(f"Required environment variable '{key}' not set")
        
        return value
    
    def _get_env_int(self, key: str, default: int = 0) -> int:
        """Get integer environment variable."""
        try:
            return int(self._get_env_value(key, default))
        except (ValueError, TypeError):
            logger.warning(f"Invalid integer value for {key}, using default: {default}")
            return default
    
    def _get_env_bool(self, key: str, default: bool = False) -> bool:
        """Get boolean environment variable."""
        value = self._get_env_value(key, "").lower()
        return value in ("true", "1", "yes", "on")
    
    def load_config(self) -> ApplicationConfig:
        """Load and validate configuration."""
        if self._config is not None:
            return self._config
        
        try:
            # SMTP Configuration
            smtp_config = SMTPConfig(
                host=self._get_env_value("SMTP_HOST", ""),
                port=self._get_env_int("SMTP_PORT", 587),
                username=self._get_env_value("SMTP_USERNAME", ""),
                password=self._get_env_value("SMTP_PASSWORD", ""),
                from_name=self._get_env_value("SMTP_FROM_NAME", "Smart Travel Optimizer"),
                timeout=self._get_env_int("SMTP_TIMEOUT", 30),
                use_tls=self._get_env_bool("SMTP_USE_TLS", True)
            )
            
            # Skip SMTP validation if not configured
            if not smtp_config.host:
                smtp_config = SMTPConfig(
                    host="", port=587, username="", password="", from_name="Smart Travel Optimizer"
                )
            
        except ValueError:
            # Fallback SMTP config for development
            smtp_config = SMTPConfig(
                host="", port=587, username="", password="", from_name="Smart Travel Optimizer"
            )
        
        # Amadeus Configuration
        amadeus_config = AmadeusConfig(
            api_key=self._get_env_value("AMADEUS_API_KEY"),
            api_secret=self._get_env_value("AMADEUS_API_SECRET"),
            rate_limit=self._get_env_int("AMADEUS_RATE_LIMIT", 100),
            timeout=self._get_env_int("AMADEUS_TIMEOUT", 30)
        )
        
        # Omio Configuration
        omio_config = OmioConfig(
            api_key=self._get_env_value("OMIO_API_KEY"),
            rate_limit=self._get_env_int("OMIO_RATE_LIMIT", 100),
            timeout=self._get_env_int("OMIO_TIMEOUT", 30)
        )
        
        # Security Configuration  
        security_config = SecurityConfig(
            max_email_size_kb=self._get_env_int("MAX_EMAIL_SIZE_KB", 1024),
            rate_limit_requests_per_minute=self._get_env_int("RATE_LIMIT_REQUESTS_PER_MINUTE", 60),
            input_validation_enabled=self._get_env_bool("INPUT_VALIDATION_ENABLED", True),
            sanitization_enabled=self._get_env_bool("SANITIZATION_ENABLED", True),
            log_security_events=self._get_env_bool("LOG_SECURITY_EVENTS", True)
        )
        
        # Application Configuration
        self._config = ApplicationConfig(
            smtp=smtp_config,
            amadeus=amadeus_config,
            omio=omio_config,
            security=security_config,
            debug=self._get_env_bool("DEBUG", False),
            log_level=self._get_env_value("LOG_LEVEL", "INFO")
        )
        
        # Validate configuration
        self._config.validate()
        
        return self._config
    
    def get_config(self) -> ApplicationConfig:
        """Get current configuration (load if not already loaded)."""
        return self.load_config()
    
    def reload_config(self) -> ApplicationConfig:
        """Reload configuration from environment."""
        self._config = None
        self._load_environment()
        return self.load_config()


# Global configuration manager
config_manager = ConfigurationManager()
config = config_manager.get_config()

# Legacy compatibility exports
SMTP_HOST = config.smtp.host
SMTP_PORT = config.smtp.port
SMTP_USERNAME = config.smtp.username
SMTP_PASSWORD = config.smtp.password
SMTP_FROM_NAME = config.smtp.from_name

AMADEUS_API_KEY = config.amadeus.api_key
AMADEUS_API_SECRET = config.amadeus.api_secret
OMIO_API_KEY = config.omio.api_key

USE_AMADEUS = config.amadeus.is_configured
USE_OMIO = config.omio.is_configured

# Security settings
MAX_EMAIL_SIZE_KB = config.security.max_email_size_kb
RATE_LIMIT_REQUESTS_PER_MINUTE = config.security.rate_limit_requests_per_minute
