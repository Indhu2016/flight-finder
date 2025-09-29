#!/usr/bin/env python3
"""
API Keys Test Script for Smart Travel Optimizer
==============================================

This script helps you test your API key configurations.
Run: python test_api_keys.py
"""

import os
import sys
from pathlib import Path
from typing import Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

# Load environment variables
load_dotenv()

console = Console()


def test_environment_setup() -> Dict[str, Any]:
    """Test basic environment setup."""
    results = {
        "env_file_exists": os.path.exists(".env"),
        "required_modules": True,
        "python_version": sys.version_info >= (3, 8)
    }
    
    try:
        import requests
        import streamlit
        import pydantic
    except ImportError as e:
        results["required_modules"] = False
        results["missing_module"] = str(e)
    
    return results


def test_mock_provider() -> Dict[str, Any]:
    """Test Mock provider (should always work)."""
    try:
        from tools.providers.mock_provider import MockProvider
        
        provider = MockProvider()
        test_routes = provider.search("Stuttgart", "Vienna", "2025-10-01")
        
        return {
            "status": "✅ Working",
            "routes_found": len(test_routes),
            "provider_available": True,
            "details": f"Found {len(test_routes)} sample routes"
        }
    except Exception as e:
        return {
            "status": "❌ Error",
            "routes_found": 0,
            "provider_available": False,
            "error": str(e)
        }


def test_amadeus_provider() -> Dict[str, Any]:
    """Test Amadeus API configuration."""
    api_key = os.getenv("AMADEUS_API_KEY")
    api_secret = os.getenv("AMADEUS_API_SECRET")
    
    if not api_key or not api_secret:
        return {
            "status": "⚠️ Not Configured",
            "configured": False,
            "details": "API key or secret not found in .env file"
        }
    
    try:
        from tools.providers.amadeus_provider import AmadeusProvider
        
        provider = AmadeusProvider()
        is_valid = provider.validate_config()
        
        if is_valid:
            return {
                "status": "✅ Configured",
                "configured": True,
                "details": "API keys are present and format looks correct"
            }
        else:
            return {
                "status": "❌ Invalid",
                "configured": False,
                "details": "API keys present but validation failed"
            }
    except Exception as e:
        return {
            "status": "❌ Error",
            "configured": False,
            "error": str(e)
        }


def test_omio_provider() -> Dict[str, Any]:
    """Test Omio API configuration."""
    api_key = os.getenv("OMIO_API_KEY")
    
    if not api_key:
        return {
            "status": "⚠️ Not Configured",
            "configured": False,
            "details": "API key not found in .env file (requires business partnership)"
        }
    
    try:
        from tools.providers.omio_provider import OmioProvider
        
        provider = OmioProvider()
        is_valid = provider.validate_config()
        
        if is_valid:
            return {
                "status": "✅ Configured",
                "configured": True,
                "details": "API key is present"
            }
        else:
            return {
                "status": "❌ Invalid", 
                "configured": False,
                "details": "API key present but validation failed"
            }
    except Exception as e:
        return {
            "status": "❌ Error",
            "configured": False,
            "error": str(e)
        }


def test_email_configuration() -> Dict[str, Any]:
    """Test email configuration."""
    smtp_host = os.getenv("SMTP_HOST")
    smtp_username = os.getenv("SMTP_USERNAME") 
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not all([smtp_host, smtp_username, smtp_password]):
        return {
            "status": "⚠️ Not Configured",
            "configured": False,
            "details": "Missing SMTP configuration in .env file"
        }
    
    # Basic validation (don't actually send email in test)
    if "@" not in smtp_username:
        return {
            "status": "❌ Invalid",
            "configured": False,
            "details": "SMTP_USERNAME should be a valid email address"
        }
    
    return {
        "status": "✅ Configured",
        "configured": True,
        "details": f"SMTP configured for {smtp_host}"
    }


def main():
    """Run all API tests and display results."""
    console.print("\n🔑 Smart Travel Optimizer - API Keys Test\n", style="bold blue")
    
    # Test environment setup
    rprint("[yellow]Testing environment setup...[/yellow]")
    env_results = test_environment_setup()
    
    # Test providers
    rprint("[yellow]Testing providers...[/yellow]")
    mock_results = test_mock_provider()
    amadeus_results = test_amadeus_provider()
    omio_results = test_omio_provider()
    email_results = test_email_configuration()
    
    # Create results table
    table = Table(title="API Configuration Test Results", show_header=True, header_style="bold magenta")
    table.add_column("Component", style="cyan", width=20)
    table.add_column("Status", width=15)
    table.add_column("Details", width=50)
    
    # Add results to table
    components = [
        ("Environment", "✅ Ready" if all(env_results.values()) else "❌ Issues", 
         f"Python {sys.version_info.major}.{sys.version_info.minor}, modules OK" if env_results["required_modules"] else "Missing required modules"),
        ("Mock Provider", mock_results["status"], mock_results.get("details", mock_results.get("error", ""))),
        ("Amadeus API", amadeus_results["status"], amadeus_results.get("details", amadeus_results.get("error", ""))),
        ("Omio API", omio_results["status"], omio_results.get("details", omio_results.get("error", ""))),
        ("Email (SMTP)", email_results["status"], email_results.get("details", email_results.get("error", "")))
    ]
    
    for component, status, details in components:
        table.add_row(component, status, details)
    
    console.print(table)
    
    # Summary and recommendations
    console.print("\n📋 Summary & Next Steps:", style="bold green")
    
    if mock_results["provider_available"]:
        rprint("✅ [green]Ready for immediate testing with Mock provider[/green]")
        rprint("   Run: [cyan]python main.py --origin Stuttgart --destination Vienna --date 2025-10-01[/cyan]")
        rprint("   Or:  [cyan]streamlit run streamlit_app.py[/cyan]")
    
    if not amadeus_results["configured"]:
        rprint("🔧 [yellow]For real flight data:[/yellow]")
        rprint("   1. Get Amadeus API keys: [blue]https://developers.amadeus.com/[/blue]")
        rprint("   2. Add keys to .env file")
    
    if not omio_results["configured"]:
        rprint("🚂 [yellow]For train/bus data:[/yellow]") 
        rprint("   1. Apply at: [blue]https://www.omio.com/affiliate[/blue]")
        rprint("   2. Business partnership required")
    
    if not email_results["configured"]:
        rprint("📧 [yellow]For email notifications:[/yellow]")
        rprint("   1. Set up Gmail App Password")
        rprint("   2. Add SMTP settings to .env file")
    
    rprint(f"\n💡 [blue]Need help? Check API_KEYS_SETUP.py for detailed instructions[/blue]")


if __name__ == "__main__":
    main()
