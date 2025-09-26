"""
Security utilities for input validation and sanitization.
"""
import re
import html
from typing import Optional
from datetime import datetime


def validate_email(email: str) -> bool:
    """Validate email format using regex."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_city_name(city: str) -> str:
    """Sanitize city name input to prevent injection attacks."""
    if not city or not isinstance(city, str):
        raise ValueError("City name must be a non-empty string")
    
    # Remove HTML tags and escape special characters
    sanitized = html.escape(city.strip())
    
    # Allow only letters, spaces, hyphens, and apostrophes
    if not re.match(r"^[a-zA-Z\s\-']+$", sanitized):
        raise ValueError("City name contains invalid characters")
    
    # Limit length
    if len(sanitized) > 100:
        raise ValueError("City name too long")
    
    return sanitized


def validate_date(date_str: str) -> bool:
    """Validate date format (YYYY-MM-DD)."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except ValueError:
        return False


def validate_numeric_input(value: any, min_val: float = 0, max_val: float = 100) -> bool:
    """Validate numeric inputs within reasonable bounds."""
    try:
        num_val = float(value)
        return min_val <= num_val <= max_val
    except (ValueError, TypeError):
        return False


def sanitize_string_input(input_str: str, max_length: int = 1000) -> Optional[str]:
    """Sanitize general string input."""
    if not input_str:
        return None
    
    if not isinstance(input_str, str):
        return None
    
    # Remove HTML tags and escape
    sanitized = html.escape(input_str.strip())
    
    # Limit length
    if len(sanitized) > max_length:
        return sanitized[:max_length]
    
    return sanitized
