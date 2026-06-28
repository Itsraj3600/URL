"""
Base AI Provider Abstract Class - Foundation for all LLM integrations.
Defines the interface that all providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator, List, Dict, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AIMessage:
    """Represents an AI message in conversation."""
    role: str  # "user", "assistant", "system"
    content: str
    model: Optional[str] = None
    tokens_used: Optional[int] = None
    cost: Optional[float] = None


@dataclass
class AIResponse:
    """Response from AI provider."""
    content: str
    model: str
    tokens_used: int
    cost: float
    provider: str
    reasoning: Optional[str] = None


class BaseAIProvider(ABC):
    """Abstract base class for AI providers."""
    
    def __init__(self, api_key: str, default_model: str):
        """Initialize provider with API key and default model."""
        self.api_key = api_key
        self.default_model = default_model
        self.name = self.__class__.__name__
        self.conversation_history: List[AIMessage] = []
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> AIResponse:
        """Generate a single response from the model."""
        pass
    
    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream response tokens as they arrive."""
        pass
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs
    ) -> AIResponse:
        """Process a chat/conversation."""
        pass
    
    @abstractmethod
    def calculate_cost(self, tokens_used: int, model: str) -> float:
        """Calculate API cost for tokens used."""
        pass
    
    async def add_to_history(self, role: str, content: str) -> None:
        """Add message to conversation history."""
        self.conversation_history.append(
            AIMessage(role=role, content=content, model=self.default_model)
        )
    
    def clear_history(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
    
    def get_history(self) -> List[AIMessage]:
        """Get conversation history."""
        return self.conversation_history.copy()
