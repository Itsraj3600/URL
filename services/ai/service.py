"""
AI Service - Main facade integrating all AI modules.
Provides unified interface for bot and dashboard integration.
"""

import logging
from typing import Optional, AsyncIterator, Dict, Any, List

from services.ai.provider_factory import ProviderFactory
from services.ai.memory import ConversationMemory, ShortTermMemory
from services.ai.streaming import StreamingService
from services.ai.search_assistant import SearchAssistant
from services.ai.moderation import ModerationManager, ContentFlagLevel
from services.ai.routing import IntelligentRouter, AdminAssistant

logger = logging.getLogger(__name__)


class CINEAIService:
    """Main AI Intelligence Service for CINE3600."""
    
    def __init__(self, db_client):
        """Initialize AI service."""
        self.db = db_client
        self.provider_factory = ProviderFactory()
        self.streaming = StreamingService()
        self.search = SearchAssistant()
        self.moderation = ModerationManager(db_client)
        self.router = IntelligentRouter()
        self.short_memory = ShortTermMemory()
        self.admin = AdminAssistant(self.provider_factory.get_default_provider())
    
    async def answer_query(
        self,
        user_id: str,
        query: str,
        use_streaming: bool = False,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Answer user query with AI."""
        
        # Check moderation
        flag_level, reason = await self.moderation.check_content(query)
        if flag_level == ContentFlagLevel.BLOCKED:
            return {"error": reason, "blocked": True}
        
        # Check cost limits
        allowed, cost_reason = await self.moderation.check_user_cost(user_id)
        if not allowed:
            return {"error": cost_reason, "limit_exceeded": True}
        
        # Get best model for query complexity
        model = self.router.get_best_model("balanced")
        provider = self.provider_factory.get_provider("openai") if "gpt" in model else self.provider_factory.get_default_provider()
        
        # Create memory
        memory = ConversationMemory(self.db, user_id)
        await memory.add_message(role="user", content=query, model=model)
        
        if use_streaming:
            return await self._stream_answer(query, provider, memory, system_prompt)
        else:
            return await self._direct_answer(query, provider, memory, system_prompt)
    
    async def _direct_answer(
        self,
        query: str,
        provider,
        memory: ConversationMemory,
        system_prompt: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate direct response."""
        
        try:
            response = await provider.generate(
                prompt=query,
                system_prompt=system_prompt,
                temperature=0.7,
                max_tokens=1024
            )
            
            await memory.add_message(
                role="assistant",
                content=response.content,
                model=response.model,
                tokens_used=response.tokens_used,
            )
            
            await self.moderation.log_usage(
                user_id=memory.user_id,
                model=response.model,
                tokens_used=response.tokens_used,
                cost=response.cost,
                provider=response.provider
            )
            
            return {
                "response": response.content,
                "model": response.model,
                "tokens": response.tokens_used,
                "cost": response.cost,
                "conversation_id": memory.conversation_id,
            }
        except Exception as e:
            logger.error(f"Error generating answer: {e}")
            return {"error": str(e)}
    
    async def _stream_answer(
        self,
        query: str,
        provider,
        memory: ConversationMemory,
        system_prompt: Optional[str] = None,
    ) -> AsyncIterator[str]:
        """Stream response tokens."""
        
        async for chunk in self.streaming.stream_response(
            prompt=query,
            system_prompt=system_prompt,
            memory=memory,
        ):
            yield chunk
    
    async def search_with_ai(
        self,
        user_id: str,
        query: str,
        search_results: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Enhance search with AI recommendations."""
        
        try:
            # Refine query
            refined = await self.search.refine_query(query)
            
            # Get recommendations
            recommendations = await self.search.get_recommendations(
                search_results=search_results
            )
            
            return {
                "original_query": query,
                "refined_query": refined,
                "recommendations": recommendations,
            }
        except Exception as e:
            logger.error(f"AI search error: {e}")
            return {"error": str(e)}
    
    async def get_admin_report(self) -> Dict[str, Any]:
        """Generate admin system report."""
        
        try:
            metrics = {
                "total_conversations": await self._count_conversations(),
                "active_users": await self._count_active_users(),
                "total_api_cost": await self._get_total_cost(),
                "models_used": await self._get_models_used(),
            }
            
            report = await self.admin.generate_report(metrics)
            
            return {
                "metrics": metrics,
                "report": report,
                "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Admin report error: {e}")
            return {"error": str(e)}
    
    async def _count_conversations(self) -> int:
        """Count total conversations."""
        try:
            return await self.db.cine3600.ai_conversations.count_documents({})
        except:
            return 0
    
    async def _count_active_users(self) -> int:
        """Count active users."""
        try:
            result = await self.db.cine3600.ai_conversations.distinct("user_id")
            return len(result)
        except:
            return 0
    
    async def _get_total_cost(self) -> float:
        """Get total API cost."""
        try:
            result = await self.db.cine3600.ai_costs.aggregate([
                {"$group": {"_id": None, "total": {"$sum": "$cost"}}}
            ]).to_list(None)
            return result[0]["total"] if result else 0.0
        except:
            return 0.0
    
    async def _get_models_used(self) -> List[str]:
        """Get list of models used."""
        try:
            result = await self.db.cine3600.ai_conversations.distinct("model")
            return result
        except:
            return []
