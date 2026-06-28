"""
AI Provider Factory - Instantiates appropriate provider based on configuration.
Handles multi-provider support with fallback mechanisms.
"""

import logging
from typing import Optional, Dict
from os import environ

from services.ai.base_provider import BaseAIProvider
from services.ai.models_config import ModelProvider

logger = logging.getLogger(__name__)


class ProviderFactory:
    """Factory for creating AI provider instances."""
    
    _providers: Dict[str, type] = {}
    _instances: Dict[str, BaseAIProvider] = {}
    
    @classmethod
    def register(cls, provider_name: str, provider_class: type) -> None:
        """Register a new provider implementation."""
        cls._providers[provider_name] = provider_class
    
    @classmethod
    def get_provider(
        cls,
        provider_type: str,
        force_new: bool = False
    ) -> Optional[BaseAIProvider]:
        """
        Get or create a provider instance.
        
        Args:
            provider_type: Type of provider (openai, groq, nvidia, etc.)
            force_new: Create new instance instead of using cached
            
        Returns:
            Provider instance or None if not configured
        """
        if not force_new and provider_type in cls._instances:
            return cls._instances[provider_type]
        
        if provider_type not in cls._providers:
            logger.warning(f"Provider {provider_type} not registered")
            return None
        
        try:
            provider_class = cls._providers[provider_type]
            instance = provider_class()
            
            if instance and not force_new:
                cls._instances[provider_type] = instance
            
            return instance
        except Exception as e:
            logger.error(f"Failed to initialize {provider_type} provider: {e}")
            return None
    
    @classmethod
    def get_default_provider(cls) -> Optional[BaseAIProvider]:
        """Get default provider based on environment."""
        default = environ.get("AI_DEFAULT_PROVIDER", "openai").lower()
        
        if default == "openai":
            return cls.get_provider("openai")
        elif default == "groq":
            return cls.get_provider("groq")
        elif default == "nvidia":
            return cls.get_provider("nvidia")
        else:
            logger.warning(f"Unknown default provider: {default}")
            return cls.get_provider("openai")  # Fallback to OpenAI
    
    @classmethod
    def get_best_provider(cls, use_case: str) -> Optional[BaseAIProvider]:
        """Get best provider for specific use case."""
        use_case_to_provider = {
            "fast": "groq",
            "cost": "groq",
            "reasoning": "openai",
            "code": "openai",
            "vision": "openai",
            "enterprise": "nvidia",
        }
        
        provider_type = use_case_to_provider.get(use_case, "openai")
        return cls.get_provider(provider_type)


# Import and register providers
def initialize_providers():
    """Initialize all available providers."""
    try:
        from services.ai.providers.openai_provider import OpenAIProvider
        ProviderFactory.register("openai", OpenAIProvider)
    except ImportError:
        logger.warning("OpenAI provider not available")
    
    try:
        from services.ai.providers.groq_provider import GroqProvider
        ProviderFactory.register("groq", GroqProvider)
    except ImportError:
        logger.warning("Groq provider not available")
    
    try:
        from services.ai.providers.nvidia_provider import NVIDIAProvider
        ProviderFactory.register("nvidia", NVIDIAProvider)
    except ImportError:
        logger.warning("NVIDIA provider not available")
    
    try:
        from services.ai.providers.google_provider import GoogleProvider
        ProviderFactory.register("google", GoogleProvider)
    except ImportError:
        logger.warning("Google provider not available")


# Initialize on import
initialize_providers()
