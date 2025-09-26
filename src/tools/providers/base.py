"""
Base provider system with advanced features and SOLID principles.

This module defines the foundation for all travel provider integrations,
implementing the Strategy pattern and providing comprehensive search capabilities.
"""

import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Callable, Protocol
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
import json

logger = logging.getLogger(__name__)


class TransportMode(Enum):
    """Available transport modes."""
    FLIGHT = "flight"
    TRAIN = "train"
    BUS = "bus"
    CAR = "car"
    FERRY = "ferry"
    ALL = "all"


class SearchStatus(Enum):
    """Search operation status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"


class CacheStrategy(Enum):
    """Cache strategy options."""
    NO_CACHE = "no_cache"
    MEMORY_ONLY = "memory_only"
    PERSISTENT = "persistent"
    DISTRIBUTED = "distributed"


@dataclass
class Location:
    """Enhanced location information."""
    city: str
    country: str = ""
    code: str = ""  # Airport/station code
    coordinates: Optional[Dict[str, float]] = None
    timezone: Optional[str] = None
    
    def __post_init__(self):
        """Validate location data."""
        if not self.city:
            raise ValueError("City name is required")
        
        # Clean city name
        self.city = self.city.strip().title()
        
        if self.coordinates:
            lat = self.coordinates.get("lat", 0)
            lng = self.coordinates.get("lng", 0)
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                raise ValueError("Invalid coordinates")
    
    @property
    def display_name(self) -> str:
        """Get human-readable location name."""
        if self.code and self.country:
            return f"{self.city} ({self.code}), {self.country}"
        elif self.country:
            return f"{self.city}, {self.country}"
        return self.city


@dataclass
class SearchParams:
    """Comprehensive search parameters."""
    origin: Union[str, Location]
    destination: Union[str, Location]
    departure_date: str
    return_date: Optional[str] = None
    passengers: int = 1
    max_connections: int = 3
    transport_modes: List[TransportMode] = field(default_factory=lambda: [TransportMode.ALL])
    max_price: Optional[float] = None
    max_duration_hours: Optional[float] = None
    preferred_carriers: List[str] = field(default_factory=list)
    excluded_carriers: List[str] = field(default_factory=list)
    cabin_class: str = "economy"
    baggage_requirements: Dict[str, Any] = field(default_factory=dict)
    flexible_dates: bool = False
    date_range_days: int = 3
    
    def __post_init__(self):
        """Validate and normalize search parameters."""
        # Convert string locations to Location objects
        if isinstance(self.origin, str):
            self.origin = Location(city=self.origin)
        if isinstance(self.destination, str):
            self.destination = Location(city=self.destination)
        
        # Validate passenger count
        if not (1 <= self.passengers <= 9):
            raise ValueError("Passengers must be between 1 and 9")
        
        # Validate connections
        if not (0 <= self.max_connections <= 5):
            raise ValueError("Max connections must be between 0 and 5")
        
        # Validate dates
        try:
            departure = datetime.fromisoformat(self.departure_date.replace('Z', '+00:00'))
            if departure < datetime.now():
                logger.warning("Departure date is in the past")
            
            if self.return_date:
                return_dt = datetime.fromisoformat(self.return_date.replace('Z', '+00:00'))
                if return_dt <= departure:
                    raise ValueError("Return date must be after departure date")
        except ValueError as e:
            raise ValueError(f"Invalid date format: {e}")
    
    @property
    def is_round_trip(self) -> bool:
        """Check if this is a round trip search."""
        return self.return_date is not None
    
    @property
    def search_key(self) -> str:
        """Generate unique key for caching."""
        key_parts = [
            self.origin.city,
            self.destination.city,
            self.departure_date,
            str(self.passengers),
            str(self.max_connections),
            "-".join([mode.value for mode in self.transport_modes])
        ]
        return "|".join(key_parts)


@dataclass
class SearchResult:
    """Search operation result."""
    provider_name: str
    status: SearchStatus
    routes: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    search_time_ms: int = 0
    cache_hit: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def is_successful(self) -> bool:
        """Check if search was successful."""
        return self.status == SearchStatus.COMPLETED and not self.error_message
    
    @property
    def route_count(self) -> int:
        """Get number of routes found."""
        return len(self.routes)


@dataclass
class ProviderConfig:
    """Provider configuration."""
    name: str
    enabled: bool = True
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    base_url: Optional[str] = None
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: float = 1.0
    rate_limit_per_minute: int = 60
    cache_strategy: CacheStrategy = CacheStrategy.MEMORY_ONLY
    cache_ttl_minutes: int = 30
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate configuration."""
        if not self.name:
            raise ValueError("Provider name is required")
        
        if self.timeout_seconds <= 0:
            raise ValueError("Timeout must be positive")
        
        if self.max_retries < 0:
            raise ValueError("Max retries cannot be negative")


class Provider(Protocol):
    """Protocol defining the provider interface."""
    def search(self, origin: str, destination: str, date: str) -> List[Dict[str, Any]]:
        """Search for travel routes."""
        ...


class BaseProvider(ABC):
    """Enhanced base class for all travel providers."""
    
    def __init__(self, config: ProviderConfig):
        self.config = config
        self.name = config.name
        self.enabled = config.enabled
        
        # Statistics tracking
        self.search_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_search_time_ms = 0
        self.cache_hits = 0
        
        # Rate limiting
        self.last_request_time = 0
        self.request_count_per_minute = 0
        self.minute_window_start = time.time()
        
        # Internal cache
        self._cache: Dict[str, Any] = {}
        self._cache_timestamps: Dict[str, float] = {}
        
        logger.info(f"Initialized provider: {self.name}")
    
    @abstractmethod
    def search_routes(self, params: SearchParams) -> SearchResult:
        """Search for travel routes."""
        pass
    
    @abstractmethod
    def validate_config(self) -> bool:
        """Validate provider configuration."""
        pass
    
    def search(self, origin: str, destination: str, date: str) -> List[Dict[str, Any]]:
        """Legacy interface for backward compatibility."""
        params = SearchParams(
            origin=origin,
            destination=destination,
            departure_date=date
        )
        result = self.search_routes_with_retry(params)
        return result.routes if result.is_successful else []
    
    def search_routes_with_retry(self, params: SearchParams) -> SearchResult:
        """Search with automatic retry logic."""
        if not self.enabled:
            return SearchResult(
                provider_name=self.name,
                status=SearchStatus.FAILED,
                error_message="Provider is disabled"
            )
        
        if not self.validate_config():
            return SearchResult(
                provider_name=self.name,
                status=SearchStatus.FAILED,
                error_message="Provider configuration is invalid"
            )
        
        # Check rate limiting
        if not self._check_rate_limit():
            return SearchResult(
                provider_name=self.name,
                status=SearchStatus.FAILED,
                error_message="Rate limit exceeded"
            )
        
        # Check cache first
        cache_result = self._check_cache(params)
        if cache_result:
            return cache_result
        
        # Perform search with retries
        last_error = None
        for attempt in range(self.config.max_retries + 1):
            try:
                start_time = time.time()
                result = self.search_routes(params)
                end_time = time.time()
                
                # Update statistics
                search_time_ms = int((end_time - start_time) * 1000)
                result.search_time_ms = search_time_ms
                self._update_statistics(result)
                
                # Cache successful results
                if result.is_successful:
                    self._cache_result(params, result)
                
                return result
                
            except Exception as e:
                last_error = str(e)
                logger.warning(f"Search attempt {attempt + 1} failed for {self.name}: {e}")
                
                if attempt < self.config.max_retries:
                    time.sleep(self.config.retry_delay_seconds * (2 ** attempt))
        
        # All retries failed
        result = SearchResult(
            provider_name=self.name,
            status=SearchStatus.FAILED,
            error_message=f"All retries failed. Last error: {last_error}"
        )
        self._update_statistics(result)
        return result
    
    async def search_routes_async(self, params: SearchParams) -> SearchResult:
        """Asynchronous search wrapper."""
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            future = loop.run_in_executor(executor, self.search_routes_with_retry, params)
            return await future
    
    def _check_rate_limit(self) -> bool:
        """Check if request is within rate limits."""
        current_time = time.time()
        
        # Reset counter if minute window has passed
        if current_time - self.minute_window_start >= 60:
            self.request_count_per_minute = 0
            self.minute_window_start = current_time
        
        # Check if we're within limits
        if self.request_count_per_minute >= self.config.rate_limit_per_minute:
            return False
        
        self.request_count_per_minute += 1
        self.last_request_time = current_time
        return True
    
    def _check_cache(self, params: SearchParams) -> Optional[SearchResult]:
        """Check if result is available in cache."""
        if self.config.cache_strategy == CacheStrategy.NO_CACHE:
            return None
        
        cache_key = params.search_key
        
        # Check if cached result exists and is not expired
        if cache_key in self._cache:
            cached_time = self._cache_timestamps.get(cache_key, 0)
            if time.time() - cached_time < (self.config.cache_ttl_minutes * 60):
                result = self._cache[cache_key]
                result_copy = SearchResult(
                    provider_name=result.provider_name,
                    status=result.status,
                    routes=result.routes.copy(),
                    error_message=result.error_message,
                    search_time_ms=result.search_time_ms,
                    cache_hit=True,
                    metadata=result.metadata.copy()
                )
                self.cache_hits += 1
                logger.debug(f"Cache hit for {self.name}: {cache_key}")
                return result_copy
            else:
                # Remove expired cache entry
                del self._cache[cache_key]
                del self._cache_timestamps[cache_key]
        
        return None
    
    def _cache_result(self, params: SearchParams, result: SearchResult):
        """Cache search result."""
        if self.config.cache_strategy == CacheStrategy.NO_CACHE:
            return
        
        cache_key = params.search_key
        self._cache[cache_key] = result
        self._cache_timestamps[cache_key] = time.time()
        
        # Limit cache size to prevent memory issues
        if len(self._cache) > 1000:
            # Remove oldest entries
            oldest_keys = sorted(
                self._cache_timestamps.items(),
                key=lambda x: x[1]
            )[:100]
            
            for key, _ in oldest_keys:
                del self._cache[key]
                del self._cache_timestamps[key]
    
    def _update_statistics(self, result: SearchResult):
        """Update provider statistics."""
        self.search_count += 1
        self.total_search_time_ms += result.search_time_ms
        
        if result.is_successful:
            self.success_count += 1
        else:
            self.failure_count += 1
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get provider performance statistics."""
        total_searches = self.search_count
        success_rate = (self.success_count / total_searches) if total_searches > 0 else 0.0
        avg_search_time = (self.total_search_time_ms / total_searches) if total_searches > 0 else 0.0
        cache_hit_rate = (self.cache_hits / total_searches) if total_searches > 0 else 0.0
        
        return {
            "provider_name": self.name,
            "enabled": self.enabled,
            "total_searches": total_searches,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": round(success_rate, 3),
            "average_search_time_ms": round(avg_search_time, 2),
            "cache_hits": self.cache_hits,
            "cache_hit_rate": round(cache_hit_rate, 3),
            "configuration_valid": self.validate_config()
        }
    
    def clear_cache(self):
        """Clear provider cache."""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info(f"Cache cleared for provider: {self.name}")
    
    def enable(self):
        """Enable the provider."""
        self.enabled = True
        self.config.enabled = True
        logger.info(f"Provider enabled: {self.name}")
    
    def disable(self):
        """Disable the provider."""
        self.enabled = False
        self.config.enabled = False
        logger.info(f"Provider disabled: {self.name}")
    
    def reset_statistics(self):
        """Reset provider statistics."""
        self.search_count = 0
        self.success_count = 0
        self.failure_count = 0
        self.total_search_time_ms = 0
        self.cache_hits = 0
        logger.info(f"Statistics reset for provider: {self.name}")
    
    def __str__(self) -> str:
        """String representation."""
        status = "enabled" if self.enabled else "disabled"
        return f"{self.name} ({status})"
    
    def __repr__(self) -> str:
        """Developer representation."""
        return f"BaseProvider(name='{self.name}', enabled={self.enabled})"


# Utility functions for provider management
def create_search_params(origin: str, destination: str, date: str, **kwargs) -> SearchParams:
    """Create search parameters with defaults."""
    return SearchParams(
        origin=origin,
        destination=destination,
        departure_date=date,
        **kwargs
    )


def validate_search_params(params: SearchParams) -> List[str]:
    """Validate search parameters and return list of issues."""
    issues = []
    
    try:
        # This will trigger validation in __post_init__
        SearchParams(**params.__dict__)
    except ValueError as e:
        issues.append(str(e))
    
    return issues


# Provider comparison utilities
def compare_provider_performance(providers: List[BaseProvider]) -> Dict[str, Any]:
    """Compare performance across multiple providers."""
    stats = [provider.get_statistics() for provider in providers]
    
    if not stats:
        return {"error": "No providers to compare"}
    
    # Find best performers
    best_success_rate = max(stats, key=lambda s: s["success_rate"])
    fastest_provider = min(
        [s for s in stats if s["average_search_time_ms"] > 0],
        key=lambda s: s["average_search_time_ms"],
        default=None
    )
    
    return {
        "total_providers": len(providers),
        "enabled_providers": len([p for p in providers if p.enabled]),
        "best_success_rate": {
            "provider": best_success_rate["provider_name"],
            "rate": best_success_rate["success_rate"]
        },
        "fastest_provider": {
            "provider": fastest_provider["provider_name"] if fastest_provider else "N/A",
            "avg_time_ms": fastest_provider["average_search_time_ms"] if fastest_provider else 0
        },
        "provider_stats": stats
    }
