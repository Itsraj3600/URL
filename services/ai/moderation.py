"""
Moderation System - Content safety and cost control with flagging.
"""

import logging
from typing import Dict, Any, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class ContentFlagLevel(Enum):
    SAFE = "safe"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKED = "blocked"


class ModerationManager:
    """Manages content safety and compliance."""
    
    # Cost thresholds (in USD)
    DAILY_LIMIT = 100.0
    WEEKLY_LIMIT = 500.0
    MONTHLY_LIMIT = 2000.0
    
    # Blocked content patterns
    BLOCKED_PATTERNS = [
        "credit card",
        "social security",
        "api key",
        "password",
    ]
    
    def __init__(self, db_client):
        """Initialize moderation manager."""
        self.db_client = db_client
        self.db = db_client.cine3600
        self.costs_collection = self.db.ai_costs
        self.flags_collection = self.db.ai_content_flags
    
    async def check_content(self, content: str) -> Tuple[ContentFlagLevel, Optional[str]]:
        """Check if content is safe and appropriate."""
        
        # Check for blocked patterns
        content_lower = content.lower()
        for pattern in self.BLOCKED_PATTERNS:
            if pattern in content_lower:
                return ContentFlagLevel.BLOCKED, f"Contains blocked content: {pattern}"
        
        # Check content length
        if len(content) > 10000:
            return ContentFlagLevel.MEDIUM, "Content exceeds recommended length"
        
        # Check for excessive profanity or abuse
        if self._contains_harmful_content(content):
            return ContentFlagLevel.HIGH, "Contains potentially harmful content"
        
        return ContentFlagLevel.SAFE, None
    
    async def check_user_cost(self, user_id: str) -> Tuple[bool, Optional[str]]:
        """Check if user is within cost limits."""
        
        daily_cost = await self._get_user_cost(user_id, period="day")
        weekly_cost = await self._get_user_cost(user_id, period="week")
        monthly_cost = await self._get_user_cost(user_id, period="month")
        
        if daily_cost >= self.DAILY_LIMIT:
            return False, "Daily cost limit exceeded"
        if weekly_cost >= self.WEEKLY_LIMIT:
            return False, "Weekly cost limit exceeded"
        if monthly_cost >= self.MONTHLY_LIMIT:
            return False, "Monthly cost limit exceeded"
        
        return True, None
    
    async def log_usage(
        self,
        user_id: str,
        model: str,
        tokens_used: int,
        cost: float,
        provider: str
    ) -> None:
        """Log AI usage for tracking and billing."""
        
        try:
            usage = {
                "user_id": user_id,
                "model": model,
                "provider": provider,
                "tokens_used": tokens_used,
                "cost": cost,
                "timestamp": __import__("datetime").datetime.utcnow(),
            }
            
            await self.costs_collection.insert_one(usage)
        except Exception as e:
            logger.error(f"Failed to log usage: {e}")
    
    async def flag_content(
        self,
        user_id: str,
        content: str,
        level: ContentFlagLevel,
        reason: str
    ) -> None:
        """Flag content for review."""
        
        try:
            flag = {
                "user_id": user_id,
                "content": content[:500],  # Store excerpt
                "level": level.value,
                "reason": reason,
                "timestamp": __import__("datetime").datetime.utcnow(),
            }
            
            await self.flags_collection.insert_one(flag)
        except Exception as e:
            logger.error(f"Failed to flag content: {e}")
    
    async def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get user AI usage statistics."""
        
        try:
            daily = await self._get_user_cost(user_id, "day")
            weekly = await self._get_user_cost(user_id, "week")
            monthly = await self._get_user_cost(user_id, "month")
            total = await self._get_user_cost(user_id, "all")
            
            return {
                "daily_cost": daily,
                "daily_limit": self.DAILY_LIMIT,
                "weekly_cost": weekly,
                "weekly_limit": self.WEEKLY_LIMIT,
                "monthly_cost": monthly,
                "monthly_limit": self.MONTHLY_LIMIT,
                "total_cost": total,
            }
        except Exception as e:
            logger.error(f"Failed to get user stats: {e}")
            return {}
    
    async def _get_user_cost(self, user_id: str, period: str) -> float:
        """Calculate user cost for period."""
        
        try:
            from datetime import datetime, timedelta
            
            if period == "day":
                start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "week":
                today = datetime.utcnow()
                start = today - timedelta(days=today.weekday())
                start = start.replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "month":
                today = datetime.utcnow()
                start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            else:
                start = datetime.min
            
            result = await self.costs_collection.aggregate([
                {"$match": {"user_id": user_id, "timestamp": {"$gte": start}}},
                {"$group": {"_id": None, "total": {"$sum": "$cost"}}},
            ]).to_list(None)
            
            return result[0]["total"] if result else 0.0
        except Exception as e:
            logger.error(f"Failed to get user cost: {e}")
            return 0.0
    
    def _contains_harmful_content(self, content: str) -> bool:
        """Check for harmful content patterns."""
        harmful_words = [
            "illegal",
            "violence",
            "abuse",
        ]
        
        content_lower = content.lower()
        return any(word in content_lower for word in harmful_words)
