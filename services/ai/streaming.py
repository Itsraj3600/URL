"""
Streaming Service - Real-time token streaming for fast response delivery.
"""

import logging
import asyncio
from typing import AsyncIterator, Optional

from services.ai.provider_factory import ProviderFactory
from services.ai.memory import ConversationMemory

logger = logging.getLogger(__name__)


class StreamingService:
    """Handles streaming AI responses."""
    
    def __init__(self):
        """Initialize streaming service."""
        self.factory = ProviderFactory()
    
    async def stream_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        provider: str = "default",
        temperature: float = 0.7,
        max_tokens: int = 1024,
        memory: Optional[ConversationMemory] = None,
    ) -> AsyncIterator[str]:
        """Stream a response from the selected provider."""
        
        if provider == "default":
            ai_provider = self.factory.get_default_provider()
        elif provider == "fast":
            ai_provider = self.factory.get_provider("groq")
        elif provider == "reasoning":
            ai_provider = self.factory.get_provider("openai")
        else:
            ai_provider = self.factory.get_provider(provider)
        
        if not ai_provider:
            yield "Error: AI provider not available"
            return
        
        try:
            full_response = ""
            
            async for chunk in ai_provider.stream(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=temperature,
                max_tokens=max_tokens,
            ):
                full_response += chunk
                yield chunk
            
            # Store in memory after streaming completes
            if memory:
                tokens_estimate = len(full_response.split()) * 1.3  # Rough estimate
                await memory.add_message(
                    role="assistant",
                    content=full_response,
                    model=ai_provider.default_model,
                    tokens_used=int(tokens_estimate)
                )
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            yield f"Error: {str(e)}"
    
    async def stream_search_results(
        self,
        query: str,
        search_results: list,
        memory: Optional[ConversationMemory] = None,
    ) -> AsyncIterator[str]:
        """Stream formatted search results with AI enhancement."""
        
        ai_provider = self.factory.get_provider("groq")  # Fast provider for formatting
        if not ai_provider:
            yield "Error: AI provider not available"
            return
        
        # Format search results
        results_text = self._format_search_results(search_results)
        
        prompt = f"""Given these search results for "{query}", provide a concise summary:

{results_text}

Highlight the most relevant results and provide insights."""
        
        try:
            async for chunk in ai_provider.stream(prompt=prompt, max_tokens=512):
                yield chunk
        except Exception as e:
            logger.error(f"Search streaming error: {e}")
    
    def _format_search_results(self, results: list) -> str:
        """Format search results for context."""
        formatted = []
        for i, result in enumerate(results[:5], 1):
            title = result.get("title", "Untitled")
            relevance = result.get("relevance_score", 0.0)
            formatted.append(f"{i}. {title} (Relevance: {relevance:.2f})")
        
        return "\n".join(formatted)
