"""
OpenAI Provider - Integration with GPT-4 and other OpenAI models.
"""

import logging
from typing import Optional, AsyncIterator, List, Dict
from os import environ

from services.ai.base_provider import BaseAIProvider, AIResponse
from services.ai.models_config import get_model_config

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseAIProvider):
    """OpenAI model provider."""
    
    DEFAULT_MODEL = "gpt-4o"
    
    def __init__(self):
        """Initialize OpenAI provider."""
        api_key = environ.get("OPENAI_API_KEY")
        if not api_key:
            logger.warning("OPENAI_API_KEY not set. Provider will not function.")
        
        super().__init__(api_key or "", self.DEFAULT_MODEL)
        
        try:
            from openai import AsyncOpenAI
            self.client = AsyncOpenAI(api_key=self.api_key)
        except ImportError:
            logger.error("OpenAI package not installed. Install with: pip install openai")
            self.client = None
    
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> AIResponse:
        """Generate a single response."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        return await self.chat(messages, temperature, max_tokens, **kwargs)
    
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream response tokens."""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        async for chunk in self._stream_chat(messages, temperature, max_tokens, **kwargs):
            yield chunk
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> AIResponse:
        """Process a chat request."""
        if not self.client:
            raise ValueError("OpenAI client not initialized")
        
        model = kwargs.get("model", self.DEFAULT_MODEL)
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            
            content = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if response.usage else 0
            
            cost = self.calculate_cost(tokens_used, model)
            
            await self.add_to_history("user", messages[-1]["content"])
            await self.add_to_history("assistant", content)
            
            return AIResponse(
                content=content,
                model=model,
                tokens_used=tokens_used,
                cost=cost,
                provider="openai"
            )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def _stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> AsyncIterator[str]:
        """Internal streaming chat method."""
        if not self.client:
            raise ValueError("OpenAI client not initialized")
        
        model = kwargs.get("model", self.DEFAULT_MODEL)
        
        try:
            async with await self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
            ) as response:
                async for chunk in response:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise
    
    def calculate_cost(self, tokens_used: int, model: str) -> float:
        """Calculate API cost."""
        config = get_model_config(model)
        if not config:
            return 0.0
        
        # OpenAI charges separately for input and output
        # Using average for simplicity (actual should track separately)
        avg_cost = (config.cost_per_1k_input + config.cost_per_1k_output) / 2
        return (tokens_used / 1000) * avg_cost
