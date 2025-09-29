"""Travel Security Configuration - Minimal Settings"""

from dataclasses import dataclass
from enum import Enum


class SecurityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class SecurityConfig:
    """Basic security settings"""
    scan_level: SecurityLevel = SecurityLevel.MEDIUM
    max_scan_time: int = 120
    api_security_checks: bool = True
    payment_security_checks: bool = True


# Travel API patterns
TRAVEL_APIS = {
    'amadeus': 'https://api.amadeus.com',
    'omio': 'https://api.omio.com',
    'booking': 'https://booking.com'
}

# Security patterns
SECRET_PATTERNS = [
    'api_key=',
    'password=', 
    'token=',
    'secret='
]

INSECURE_PATTERNS = [
    'http://',
    'verify=False'
]

# Default config
DEFAULT_CONFIG = SecurityConfig()


def get_security_config(env: str = "development") -> SecurityConfig:
    """Get security config for environment"""
    config = SecurityConfig()
    
    if env == "production":
        config.scan_level = SecurityLevel.HIGH
        config.max_scan_time = 300
    elif env == "development":
        config.scan_level = SecurityLevel.MEDIUM
        config.max_scan_time = 60
    
    return config
