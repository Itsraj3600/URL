"""
Event Bus System

Decoupled pub/sub event system for CINE3600.

Instead of services calling each other directly:

    IndexService.finished()
        ↓
    StatsService.record()
    NotificationService.notify()
    DashboardService.update()
    LogService.log()

Services publish events:

    event_bus.publish("index.finished", job_id="abc", files=500)

Subscribers react independently:

    @event_bus.on("index.finished")
    async def on_index_finished(event):
        stats.record(event.data)

    @event_bus.on("index.finished")
    async def notify_admins(event):
        notifications.send(...)

Benefits:
- Loose coupling
- Easy to add new subscribers
- Easier testing
- Better scalability
"""

import logging
import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set
from collections import defaultdict
import inspect

logger = logging.getLogger(__name__)


# =============================================================================
# Event Types
# =============================================================================

class Events:
    """Event type constants for type safety."""

    # Indexing Events
    INDEX_STARTED = "index.started"
    INDEX_PROGRESS = "index.progress"
    INDEX_PAUSED = "index.paused"
    INDEX_RESUMED = "index.resumed"
    INDEX_COMPLETED = "index.completed"
    INDEX_FAILED = "index.failed"
    INDEX_CANCELLED = "index.cancelled"
    BATCH_PROCESSED = "index.batch_processed"

    # Search Events
    SEARCH_PERFORMED = "search.performed"
    SEARCH_FAILED = "search.failed"
    SEARCH_SLOW = "search.slow"
    CACHE_HIT = "search.cache_hit"
    CACHE_MISS = "search.cache_miss"

    # User Events
    USER_JOINED = "user.joined"
    USER_BANNED = "user.banned"
    USER_UNBANNED = "user.unbanned"
    USER_PREMIUM_GRANTED = "user.premium_granted"
    USER_PREMIUM_EXPIRED = "user.premium_expired"

    # Channel Events
    CHANNEL_ADDED = "channel.added"
    CHANNEL_REMOVED = "channel.removed"
    CHANNEL_SYNC_STARTED = "channel.sync_started"
    CHANNEL_SYNC_COMPLETED = "channel.sync_completed"

    # System Events
    WORKER_STARTED = "worker.started"
    WORKER_STOPPED = "worker.stopped"
    WORKER_ERROR = "worker.error"
    DB_CONNECTED = "database.connected"
    DB_DISCONNECTED = "database.disconnected"
    DB_ERROR = "database.error"
    FLOOD_WAIT = "telegram.flood_wait"
    API_ERROR = "api.error"

    # Monitoring Events
    HEALTH_CHECK = "monitoring.health_check"
    HIGH_CPU = "monitoring.high_cpu"
    HIGH_MEMORY = "monitoring.high_memory"
    DISK_FULL = "monitoring.disk_full"

    # Cache Events
    CACHE_CLEARED = "cache.cleared"
    CACHE_WARMED = "cache.warmed"


@dataclass
class Event:
    """Represents a single event."""
    type: str
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    source: str = ""
    priority: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "type": self.type,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "priority": self.priority
        }


# =============================================================================
# Event Bus Implementation
# =============================================================================

class EventBus:
    """
    Asynchronous pub/sub event bus.

    Usage:
        # Get instance
        bus = get_event_bus()

        # Subscribe to events
        @bus.on(Events.INDEX_COMPLETED)
        async def handle_index_complete(event):
            print(f"Indexed {event.data['files']} files")

        # Publish events
        await bus.publish(Events.INDEX_COMPLETED, files=500, job_id="abc")

        # One-time handlers
        bus.once(Events.DB_CONNECTED, on_first_connect)

        # Remove handlers
        bus.off(Events.INDEX_COMPLETED, handle_index_complete)
    """

    def __init__(self):
        # Map of event type -> list of handlers
        self._handlers: Dict[str, List[Callable]] = defaultdict(list)

        # One-time handlers
        self._once_handlers: Dict[str, List[Callable]] = defaultdict(list)

        # Event history for replay
        self._history: List[Event] = []
        self._max_history = 1000

        # Middleware
        self._middleware: List[Callable] = []

        # Async queue for thread-safe publishing
        self._queue: asyncio.Queue = asyncio.Queue()
        self._processing = False

    # =========================================================================
    # Subscription
    # =========================================================================

    def on(self, event_type: str, priority: int = 0) -> Callable:
        """
        Decorator to subscribe to an event type.

        Args:
            event_type: Event type to listen for
            priority: Handler priority (higher = called first)

        Returns:
            Decorator function

        Usage:
            @bus.on("index.completed")
            async def handler(event):
                print(event.data)
        """
        def decorator(func: Callable) -> Callable:
            handler = EventBus._wrap_handler(func)
            handler._priority = priority
            self._handlers[event_type].append(handler)

            # Sort by priority
            self._handlers[event_type].sort(
                key=lambda h: getattr(h, '_priority', 0),
                reverse=True
            )

            logger.debug(f"Registered handler for '{event_type}': {func.__name__}")
            return func
        return decorator

    def once(self, event_type: str) -> Callable:
        """
        Decorator for one-time event subscription.

        Handler is removed after first invocation.

        Usage:
            @bus.once("database.connected")
            async def on_first_connect(event):
                initialize_services()
        """
        def decorator(func: Callable) -> Callable:
            handler = EventBus._wrap_handler(func)
            self._once_handlers[event_type].append(handler)
            return func
        return decorator

    def subscribe(self, event_type: str, handler: Callable, priority: int = 0) -> None:
        """
        Programmatic subscription (non-decorator).

        Args:
            event_type: Event type
            handler: Handler function
            priority: Handler priority
        """
        wrapped = EventBus._wrap_handler(handler)
        wrapped._priority = priority
        self._handlers[event_type].append(wrapped)
        self._handlers[event_type].sort(
            key=lambda h: getattr(h, '_priority', 0),
            reverse=True
        )

    def off(self, event_type: str, handler: Callable) -> bool:
        """
        Unsubscribe from an event.

        Args:
            event_type: Event type
            handler: Original handler function

        Returns:
            True if handler was removed
        """
        removed = False

        # Remove from regular handlers
        for i, h in enumerate(self._handlers.get(event_type, [])):
            if getattr(h, '_original', None) == handler:
                self._handlers[event_type].pop(i)
                removed = True
                break

        # Remove from once handlers
        for i, h in enumerate(self._once_handlers.get(event_type, [])):
            if getattr(h, '_original', None) == handler:
                self._once_handlers[event_type].pop(i)
                removed = True
                break

        return removed

    # =========================================================================
    # Publishing
    # =========================================================================

    async def publish(
        self,
        event_type: str,
        source: str = "",
        priority: int = 0,
        **data: Any
    ) -> None:
        """
        Publish an event.

        Args:
            event_type: Event type
            source: Event source
            priority: Event priority
            **data: Event data
        """
        event = Event(
            type=event_type,
            data=data,
            source=source,
            priority=priority
        )

        # Add to history
        self._history.append(event)
        if len(self._history) > self._max_history:
            self._history = self._history[-self._max_history:]

        # Run middleware
        for middleware in self._middleware:
            try:
                result = middleware(event)
                if inspect.isawaitable(result):
                    await result
            except Exception as e:
                logger.error(f"Middleware error: {e}")

        # Get all handlers
        handlers = self._handlers.get(event_type, [])
        once_handlers = self._once_handlers.pop(event_type, [])

        # Execute handlers
        all_handlers = handlers + once_handlers

        for handler in all_handlers:
            try:
                result = handler(event)
                if inspect.isawaitable(result):
                    await result
            except Exception as e:
                logger.error(f"Event handler error for '{event_type}': {e}")

        logger.debug(f"Published event '{event_type}' to {len(all_handlers)} handlers")

    def publish_sync(self, event_type: str, source: str = "", **data: Any) -> None:
        """
        Publish event synchronously (fire and forget).

        Creates task for async processing.
        """
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self.publish(event_type, source=source, **data))
        except RuntimeError:
            # No running loop, create new one
            asyncio.run(self.publish(event_type, source=source, **data))

    # =========================================================================
    # Middleware
    # =========================================================================

    def use(self, middleware: Callable) -> None:
        """
        Add middleware for all events.

        Args:
            middleware: Function that receives Event

        Usage:
            @bus.use
            def log_all_events(event):
                logging.info(f"Event: {event.type}")
        """
        self._middleware.append(middleware)

    # =========================================================================
    # History & Replay
    # =========================================================================

    def get_history(self, event_type: Optional[str] = None, limit: int = 100) -> List[Event]:
        """
        Get event history.

        Args:
            event_type: Filter by type (optional)
            limit: Max events to return

        Returns:
            List of events
        """
        events = self._history
        if event_type:
            events = [e for e in events if e.type == event_type]
        return events[-limit:]

    def clear_history(self) -> int:
        """Clear event history. Returns count cleared."""
        count = len(self._history)
        self._history.clear()
        return count

    # =========================================================================
    # Utilities
    # =========================================================================

    @staticmethod
    def _wrap_handler(func: Callable) -> Callable:
        """Wrap handler to store original reference."""
        async def wrapper(event: Event) -> Any:
            if inspect.iscoroutinefunction(func):
                return await func(event)
            return func(event)
        wrapper._original = func
        return wrapper

    def handlers_for(self, event_type: str) -> List[Callable]:
        """Get handlers for an event type."""
        return self._handlers.get(event_type, []) + self._once_handlers.get(event_type, [])

    def event_types(self) -> Set[str]:
        """Get all registered event types."""
        return set(self._handlers.keys()) | set(self._once_handlers.keys())


# =============================================================================
# Global Instance
# =============================================================================

_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get or create global EventBus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


def reset_event_bus() -> None:
    """Reset global EventBus instance (for testing)."""
    global _event_bus
    _event_bus = None
