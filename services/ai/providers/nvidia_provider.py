"""
NVIDIA Provider - Enterprise-grade LLM integration with Nemotron models.
Supports streaming, reasoning, and low-latency inference.
"""

import logging
from typing import Optional, AsyncIterator, List, Dict, Any
from os import environ
import httpx
import json

from services.ai.base_provider import BaseAIProvider, AIResponse, AIMessage
from services.ai.models_config import get_model_config, calculate_model_cost

logger = logging.getLogger(__name__)


class NVIDIAProvider(BaseAIProvider):
    """NVIDIA Nemotron model provider."""
    
    API_BASE = "https://integrate.api.nvidia.com/v1"
    DEFAULT_MODEL = "nvidia/nemotron-4-340b-instruct"
    
    def __init__(self):
        """Initialize NVIDIA provider."""
        api_key = environ.get("NVIDIA_API_KEY")
        if not api_key:
            logger.warning("NVIDIA_API_KEY not set. Provider will not function.")
        
        super().__init__(api_key or "", self.DEFAULT_MODEL)
        self.client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
    
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
        if not self.api_key:
            raise ValueError("NVIDIA API key not configured")
        
        payload = {
            "model": kwargs.get("model", self.DEFAULT_MODEL),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": kwargs.get("top_p", 0.95),
            "frequency_penalty": kwargs.get("frequency_penalty", 0.0),
            "presence_penalty": kwargs.get("presence_penalty", 0.0),
        }
        
        try:
            response = await self.client.post(
                f"{self.API_BASE}/chat/completions",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens", 0)
            
            cost = self.calculate_cost(tokens_used, payload["model"])
            
            await self.add_to_history("user", messages[-1]["content"])
            await self.add_to_history("assistant", content)
            
            return AIResponse(
                content=content,
                model=payload["model"],
                tokens_used=tokens_used,
                cost=cost,
                provider="nvidia"
            )
        except Exception as e:
            logger.error(f"NVIDIA API error: {e}")
            raise
    
    async def _stream_chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> AsyncIterator[str]:
        """Internal streaming chat method."""
        if not self.api_key:
            raise ValueError("NVIDIA API key not configured")
        
        payload = {
            "model": kwargs.get("model", self.DEFAULT_MODEL),
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.API_BASE}/chat/completions",
                json=payload,
                timeout=30.0
            ) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            chunk = json.loads(line[6:])
                            delta = chunk["choices"][0]["delta"]
                            
                            if "content" in delta:
                                yield delta["content"]
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"NVIDIA streaming error: {e}")
            raise
    
    def calculate_cost(self, tokens_used: int, model: str) -> float:
        """Calculate API cost."""
        config = get_model_config(model)
        if not config:
            return 0.0
        
        # NVIDIA charges equally for input and output
        return (tokens_used / 1000) * config.cost_per_1k_input
    
    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
