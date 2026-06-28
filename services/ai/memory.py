"""
AI Memory System - Persistent conversation storage with MongoDB.
Enables multi-turn conversations and context awareness.
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Manages conversation history and context."""
    
    def __init__(self, db_client, user_id: str, conversation_id: Optional[str] = None):
        """Initialize memory for a conversation."""
        self.db_client = db_client
        self.user_id = user_id
        self.conversation_id = conversation_id or str(ObjectId())
        self.db = db_client.cine3600
        self.collection = self.db.ai_conversations
        self.max_history = 50  # Keep last 50 messages
    
    async def add_message(
        self,
        role: str,
        content: str,
        model: str,
        tokens_used: int = 0,
        cost: float = 0.0
    ) -> None:
        """Add a message to conversation history."""
        try:
            message = {
                "conversation_id": self.conversation_id,
                "user_id": self.user_id,
                "role": role,
                "content": content,
                "model": model,
                "tokens_used": tokens_used,
                "cost": cost,
                "timestamp": datetime.utcnow(),
            }
            
            await self.collection.insert_one(message)
            
            # Cleanup old messages if exceeding max
            await self._cleanup_old_messages()
        except Exception as e:
            logger.error(f"Failed to add message to memory: {e}")
    
    async def get_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversation history."""
        try:
            messages = await self.collection.find(
                {"conversation_id": self.conversation_id},
                {"_id": 0, "timestamp": 0}
            ).sort("timestamp", -1).limit(limit).to_list(None)
            
            return list(reversed(messages))
        except Exception as e:
            logger.error(f"Failed to retrieve conversation history: {e}")
            return []
    
    async def get_context(self, limit: int = 5) -> str:
        """Get formatted context from recent messages."""
        history = await self.get_history(limit * 2)
        
        context_lines = []
        for msg in history:
            role = "User" if msg["role"] == "user" else "Assistant"
            context_lines.append(f"{role}: {msg['content'][:200]}...")
        
        return "\n".join(context_lines)
    
    async def clear(self) -> None:
        """Clear conversation history."""
        try:
            await self.collection.delete_many({"conversation_id": self.conversation_id})
        except Exception as e:
            logger.error(f"Failed to clear conversation: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        try:
            messages = await self.collection.find(
                {"conversation_id": self.conversation_id}
            ).to_list(None)
            
            total_tokens = sum(m.get("tokens_used", 0) for m in messages)
            total_cost = sum(m.get("cost", 0) for m in messages)
            
            return {
                "total_messages": len(messages),
                "total_tokens": total_tokens,
                "total_cost": total_cost,
                "conversation_id": self.conversation_id,
                "user_id": self.user_id,
            }
        except Exception as e:
            logger.error(f"Failed to get conversation stats: {e}")
            return {}
    
    async def _cleanup_old_messages(self) -> None:
        """Remove oldest messages if exceeding limit."""
        try:
            count = await self.collection.count_documents(
                {"conversation_id": self.conversation_id}
            )
            
            if count > self.max_history:
                # Get the oldest message to delete
                oldest = await self.collection.find_one(
                    {"conversation_id": self.conversation_id},
                    sort=[("timestamp", 1)]
                )
                
                if oldest:
                    await self.collection.delete_one({"_id": oldest["_id"]})
        except Exception as e:
            logger.error(f"Failed to cleanup old messages: {e}")


class ShortTermMemory:
    """Fast, in-memory cache for active conversations."""
    
    def __init__(self, ttl_seconds: int = 3600):
        """Initialize short-term memory."""
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
    
    def set(self, key: str, value: Any) -> None:
        """Store value with TTL."""
        self.cache[key] = {
            "value": value,
            "expires_at": datetime.utcnow() + timedelta(seconds=self.ttl)
        }
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve value if not expired."""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if datetime.utcnow() > entry["expires_at"]:
            del self.cache[key]
            return None
        
        return entry["value"]
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        self.cache.pop(key, None)
    
    def clear(self) -> None:
        """Clear all cached values."""
        self.cache.clear()
    
    def cleanup_expired(self) -> None:
        """Remove expired entries."""
        now = datetime.utcnow()
        expired_keys = [
            k for k, v in self.cache.items()
            if now > v["expires_at"]
        ]
        for k in expired_keys:
            del self.cache[k]
