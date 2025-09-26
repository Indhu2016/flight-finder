"""
Unit tests for security utilities.
"""
import pytest
from src.tools.security import (
    validate_email,
    sanitize_city_name,
    validate_date,
    validate_numeric_input,
    sanitize_string_input
)


class TestSecurityValidation:
    """Test security validation functions."""
    
    def test_validate_email_valid(self):
        """Test valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@example.com"
        ]
        for email in valid_emails:
            assert validate_email(email), f"Email {email} should be valid"
    
    def test_validate_email_invalid(self):
        """Test invalid email addresses."""
        invalid_emails = [
            "invalid",
            "@example.com",
            "test@",
            "test..test@example.com",
            "test@example",
            "",
            None
        ]
        for email in invalid_emails:
            assert not validate_email(email), f"Email {email} should be invalid"
    
    def test_sanitize_city_name_valid(self):
        """Test valid city names."""
        valid_cities = [
            "Stuttgart",
            "New York",
            "Saint-Denis",
            "O'Connor"
        ]
        for city in valid_cities:
            result = sanitize_city_name(city)
            assert result == city
    
    def test_sanitize_city_name_invalid(self):
        """Test invalid city names."""
        with pytest.raises(ValueError):
            sanitize_city_name("City123")
        
        with pytest.raises(ValueError):
            sanitize_city_name("City<script>")
        
        with pytest.raises(ValueError):
            sanitize_city_name("")
        
        with pytest.raises(ValueError):
            sanitize_city_name("A" * 101)  # Too long
    
    def test_validate_date_valid(self):
        """Test valid dates."""
        valid_dates = [
            "2025-01-01",
            "2025-12-31",
            "2024-02-29"  # Leap year
        ]
        for date in valid_dates:
            assert validate_date(date), f"Date {date} should be valid"
    
    def test_validate_date_invalid(self):
        """Test invalid dates."""
        invalid_dates = [
            "2025-13-01",
            "2025-01-32",
            "25-01-01",
            "2025/01/01",
            "invalid"
        ]
        for date in invalid_dates:
            assert not validate_date(date), f"Date {date} should be invalid"
    
    def test_validate_numeric_input(self):
        """Test numeric input validation."""
        assert validate_numeric_input(5, 0, 10)
        assert validate_numeric_input(0, 0, 10)
        assert validate_numeric_input(10, 0, 10)
        assert not validate_numeric_input(-1, 0, 10)
        assert not validate_numeric_input(11, 0, 10)
        assert not validate_numeric_input("invalid", 0, 10)
    
    def test_sanitize_string_input(self):
        """Test string input sanitization."""
        assert sanitize_string_input("test") == "test"
        assert sanitize_string_input("  test  ") == "test"
        assert sanitize_string_input("<script>") == "&lt;script&gt;"
        assert sanitize_string_input("") is None
        assert sanitize_string_input(None) is None
        
        # Test length limiting
        long_string = "A" * 1500
        result = sanitize_string_input(long_string, 1000)
        assert len(result) == 1000
