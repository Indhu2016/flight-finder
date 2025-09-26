"""
Advanced route formatting and presentation system with rich output support.

This module provides comprehensive formatting capabilities for travel routes,
implementing the Template Method pattern and supporting multiple output formats.
"""

import logging
from typing import List, Dict, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import json

logger = logging.getLogger(__name__)


class OutputFormat(Enum):
    """Available output formats."""
    PLAIN_TEXT = "plain_text"
    RICH_TEXT = "rich_text"
    HTML = "html"
    JSON = "json"
    MARKDOWN = "markdown"
    CSV = "csv"


class DetailLevel(Enum):
    """Level of detail for route formatting."""
    MINIMAL = "minimal"
    SUMMARY = "summary"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"


@dataclass
class FormattingOptions:
    """Configuration for route formatting."""
    format_type: OutputFormat = OutputFormat.PLAIN_TEXT
    detail_level: DetailLevel = DetailLevel.SUMMARY
    max_routes: int = 5
    include_analytics: bool = False
    include_timestamps: bool = True
    currency_symbol: str = "€"
    time_format: str = "%Y-%m-%d %H:%M"
    date_only: bool = False
    show_duration: bool = True
    show_connections: bool = True
    show_baggage: bool = True
    show_price_breakdown: bool = False
    highlight_best: bool = True
    sort_by: Optional[str] = "price_eur"
    group_by: Optional[str] = None
    custom_fields: List[str] = field(default_factory=list)


@dataclass
class RouteAnalytics:
    """Analytics for a set of routes."""
    total_routes: int
    price_range: Dict[str, float]
    duration_range: Dict[str, float]
    carrier_distribution: Dict[str, int]
    connection_distribution: Dict[str, int]
    average_price: float
    average_duration: float
    best_value_index: Optional[int] = None
    fastest_route_index: Optional[int] = None
    cheapest_route_index: Optional[int] = None


class BaseRouteFormatter(ABC):
    """Abstract base class for route formatters."""
    
    def __init__(self, options: FormattingOptions):
        self.options = options
        
    @abstractmethod
    def format_single_route(self, route: Dict[str, Any], index: Optional[int] = None) -> str:
        """Format a single route."""
        pass
    
    @abstractmethod
    def format_multiple_routes(self, routes: List[Dict[str, Any]]) -> str:
        """Format multiple routes."""
        pass
    
    def _extract_route_data(self, route: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize route data."""
        departure = route.get("departure", {})
        arrival = route.get("arrival", {})
        
        return {
            "price": route.get("price_eur", 0),
            "currency": self.options.currency_symbol,
            "carrier": route.get("airline") or route.get("carrier", "Unknown"),
            "dep_time": departure.get("datetime", "Unknown"),
            "arr_time": arrival.get("datetime", "Unknown"),
            "dep_city": departure.get("city", "Unknown"),
            "arr_city": arrival.get("city", "Unknown"),
            "dep_code": departure.get("code", ""),
            "arr_code": arrival.get("code", ""),
            "duration": route.get("total_hours", 0),
            "connections": route.get("connections", 0),
            "baggage": route.get("baggage", {}),
            "mode": route.get("mode", "flight"),
            "via": route.get("via", [])
        }
    
    def _format_time(self, time_str: str) -> str:
        """Format time string according to options."""
        if time_str == "Unknown":
            return time_str
            
        try:
            # Try to parse ISO format
            dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            if self.options.date_only:
                return dt.strftime("%Y-%m-%d")
            return dt.strftime(self.options.time_format)
        except (ValueError, AttributeError):
            # Return as-is if parsing fails
            return str(time_str)
    
    def _calculate_analytics(self, routes: List[Dict[str, Any]]) -> RouteAnalytics:
        """Calculate analytics for the routes."""
        if not routes:
            return RouteAnalytics(
                total_routes=0,
                price_range={},
                duration_range={},
                carrier_distribution={},
                connection_distribution={},
                average_price=0,
                average_duration=0
            )
        
        prices = [r.get("price_eur", 0) for r in routes]
        durations = [r.get("total_hours", 0) for r in routes]
        carriers = [r.get("airline") or r.get("carrier", "Unknown") for r in routes]
        connections = [r.get("connections", 0) for r in routes]
        
        # Find best routes
        cheapest_idx = min(range(len(routes)), key=lambda i: prices[i]) if prices else None
        fastest_idx = min(range(len(routes)), key=lambda i: durations[i]) if durations else None
        
        # Calculate value score (normalized price + duration)
        if prices and durations:
            max_price = max(prices) if max(prices) > 0 else 1
            max_duration = max(durations) if max(durations) > 0 else 1
            
            value_scores = [
                (prices[i] / max_price) + (durations[i] / max_duration)
                for i in range(len(routes))
            ]
            best_value_idx = min(range(len(value_scores)), key=lambda i: value_scores[i])
        else:
            best_value_idx = None
        
        return RouteAnalytics(
            total_routes=len(routes),
            price_range={
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0,
                "avg": sum(prices) / len(prices) if prices else 0
            },
            duration_range={
                "min": min(durations) if durations else 0,
                "max": max(durations) if durations else 0,
                "avg": sum(durations) / len(durations) if durations else 0
            },
            carrier_distribution={
                carrier: carriers.count(carrier) for carrier in set(carriers)
            },
            connection_distribution={
                str(conn): connections.count(conn) for conn in set(connections)
            },
            average_price=sum(prices) / len(prices) if prices else 0,
            average_duration=sum(durations) / len(durations) if durations else 0,
            cheapest_route_index=cheapest_idx,
            fastest_route_index=fastest_idx,
            best_value_index=best_value_idx
        )


class PlainTextFormatter(BaseRouteFormatter):
    """Plain text route formatter."""
    
    def format_single_route(self, route: Dict[str, Any], index: Optional[int] = None) -> str:
        """Format a single route as plain text."""
        data = self._extract_route_data(route)
        
        # Build route string based on detail level
        if self.options.detail_level == DetailLevel.MINIMAL:
            return f"{data['carrier']}: {data['dep_city']} → {data['arr_city']} - {data['currency']}{data['price']}"
        
        # Enhanced human-readable format
        mode = data['mode'].title()
        carrier = data['carrier']
        price = f"{data['currency']}{data['price']}"
        duration = f"{data['duration']}h"
        connections = f"{data['connections']} connections"
        
        # Via information
        via = f" via {', '.join(data['via'])}" if data['via'] else ""
        
        # Baggage information
        baggage_info = ""
        if self.options.show_baggage and data['baggage']:
            bags = data['baggage'].get('checked_bags', '?')
            weight = data['baggage'].get('per_bag_kg', '?')
            baggage_info = f" • Bags: {bags}x{weight}kg"
        
        route_str = f"{mode} • {carrier} • {price} • {duration} • {connections}{via}{baggage_info}"
        
        if index is not None:
            route_str = f"{index}. {route_str}"
            
        return route_str
    
    def format_multiple_routes(self, routes: List[Dict[str, Any]]) -> str:
        """Format multiple routes as plain text."""
        if not routes:
            return "No routes found."
        
        # Sort routes if requested
        if self.options.sort_by:
            try:
                routes = sorted(routes, key=lambda r: r.get(self.options.sort_by, 0))
            except (TypeError, KeyError):
                logger.warning(f"Could not sort by {self.options.sort_by}")
        
        # Calculate analytics if requested
        analytics = self._calculate_analytics(routes) if self.options.include_analytics else None
        
        # Build result string
        lines = []
        
        # Highlight best routes
        best_indicators = {}
        if self.options.highlight_best and analytics:
            if analytics.cheapest_route_index is not None:
                best_indicators[analytics.cheapest_route_index] = " 💰 CHEAPEST"
            if analytics.fastest_route_index is not None:
                best_indicators[analytics.fastest_route_index] = " ⚡ FASTEST"
            if analytics.best_value_index is not None:
                best_indicators[analytics.best_value_index] = " ⭐ BEST VALUE"
        
        # Format each route
        for i, route in enumerate(routes[:self.options.max_routes], 1):
            route_str = self.format_single_route(route, i)
            
            # Add best indicator if applicable
            if (i - 1) in best_indicators:
                route_str += best_indicators[i - 1]
            
            lines.append(route_str)
        
        result = "\n".join(lines)
        
        # Add truncation notice
        if len(routes) > self.options.max_routes:
            result += f"\n\n... and {len(routes) - self.options.max_routes} more routes available"
        
        # Add analytics if requested
        if self.options.include_analytics and analytics:
            result += f"\n\n📊 Route Analytics:"
            result += f"\nAverage price: {analytics.average_price:.2f}{self.options.currency_symbol}"
            result += f"\nPrice range: {analytics.price_range['min']}{self.options.currency_symbol} - {analytics.price_range['max']}{self.options.currency_symbol}"
            if analytics.average_duration > 0:
                result += f"\nAverage duration: {analytics.average_duration:.1f}h"
            
            # Carrier distribution
            if analytics.carrier_distribution:
                carrier_info = ', '.join([f'{k}({v})' for k, v in analytics.carrier_distribution.items()])
                result += f"\nCarriers: {carrier_info}"
        
        return result


class HTMLFormatter(BaseRouteFormatter):
    """HTML table route formatter."""
    
    def format_single_route(self, route: Dict[str, Any], index: Optional[int] = None) -> str:
        """Format a single route as HTML table row."""
        data = self._extract_route_data(route)
        
        via = ", ".join(data['via']) if data['via'] else "-"
        baggage = f"{data['baggage'].get('checked_bags','?')}×{data['baggage'].get('per_bag_kg','?')}kg"
        
        return f"""        <tr>
            <td>{data['mode'].title()}</td>
            <td>{data['carrier']}</td>
            <td>{data['currency']}{data['price']}</td>
            <td>{data['duration']} h</td>
            <td>{data['connections']}</td>
            <td>{via}</td>
            <td>{baggage}</td>
        </tr>"""
    
    def format_multiple_routes(self, routes: List[Dict[str, Any]]) -> str:
        """Format multiple routes as HTML table."""
        if not routes:
            return "<p>No routes found.</p>"
        
        # Sort routes if requested  
        if self.options.sort_by:
            try:
                routes = sorted(routes, key=lambda r: r.get(self.options.sort_by, 0))
            except (TypeError, KeyError):
                logger.warning(f"Could not sort by {self.options.sort_by}")
        
        rows = []
        for route in routes[:self.options.max_routes]:
            rows.append(self.format_single_route(route))
        
        table_html = f"""    <table border="1" cellpadding="6" cellspacing="0" style="border-collapse: collapse; width: 100%;">
        <thead>
            <tr style="background-color: #f0f0f0;">
                <th>Mode</th>
                <th>Carrier</th>
                <th>Price</th>
                <th>Duration</th>
                <th>Connections</th>
                <th>Via</th>
                <th>Baggage</th>
            </tr>
        </thead>
        <tbody>
{''.join(rows)}
        </tbody>
    </table>"""
        
        if len(routes) > self.options.max_routes:
            table_html += f"\n    <p><em>... and {len(routes) - self.options.max_routes} more routes available</em></p>"
        
        # Add analytics if requested
        if self.options.include_analytics:
            analytics = self._calculate_analytics(routes)
            table_html += f"""
    <div style="margin-top: 20px; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
        <h4>📊 Route Analytics</h4>
        <ul>
            <li><strong>Total routes:</strong> {analytics.total_routes}</li>
            <li><strong>Average price:</strong> {analytics.average_price:.2f}{self.options.currency_symbol}</li>
            <li><strong>Price range:</strong> {analytics.price_range['min']}{self.options.currency_symbol} - {analytics.price_range['max']}{self.options.currency_symbol}</li>
            <li><strong>Average duration:</strong> {analytics.average_duration:.1f}h</li>
        </ul>
    </div>"""
        
        return table_html


class JSONFormatter(BaseRouteFormatter):
    """JSON route formatter."""
    
    def format_single_route(self, route: Dict[str, Any], index: Optional[int] = None) -> str:
        """Format a single route as JSON."""
        return json.dumps(route, indent=2)
    
    def format_multiple_routes(self, routes: List[Dict[str, Any]]) -> str:
        """Format multiple routes as JSON."""
        if self.options.sort_by:
            try:
                routes = sorted(routes, key=lambda r: r.get(self.options.sort_by, 0))
            except (TypeError, KeyError):
                logger.warning(f"Could not sort by {self.options.sort_by}")
        
        output_data = {
            "total_routes": len(routes),
            "displayed_routes": min(len(routes), self.options.max_routes),
            "routes": routes[:self.options.max_routes]
        }
        
        if self.options.include_analytics:
            analytics = self._calculate_analytics(routes)
            output_data["analytics"] = {
                "average_price": analytics.average_price,
                "price_range": analytics.price_range,
                "average_duration": analytics.average_duration,
                "duration_range": analytics.duration_range,
                "carrier_distribution": analytics.carrier_distribution,
                "connection_distribution": analytics.connection_distribution
            }
        
        return json.dumps(output_data, indent=2)


class FormatterFactory:
    """Factory for creating route formatters."""
    
    _formatters = {
        OutputFormat.PLAIN_TEXT: PlainTextFormatter,
        OutputFormat.HTML: HTMLFormatter,
        OutputFormat.JSON: JSONFormatter
    }
    
    @classmethod
    def create_formatter(cls, options: FormattingOptions) -> BaseRouteFormatter:
        """Create a formatter based on options."""
        formatter_class = cls._formatters.get(options.format_type, PlainTextFormatter)
        return formatter_class(options)
    
    @classmethod
    def register_formatter(cls, format_type: OutputFormat, formatter_class: type):
        """Register a custom formatter."""
        cls._formatters[format_type] = formatter_class


class RouteFormatter:
    """Main route formatting interface."""
    
    def __init__(self, options: Optional[FormattingOptions] = None):
        self.options = options or FormattingOptions()
        self.formatter = FormatterFactory.create_formatter(self.options)
    
    def format_routes(self, routes: List[Dict[str, Any]]) -> str:
        """Format routes using the configured formatter."""
        try:
            return self.formatter.format_multiple_routes(routes)
        except Exception as e:
            logger.error(f"Error formatting routes: {e}")
            return f"Error formatting routes: {str(e)}"
    
    def format_single(self, route: Dict[str, Any]) -> str:
        """Format a single route."""
        try:
            return self.formatter.format_single_route(route)
        except Exception as e:
            logger.error(f"Error formatting route: {e}")
            return f"Error formatting route: {str(e)}"


# Legacy compatibility functions
def human_readable(routes: List[Dict[str, Any]]) -> str:
    """Legacy function for backward compatibility."""
    formatter = RouteFormatter()
    return formatter.format_routes(routes)


def html_table(routes: List[Dict[str, Any]]) -> str:
    """Legacy function for backward compatibility."""
    options = FormattingOptions(format_type=OutputFormat.HTML)
    formatter = RouteFormatter(options)
    return formatter.format_routes(routes)


# Convenience functions for common formatting scenarios
def format_routes_simple(routes: List[Dict[str, Any]], max_count: int = 5) -> str:
    """Simple route formatting with minimal options."""
    options = FormattingOptions(
        detail_level=DetailLevel.SUMMARY,
        max_routes=max_count,
        highlight_best=True
    )
    formatter = RouteFormatter(options)
    return formatter.format_routes(routes)


def format_routes_detailed(routes: List[Dict[str, Any]], include_analytics: bool = True) -> str:
    """Detailed route formatting with analytics."""
    options = FormattingOptions(
        detail_level=DetailLevel.DETAILED,
        include_analytics=include_analytics,
        highlight_best=True,
        show_duration=True,
        show_connections=True,
        show_baggage=True
    )
    formatter = RouteFormatter(options)
    return formatter.format_routes(routes)
