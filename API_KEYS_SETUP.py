"""
API Keys Setup Guide for Smart Travel Optimizer
===============================================

This guide walks you through obtaining API keys for all supported providers.
"""

# ==============================================================================
# 1. AMADEUS API KEYS (Flight Data)
# ==============================================================================

AMADEUS_SETUP = {
    "website": "https://developers.amadeus.com/",
    "steps": [
        "1. Go to https://developers.amadeus.com/",
        "2. Click 'Get Started' or 'Sign Up'",
        "3. Create free developer account",
        "4. Verify your email address",
        "5. Go to 'My Apps' section",
        "6. Click 'Create New App'",
        "7. Fill in application details:",
        "   - App Name: 'Smart Travel Optimizer'",
        "   - Description: 'AI-powered travel route optimization'",
        "   - Website: Optional",
        "8. Once approved, copy your credentials:",
        "   - API Key (Client ID)",
        "   - API Secret (Client Secret)"
    ],
    "free_tier": {
        "requests_per_month": 2000,
        "environment": "Test (Mock data)",
        "cost": "Free"
    },
    "production": {
        "environment": "Live (Real data)",
        "cost": "Pay per request",
        "features": ["Real-time flight data", "Higher rate limits", "Better performance"]
    },
    "endpoints": {
        "test": "https://test.api.amadeus.com",
        "production": "https://api.amadeus.com"
    }
}

# ==============================================================================
# 2. OMIO API KEYS (Train & Bus Data)
# ==============================================================================

OMIO_SETUP = {
    "website": "https://www.omio.com/affiliate",
    "type": "Business Partnership Required",
    "steps": [
        "1. Go to https://www.omio.com/affiliate",
        "2. Apply for Partner Program",
        "3. Fill out business application form:",
        "   - Company name and details",
        "   - Expected monthly bookings",
        "   - Website/app information",
        "   - Use case description",
        "4. Wait for approval (can take 1-2 weeks)",
        "5. Once approved, you'll receive:",
        "   - API Key",
        "   - API Documentation",
        "   - Integration guidelines"
    ],
    "requirements": [
        "Legitimate business use case",
        "Professional website or application",
        "Minimum expected booking volume",
        "EU/European focus preferred"
    ],
    "alternative": {
        "name": "Omio Affiliate Program",
        "website": "https://www.omio.com/affiliate",
        "description": "Easier approval, commission-based model",
        "api_access": "Limited to booking referrals"
    },
    "features": [
        "Multi-modal search (train, bus, flight)",
        "Real-time pricing and availability",
        "European route coverage",
        "Booking capabilities"
    ]
}

# ==============================================================================
# 3. MOCK PROVIDER (No API Key Required)
# ==============================================================================

MOCK_PROVIDER_INFO = {
    "description": "Built-in test provider with sample data",
    "api_key_required": False,
    "data_source": "data/sample_routes.json",
    "features": [
        "✅ No API key needed",
        "✅ Works immediately",
        "✅ Realistic sample data", 
        "✅ Dynamic pricing simulation",
        "✅ Error simulation for testing",
        "✅ Perfect for development"
    ],
    "sample_routes": [
        "Stuttgart → Vienna (flight, train, bus)",
        "Berlin → Paris (multiple options)",
        "London → Rome (various carriers)",
        "Madrid → Prague (mixed transport)"
    ],
    "customization": [
        "Add your own sample routes",
        "Modify pricing algorithms",
        "Simulate different scenarios",
        "Test error handling"
    ]
}

# ==============================================================================
# 4. QUICK START GUIDE
# ==============================================================================

def quick_start_guide():
    """
    Quick start instructions for different scenarios.
    """
    
    scenarios = {
        "development_testing": {
            "description": "Just want to test the app",
            "setup": [
                "1. No API keys needed!",
                "2. Use Mock Provider (already configured)",
                "3. Run: python main.py --origin Stuttgart --destination Vienna --date 2025-10-01",
                "4. Or run: streamlit run streamlit_app.py"
            ],
            "time_required": "0 minutes",
            "cost": "Free"
        },
        
        "real_flight_data": {
            "description": "Want real flight data",
            "setup": [
                "1. Register at https://developers.amadeus.com/",
                "2. Get API Key and Secret (5 minutes)",
                "3. Add to .env file:",
                "   AMADEUS_API_KEY=your_key_here",
                "   AMADEUS_API_SECRET=your_secret_here",
                "4. Run the app - it will use real data!"
            ],
            "time_required": "5-10 minutes",
            "cost": "Free (2000 requests/month)"
        },
        
        "full_production": {
            "description": "Production app with all providers",
            "setup": [
                "1. Get Amadeus keys (5 minutes)",
                "2. Apply for Omio partnership (1-2 weeks)",
                "3. Configure all keys in .env",
                "4. Test with small traffic",
                "5. Scale up as needed"
            ],
            "time_required": "1-2 weeks (due to Omio approval)",
            "cost": "Variable (pay per request)"
        }
    }
    
    return scenarios

# ==============================================================================
# 5. ENVIRONMENT SETUP
# ==============================================================================

def setup_environment_variables():
    """
    How to properly set up your .env file.
    """
    
    env_template = '''
# =============================================================================
# Smart Travel Optimizer - Environment Configuration
# =============================================================================

# Email Configuration (Required for notifications)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password  # Use App Password for Gmail!
SMTP_FROM_NAME=Smart Travel Optimizer

# Amadeus API (Optional - get from https://developers.amadeus.com/)
AMADEUS_API_KEY=your_amadeus_api_key_here
AMADEUS_API_SECRET=your_amadeus_api_secret_here

# Omio API (Optional - requires business partnership)
OMIO_API_KEY=your_omio_api_key_here

# Security Settings (Optional)
RATE_LIMIT_REQUESTS_PER_MINUTE=60
MAX_EMAIL_SIZE_KB=1024

# Development Settings (Optional)
DEBUG_MODE=false
LOG_LEVEL=INFO
ENABLE_MOCK_PROVIDER=true
'''
    
    return env_template.strip()

# ==============================================================================
# 6. TESTING YOUR SETUP
# ==============================================================================

TEST_COMMANDS = {
    "mock_only": {
        "description": "Test with Mock provider only",
        "command": "python main.py --origin Stuttgart --destination Vienna --date 2025-10-01",
        "expected": "Should return 2-4 sample routes immediately"
    },
    
    "amadeus_test": {
        "description": "Test Amadeus API integration",
        "command": "python -c \"from src.tools.providers.amadeus_provider import AmadeusProvider; print('Amadeus:', AmadeusProvider().validate_config())\"",
        "expected": "Should return True if keys are valid"
    },
    
    "omio_test": {
        "description": "Test Omio API integration", 
        "command": "python -c \"from src.tools.providers.omio_provider import OmioProvider; print('Omio:', OmioProvider().validate_config())\"",
        "expected": "Should return True if keys are valid"
    },
    
    "web_interface": {
        "description": "Test web interface",
        "command": "streamlit run streamlit_app.py",
        "expected": "Should open web interface at http://localhost:8501"
    }
}

# ==============================================================================
# 7. TROUBLESHOOTING
# ==============================================================================

TROUBLESHOOTING = {
    "amadeus_issues": {
        "invalid_credentials": {
            "error": "401 Unauthorized",
            "solution": "Check API Key and Secret are correct"
        },
        "quota_exceeded": {
            "error": "429 Too Many Requests",
            "solution": "You've exceeded the free tier limit (2000/month)"
        },
        "test_vs_production": {
            "error": "No data returned",
            "solution": "Make sure you're using test.api.amadeus.com for free tier"
        }
    },
    
    "omio_issues": {
        "not_approved": {
            "error": "API key not working",
            "solution": "Omio API requires business partnership approval"
        },
        "geographic_restrictions": {
            "error": "Limited route data",
            "solution": "Omio focuses on European routes"
        }
    },
    
    "mock_provider_issues": {
        "no_routes": {
            "error": "No routes found",
            "solution": "Check data/sample_routes.json exists and has matching routes"
        }
    }
}

# ==============================================================================
# 8. USAGE EXAMPLES
# ==============================================================================

if __name__ == "__main__":
    print("🔑 Smart Travel Optimizer - API Keys Setup Guide")
    print("=" * 60)
    print()
    
    print("🚀 QUICK START:")
    print("For immediate testing (no API keys needed):")
    print("1. python main.py --origin Stuttgart --destination Vienna --date 2025-10-01")
    print("2. streamlit run streamlit_app.py")
    print()
    
    print("🌐 FOR REAL DATA:")
    print("1. Get Amadeus keys: https://developers.amadeus.com/")
    print("2. Add keys to .env file")
    print("3. Run the app - it will automatically use real data!")
    print()
    
    print("📧 EMAIL SETUP:")
    print("1. Use Gmail App Password (not regular password)")
    print("2. Enable 2FA on Gmail")
    print("3. Generate App Password in Google Account settings")
    print()
    
    scenarios = quick_start_guide()
    for name, scenario in scenarios.items():
        print(f"📋 {name.upper().replace('_', ' ')}:")
        print(f"   {scenario['description']}")
        print(f"   Time: {scenario['time_required']}")
        print(f"   Cost: {scenario['cost']}")
        print()
