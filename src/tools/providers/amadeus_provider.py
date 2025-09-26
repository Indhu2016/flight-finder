"""
Amadeus Travel API Provider Implementation.

This module integrates with the Amadeus for Developers API to fetch real-time
flight, hotel, and travel data. It implements enterprise-grade features like
authentication, rate limiting, error handling, and response caching.
"""

import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .base import BaseProvider, ProviderConfig, SearchParams, SearchResult, SearchStatus
from src.config import AMADEUS_API_KEY, AMADEUS_API_SECRET

logger = logging.getLogger(__name__)


class AmadeusError(Exception):
    """Custom exception for Amadeus API errors."""
    def __init__(self, message: str, error_code: Optional[str] = None, status_code: Optional[int] = None):
        super().__init__(message)
        self.error_code = error_code
        self.status_code = status_code


class AmadeusProvider(BaseProvider):
    """
    Professional Amadeus API integration with enterprise features.
    
    Features:
    - OAuth2 authentication with automatic token refresh
    - Comprehensive error handling and retry logic
    - Rate limiting and quota management
    - Response validation and standardization
    - Request/response logging for debugging
    - Caching for performance optimization
    """
    
    # Amadeus API endpoints
    BASE_URL = "https://api.amadeus.com"
    AUTH_URL = f"{BASE_URL}/v1/security/oauth2/token"
    FLIGHT_OFFERS_URL = f"{BASE_URL}/v2/shopping/flight-offers"
    FLIGHT_DATES_URL = f"{BASE_URL}/v1/shopping/flight-dates"
    LOCATIONS_URL = f"{BASE_URL}/v1/reference-data/locations"
    
    def __init__(self, config: Optional[ProviderConfig] = None):
        if config is None:
            config = ProviderConfig(
                name="AmadeusProvider",
                enabled=bool(AMADEUS_API_KEY and AMADEUS_API_SECRET),
                api_key=AMADEUS_API_KEY,
                api_secret=AMADEUS_API_SECRET,
                timeout_seconds=30,
                max_retries=3,
                retry_delay_seconds=1.0,
                rate_limit_per_minute=30,  # Amadeus rate limit
                cache_ttl_minutes=15  # Cache for 15 minutes
            )
        
        super().__init__(config)
        
        # Authentication
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[datetime] = None
        
        # HTTP session with connection pooling and retries
        self._session = self._create_http_session()
        
        # API-specific settings
        self.max_flight_offers = config.custom_settings.get("max_flight_offers", 50)
        self.cabin_class_mapping = {
            "economy": "ECONOMY",
            "premium_economy": "PREMIUM_ECONOMY", 
            "business": "BUSINESS",
            "first": "FIRST"
        }
        
        logger.info("AmadeusProvider initialized")
    
    def _create_http_session(self) -> requests.Session:
        """Create configured HTTP session with retries and connection pooling."""
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=self.config.max_retries,
            backoff_factor=self.config.retry_delay_seconds,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=20
        )
        
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Set default headers
        session.headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "SmartTravelOptimizer/1.0"
        })
        
        return session
    
    def validate_config(self) -> bool:
        """Validate Amadeus API configuration."""
        if not self.config.api_key or not self.config.api_secret:
            logger.error("Amadeus API credentials not configured")
            return False
        
        try:
            # Test authentication
            token = self._get_access_token()
            return bool(token)
        except Exception as e:
            logger.error(f"Amadeus configuration validation failed: {e}")
            return False
    
    def _get_access_token(self) -> str:
        """Get or refresh OAuth2 access token."""
        # Check if current token is still valid
        if (self._access_token and self._token_expires_at and 
            datetime.now() < self._token_expires_at - timedelta(minutes=5)):
            return self._access_token
        
        # Request new token
        try:
            logger.debug("Requesting new Amadeus access token")
            
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.config.api_key,
                "client_secret": self.config.api_secret
            }
            
            response = self._session.post(
                self.AUTH_URL,
                data=auth_data,
                timeout=self.config.timeout_seconds
            )
            
            if response.status_code != 200:
                raise AmadeusError(
                    f"Authentication failed: {response.text}",
                    status_code=response.status_code
                )
            
            token_data = response.json()
            self._access_token = token_data["access_token"]
            
            # Calculate expiration time (subtract buffer for safety)
            expires_in = token_data.get("expires_in", 1799)  # Default 30 minutes
            self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
            
            logger.info("Amadeus access token refreshed successfully")
            return self._access_token
            
        except requests.RequestException as e:
            raise AmadeusError(f"Failed to get access token: {e}")
        except (KeyError, ValueError) as e:
            raise AmadeusError(f"Invalid token response format: {e}")
    
    def search_routes(self, params: SearchParams) -> SearchResult:
        """
        Search for flight offers using Amadeus API.
        """
        try:
            # Get access token
            token = self._get_access_token()
            
            # Convert locations to IATA codes if needed
            origin_code = self._resolve_location_code(params.origin.city)
            destination_code = self._resolve_location_code(params.destination.city)
            
            if not origin_code or not destination_code:
                return SearchResult(
                    provider_name=self.name,
                    status=SearchStatus.FAILED,
                    error_message="Could not resolve airport codes for given cities"
                )
            
            # Prepare search request
            search_params = self._build_flight_search_params(
                params, origin_code, destination_code
            )
            
            # Make API request
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            logger.debug(f"Searching Amadeus flights: {origin_code} -> {destination_code}")
            
            response = self._session.get(
                self.FLIGHT_OFFERS_URL,
                params=search_params,
                headers=headers,
                timeout=self.config.timeout_seconds
            )
            
            if response.status_code != 200:
                error_msg = self._parse_error_response(response)
                raise AmadeusError(error_msg, status_code=response.status_code)
            
            # Parse and standardize results
            flight_data = response.json()
            routes = self._parse_flight_offers(flight_data, params)
            
            return SearchResult(
                provider_name=self.name,
                status=SearchStatus.COMPLETED,
                routes=routes,
                metadata={
                    "api_version": "v2",
                    "origin_code": origin_code,
                    "destination_code": destination_code,
                    "offers_count": len(flight_data.get("data", []))
                }
            )
            
        except AmadeusError:
            # Re-raise Amadeus-specific errors
            raise
        except Exception as e:
            logger.error(f"Amadeus search failed: {e}")
            return SearchResult(
                provider_name=self.name,
                status=SearchStatus.FAILED,
                error_message=f"Unexpected error: {str(e)}"
            )
    
    def _resolve_location_code(self, city_name: str) -> Optional[str]:
        """Resolve city name to IATA airport code."""
        # Common airport codes cache
        airport_codes = {
            "stuttgart": "STR",
            "vienna": "VIE", 
            "berlin": "BER",
            "munich": "MUC",
            "frankfurt": "FRA",
            "hamburg": "HAM",
            "cologne": "CGN",
            "dusseldorf": "DUS",
            "paris": "CDG",
            "london": "LHR",
            "amsterdam": "AMS",
            "zurich": "ZUR",
            "milan": "MXP",
            "rome": "FCO",
            "madrid": "MAD",
            "barcelona": "BCN"
        }
        
        city_lower = city_name.lower().strip()
        
        # Check cache first
        if city_lower in airport_codes:
            return airport_codes[city_lower]
        
        # If not in cache, try API lookup (implement if needed)
        # For now, return None for unknown cities
        logger.warning(f"Airport code not found for city: {city_name}")
        return None
    
    def _build_flight_search_params(self, params: SearchParams, origin: str, destination: str) -> Dict[str, Any]:
        """Build flight search parameters for Amadeus API."""
        search_params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": params.departure_date,
            "adults": params.passengers,
            "max": min(self.max_flight_offers, 250),  # Amadeus limit
            "currencyCode": "EUR"
        }
        
        # Add return date for round trips
        if params.return_date:
            search_params["returnDate"] = params.return_date
        
        # Add cabin class
        if hasattr(params, 'cabin_class') and params.cabin_class:
            amadeus_class = self.cabin_class_mapping.get(params.cabin_class.lower())
            if amadeus_class:
                search_params["travelClass"] = amadeus_class
        
        # Add connection preferences
        if params.max_connections == 0:
            search_params["nonStop"] = "true"
        
        return search_params
    
    def _parse_flight_offers(self, api_response: Dict[str, Any], params: SearchParams) -> List[Dict[str, Any]]:
        """Parse Amadeus flight offers into standardized format."""
        routes = []
        
        offers = api_response.get("data", [])
        dictionaries = api_response.get("dictionaries", {})
        
        for offer in offers:
            try:
                route = self._parse_single_offer(offer, dictionaries, params)
                if route:
                    routes.append(route)
            except Exception as e:
                logger.warning(f"Failed to parse flight offer: {e}")
                continue
        
        return routes
    
    def _parse_single_offer(self, offer: Dict[str, Any], dictionaries: Dict[str, Any], params: SearchParams) -> Optional[Dict[str, Any]]:
        """Parse a single flight offer into standardized route format."""
        try:
            # Extract price information
            price_info = offer.get("price", {})
            total_price = float(price_info.get("total", 0))
            
            # Extract itinerary information
            itineraries = offer.get("itineraries", [])
            if not itineraries:
                return None
            
            # For now, use the first (outbound) itinerary
            outbound = itineraries[0]
            segments = outbound.get("segments", [])
            
            if not segments:
                return None
            
            # Calculate total duration
            duration_str = outbound.get("duration", "PT0H0M")
            total_hours = self._parse_duration(duration_str)
            
            # Count connections (segments - 1)
            connections = max(0, len(segments) - 1)
            
            # Extract carrier information
            first_segment = segments[0]
            carrier_code = first_segment.get("carrierCode", "")
            carrier_name = dictionaries.get("carriers", {}).get(carrier_code, carrier_code)
            
            # Extract route information
            origin_code = first_segment.get("departure", {}).get("iataCode", "")
            destination_code = segments[-1].get("arrival", {}).get("iataCode", "")
            
            # Build via cities list for connections
            via_cities = []
            if connections > 0:
                for segment in segments[:-1]:  # All but last segment
                    arrival_code = segment.get("arrival", {}).get("iataCode", "")
                    if arrival_code:
                        # Convert airport code back to city name (simplified)
                        city_name = self._airport_code_to_city(arrival_code)
                        if city_name:
                            via_cities.append(city_name)
            
            # Standard baggage allowance for flights
            baggage = {
                "checked_bags": 1,  # Standard for most airlines
                "per_bag_kg": 23,   # Standard weight limit
                "carry_on": True
            }
            
            # Try to extract actual baggage info from offer
            traveler_pricings = offer.get("travelerPricings", [])
            if traveler_pricings:
                fare_options = traveler_pricings[0].get("fareDetailsBySegment", [])
                if fare_options:
                    baggage_info = fare_options[0].get("includedCheckedBags")
                    if baggage_info:
                        baggage["checked_bags"] = baggage_info.get("quantity", 1)
                        if baggage_info.get("weight"):
                            baggage["per_bag_kg"] = baggage_info["weight"]
            
            # Build standardized route
            route = {
                "provider": self.name,
                "mode": "flight",
                "airline": carrier_name,
                "origin": params.origin.city,
                "destination": params.destination.city,
                "date": params.departure_date,
                "price_eur": round(total_price, 2),
                "total_hours": round(total_hours, 2),
                "connections": connections,
                "baggage": baggage,
                "departure_time": first_segment.get("departure", {}).get("at", ""),
                "arrival_time": segments[-1].get("arrival", {}).get("at", ""),
                "aircraft_type": first_segment.get("aircraft", {}).get("code", ""),
                "booking_class": segments[0].get("cabin", "ECONOMY"),
                "amadeus_offer_id": offer.get("id", "")
            }
            
            # Add via cities if present
            if via_cities:
                route["via"] = via_cities
            
            return route
            
        except (KeyError, ValueError, TypeError) as e:
            logger.warning(f"Error parsing flight offer: {e}")
            return None
    
    def _parse_duration(self, duration_str: str) -> float:
        """Parse ISO 8601 duration string to hours."""
        try:
            # Example: "PT2H30M" -> 2.5 hours
            import re
            
            # Remove PT prefix
            duration_str = duration_str.replace("PT", "")
            
            hours = 0
            minutes = 0
            
            # Extract hours
            hour_match = re.search(r'(\d+)H', duration_str)
            if hour_match:
                hours = int(hour_match.group(1))
            
            # Extract minutes
            minute_match = re.search(r'(\d+)M', duration_str)
            if minute_match:
                minutes = int(minute_match.group(1))
            
            return hours + (minutes / 60.0)
            
        except Exception:
            return 0.0
    
    def _airport_code_to_city(self, airport_code: str) -> Optional[str]:
        """Convert airport code back to city name (simplified mapping)."""
        code_to_city = {
            "STR": "Stuttgart",
            "VIE": "Vienna", 
            "BER": "Berlin",
            "MUC": "Munich",
            "FRA": "Frankfurt",
            "HAM": "Hamburg",
            "CGN": "Cologne",
            "DUS": "Düsseldorf",
            "CDG": "Paris",
            "LHR": "London",
            "AMS": "Amsterdam",
            "ZUR": "Zurich",
            "MXP": "Milan",
            "FCO": "Rome",
            "MAD": "Madrid",
            "BCN": "Barcelona"
        }
        
        return code_to_city.get(airport_code.upper())
    
    def _parse_error_response(self, response: requests.Response) -> str:
        """Parse Amadeus API error response."""
        try:
            error_data = response.json()
            errors = error_data.get("errors", [])
            
            if errors:
                error = errors[0]
                code = error.get("code", "UNKNOWN")
                title = error.get("title", "API Error")
                detail = error.get("detail", response.text)
                return f"[{code}] {title}: {detail}"
            
        except (ValueError, KeyError):
            pass
        
        return f"HTTP {response.status_code}: {response.text}"
    
    def search(self, origin: str, destination: str, date: str) -> List[Dict[str, Any]]:
        """Legacy interface for backward compatibility."""
        try:
            params = SearchParams(
                origin=origin,
                destination=destination,
                departure_date=date
            )
            
            result = self.search_routes(params)
            return result.routes if result.is_successful else []
            
        except Exception as e:
            logger.error(f"Amadeus legacy search failed: {e}")
            return []
    
    def __del__(self):
        """Cleanup resources."""
        if hasattr(self, '_session'):
            self._session.close()
