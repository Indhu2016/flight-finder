"""
Smart Travel Route Agent with Agentic Design Patterns.

This module implements an autonomous AI agent that optimizes travel routes using:
- Reflection Pattern: Self-evaluation and iterative improvement
- Tool Use Pattern: Multiple provider integration with error handling
- Planning Pattern: Strategic multi-criteria decision making
- Autonomous execution with graceful degradation
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
from enum import Enum

from src.tools.providers.mock_provider import MockProvider
from src.tools.providers.amadeus_provider import AmadeusProvider
from src.tools.providers.omio_provider import OmioProvider
from src.tools.filters import filter_by_connections, filter_by_baggage
from src.tools.scoring import score_routes
from src.tools.security import sanitize_city_name, validate_date, validate_numeric_input
from src.config import USE_AMADEUS, USE_OMIO

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(Enum):
    """Agent execution states for monitoring and debugging."""
    INITIALIZING = "initializing"
    COLLECTING_DATA = "collecting_data"
    FILTERING = "filtering"
    SCORING = "scoring"
    REFLECTING = "reflecting"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class RouteRequest:
    """Structured request for route planning with validation."""
    origin: str
    destination: str
    date: str
    min_checked_bags: int = 2
    max_connections: int = 2
    w_time: float = 0.6
    w_cost: float = 0.4
    
    def __post_init__(self):
        """Validate request parameters."""
        self.origin = sanitize_city_name(self.origin)
        self.destination = sanitize_city_name(self.destination)
        
        if not validate_date(self.date):
            raise ValueError(f"Invalid date format: {self.date}")
        
        if not validate_numeric_input(self.min_checked_bags, 0, 10):
            raise ValueError(f"Invalid checked bags: {self.min_checked_bags}")
        
        if not validate_numeric_input(self.max_connections, 0, 5):
            raise ValueError(f"Invalid max connections: {self.max_connections}")
        
        if not validate_numeric_input(self.w_time, 0, 1):
            raise ValueError(f"Invalid time weight: {self.w_time}")
        
        if not validate_numeric_input(self.w_cost, 0, 1):
            raise ValueError(f"Invalid cost weight: {self.w_cost}")
        
        # Ensure weights sum to 1.0
        if abs(self.w_time + self.w_cost - 1.0) > 0.01:
            self.w_cost = 1.0 - self.w_time
            logger.warning(f"Adjusted cost weight to {self.w_cost:.2f}")


@dataclass
class AgentReflection:
    """Agent's self-reflection on execution quality."""
    execution_time: float
    providers_used: int
    providers_failed: int
    routes_found: int
    routes_after_filtering: int
    quality_score: float
    suggestions: List[str]


class SmartTravelAgent:
    """
    Autonomous travel route optimization agent implementing agentic design patterns.
    
    Features:
    - Autonomous provider selection and error handling
    - Self-reflection and quality assessment
    - Strategic planning with fallback mechanisms
    - Comprehensive logging and monitoring
    """
    
    def __init__(self):
        self.state = AgentState.INITIALIZING
        self.providers = self._initialize_providers()
        self.execution_history = []
        
    def _initialize_providers(self) -> List[Any]:
        """Initialize available providers based on configuration."""
        providers = [MockProvider()]
        
        if USE_AMADEUS:
            try:
                providers.append(AmadeusProvider())
                logger.info("Amadeus provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Amadeus: {e}")
        
        if USE_OMIO:
            try:
                providers.append(OmioProvider())
                logger.info("Omio provider initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Omio: {e}")
        
        logger.info(f"Initialized {len(providers)} providers")
        return providers
    
    def collect_routes(self, request: RouteRequest) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Collect routes from all available providers with error handling.
        
        Returns:
            Tuple of (routes, execution_stats)
        """
        self.state = AgentState.COLLECTING_DATA
        routes: List[Dict[str, Any]] = []
        execution_stats = {
            "providers_tried": 0,
            "providers_failed": 0,
            "routes_collected": 0
        }
        
        for provider in self.providers:
            execution_stats["providers_tried"] += 1
            
            try:
                provider_routes = provider.search(
                    request.origin, 
                    request.destination, 
                    request.date
                )
                routes.extend(provider_routes)
                execution_stats["routes_collected"] += len(provider_routes)
                
                logger.info(
                    f"Provider {provider.__class__.__name__} returned "
                    f"{len(provider_routes)} routes"
                )
                
            except Exception as e:
                execution_stats["providers_failed"] += 1
                logger.warning(
                    f"Provider {provider.__class__.__name__} failed: {e}"
                )
        
        logger.info(f"Total routes collected: {len(routes)}")
        return routes, execution_stats
    
    def apply_filters(self, routes: List[Dict[str, Any]], request: RouteRequest) -> List[Dict[str, Any]]:
        """Apply intelligent filtering with logging."""
        self.state = AgentState.FILTERING
        
        initial_count = len(routes)
        
        # Apply connection filter
        routes = filter_by_connections(routes, request.max_connections)
        after_connections = len(routes)
        
        # Apply baggage filter
        routes = filter_by_baggage(routes, request.min_checked_bags)
        after_baggage = len(routes)
        
        logger.info(
            f"Filtering: {initial_count} → {after_connections} "
            f"(connections) → {after_baggage} (baggage)"
        )
        
        return routes
    
    def score_and_rank(self, routes: List[Dict[str, Any]], request: RouteRequest) -> List[Dict[str, Any]]:
        """Score and rank routes using multi-criteria optimization."""
        self.state = AgentState.SCORING
        
        if not routes:
            logger.warning("No routes to score")
            return []
        
        scored_routes = score_routes(routes, w_time=request.w_time, w_cost=request.w_cost)
        
        logger.info(
            f"Scored {len(scored_routes)} routes. "
            f"Best score: {scored_routes[0]['_score']:.4f}"
        )
        
        return scored_routes
    
    def reflect_on_execution(self, 
                           execution_stats: Dict[str, Any], 
                           final_routes: List[Dict[str, Any]], 
                           execution_time: float) -> AgentReflection:
        """
        Implement reflection pattern: analyze execution quality and suggest improvements.
        """
        self.state = AgentState.REFLECTING
        
        suggestions = []
        
        # Analyze provider performance
        success_rate = 1.0 - (execution_stats["providers_failed"] / max(execution_stats["providers_tried"], 1))
        if success_rate < 0.5:
            suggestions.append("Consider reviewing provider configurations - high failure rate detected")
        
        # Analyze result quality
        if not final_routes:
            suggestions.append("No routes found - consider relaxing filter criteria")
        elif len(final_routes) < 3:
            suggestions.append("Few routes found - consider expanding search parameters")
        
        # Analyze performance
        if execution_time > 10.0:
            suggestions.append("Slow execution detected - consider optimizing provider calls")
        
        # Calculate quality score
        quality_factors = [
            success_rate,
            min(len(final_routes) / 5.0, 1.0),  # Prefer 5+ options
            max(0, 1.0 - execution_time / 30.0)  # Prefer <30s execution
        ]
        quality_score = sum(quality_factors) / len(quality_factors)
        
        reflection = AgentReflection(
            execution_time=execution_time,
            providers_used=execution_stats["providers_tried"],
            providers_failed=execution_stats["providers_failed"],
            routes_found=execution_stats["routes_collected"],
            routes_after_filtering=len(final_routes),
            quality_score=quality_score,
            suggestions=suggestions
        )
        
        logger.info(f"Execution quality score: {quality_score:.2f}")
        for suggestion in suggestions:
            logger.info(f"Suggestion: {suggestion}")
        
        return reflection
    
    def plan_and_execute(self, request: RouteRequest) -> Tuple[List[Dict[str, Any]], AgentReflection]:
        """
        Main execution method implementing the planning pattern.
        
        Returns:
            Tuple of (optimized_routes, execution_reflection)
        """
        import time
        start_time = time.time()
        
        try:
            self.state = AgentState.INITIALIZING
            logger.info(f"Planning route: {request.origin} → {request.destination} on {request.date}")
            
            # Step 1: Collect routes from all providers
            routes, execution_stats = self.collect_routes(request)
            
            # Step 2: Apply intelligent filtering
            filtered_routes = self.apply_filters(routes, request)
            
            # Step 3: Score and rank routes
            final_routes = self.score_and_rank(filtered_routes, request)
            
            # Step 4: Reflect on execution quality
            execution_time = time.time() - start_time
            reflection = self.reflect_on_execution(execution_stats, final_routes, execution_time)
            
            self.state = AgentState.COMPLETED
            logger.info(f"Agent completed successfully in {execution_time:.2f}s")
            
            return final_routes, reflection
            
        except Exception as e:
            self.state = AgentState.FAILED
            logger.error(f"Agent execution failed: {e}")
            raise


# Global agent instance for backward compatibility
_agent = SmartTravelAgent()


def collect_routes(origin: str, destination: str, date: str) -> List[Dict[str, Any]]:
    """
    Legacy function for backward compatibility.
    Collects routes from all available providers.
    """
    request = RouteRequest(origin=origin, destination=destination, date=date)
    routes, _ = _agent.collect_routes(request)
    return routes


def plan_best_routes(
    origin: str,
    destination: str,
    date: str,
    min_checked_bags: int = 2,
    max_connections: int = 2,
    w_time: float = 0.6,
    w_cost: float = 0.4,
) -> List[Dict[str, Any]]:
    """
    Legacy function for backward compatibility.
    Plans and optimizes travel routes using the smart agent.
    """
    try:
        request = RouteRequest(
            origin=origin,
            destination=destination,
            date=date,
            min_checked_bags=min_checked_bags,
            max_connections=max_connections,
            w_time=w_time,
            w_cost=w_cost
        )
        
        routes, reflection = _agent.plan_and_execute(request)
        return routes
        
    except ValueError as e:
        logger.error(f"Invalid request parameters: {e}")
        raise
    except Exception as e:
        logger.error(f"Route planning failed: {e}")
        return []
