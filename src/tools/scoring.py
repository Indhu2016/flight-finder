"""
Intelligent route scoring and ranking system with multiple algorithms.

This module implements sophisticated scoring algorithms following the Strategy pattern,
providing flexible and extensible route evaluation capabilities.
"""

import logging
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import math
import statistics

logger = logging.getLogger(__name__)


class ScoringMethod(Enum):
    """Available scoring methods."""
    PRICE = "price"
    DURATION = "duration"
    CONNECTIONS = "connections"
    COMBINED = "combined"
    VALUE = "value"
    CONVENIENCE = "convenience"
    COMFORT = "comfort"
    SUSTAINABILITY = "sustainability"


class OptimizationGoal(Enum):
    """Optimization goals for scoring."""
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"


@dataclass
class ScoringWeights:
    """Weights for different scoring criteria."""
    price: float = 0.4
    duration: float = 0.3
    connections: float = 0.2
    baggage: float = 0.05
    carrier_preference: float = 0.05
    departure_time: float = 0.0
    
    def __post_init__(self):
        """Normalize weights to sum to 1.0."""
        total = (self.price + self.duration + self.connections + 
                self.baggage + self.carrier_preference + self.departure_time)
        if total > 0:
            self.price /= total
            self.duration /= total
            self.connections /= total
            self.baggage /= total
            self.carrier_preference /= total
            self.departure_time /= total
    
    @property
    def total(self) -> float:
        """Get total weight (should be 1.0 after normalization)."""
        return (self.price + self.duration + self.connections + 
                self.baggage + self.carrier_preference + self.departure_time)


@dataclass
class ScoringConfig:
    """Configuration for route scoring."""
    method: ScoringMethod = ScoringMethod.COMBINED
    weights: ScoringWeights = field(default_factory=ScoringWeights)
    goal: OptimizationGoal = OptimizationGoal.MINIMIZE
    normalization_ranges: Dict[str, Dict[str, float]] = field(default_factory=dict)
    preferred_carriers: List[str] = field(default_factory=list)
    penalty_factors: Dict[str, float] = field(default_factory=dict)
    bonus_factors: Dict[str, float] = field(default_factory=dict)
    
    def __post_init__(self):
        """Set default normalization ranges if not provided."""
        if not self.normalization_ranges:
            self.normalization_ranges = {
                "price_eur": {"min": 50, "max": 2000},
                "total_hours": {"min": 1, "max": 48},
                "connections": {"min": 0, "max": 5},
                "baggage_score": {"min": 0, "max": 10}
            }


@dataclass
class RouteScore:
    """Score result for a route."""
    route_index: int
    overall_score: float
    component_scores: Dict[str, float]
    normalized_scores: Dict[str, float]
    penalties: Dict[str, float] = field(default_factory=dict)
    bonuses: Dict[str, float] = field(default_factory=dict)
    rank: Optional[int] = None
    
    @property
    def adjusted_score(self) -> float:
        """Get score adjusted for penalties and bonuses."""
        penalty_sum = sum(self.penalties.values())
        bonus_sum = sum(self.bonuses.values())
        return self.overall_score + penalty_sum - bonus_sum


class BaseScorer(ABC):
    """Abstract base class for route scorers."""
    
    def __init__(self, config: ScoringConfig):
        self.config = config
        self.scoring_count = 0
    
    @abstractmethod
    def score_route(self, route: Dict[str, Any], index: int = 0) -> RouteScore:
        """Score a single route."""
        pass
    
    def score_routes(self, routes: List[Dict[str, Any]]) -> List[RouteScore]:
        """Score multiple routes."""
        scores = []
        for i, route in enumerate(routes):
            try:
                score = self.score_route(route, i)
                scores.append(score)
            except Exception as e:
                logger.error(f"Error scoring route {i}: {e}")
                # Create a fallback score
                scores.append(RouteScore(
                    route_index=i,
                    overall_score=float('inf'),
                    component_scores={},
                    normalized_scores={}
                ))
        
        # Assign ranks
        sorted_scores = sorted(scores, key=lambda s: s.adjusted_score)
        for rank, score in enumerate(sorted_scores, 1):
            score.rank = rank
        
        self.scoring_count += 1
        return scores
    
    def _normalize_value(self, value: float, field_name: str) -> float:
        """Normalize a value to 0-1 range based on configuration."""
        range_config = self.config.normalization_ranges.get(field_name, {})
        min_val = range_config.get("min", 0)
        max_val = range_config.get("max", 1)
        
        if max_val <= min_val:
            return 0.0
        
        # Clamp value to range
        clamped = max(min_val, min(max_val, value))
        return (clamped - min_val) / (max_val - min_val)
    
    def _calculate_carrier_score(self, route: Dict[str, Any]) -> float:
        """Calculate carrier preference score."""
        if not self.config.preferred_carriers:
            return 0.0
        
        carrier = route.get("airline") or route.get("carrier", "")
        if carrier in self.config.preferred_carriers:
            # Bonus for preferred carrier
            preferred_index = self.config.preferred_carriers.index(carrier)
            # Higher preference = lower index = higher score
            return 1.0 - (preferred_index / len(self.config.preferred_carriers))
        
        return 0.0  # No bonus for non-preferred carriers
    
    def _calculate_baggage_score(self, route: Dict[str, Any]) -> float:
        """Calculate baggage allowance score."""
        baggage = route.get("baggage", {})
        bags = baggage.get("checked_bags", 0)
        weight_per_bag = baggage.get("per_bag_kg", 0)
        
        # Simple scoring: more bags and weight = higher score
        bag_score = min(bags / 3.0, 1.0)  # Normalize to 3 bags max
        weight_score = min(weight_per_bag / 30.0, 1.0)  # Normalize to 30kg max
        
        return (bag_score + weight_score) / 2.0


class PriceScorer(BaseScorer):
    """Scorer focused on price optimization."""
    
    def score_route(self, route: Dict[str, Any], index: int = 0) -> RouteScore:
        """Score route based primarily on price."""
        price = route.get("price_eur", float('inf'))
        
        if price == float('inf'):
            logger.warning(f"Route {index} has no price information")
            price = 9999  # Fallback high price
        
        normalized_price = self._normalize_value(price, "price_eur")
        
        return RouteScore(
            route_index=index,
            overall_score=price,
            component_scores={"price": price},
            normalized_scores={"price": normalized_price}
        )


class DurationScorer(BaseScorer):
    """Scorer focused on travel duration."""
    
    def score_route(self, route: Dict[str, Any], index: int = 0) -> RouteScore:
        """Score route based primarily on duration."""
        duration = route.get("total_hours", float('inf'))
        
        if duration == float('inf'):
            logger.warning(f"Route {index} has no duration information")
            duration = 48  # Fallback high duration
        
        normalized_duration = self._normalize_value(duration, "total_hours")
        
        return RouteScore(
            route_index=index,
            overall_score=duration,
            component_scores={"duration": duration},
            normalized_scores={"duration": normalized_duration}
        )


class ConnectionScorer(BaseScorer):
    """Scorer focused on minimizing connections."""
    
    def score_route(self, route: Dict[str, Any], index: int = 0) -> RouteScore:
        """Score route based primarily on connections."""
        connections = route.get("connections", 0)
        normalized_connections = self._normalize_value(connections, "connections")
        
        return RouteScore(
            route_index=index,
            overall_score=connections,
            component_scores={"connections": connections},
            normalized_scores={"connections": normalized_connections}
        )


class CombinedScorer(BaseScorer):
    """Scorer using weighted combination of multiple factors."""
    
    def score_route(self, route: Dict[str, Any], index: int = 0) -> RouteScore:
        """Score route using weighted combination."""
        # Extract raw values
        price = route.get("price_eur", 9999)
        duration = route.get("total_hours", 48)
        connections = route.get("connections", 5)
        
        # Normalize values
        norm_price = self._normalize_value(price, "price_eur")
        norm_duration = self._normalize_value(duration, "total_hours")
        norm_connections = self._normalize_value(connections, "connections")
        norm_baggage = self._calculate_baggage_score(route)
        norm_carrier = self._calculate_carrier_score(route)
        
        # Calculate component scores
        component_scores = {
            "price": price,
            "duration": duration,
            "connections": connections,
            "baggage": norm_baggage * 10,  # Scale for display
            "carrier": norm_carrier * 10   # Scale for display
        }
        
        normalized_scores = {
            "price": norm_price,
            "duration": norm_duration,
            "connections": norm_connections,
            "baggage": norm_baggage,
            "carrier": norm_carrier
        }
        
        # Calculate weighted score
        weights = self.config.weights
        combined_score = (
            weights.price * norm_price +
            weights.duration * norm_duration +
            weights.connections * norm_connections +
            weights.baggage * norm_baggage +
            weights.carrier_preference * norm_carrier
        )
        
        # Apply penalties and bonuses
        penalties = {}
        bonuses = {}
        
        # Example: penalty for red-eye flights
        if hasattr(route.get("departure", {}), "get"):
            dep_time = route["departure"].get("datetime", "")
            if "T02:" in dep_time or "T03:" in dep_time or "T04:" in dep_time:
                penalties["red_eye"] = 0.1
        
        # Bonus for direct flights
        if connections == 0:
            bonuses["direct_flight"] = 0.05
        
        return RouteScore(
            route_index=index,
            overall_score=combined_score,
            component_scores=component_scores,
            normalized_scores=normalized_scores,
            penalties=penalties,
            bonuses=bonuses
        )


class ValueScorer(BaseScorer):
    """Scorer optimizing for best value (price vs. quality)."""
    
    def score_route(self, route: Dict[str, Any], index: int = 0) -> RouteScore:
        """Score route based on value proposition."""
        price = route.get("price_eur", 9999)
        duration = route.get("total_hours", 48)
        connections = route.get("connections", 5)
        
        # Quality score (lower duration and connections = higher quality)
        quality_score = 1.0 - (
            self._normalize_value(duration, "total_hours") * 0.6 +
            self._normalize_value(connections, "connections") * 0.4
        )
        
        # Value is quality per unit price
        if price > 0:
            value_score = quality_score / self._normalize_value(price, "price_eur")
        else:
            value_score = quality_score
        
        return RouteScore(
            route_index=index,
            overall_score=1.0 - value_score,  # Invert for minimize goal
            component_scores={
                "price": price,
                "duration": duration,
                "connections": connections,
                "quality": quality_score * 10,
                "value": value_score * 10
            },
            normalized_scores={
                "quality": quality_score,
                "value": value_score
            }
        )


class ScorerFactory:
    """Factory for creating route scorers."""
    
    _scorers = {
        ScoringMethod.PRICE: PriceScorer,
        ScoringMethod.DURATION: DurationScorer,
        ScoringMethod.CONNECTIONS: ConnectionScorer,
        ScoringMethod.COMBINED: CombinedScorer,
        ScoringMethod.VALUE: ValueScorer
    }
    
    @classmethod
    def create_scorer(cls, config: ScoringConfig) -> BaseScorer:
        """Create a scorer based on configuration."""
        scorer_class = cls._scorers.get(config.method, CombinedScorer)
        return scorer_class(config)
    
    @classmethod
    def register_scorer(cls, method: ScoringMethod, scorer_class: type):
        """Register a custom scorer."""
        cls._scorers[method] = scorer_class


class RouteRanker:
    """Main interface for route ranking and scoring."""
    
    def __init__(self, config: Optional[ScoringConfig] = None):
        self.config = config or ScoringConfig()
        self.scorer = ScorerFactory.create_scorer(self.config)
        self.last_scores: List[RouteScore] = []
    
    def rank_routes(self, routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Rank routes and return them sorted by score."""
        if not routes:
            return []
        
        # Score all routes
        self.last_scores = self.scorer.score_routes(routes)
        
        # Create list of (route, score) pairs
        route_score_pairs = list(zip(routes, self.last_scores))
        
        # Sort by adjusted score
        sorted_pairs = sorted(route_score_pairs, key=lambda pair: pair[1].adjusted_score)
        
        # Return sorted routes with score information added
        ranked_routes = []
        for route, score in sorted_pairs:
            route_with_score = route.copy()
            route_with_score["_score_info"] = {
                "overall_score": score.overall_score,
                "adjusted_score": score.adjusted_score,
                "rank": score.rank,
                "component_scores": score.component_scores,
                "penalties": score.penalties,
                "bonuses": score.bonuses
            }
            ranked_routes.append(route_with_score)
        
        logger.info(f"Ranked {len(routes)} routes using {self.config.method.value} method")
        return ranked_routes
    
    def get_best_routes(self, routes: List[Dict[str, Any]], top_n: int = 5) -> List[Dict[str, Any]]:
        """Get the top N best routes."""
        ranked = self.rank_routes(routes)
        return ranked[:top_n]
    
    def get_scoring_analytics(self) -> Dict[str, Any]:
        """Get analytics about the last scoring operation."""
        if not self.last_scores:
            return {}
        
        scores = [s.adjusted_score for s in self.last_scores]
        
        return {
            "total_routes": len(self.last_scores),
            "scoring_method": self.config.method.value,
            "score_statistics": {
                "min": min(scores),
                "max": max(scores),
                "mean": statistics.mean(scores),
                "median": statistics.median(scores),
                "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0
            },
            "best_route_index": min(self.last_scores, key=lambda s: s.adjusted_score).route_index,
            "weights_used": {
                "price": self.config.weights.price,
                "duration": self.config.weights.duration,
                "connections": self.config.weights.connections,
                "baggage": self.config.weights.baggage,
                "carrier": self.config.weights.carrier_preference
            }
        }


# Legacy compatibility functions
def score_routes(routes: List[Dict[str, Any]], w_time: float = 0.6, w_cost: float = 0.4) -> List[Dict[str, Any]]:
    """Legacy function for backward compatibility. Lower score is better."""
    if not routes:
        return []
    
    # Use the new scoring system with legacy weights
    weights = ScoringWeights(duration=w_time, price=w_cost)
    config = ScoringConfig(method=ScoringMethod.COMBINED, weights=weights)
    ranker = RouteRanker(config)
    
    return ranker.rank_routes(routes)


def score_by_price(route: Dict[str, Any]) -> float:
    """Legacy function for backward compatibility. Lower is better."""
    return route.get("price_eur", float('inf'))


def score_by_duration(route: Dict[str, Any]) -> float:
    """Legacy function for backward compatibility. Lower is better."""
    return route.get("total_hours", float('inf'))


def score_by_connections(route: Dict[str, Any]) -> float:
    """Legacy function for backward compatibility. Lower is better."""
    return route.get("connections", float('inf'))


def score_combined(route: Dict[str, Any], weights: Dict[str, float] = None) -> float:
    """Legacy function for backward compatibility. Lower is better."""
    if weights is None:
        weights = {"price": 0.4, "duration": 0.3, "connections": 0.3}
    
    # Use the new scoring system with legacy weights
    scoring_weights = ScoringWeights(
        price=weights.get("price", 0.4),
        duration=weights.get("duration", 0.3),
        connections=weights.get("connections", 0.3)
    )
    
    config = ScoringConfig(
        method=ScoringMethod.COMBINED,
        weights=scoring_weights
    )
    
    scorer = CombinedScorer(config)
    score_result = scorer.score_route(route)
    
    return score_result.overall_score


# Convenience functions for common scoring scenarios
def create_price_optimizer() -> RouteRanker:
    """Create a ranker optimized for lowest price."""
    config = ScoringConfig(method=ScoringMethod.PRICE)
    return RouteRanker(config)


def create_speed_optimizer() -> RouteRanker:
    """Create a ranker optimized for shortest duration."""
    config = ScoringConfig(method=ScoringMethod.DURATION)
    return RouteRanker(config)


def create_convenience_optimizer() -> RouteRanker:
    """Create a ranker optimized for convenience (fewer connections)."""
    weights = ScoringWeights(price=0.2, duration=0.3, connections=0.5)
    config = ScoringConfig(method=ScoringMethod.COMBINED, weights=weights)
    return RouteRanker(config)


def create_balanced_optimizer() -> RouteRanker:
    """Create a ranker with balanced weights."""
    weights = ScoringWeights(price=0.35, duration=0.35, connections=0.25, baggage=0.05)
    config = ScoringConfig(method=ScoringMethod.COMBINED, weights=weights)
    return RouteRanker(config)


def create_value_optimizer() -> RouteRanker:
    """Create a ranker optimized for best value."""
    config = ScoringConfig(method=ScoringMethod.VALUE)
    return RouteRanker(config)
