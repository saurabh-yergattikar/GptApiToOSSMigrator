"""Cost analyzer for OpenAI API calls."""

from typing import Dict, List, Optional

from pydantic import BaseModel

from ..scanner.scanner import APICall


class CostEstimate(BaseModel):
    """Cost estimate for OpenAI API usage."""
    monthly_cost: float
    potential_savings: float
    breakdown: Dict[str, float]
    call_counts: Dict[str, int]


class CostAnalyzer:
    """Analyzer for estimating OpenAI API costs."""
    
    # Cost per 1K tokens (as of 2024)
    COST_PER_1K_TOKENS = {
        "gpt-4": 0.03,
        "gpt-4-32k": 0.06,
        "gpt-3.5-turbo": 0.0015,
        "gpt-3.5-turbo-16k": 0.003,
        "text-embedding-ada-002": 0.0001,
        "text-davinci-003": 0.02,
    }
    
    # Default token estimates
    DEFAULT_TOKENS = {
        "chat": 500,
        "completion": 250,
        "embedding": 1000,
    }
    
    def __init__(self):
        self.total_cost = 0.0
        self.breakdown = {}
        self.call_counts = {}
    
    def analyze_calls(self, api_calls: List[APICall]) -> CostEstimate:
        """Analyze API calls and estimate costs."""
        for call in api_calls:
            cost = self._estimate_call_cost(call)
            
            # Update totals
            self.total_cost += cost
            self.breakdown[call.type] = self.breakdown.get(call.type, 0) + cost
            self.call_counts[call.type] = self.call_counts.get(call.type, 0) + 1
        
        # Estimate potential savings (assume 80% cost reduction)
        potential_savings = self.total_cost * 0.8
        
        return CostEstimate(
            monthly_cost=self.total_cost,
            potential_savings=potential_savings,
            breakdown=self.breakdown,
            call_counts=self.call_counts
        )
    
    def _estimate_call_cost(self, call: APICall) -> float:
        """Estimate cost for a single API call."""
        # Get token estimate
        tokens = call.estimated_tokens or self.DEFAULT_TOKENS.get(call.type, 500)
        
        # Adjust tokens based on complexity
        if call.complexity == "complex":
            tokens *= 2
        elif call.complexity == "medium":
            tokens *= 1.5
        
        # Get cost per 1K tokens
        if call.model:
            cost_per_1k = self.COST_PER_1K_TOKENS.get(call.model)
        else:
            # Default costs if model not specified
            cost_per_1k = {
                "chat": 0.0015,  # gpt-3.5-turbo
                "completion": 0.02,  # text-davinci-003
                "embedding": 0.0001,  # text-embedding-ada-002
            }.get(call.type, 0.0015)
        
        # Calculate cost
        return (tokens / 1000) * cost_per_1k
    
    def generate_report(self, estimate: CostEstimate) -> str:
        """Generate a human-readable cost report."""
        report = [
            "📊 OpenAI API Cost Analysis",
            "=" * 30,
            f"Monthly Cost Estimate: ${estimate.monthly_cost:.2f}",
            f"Potential Savings: ${estimate.potential_savings:.2f}",
            "",
            "Breakdown by API Type:",
        ]
        
        for api_type, cost in estimate.breakdown.items():
            calls = estimate.call_counts[api_type]
            report.append(
                f"- {api_type}: ${cost:.2f} ({calls} calls)"
            )
        
        return "\n".join(report)