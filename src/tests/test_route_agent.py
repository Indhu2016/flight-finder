"""
Unit tests for route agent functionality.
"""
import pytest
from unittest.mock import patch, MagicMock
from src.agents.route_agent import collect_routes, plan_best_routes


class TestRouteAgent:
    """Test route agent functionality."""
    
    def test_collect_routes_mock_provider(self):
        """Test route collection with mock provider."""
        with patch('src.config.USE_AMADEUS', False), \
             patch('src.config.USE_OMIO', False):
            routes = collect_routes("Stuttgart", "Vienna", "2025-10-01")
            assert isinstance(routes, list)
    
    def test_plan_best_routes_with_filters(self):
        """Test route planning with filters."""
        with patch('src.config.USE_AMADEUS', False), \
             patch('src.config.USE_OMIO', False):
            routes = plan_best_routes(
                "Stuttgart", 
                "Vienna", 
                "2025-10-01",
                min_checked_bags=2,
                max_connections=2
            )
            assert isinstance(routes, list)
    
    def test_collect_routes_provider_failure(self):
        """Test graceful handling of provider failures."""
        with patch('src.tools.providers.mock_provider.MockProvider.search') as mock_search:
            mock_search.side_effect = Exception("Provider failed")
            routes = collect_routes("Stuttgart", "Vienna", "2025-10-01")
            assert routes == []  # Should return empty list on failure
