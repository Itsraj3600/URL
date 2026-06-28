import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorCollection

logger = logging.getLogger(__name__)

class IndexEventDB:
    """Manages index lifecycle events for timeline visualization."""
    
    collection: Optional[AsyncIOMotorCollection] = None
    
    @classmethod
    async def initialize(cls, client: AsyncIOMotorClient) -> None:
        """Initialize the index_events collection with proper indexes."""
        db = client.cine_db
        cls.collection = db.index_events
        
        # Create indexes
        await cls.collection.create_index("job_id")
        await cls.collection.create_index("timestamp")
        await cls.collection.create_index([("job_id", 1), ("timestamp", 1)])
        await cls.collection.create_index("event")
        
        # TTL index - keep events for 2 years
        await cls.collection.create_index("created_at", expireAfterSeconds=63072000)
        
        logger.info("Index events collection initialized")
    
    @classmethod
    async def log_event(
        cls,
        job_id: str,
        event: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log a significant lifecycle event."""
        if not cls.collection:
            raise RuntimeError("Collection not initialized")
        
        event_doc = {
            "job_id": job_id,
            "event": event,
            "timestamp": datetime.utcnow(),
            "created_at": datetime.utcnow(),
            "metadata": metadata or {}
        }
        
        await cls.collection.insert_one(event_doc)
        logger.debug(f"Logged event: {job_id} -> {event}")
    
    @classmethod
    async def get_job_timeline(cls, job_id: str) -> List[Dict[str, Any]]:
        """Get all events for a job in chronological order."""
        if not cls.collection:
            raise RuntimeError("Collection not initialized")
        
        events = []
        async for event in cls.collection.find({"job_id": job_id}).sort("timestamp", 1):
            event.pop("_id", None)
            events.append(event)
        
        return events
    
    @classmethod
    async def get_recent_events(cls, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent events across all jobs."""
        if not cls.collection:
            raise RuntimeError("Collection not initialized")
        
        events = []
        async for event in cls.collection.find().sort("timestamp", -1).limit(limit):
            event.pop("_id", None)
            events.append(event)
        
        return events
