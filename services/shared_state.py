"""
Shared State Service

Communication bridge between Worker (Telegram bot) and Web (Dashboard).

Architecture:
    Worker (bot.py)          Web (web.py)
         ↓                        ↓
    Telegram API             HTTP Dashboard
         ↓                        ↓
    Shared State Service ←→ Shared State Service
         ↓                        ↓
         MongoDB / Supabase
              ↑
         Shared State Collection

The worker publishes:
- Bot status (online/offline/syncing)
- Indexing progress
- Active jobs
- Statistics
- Worker status

The web process reads:
- Bot status for dashboard
- Indexing progress for UI
- Statistics for charts

Both can read/write, but only worker updates bot status.
"""

import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
import asyncio

logger = logging.getLogger(__name__)


# =============================================================================
# Shared State Keys
# =============================================================================

class StateKeys:
    """Keys for shared state storage."""
    # Bot
    BOT_STATUS = "bot.status"
    BOT_UPTIME = "bot.uptime"
    BOT_USERNAME = "bot.username"
    BOT_START_TIME = "bot.start_time"

    # Indexing
    INDEX_ACTIVE_JOB = "index.active_job"
    INDEX_PROGRESS = "index.progress"
    INDEX_QUEUE = "index.queue"

    # Workers
    WORKERS_STATUS = "workers.status"
    WORKERS_ACTIVE = "workers.active"

    # Statistics
    STAT_USERS = "stat.users"
    STAT_FILES = "stat.files"
    STAT_SEARCHES_TODAY = "stat.searches_today"
    STAT_DOWNLOADS_TODAY = "stat.downloads_today"

    # Health
    HEALTH_MONGODB = "health.mongodb"
    HEALTH_CACHE = "health.cache"
    HEALTH_LAST_UPDATE = "health.last_update"


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class BotStatus:
    """Bot status information."""
    status: str = "offline"  # online, offline, syncing, error
    username: str = ""
    user_id: int = 0
    start_time: Optional[datetime] = None
    uptime_seconds: int = 0
    last_update: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if self.start_time:
            data["start_time"] = self.start_time.isoformat()
        if self.last_update:
            data["last_update"] = self.last_update.isoformat()
        return data


@dataclass
class IndexStatus:
    """Index status information."""
    active_job_id: Optional[str] = None
    channel_id: int = 0
    channel_name: str = ""
    progress_percent: float = 0.0
    processed: int = 0
    inserted: int = 0
    speed: float = 0.0
    eta: str = ""
    last_update: Optional[datetime] = None


@dataclass
class WorkerStatus:
    """Worker status information."""
    worker_id: str
    status: str  # running, idle, error
    current_task: str = ""
    processed_count: int = 0
    last_update: Optional[datetime] = None


# =============================================================================
# Shared State Service
# =============================================================================

class SharedStateService:
    """
    Service for managing shared state between worker and web processes.

    Uses MongoDB as primary storage with Supabase as optional backup.

    Usage (Worker):
        state = get_shared_state()

        # Called from bot.py
        await state.set_bot_status("online", username="CineBot")
        await state.update_index_progress(...)

    Usage (Web):
        state = get_shared_state()

        # Called from web.py / dashboard
        status = await state.get_bot_status()
        progress = await state.get_index_progress()
    """

    COLLECTION_NAME = "shared_state"

    def __init__(self):
        self._mongo = None
        self._supabase = None
        self._cache: Dict[str, Any] = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize connections to storage backends."""
        if self._initialized:
            return

        # MongoDB connection
        try:
            from database.client import get_client
            self._mongo = get_client()
        except Exception as e:
            logger.warning(f"MongoDB not available for shared state: {e}")

        # Supabase connection (optional)
        try:
            from core import get_config
            config = get_config()
            if config.database.supabase_url:
                from supabase import create_client
                self._supabase = create_client(
                    config.database.supabase_url,
                    config.database.supabase_service_role_key
                )
        except Exception as e:
            logger.warning(f"Supabase not available: {e}")

        self._initialized = True
        logger.info("Shared state service initialized")

    # =========================================================================
    # Bot Status (Updated by Worker, Read by Web)
    # =========================================================================

    async def set_bot_status(
        self,
        status: str,
        username: str = "",
        user_id: int = 0,
        start_time: Optional[datetime] = None
    ) -> None:
        """Set bot status (called by worker)."""
        bot_status = BotStatus(
            status=status,
            username=username,
            user_id=user_id,
            start_time=start_time or datetime.utcnow(),
            last_update=datetime.utcnow()
        )

        await self._set(StateKeys.BOT_STATUS, bot_status.to_dict())

        # Also update in Supabase for persistence
        await self._sync_to_supabase("bot_status", bot_status.to_dict())

        logger.debug(f"Bot status set: {status}")

    async def get_bot_status(self) -> Optional[BotStatus]:
        """Get bot status (called by web)."""
        data = await self._get(StateKeys.BOT_STATUS)

        if not data:
            return BotStatus(status="offline")

        return BotStatus(
            status=data.get("status", "offline"),
            username=data.get("username", ""),
            user_id=data.get("user_id", 0),
            start_time=_parse_datetime(data.get("start_time")),
            last_update=_parse_datetime(data.get("last_update")),
            uptime_seconds=int((datetime.utcnow() - _parse_datetime(data.get("start_time"))).total_seconds()) if data.get("start_time") else 0
        )

    async def update_bot_heartbeat(self) -> None:
        """Update bot heartbeat timestamp."""
        await self._set(StateKeys.HEALTH_LAST_UPDATE, datetime.utcnow().isoformat())

    # =========================================================================
    # Index Status
    # =========================================================================

    async def set_index_status(self, status: IndexStatus) -> None:
        """Set current index status."""
        data = status.to_dict() if hasattr(status, 'to_dict') else status
        await self._set(StateKeys.INDEX_PROGRESS, data)

    async def get_index_status(self) -> Optional[Dict[str, Any]]:
        """Get current index status."""
        return await self._get(StateKeys.INDEX_PROGRESS)

    # =========================================================================
    # Workers
    # =========================================================================

    async def set_worker_status(self, worker: WorkerStatus) -> None:
        """Update worker status."""
        workers = await self._get(StateKeys.WORKERS_STATUS) or {}
        workers[worker.worker_id] = worker.to_dict() if hasattr(worker, 'to_dict') else worker
        await self._set(StateKeys.WORKERS_STATUS, workers)

    async def get_workers(self) -> Dict[str, WorkerStatus]:
        """Get all worker statuses."""
        data = await self._get(StateKeys.WORKERS_STATUS) or {}
        return {
            wid: WorkerStatus(**w) if isinstance(w, dict) else w
            for wid, w in data.items()
        }

    # =========================================================================
    # Statistics
    # =========================================================================

    async def update_statistics(self, stats: Dict[str, Any]) -> None:
        """Update statistics from worker."""
        for key, value in stats.items():
            state_key = f"stat.{key}"
            await self._set(state_key, value)

    async def get_statistics(self) -> Dict[str, Any]:
        """Get all statistics."""
        stats = {}
        for key in [
            StateKeys.STAT_USERS,
            StateKeys.STAT_FILES,
            StateKeys.STAT_SEARCHES_TODAY,
            StateKeys.STAT_DOWNLOADS_TODAY
        ]:
            value = await self._get(key)
            if value is not None:
                stats[key.split(".")[-1]] = value
        return stats

    # =========================================================================
    # Health
    # =========================================================================

    async def set_health(self, component: str, status: str, details: str = "") -> None:
        """Set health status for a component."""
        key = f"health.{component}"
        await self._set(key, {
            "status": status,
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        })

    async def get_health(self) -> Dict[str, Any]:
        """Get all health statuses."""
        health = {}
        for component in ["mongodb", "cache", "telegram", "workers"]:
            key = f"health.{component}"
            data = await self._get(key)
            if data:
                health[component] = data
        return health

    # =========================================================================
    # Storage Operations
    # =========================================================================

    async def _set(self, key: str, value: Any) -> None:
        """Set a value in shared state."""
        # Update cache
        self._cache[key] = value

        # Persist to MongoDB
        if self._mongo:
            try:
                collection = self._mongo[self.COLLECTION_NAME]
                await collection.update_one(
                    {"_id": key},
                    {"$set": {"value": value, "updated_at": datetime.utcnow()}},
                    upsert=True
                )
            except Exception as e:
                logger.debug(f"Failed to persist {key} to MongoDB: {e}")

    async def _get(self, key: str) -> Optional[Any]:
        """Get a value from shared state."""
        # Check cache first
        if key in self._cache:
            return self._cache[key]

        # Read from MongoDB
        if self._mongo:
            try:
                collection = self._mongo[self.COLLECTION_NAME]
                doc = await collection.find_one({"_id": key})
                if doc:
                    self._cache[key] = doc.get("value")
                    return self._cache[key]
            except Exception as e:
                logger.debug(f"Failed to read {key} from MongoDB: {e}")

        return None

    async def _sync_to_supabase(self, table: str, data: Dict) -> None:
        """Sync data to Supabase for persistence."""
        if not self._supabase:
            return

        try:
            self._supabase.table(table).upsert(
                data,
                on_conflict="id"
            ).execute()
        except Exception as e:
            logger.debug(f"Supabase sync failed: {e}")


def _parse_datetime(value: Any) -> Optional[datetime]:
    """Parse datetime from string or return as-is."""
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return None
    return None


# =============================================================================
# Global Instance
# =============================================================================

_shared_state: Optional[SharedStateService] = None


def get_shared_state() -> SharedStateService:
    """Get or create the global SharedStateService instance."""
    global _shared_state
    if _shared_state is None:
        _shared_state = SharedStateService()
    return _shared_state


async def initialize_shared_state() -> SharedStateService:
    """Initialize and return shared state service."""
    state = get_shared_state()
    await state.initialize()
    return state
