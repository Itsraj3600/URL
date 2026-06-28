"""
AI Models Configuration - Centralized pricing, capabilities, and model definitions.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class ModelProvider(Enum):
    OPENAI = "openai"
    GROQ = "groq"
    NVIDIA = "nvidia"
    GOOGLE = "google"
    ANTHROPIC = "anthropic"


class ModelCapability(Enum):
    TEXT_GENERATION = "text_generation"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    VISION = "vision"
    EMBEDDINGS = "embeddings"


@dataclass
class ModelConfig:
    """Configuration for a single model."""
    name: str
    provider: ModelProvider
    context_window: int
    cost_per_1k_input: float  # in USD
    cost_per_1k_output: float  # in USD
    capabilities: List[ModelCapability]
    max_tokens: int = 4096
    supports_streaming: bool = True
    supports_reasoning: bool = False


# Available Models with Pricing (as of 2024-12-27)
MODELS = {
    # OpenAI Models
    "gpt-4o": ModelConfig(
        name="gpt-4o",
        provider=ModelProvider.OPENAI,
        context_window=128000,
        cost_per_1k_input=0.005,
        cost_per_1k_output=0.015,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.VISION,
        ],
        max_tokens=4096,
        supports_reasoning=True,
    ),
    "gpt-4-turbo": ModelConfig(
        name="gpt-4-turbo",
        provider=ModelProvider.OPENAI,
        context_window=128000,
        cost_per_1k_input=0.01,
        cost_per_1k_output=0.03,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.VISION,
        ],
        max_tokens=4096,
    ),
    "gpt-3.5-turbo": ModelConfig(
        name="gpt-3.5-turbo",
        provider=ModelProvider.OPENAI,
        context_window=16385,
        cost_per_1k_input=0.0005,
        cost_per_1k_output=0.0015,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
        ],
        max_tokens=4096,
    ),
    
    # Groq Models (Fast, Cost-Effective)
    "groq-mixtral": ModelConfig(
        name="mixtral-8x7b-32768",
        provider=ModelProvider.GROQ,
        context_window=32768,
        cost_per_1k_input=0.00027,
        cost_per_1k_output=0.00027,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
        ],
        max_tokens=8192,
    ),
    "groq-llama": ModelConfig(
        name="llama-2-70b-chat",
        provider=ModelProvider.GROQ,
        context_window=4096,
        cost_per_1k_input=0.0007,
        cost_per_1k_output=0.0009,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
        ],
        max_tokens=4096,
    ),
    
    # NVIDIA Models (Enterprise)
    "nvidia-nemotron": ModelConfig(
        name="nvidia/nemotron-4-340b-instruct",
        provider=ModelProvider.NVIDIA,
        context_window=4096,
        cost_per_1k_input=0.0002,
        cost_per_1k_output=0.0002,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
        ],
        max_tokens=4096,
        supports_reasoning=True,
    ),
    
    # Google Models
    "gemini-pro": ModelConfig(
        name="gemini-pro",
        provider=ModelProvider.GOOGLE,
        context_window=32000,
        cost_per_1k_input=0.00025,
        cost_per_1k_output=0.0005,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
        ],
        max_tokens=8192,
    ),
    
    # Anthropic Models
    "claude-3": ModelConfig(
        name="claude-3-opus-20240229",
        provider=ModelProvider.ANTHROPIC,
        context_window=200000,
        cost_per_1k_input=0.015,
        cost_per_1k_output=0.075,
        capabilities=[
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
        ],
        max_tokens=4096,
        supports_reasoning=True,
    ),
}


# Model Recommendations by Use Case
RECOMMENDED_MODELS = {
    "fast_response": "groq-mixtral",  # Fastest inference
    "cost_effective": "gpt-3.5-turbo",  # Best value
    "reasoning": "claude-3",  # Best reasoning capabilities
    "code_generation": "gpt-4o",  # Best for code
    "balanced": "gpt-4o",  # Best all-around
    "enterprise": "nvidia-nemotron",  # Enterprise grade
}


def get_model_config(model_name: str) -> Optional[ModelConfig]:
    """Get configuration for a specific model."""
    return MODELS.get(model_name)


def get_provider_models(provider: ModelProvider) -> Dict[str, ModelConfig]:
    """Get all models from a specific provider."""
    return {
        name: config 
        for name, config in MODELS.items() 
        if config.provider == provider
    }


def calculate_model_cost(model_name: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate cost for model usage."""
    config = get_model_config(model_name)
    if not config:
        return 0.0
    
    input_cost = (input_tokens / 1000) * config.cost_per_1k_input
    output_cost = (output_tokens / 1000) * config.cost_per_1k_output
    return input_cost + output_cost
