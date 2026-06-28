"""
Advanced Routing - Intelligent model selection based on task complexity.
"""

import logging
from typing import Optional, Dict, Any

from services.ai.models_config import RECOMMENDED_MODELS, get_model_config

logger = logging.getLogger(__name__)


class IntelligentRouter:
    """Routes requests to optimal AI models."""
    
    def __init__(self):
        """Initialize intelligent router."""
        self.task_to_model = {
            "search": "fast",
            "recommendation": "balanced",
            "complex_reasoning": "reasoning",
            "code_generation": "code_generation",
            "cost_optimization": "cost",
            "enterprise_critical": "enterprise",
        }
    
    def get_best_model(
        self,
        task_type: str,
        budget: Optional[float] = None,
        speed_priority: bool = False,
        quality_priority: bool = False
    ) -> str:
        """Select best model for task."""
        
        # Base selection by task type
        base_model = RECOMMENDED_MODELS.get(
            self.task_to_model.get(task_type, "balanced"),
            "gpt-4o"
        )
        
        # Adjust for constraints
        if budget and budget < 0.01:
            return RECOMMENDED_MODELS["cost_effective"]
        
        if speed_priority:
            return RECOMMENDED_MODELS["fast_response"]
        
        if quality_priority:
            return RECOMMENDED_MODELS["reasoning"]
        
        return base_model
    
    def estimate_cost(self, model: str, prompt_length: int, max_tokens: int) -> float:
        """Estimate API cost for request."""
        
        config = get_model_config(model)
        if not config:
            return 0.0
        
        # Rough estimation: prompt tokens + output tokens
        prompt_tokens = int(prompt_length / 4)  # Rough conversion
        estimated_total = prompt_tokens + max_tokens
        
        avg_cost = (config.cost_per_1k_input + config.cost_per_1k_output) / 2
        return (estimated_total / 1000) * avg_cost
    
    def should_use_streaming(self, task_type: str, response_size: int) -> bool:
        """Determine if streaming is beneficial."""
        
        if task_type in ["search", "recommendation"]:
            return True
        
        if response_size > 2000:
            return True
        
        return False


class AdminAssistant:
    """AI-powered admin assistant for bot management."""
    
    def __init__(self, provider):
        """Initialize admin assistant."""
        self.provider = provider
    
    async def analyze_logs(self, logs: str, question: str) -> str:
        """Analyze bot logs with AI."""
        
        if not self.provider:
            return "Provider not available"
        
        prompt = f"""Analyze these bot logs and answer the question:

Question: {question}

Logs (latest first):
{logs[:2000]}

Provide a concise analysis with potential issues and recommendations."""
        
        try:
            response = await self.provider.generate(
                prompt=prompt,
                max_tokens=512,
                temperature=0.3
            )
            return response.content
        except Exception as e:
            logger.error(f"Log analysis error: {e}")
            return f"Error analyzing logs: {str(e)}"
    
    async def generate_report(self, metrics: Dict[str, Any]) -> str:
        """Generate system performance report."""
        
        if not self.provider:
            return "Provider not available"
        
        metrics_text = "\n".join(f"- {k}: {v}" for k, v in metrics.items())
        
        prompt = f"""Based on these system metrics, generate a brief performance report:

{metrics_text}

Include: Status assessment, key insights, and recommendations."""
        
        try:
            response = await self.provider.generate(
                prompt=prompt,
                max_tokens=256,
                temperature=0.5
            )
            return response.content
        except Exception as e:
            logger.error(f"Report generation error: {e}")
            return f"Error generating report: {str(e)}"
    
    async def suggest_optimizations(self, current_config: Dict[str, Any]) -> Dict[str, str]:
        """Suggest configuration optimizations."""
        
        if not self.provider:
            return {}
        
        config_text = "\n".join(f"- {k}: {v}" for k, v in current_config.items())
        
        prompt = f"""Review this bot configuration and suggest optimizations:

Current Configuration:
{config_text}

Provide 3-5 specific, actionable optimization recommendations."""
        
        try:
            response = await self.provider.generate(
                prompt=prompt,
                max_tokens=512,
                temperature=0.5
            )
            
            # Parse recommendations
            recommendations = {}
            for i, line in enumerate(response.content.split("\n"), 1):
                if line.strip():
                    recommendations[f"recommendation_{i}"] = line.strip()
            
            return recommendations
        except Exception as e:
            logger.error(f"Optimization suggestion error: {e}")
            return {}
