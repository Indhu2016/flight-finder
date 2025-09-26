"""
Mock Travel Data Provider for Testing and Development.

This provider serves sample data for testing and development purposes,
implementing all the features of a real provider but using static data.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import random

from .base import BaseProvider, ProviderConfig, SearchParams, SearchResult, SearchStatus

logger = logging.getLogger(__name__)

# Default data path
DATA_PATH = Path(__file__).parents[2] / "data" / "sample_routes.json"


class MockProvider(BaseProvider):
    """
    Mock provider for testing and development.
    
    Features:
    - Serves realistic sample data
    - Configurable response delays for testing
    - Error simulation for testing error handling
    - Dynamic route generation based on parameters
    """
    
    def __init__(self, config: Optional[ProviderConfig] = None, data_path: Optional[Path] = None):
        if config is None:
            config = ProviderConfig(
                name="MockProvider",
                enabled=True,
                timeout_seconds=5,
                max_retries=1,
                cache_ttl_minutes=60
            )
        
        super().__init__(config)
        self.data_path = data_path or DATA_PATH
        self.sample_routes = self._load_sample_data()
        
        # Mock provider specific settings
        self.simulate_delay = config.custom_settings.get("simulate_delay", False)
        self.max_delay_seconds = config.custom_settings.get("max_delay_seconds", 2.0)
        self.error_rate = config.custom_settings.get("error_rate", 0.0)  # 0.0 to 1.0
        self.dynamic_pricing = config.custom_settings.get("dynamic_pricing", True)
        
        logger.info(f"MockProvider initialized with {len(self.sample_routes)} sample routes")
    
    def _load_sample_data(self) -> List[Dict[str, Any]]:
        """Load sample route data from JSON file."""
        try:
            if not self.data_path.exists():
                logger.warning(f"Sample data file not found: {self.data_path}")
                return self._generate_default_routes()
            
            with open(self.data_path, 'r', encoding='utf-8') as f:
                routes = json.load(f)
            
            # Validate route data
            validated_routes = []
            for route in routes:
                if self._validate_route_data(route):
                    validated_routes.append(route)
                else:
                    logger.warning(f"Invalid route data skipped: {route}")
            
            return validated_routes
            
        except Exception as e:
            logger.error(f"Failed to load sample data: {e}")
            return self._generate_default_routes()
    
    def _validate_route_data(self, route: Dict[str, Any]) -> bool:
        """Validate that route data has required fields."""
        required_fields = [
            'mode', 'origin', 'destination', 'date', 
            'price_eur', 'total_hours', 'connections'
        ]
        
        return all(field in route for field in required_fields)
    
    def _generate_default_routes(self) -> List[Dict[str, Any]]:
        """Generate default sample routes when no data file is available."""
        return [
            {
                "provider": "MOCK",
                "mode": "flight",
                "airline": "Mock Airlines",
                "origin": "Stuttgart",
                "destination": "Vienna",
                "date": "2025-10-01",
                "price_eur": 180,
                "total_hours": 1.25,
                "connections": 0,
                "baggage": {"checked_bags": 2, "per_bag_kg": 23}
            },
            {
                "provider": "MOCK",
                "mode": "train",
                "carrier": "Mock Rail",
                "origin": "Stuttgart",
                "destination": "Vienna",
                "date": "2025-10-01",
                "price_eur": 120,
                "total_hours": 7.2,
                "connections": 1,
                "baggage": {"checked_bags": 3, "per_bag_kg": 30}
            }
        ]
    
    def validate_config(self) -> bool:
        """Validate mock provider configuration."""
        # Mock provider doesn't need external credentials
        return True
    
    def search_routes(self, params: SearchParams) -> SearchResult:
        """
        Search for routes using sample data with realistic behavior simulation.
        """
        try:
            # Simulate processing delay if configured
            if self.simulate_delay:
                import time
                delay = random.uniform(0.1, self.max_delay_seconds)
                time.sleep(delay)
            
            # Simulate random errors if configured
            if self.error_rate > 0 and random.random() < self.error_rate:
                raise Exception("Simulated provider error for testing")
            
            # Find matching routes
            matching_routes = self._find_matching_routes(params)
            
            # Apply dynamic modifications
            if self.dynamic_pricing:
                matching_routes = self._apply_dynamic_pricing(matching_routes, params)
            
            # Add realistic variations
            matching_routes = self._add_route_variations(matching_routes, params)
            
            return SearchResult(
                provider_name=self.name,
                status=SearchStatus.COMPLETED,
                routes=matching_routes,
                metadata={
                    "simulated_delay": self.simulate_delay,
                    "dynamic_pricing": self.dynamic_pricing,
                    "total_sample_routes": len(self.sample_routes)
                }
            )
            
        except Exception as e:
            logger.error(f"Mock provider search failed: {e}")
            return SearchResult(
                provider_name=self.name,
                status=SearchStatus.FAILED,
                error_message=str(e)
            )
    
    def _find_matching_routes(self, params: SearchParams) -> List[Dict[str, Any]]:
        """Find routes matching search parameters."""
        matching_routes = []
        
        origin_city = params.origin.city.lower()
        destination_city = params.destination.city.lower()
        
        for route in self.sample_routes:
            # Check origin and destination match
            if (route["origin"].lower() == origin_city and 
                route["destination"].lower() == destination_city):
                
                # Create a copy to avoid modifying original data
                route_copy = route.copy()
                
                # Update date to match search
                route_copy["date"] = params.departure_date
                
                # Apply connection filter
                if route_copy["connections"] <= params.max_connections:
                    matching_routes.append(route_copy)
        
        return matching_routes
    
    def _apply_dynamic_pricing(self, routes: List[Dict[str, Any]], params: SearchParams) -> List[Dict[str, Any]]:
        """Apply dynamic pricing based on search parameters and random factors."""
        for route in routes:
            base_price = route["price_eur"]
            
            # Apply date-based pricing (weekend premium, advance booking discount)
            try:
                search_date = datetime.fromisoformat(params.departure_date.replace('Z', '+00:00'))
                days_ahead = (search_date - datetime.now()).days
                
                # Advance booking discount
                if days_ahead > 30:
                    base_price *= 0.85  # 15% discount
                elif days_ahead < 7:
                    base_price *= 1.20  # 20% premium for last-minute
                
                # Weekend premium
                if search_date.weekday() >= 5:  # Saturday or Sunday
                    base_price *= 1.10  # 10% weekend premium
                
            except ValueError:
                pass  # Keep original price if date parsing fails
            
            # Add random variation (±10%)
            variation = random.uniform(0.9, 1.1)
            route["price_eur"] = round(base_price * variation, 2)
            
            # Ensure minimum price
            route["price_eur"] = max(route["price_eur"], 10.0)
        
        return routes
    
    def _add_route_variations(self, routes: List[Dict[str, Any]], params: SearchParams) -> List[Dict[str, Any]]:
        """Add realistic variations to routes for more diverse results."""
        enhanced_routes = []
        
        for route in routes:
            enhanced_routes.append(route)
            
            # Add variations for some routes
            if len(enhanced_routes) < 5 and random.random() < 0.6:
                variations = self._create_route_variations(route)
                enhanced_routes.extend(variations)
        
        # Sort by price (ascending)
        enhanced_routes.sort(key=lambda r: r["price_eur"])
        
        return enhanced_routes[:8]  # Limit to 8 routes max
    
    def _create_route_variations(self, base_route: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create realistic variations of a base route."""
        variations = []
        
        # Time variation (different departure times)
        if base_route["mode"] in ["flight", "train"]:
            time_variant = base_route.copy()
            time_variant["price_eur"] = round(base_route["price_eur"] * random.uniform(0.95, 1.15), 2)
            time_variant["total_hours"] = round(base_route["total_hours"] * random.uniform(0.9, 1.2), 2)
            
            # Add departure time info
            departure_times = ["06:30", "09:15", "14:20", "18:45", "21:10"]
            time_variant["departure_time"] = random.choice(departure_times)
            
            variations.append(time_variant)
        
        # Connection variation (add/remove connections)
        if base_route["connections"] == 0 and random.random() < 0.4:
            connection_variant = base_route.copy()
            connection_variant["connections"] = 1
            connection_variant["price_eur"] = round(base_route["price_eur"] * 0.8, 2)  # Cheaper with connection
            connection_variant["total_hours"] = round(base_route["total_hours"] * 1.5, 2)  # Longer
            connection_variant["via"] = self._get_random_via_city(base_route["origin"], base_route["destination"])
            
            variations.append(connection_variant)
        
        return variations
    
    def _get_random_via_city(self, origin: str, destination: str) -> List[str]:
        """Get realistic via cities for a route."""
        via_cities = {
            ("Stuttgart", "Vienna"): ["Munich", "Salzburg", "Frankfurt"],
            ("Berlin", "Paris"): ["Frankfurt", "Brussels", "Cologne"],
            ("London", "Rome"): ["Paris", "Milan", "Zurich"],
            ("Madrid", "Prague"): ["Barcelona", "Vienna", "Munich"]
        }
        
        key = (origin, destination)
        if key in via_cities:
            return [random.choice(via_cities[key])]
        
        # Default via cities
        default_hubs = ["Frankfurt", "Paris", "Amsterdam", "Munich", "Vienna"]
        return [random.choice(default_hubs)]
    
    def search(self, origin: str, destination: str, date: str) -> List[Dict[str, Any]]:
        """Legacy interface for backward compatibility."""
        params = SearchParams(
            origin=origin,
            destination=destination,
            departure_date=date
        )
        
        result = self.search_routes(params)
        return result.routes if result.is_successful else []
    
    def add_sample_route(self, route: Dict[str, Any]) -> bool:
        """Add a new sample route for testing."""
        if self._validate_route_data(route):
            self.sample_routes.append(route)
            logger.info(f"Added sample route: {route['origin']} -> {route['destination']}")
            return True
        else:
            logger.warning(f"Invalid route data not added: {route}")
            return False
    
    def clear_sample_routes(self):
        """Clear all sample routes."""
        self.sample_routes.clear()
        logger.info("All sample routes cleared")
    
    def get_sample_routes_count(self) -> int:
        """Get count of available sample routes."""
        return len(self.sample_routes)
    
    def set_error_simulation(self, error_rate: float):
        """Set error simulation rate for testing."""
        self.error_rate = max(0.0, min(1.0, error_rate))  # Clamp between 0 and 1
        logger.info(f"Error simulation rate set to {self.error_rate:.2%}")
    
    def set_delay_simulation(self, enabled: bool, max_delay: float = 2.0):
        """Configure delay simulation for testing."""
        self.simulate_delay = enabled
        self.max_delay_seconds = max_delay
        logger.info(f"Delay simulation: {'enabled' if enabled else 'disabled'} (max: {max_delay}s)")
