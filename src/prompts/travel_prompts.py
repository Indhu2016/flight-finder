"""
AI Prompts for Smart Travel Optimizer.

This module contains all AI prompts used throughout the system for consistency
and easy maintenance. All prompts follow best practices for AI interaction.
"""

from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class PromptTemplate:
    """Template for structured prompts."""
    name: str
    system_prompt: str
    user_template: str
    examples: List[Dict[str, str]] = None
    

class TravelPrompts:
    """Collection of all travel-related AI prompts."""
    
    # System prompts
    SUMMARY_SYSTEM = """
You are a helpful travel assistant that summarizes travel options clearly and concisely for non-technical users.

Your focus areas are:
- Travel time and duration
- Price and cost efficiency
- Number of connections 
- Luggage allowance and policies

Guidelines:
- Use simple, clear language
- Highlight trade-offs between options
- Mention key benefits and drawbacks
- Focus on practical travel considerations
- Be concise but informative
"""

    ROUTE_OPTIMIZATION_SYSTEM = """
You are an expert travel route optimizer with deep knowledge of:
- Transportation networks and connections
- Cost optimization strategies
- Time efficiency analysis
- Luggage policies and restrictions
- Travel comfort and convenience factors

Your goal is to help users find the optimal balance between cost, time, and convenience.
"""

    SAFETY_ANALYSIS_SYSTEM = """
You are a travel safety analyst responsible for:
- Evaluating route safety and reliability
- Identifying potential travel disruptions
- Assessing carrier reputation and safety records
- Providing risk mitigation suggestions
- Highlighting seasonal travel considerations
"""

    # User prompt templates
    SUMMARY_USER_TEMPLATE = """
Summarize the top {num_routes} travel itineraries from {origin} to {destination} on {date}.

Routes:
{routes_data}

Instructions:
- Mention trade-offs (time vs. price vs. convenience)
- Highlight the best option for different priorities
- Keep it concise and actionable
- Use bullet points for clarity
"""

    ROUTE_COMPARISON_TEMPLATE = """
Compare these travel options and recommend the best choice:

Origin: {origin}
Destination: {destination}  
Date: {date}
User Priorities: {priorities}

Routes:
{routes_data}

Provide:
1. Quick recommendation
2. Detailed comparison
3. Alternative suggestions
"""

    OPTIMIZATION_FEEDBACK_TEMPLATE = """
Analyze this route optimization result and suggest improvements:

Search Parameters:
- Origin: {origin}
- Destination: {destination}
- Date: {date}
- Max Connections: {max_connections}
- Min Bags: {min_bags}
- Time Weight: {w_time}
- Cost Weight: {w_cost}

Results:
- Routes Found: {routes_found}
- After Filtering: {routes_filtered}
- Execution Time: {execution_time}s

Suggest improvements for better results.
"""

    @classmethod
    def get_summary_prompt(cls, routes: List[Dict[str, Any]], origin: str, 
                          destination: str, date: str, num_routes: int = 2) -> Dict[str, str]:
        """Generate summary prompt for given routes."""
        routes_text = cls._format_routes_for_prompt(routes[:num_routes])
        
        return {
            "system": cls.SUMMARY_SYSTEM,
            "user": cls.SUMMARY_USER_TEMPLATE.format(
                num_routes=num_routes,
                origin=origin,
                destination=destination,
                date=date,
                routes_data=routes_text
            )
        }
    
    @classmethod
    def get_comparison_prompt(cls, routes: List[Dict[str, Any]], origin: str,
                            destination: str, date: str, priorities: str) -> Dict[str, str]:
        """Generate route comparison prompt."""
        routes_text = cls._format_routes_for_prompt(routes)
        
        return {
            "system": cls.ROUTE_OPTIMIZATION_SYSTEM,
            "user": cls.ROUTE_COMPARISON_TEMPLATE.format(
                origin=origin,
                destination=destination,
                date=date,
                priorities=priorities,
                routes_data=routes_text
            )
        }
    
    @classmethod
    def get_optimization_feedback_prompt(cls, search_params: Dict[str, Any], 
                                       results: Dict[str, Any]) -> Dict[str, str]:
        """Generate optimization feedback prompt."""
        return {
            "system": cls.ROUTE_OPTIMIZATION_SYSTEM,
            "user": cls.OPTIMIZATION_FEEDBACK_TEMPLATE.format(**search_params, **results)
        }
    
    @staticmethod
    def _format_routes_for_prompt(routes: List[Dict[str, Any]]) -> str:
        """Format routes data for inclusion in prompts."""
        if not routes:
            return "No routes found."
        
        formatted_routes = []
        for i, route in enumerate(routes, 1):
            carrier = route.get('airline') or route.get('carrier', 'Unknown')
            mode = route.get('mode', 'Unknown').title()
            price = route.get('price_eur', 0)
            duration = route.get('total_hours', 0)
            connections = route.get('connections', 0)
            baggage = route.get('baggage', {})
            bags = baggage.get('checked_bags', 0)
            bag_weight = baggage.get('per_bag_kg', 0)
            
            route_text = f"""
Route {i}: {mode} with {carrier}
- Price: €{price}
- Duration: {duration} hours
- Connections: {connections}
- Baggage: {bags} bags × {bag_weight}kg each
"""
            if route.get('via'):
                route_text += f"- Via: {', '.join(route['via'])}\n"
            
            formatted_routes.append(route_text.strip())
        
        return "\n\n".join(formatted_routes)


# Legacy support - maintain backward compatibility
def get_summary_system_prompt() -> str:
    """Get the system prompt for summarization."""
    return TravelPrompts.SUMMARY_SYSTEM


def get_summary_user_prompt(num_routes: int = 2) -> str:
    """Get the user prompt template for summarization."""
    return f"Summarize the top {num_routes} itineraries. Mention trade-offs (time vs. price)."


# Prompt templates for different use cases
PROMPT_TEMPLATES = {
    "route_summary": PromptTemplate(
        name="route_summary",
        system_prompt=TravelPrompts.SUMMARY_SYSTEM,
        user_template=TravelPrompts.SUMMARY_USER_TEMPLATE,
        examples=[
            {
                "user": "Summarize top 2 routes from Berlin to Paris",
                "assistant": "Here are your best options:\n\n1. **Flight (Lufthansa)** - €180, 1.5h, direct\n   ✅ Fastest option\n   ❌ Higher cost\n\n2. **Train (DB/SNCF)** - €120, 8h, 1 connection\n   ✅ Most economical\n   ✅ City center to city center\n   ❌ Longer journey"
            }
        ]
    ),
    
    "route_optimization": PromptTemplate(
        name="route_optimization", 
        system_prompt=TravelPrompts.ROUTE_OPTIMIZATION_SYSTEM,
        user_template=TravelPrompts.ROUTE_COMPARISON_TEMPLATE
    ),
    
    "safety_analysis": PromptTemplate(
        name="safety_analysis",
        system_prompt=TravelPrompts.SAFETY_ANALYSIS_SYSTEM,
        user_template="Analyze the safety and reliability of these travel options: {routes_data}"
    )
}
