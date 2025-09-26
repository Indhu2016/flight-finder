"""
Intelligent route filtering system with advanced criteria and analytics.

This module implements sophisticated filtering logic following SOLID principles
and functional programming patterns for maintainability and extensibility.
"""

import logging
from typing import List, Dict, Any, Callable, Optional, Set
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class FilterCriterion(Enum):
    """Available filter criteria."""
    CONNECTIONS = "connections"
    BAGGAGE = "baggage"
    DURATION = "duration"
    PRICE = "price"
    DEPARTURE_TIME = "departure_time"
    ARRIVAL_TIME = "arrival_time"
    CARRIER = "carrier"
    MODE = "mode"


@dataclass
class FilterResult:
    """Result of a filtering operation with analytics."""
    routes: List[Dict[str, Any]]
    initial_count: int
    filtered_count: int
    filter_name: str
    criteria_met: int
    criteria_failed: int
    
    @property
    def filter_rate(self) -> float:
        """Percentage of routes that passed the filter."""
        return (self.filtered_count / self.initial_count) if self.initial_count > 0 else 0.0
    
    @property
    def removed_count(self) -> int:
        """Number of routes removed by the filter."""
        return self.initial_count - self.filtered_count


class BaseRouteFilter(ABC):
    """Abstract base class for route filters implementing Strategy pattern."""
    
    def __init__(self, name: str):
        self.name = name
        self.application_count = 0
        
    @abstractmethod
    def apply(self, routes: List[Dict[str, Any]]) -> FilterResult:
        """Apply the filter to a list of routes."""
        pass
    
    @abstractmethod
    def validate_parameters(self) -> bool:
        """Validate filter parameters."""
        pass
    
    def __call__(self, routes: List[Dict[str, Any]]) -> FilterResult:
        """Make the filter callable."""
        self.application_count += 1
        return self.apply(routes)


class ConnectionFilter(BaseRouteFilter):
    """Filter routes by maximum number of connections."""
    
    def __init__(self, max_connections: int):
        super().__init__(f"connections_≤{max_connections}")
        self.max_connections = max_connections
        
    def validate_parameters(self) -> bool:
        """Validate filter parameters."""
        if not isinstance(self.max_connections, int):
            logger.error("max_connections must be an integer")
            return False
        if self.max_connections < 0:
            logger.error("max_connections cannot be negative")
            return False
        if self.max_connections > 10:
            logger.warning(f"Unusually high max_connections: {self.max_connections}")
        return True
    
    def apply(self, routes: List[Dict[str, Any]]) -> FilterResult:
        """Apply connection filter."""
        if not self.validate_parameters():
            raise ValueError("Invalid filter parameters")
        
        initial_count = len(routes)
        criteria_met = 0
        criteria_failed = 0
        
        filtered_routes = []
        for route in routes:
            connections = route.get("connections", 0)
            
            if connections <= self.max_connections:
                filtered_routes.append(route)
                criteria_met += 1
            else:
                criteria_failed += 1
        
        result = FilterResult(
            routes=filtered_routes,
            initial_count=initial_count,
            filtered_count=len(filtered_routes),
            filter_name=self.name,
            criteria_met=criteria_met,
            criteria_failed=criteria_failed
        )
        
        logger.info(
            f"Connection filter: {initial_count} → {len(filtered_routes)} routes "
            f"(≤{self.max_connections} connections)"
        )
        
        return result


class BaggageFilter(BaseRouteFilter):
    """Filter routes by minimum baggage allowance."""
    
    def __init__(self, min_checked_bags: int, min_weight_kg: Optional[int] = None):
        super().__init__(f"baggage_≥{min_checked_bags}bags")
        self.min_checked_bags = min_checked_bags
        self.min_weight_kg = min_weight_kg
        
    def validate_parameters(self) -> bool:
        """Validate filter parameters."""
        if not isinstance(self.min_checked_bags, int):
            logger.error("min_checked_bags must be an integer")
            return False
        if self.min_checked_bags < 0:
            logger.error("min_checked_bags cannot be negative")
            return False
        if self.min_checked_bags > 10:
            logger.warning(f"Unusually high min_checked_bags: {self.min_checked_bags}")
        
        if self.min_weight_kg is not None:
            if not isinstance(self.min_weight_kg, int) or self.min_weight_kg <= 0:
                logger.error("min_weight_kg must be a positive integer")
                return False
                
        return True
    
    def apply(self, routes: List[Dict[str, Any]]) -> FilterResult:
        """Apply baggage filter."""
        if not self.validate_parameters():
            raise ValueError("Invalid filter parameters")
        
        initial_count = len(routes)
        criteria_met = 0
        criteria_failed = 0
        
        filtered_routes = []
        for route in routes:
            baggage = route.get("baggage", {})
            checked_bags = baggage.get("checked_bags", 0)
            weight_kg = baggage.get("per_bag_kg", 0)
            
            # Check bag count requirement
            meets_bag_count = checked_bags >= self.min_checked_bags
            
            # Check weight requirement if specified
            meets_weight = (self.min_weight_kg is None or 
                          weight_kg >= self.min_weight_kg)
            
            if meets_bag_count and meets_weight:
                filtered_routes.append(route)
                criteria_met += 1
            else:
                criteria_failed += 1
        
        result = FilterResult(
            routes=filtered_routes,
            initial_count=initial_count,
            filtered_count=len(filtered_routes),
            filter_name=self.name,
            criteria_met=criteria_met,
            criteria_failed=criteria_failed
        )
        
        weight_info = f", ≥{self.min_weight_kg}kg" if self.min_weight_kg else ""
        logger.info(
            f"Baggage filter: {initial_count} → {len(filtered_routes)} routes "
            f"(≥{self.min_checked_bags} bags{weight_info})"
        )
        
        return result


class PriceRangeFilter(BaseRouteFilter):
    """Filter routes by price range."""
    
    def __init__(self, min_price: Optional[float] = None, max_price: Optional[float] = None):
        price_range = []
        if min_price is not None:
            price_range.append(f"≥€{min_price}")
        if max_price is not None:
            price_range.append(f"≤€{max_price}")
        
        super().__init__(f"price_{'-'.join(price_range) if price_range else 'any'}")
        self.min_price = min_price
        self.max_price = max_price
        
    def validate_parameters(self) -> bool:
        """Validate filter parameters."""
        if self.min_price is not None and (not isinstance(self.min_price, (int, float)) or self.min_price < 0):
            logger.error("min_price must be a non-negative number")
            return False
            
        if self.max_price is not None and (not isinstance(self.max_price, (int, float)) or self.max_price <= 0):
            logger.error("max_price must be a positive number")
            return False
            
        if (self.min_price is not None and self.max_price is not None and 
            self.min_price >= self.max_price):
            logger.error("min_price must be less than max_price")
            return False
            
        return True
    
    def apply(self, routes: List[Dict[str, Any]]) -> FilterResult:
        """Apply price range filter."""
        if not self.validate_parameters():
            raise ValueError("Invalid filter parameters")
        
        initial_count = len(routes)
        criteria_met = 0
        criteria_failed = 0
        
        filtered_routes = []
        for route in routes:
            price = route.get("price_eur", 0)
            
            meets_min = self.min_price is None or price >= self.min_price
            meets_max = self.max_price is None or price <= self.max_price
            
            if meets_min and meets_max:
                filtered_routes.append(route)
                criteria_met += 1
            else:
                criteria_failed += 1
        
        result = FilterResult(
            routes=filtered_routes,
            initial_count=initial_count,
            filtered_count=len(filtered_routes),
            filter_name=self.name,
            criteria_met=criteria_met,
            criteria_failed=criteria_failed
        )
        
        logger.info(f"Price filter: {initial_count} → {len(filtered_routes)} routes")
        return result


class DurationFilter(BaseRouteFilter):
    """Filter routes by travel duration."""
    
    def __init__(self, max_hours: float):
        super().__init__(f"duration_≤{max_hours}h")
        self.max_hours = max_hours
        
    def validate_parameters(self) -> bool:
        """Validate filter parameters."""
        if not isinstance(self.max_hours, (int, float)) or self.max_hours <= 0:
            logger.error("max_hours must be a positive number")
            return False
        if self.max_hours > 48:
            logger.warning(f"Unusually long max_hours: {self.max_hours}")
        return True
    
    def apply(self, routes: List[Dict[str, Any]]) -> FilterResult:
        """Apply duration filter."""
        if not self.validate_parameters():
            raise ValueError("Invalid filter parameters")
        
        initial_count = len(routes)
        criteria_met = 0
        criteria_failed = 0
        
        filtered_routes = []
        for route in routes:
            duration = route.get("total_hours", float('inf'))
            
            if duration <= self.max_hours:
                filtered_routes.append(route)
                criteria_met += 1
            else:
                criteria_failed += 1
        
        result = FilterResult(
            routes=filtered_routes,
            initial_count=initial_count,
            filtered_count=len(filtered_routes),
            filter_name=self.name,
            criteria_met=criteria_met,
            criteria_failed=criteria_failed
        )
        
        logger.info(
            f"Duration filter: {initial_count} → {len(filtered_routes)} routes "
            f"(≤{self.max_hours}h)"
        )
        
        return result


class CarrierFilter(BaseRouteFilter):
    """Filter routes by preferred or excluded carriers."""
    
    def __init__(self, preferred_carriers: Optional[Set[str]] = None, 
                 excluded_carriers: Optional[Set[str]] = None):
        self.preferred_carriers = preferred_carriers or set()
        self.excluded_carriers = excluded_carriers or set()
        
        filter_desc = []
        if self.preferred_carriers:
            filter_desc.append(f"preferred_{len(self.preferred_carriers)}")
        if self.excluded_carriers:
            filter_desc.append(f"excluded_{len(self.excluded_carriers)}")
            
        super().__init__(f"carrier_{'-'.join(filter_desc) if filter_desc else 'any'}")
        
    def validate_parameters(self) -> bool:
        """Validate filter parameters."""
        overlap = self.preferred_carriers & self.excluded_carriers
        if overlap:
            logger.error(f"Carriers cannot be both preferred and excluded: {overlap}")
            return False
        return True
    
    def apply(self, routes: List[Dict[str, Any]]) -> FilterResult:
        """Apply carrier filter."""
        if not self.validate_parameters():
            raise ValueError("Invalid filter parameters")
        
        initial_count = len(routes)
        criteria_met = 0
        criteria_failed = 0
        
        filtered_routes = []
        for route in routes:
            carrier = route.get("airline") or route.get("carrier", "")
            
            # If preferred carriers specified, route must use one of them
            if self.preferred_carriers and carrier not in self.preferred_carriers:
                criteria_failed += 1
                continue
                
            # Route must not use excluded carriers
            if carrier in self.excluded_carriers:
                criteria_failed += 1
                continue
                
            filtered_routes.append(route)
            criteria_met += 1
        
        result = FilterResult(
            routes=filtered_routes,
            initial_count=initial_count,
            filtered_count=len(filtered_routes),
            filter_name=self.name,
            criteria_met=criteria_met,
            criteria_failed=criteria_failed
        )
        
        logger.info(f"Carrier filter: {initial_count} → {len(filtered_routes)} routes")
        return result


class FilterChain:
    """Chain multiple filters together with analytics."""
    
    def __init__(self, filters: List[BaseRouteFilter]):
        self.filters = filters
        self.results: List[FilterResult] = []
        
    def apply_all(self, routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply all filters in sequence."""
        self.results = []
        current_routes = routes
        
        logger.info(f"Starting filter chain with {len(routes)} routes")
        
        for filter_obj in self.filters:
            result = filter_obj.apply(current_routes)
            self.results.append(result)
            current_routes = result.routes
            
            if not current_routes:
                logger.warning(f"No routes remaining after {filter_obj.name}")
                break
        
        logger.info(f"Filter chain complete: {len(routes)} → {len(current_routes)} routes")
        return current_routes
    
    def get_analytics(self) -> Dict[str, Any]:
        """Get detailed analytics of the filtering process."""
        if not self.results:
            return {}
        
        return {
            "total_filters": len(self.filters),
            "initial_routes": self.results[0].initial_count if self.results else 0,
            "final_routes": self.results[-1].filtered_count if self.results else 0,
            "filter_steps": [
                {
                    "filter": result.filter_name,
                    "input_count": result.initial_count,
                    "output_count": result.filtered_count,
                    "removed": result.removed_count,
                    "filter_rate": round(result.filter_rate, 3)
                }
                for result in self.results
            ],
            "overall_filter_rate": (
                self.results[-1].filtered_count / self.results[0].initial_count
                if self.results and self.results[0].initial_count > 0
                else 0.0
            )
        }


# Legacy compatibility functions
def filter_by_connections(routes: List[Dict[str, Any]], max_connections: int) -> List[Dict[str, Any]]:
    """Legacy function for backward compatibility."""
    filter_obj = ConnectionFilter(max_connections)
    result = filter_obj.apply(routes)
    return result.routes


def filter_by_baggage(routes: List[Dict[str, Any]], min_checked_bags: int) -> List[Dict[str, Any]]:
    """Legacy function for backward compatibility."""
    filter_obj = BaggageFilter(min_checked_bags)
    result = filter_obj.apply(routes)
    return result.routes


# Convenience functions for common filtering scenarios
def create_basic_filter_chain(max_connections: int, min_checked_bags: int) -> FilterChain:
    """Create a basic filter chain with connection and baggage filters."""
    return FilterChain([
        ConnectionFilter(max_connections),
        BaggageFilter(min_checked_bags)
    ])


def create_advanced_filter_chain(max_connections: int, min_checked_bags: int, 
                                max_price: Optional[float] = None,
                                max_duration: Optional[float] = None) -> FilterChain:
    """Create an advanced filter chain with additional criteria."""
    filters = [
        ConnectionFilter(max_connections),
        BaggageFilter(min_checked_bags)
    ]
    
    if max_price is not None:
        filters.append(PriceRangeFilter(max_price=max_price))
    
    if max_duration is not None:
        filters.append(DurationFilter(max_duration))
    
    return FilterChain(filters)
