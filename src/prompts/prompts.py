"""
AI Prompts for Smart Travel Optimizer.

This module contains structured prompts using Python classes for type safety,
validation, and better maintainability following agentic AI best practices.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod


class PromptType(Enum):
    """Types of prompts used in the system."""
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class PromptCategory(Enum):
    """Categories of prompts for organization."""
    ROUTE_PLANNING = "route_planning"
    SUMMARIZATION = "summarization"
    VALIDATION = "validation"
    ERROR_HANDLING = "error_handling"
    REFLECTION = "reflection"


@dataclass
class PromptTemplate:
    """Base class for structured prompts."""
    name: str
    category: PromptCategory
    prompt_type: PromptType
    template: str
    variables: List[str]
    description: str
    
    def format(self, **kwargs) -> str:
        """Format the prompt template with provided variables."""
        # Validate that all required variables are provided
        missing_vars = set(self.variables) - set(kwargs.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        return self.template.format(**kwargs)
    
    def validate_inputs(self, **kwargs) -> bool:
        """Validate input parameters."""
        return all(var in kwargs for var in self.variables)


class TravelSummaryPrompts:
    """Prompts for travel route summarization."""
    
    SYSTEM_PROMPT = PromptTemplate(
        name="travel_summary_system",
        category=PromptCategory.SUMMARIZATION,
        prompt_type=PromptType.SYSTEM,
        template="""You are an expert travel advisor AI that helps users understand travel options clearly and concisely.

Your role is to:
- Analyze travel routes and present them in user-friendly language
- Highlight key trade-offs between time, cost, and convenience
- Focus on practical considerations like luggage allowances and connections
- Present information without technical jargon
- Always prioritize user safety and practical considerations

Guidelines:
- Be concise but comprehensive
- Use clear, everyday language
- Highlight important trade-offs
- Consider the user's specific needs (luggage, time preferences, budget)
- Always mention any significant limitations or considerations
""",
        variables=[],
        description="System prompt for travel route summarization"
    )
    
    USER_SUMMARIZATION_PROMPT = PromptTemplate(
        name="travel_summary_user",
        category=PromptCategory.SUMMARIZATION,  
        prompt_type=PromptType.USER,
        template="""Please analyze and summarize the following travel options from {origin} to {destination} on {date}.

Travel Options:
{routes_data}

User Preferences:
- Time weight: {time_weight}
- Cost weight: {cost_weight}
- Minimum checked bags needed: {min_bags}
- Maximum connections acceptable: {max_connections}

Please provide:
1. A summary of the top 2-3 options
2. Key trade-offs (time vs. price vs. convenience)
3. Recommendations based on different priorities (fastest, cheapest, most convenient)
4. Any important considerations (luggage restrictions, connection times, etc.)

Focus on practical advice a traveler would need to make an informed decision.""",
        variables=["origin", "destination", "date", "routes_data", "time_weight", 
                  "cost_weight", "min_bags", "max_connections"],
        description="User prompt for requesting travel route summary"
    )
    
    COMPARISON_PROMPT = PromptTemplate(
        name="route_comparison",
        category=PromptCategory.SUMMARIZATION,
        prompt_type=PromptType.USER,
        template="""Compare these travel routes and explain the trade-offs:

Route 1: {route1_details}
Route 2: {route2_details}

Consider:
- Total travel time vs. cost
- Number of connections and layover quality
- Baggage allowances
- Departure/arrival times
- Carrier reliability and comfort

Provide a clear recommendation for:
- Budget-conscious travelers
- Time-sensitive travelers  
- Comfort-priority travelers""",
        variables=["route1_details", "route2_details"],
        description="Prompt for comparing two specific routes"
    )


class AgentReflectionPrompts:
    """Prompts for agent self-reflection and improvement."""
    
    EXECUTION_ANALYSIS_PROMPT = PromptTemplate(
        name="execution_analysis",
        category=PromptCategory.REFLECTION,
        prompt_type=PromptType.SYSTEM,
        template="""Analyze the following agent execution and provide insights:

Execution Summary:
- Providers used: {providers_used}
- Providers failed: {providers_failed}
- Routes found: {routes_found}
- Routes after filtering: {routes_filtered}
- Execution time: {execution_time}s
- Quality score: {quality_score}

Search Parameters:
- Origin: {origin}
- Destination: {destination}
- Date: {date}
- Min bags: {min_bags}
- Max connections: {max_connections}

Analyze:
1. Provider performance and reliability
2. Filter effectiveness
3. Search result quality
4. Performance bottlenecks
5. Suggestions for improvement

Provide specific, actionable recommendations.""",
        variables=["providers_used", "providers_failed", "routes_found", "routes_filtered",
                  "execution_time", "quality_score", "origin", "destination", "date",
                  "min_bags", "max_connections"],
        description="Prompt for analyzing agent execution performance"
    )


class ValidationPrompts:
    """Prompts for input validation and error handling."""
    
    INPUT_VALIDATION_PROMPT = PromptTemplate(
        name="input_validation",
        category=PromptCategory.VALIDATION,
        prompt_type=PromptType.SYSTEM,
        template="""Validate the following travel search inputs and provide feedback:

User Input:
- Origin: "{origin}"
- Destination: "{destination}"
- Date: "{date}"
- Bags: {bags}
- Max connections: {max_connections}

Check for:
1. Valid city names (real places, proper spelling)
2. Reasonable date (not in past, format correct)
3. Logical baggage requirements
4. Reasonable connection limits
5. Potential ambiguities or issues

If invalid, provide clear, helpful error messages.
If valid, confirm the search parameters.""",
        variables=["origin", "destination", "date", "bags", "max_connections"],
        description="Prompt for validating user search inputs"
    )


class ErrorHandlingPrompts:
    """Prompts for handling various error scenarios."""
    
    NO_ROUTES_FOUND_PROMPT = PromptTemplate(
        name="no_routes_found",
        category=PromptCategory.ERROR_HANDLING,
        prompt_type=PromptType.ASSISTANT,
        template="""No travel routes were found for your search from {origin} to {destination} on {date}.

This could be because:
- The route is not commonly served
- Your requirements are too restrictive ({min_bags} bags, max {max_connections} connections)
- The date is too far in advance or during a restricted period
- There may be seasonal limitations

Suggestions:
1. Try nearby airports or cities
2. Consider different dates (±1-3 days)
3. Reduce baggage requirements to {suggested_bags} bags
4. Allow more connections (up to {suggested_connections})
5. Check if this is a popular travel route

Would you like to modify your search parameters?""",
        variables=["origin", "destination", "date", "min_bags", "max_connections",
                  "suggested_bags", "suggested_connections"],
        description="Response when no routes are found"
    )
    
    PROVIDER_ERROR_PROMPT = PromptTemplate(
        name="provider_error",
        category=PromptCategory.ERROR_HANDLING,
        prompt_type=PromptType.ASSISTANT,
        template="""Some travel data providers are currently experiencing issues:

Failed providers: {failed_providers}
Working providers: {working_providers}

Your search results may be incomplete. We've found {route_count} options using available providers.

{suggestion_message}

The system will continue to retry failed providers automatically.""",
        variables=["failed_providers", "working_providers", "route_count", "suggestion_message"],
        description="Response when providers fail"
    )


class PromptManager:
    """Centralized prompt management with caching and validation."""
    
    def __init__(self):
        self.prompts = {}
        self._load_all_prompts()
    
    def _load_all_prompts(self):
        """Load all prompt templates into the manager."""
        # Load travel summary prompts
        self.prompts.update({
            "travel_summary_system": TravelSummaryPrompts.SYSTEM_PROMPT,
            "travel_summary_user": TravelSummaryPrompts.USER_SUMMARIZATION_PROMPT,
            "route_comparison": TravelSummaryPrompts.COMPARISON_PROMPT,
        })
        
        # Load reflection prompts
        self.prompts.update({
            "execution_analysis": AgentReflectionPrompts.EXECUTION_ANALYSIS_PROMPT,
        })
        
        # Load validation prompts
        self.prompts.update({
            "input_validation": ValidationPrompts.INPUT_VALIDATION_PROMPT,
        })
        
        # Load error handling prompts
        self.prompts.update({
            "no_routes_found": ErrorHandlingPrompts.NO_ROUTES_FOUND_PROMPT,
            "provider_error": ErrorHandlingPrompts.PROVIDER_ERROR_PROMPT,
        })
    
    def get_prompt(self, name: str) -> PromptTemplate:
        """Get a prompt template by name."""
        if name not in self.prompts:
            raise ValueError(f"Prompt '{name}' not found")
        return self.prompts[name]
    
    def format_prompt(self, name: str, **kwargs) -> str:
        """Format a prompt with the given variables."""
        prompt = self.get_prompt(name)
        return prompt.format(**kwargs)
    
    def list_prompts(self, category: Optional[PromptCategory] = None) -> List[str]:
        """List available prompts, optionally filtered by category."""
        if category:
            return [name for name, prompt in self.prompts.items() 
                   if prompt.category == category]
        return list(self.prompts.keys())


# Global prompt manager instance
prompt_manager = PromptManager()


def get_travel_summary_prompt(origin: str, destination: str, date: str, 
                            routes_data: str, time_weight: float, cost_weight: float,
                            min_bags: int, max_connections: int) -> str:
    """Convenience function for getting formatted travel summary prompt."""
    return prompt_manager.format_prompt(
        "travel_summary_user",
        origin=origin,
        destination=destination,
        date=date,
        routes_data=routes_data,
        time_weight=time_weight,
        cost_weight=cost_weight,
        min_bags=min_bags,
        max_connections=max_connections
    )


def get_system_prompt(prompt_name: str = "travel_summary_system") -> str:
    """Get a system prompt by name."""
    return prompt_manager.format_prompt(prompt_name)


def get_error_prompt(error_type: str, **kwargs) -> str:
    """Get an error handling prompt."""
    return prompt_manager.format_prompt(error_type, **kwargs)
