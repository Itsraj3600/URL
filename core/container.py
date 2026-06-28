"""
Service Container

Dependency injection container for CINE3600.

Instead of:

    search = SearchService()
    stats = StatsService()
    cache = CacheService()

    # In every file:

    search = get_search_service()
    stats = get_stats_service()

Use:

    container = get_container()

    # Register services
    container.register("search", SearchService)
    container.register("stats", StatsService)
    container.register("cache", CacheService, singleton=True)

    # Get services
    search = container.get("search")
    stats = container.get("stats")

    # Or inject by type annotation
    @inject
    class MyHandler:
        def __init__(self, search: SearchService):
            self.search = search

Benefits:
- Single point of configuration
- Easier testing (swap implementations)
- Lazy initialization
- Singleton management
"""

import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar, Union, get_type_hints
from dataclasses import dataclass, field
from enum import Enum
import inspect

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceLifecycle(str, Enum):
    """Service lifecycle options."""
    SINGLETON = "singleton"      # One instance for all requests
    TRANSIENT = "transient"      # New instance every request
    LAZY = "lazy"               # Created on first access


@dataclass
class ServiceRegistration:
    """Registration info for a service."""
    name: str
    factory: Union[Type, Callable]
    lifecycle: ServiceLifecycle = ServiceLifecycle.SINGLETON
    instance: Optional[Any] = None
    initialized: bool = False


class ServiceContainer:
    """
    Inversion of control container for dependency injection.

    Usage:
        container = get_container()

        # Register services
        container.register("search", SearchService)
        container.register("stats", StatsService, singleton=True)
        container.register("cache", lambda: CacheService())

        # Get by name
        search = container.get("search")

        # Get by type
        search = container.get(SearchService)

        # Check if registered
        if container.has("search"):
            ...

        # List all
        services = container.list_services()
    """

    def __init__(self):
        self._registrations: Dict[str, ServiceRegistration] = {}
        self._type_map: Dict[Type, str] = {}
        self._resolving: set = set()  # Circular dependency detection

    # =========================================================================
    # Registration
    # =========================================================================

    def register(
        self,
        name: str,
        factory: Union[Type, Callable],
        lifecycle: ServiceLifecycle = ServiceLifecycle.SINGLETON,
        as_type: Optional[Type] = None
    ) -> None:
        """
        Register a service.

        Args:
            name: Service name
            factory: Class or factory function
            lifecycle: SINGLETON, TRANSIENT, or LAZY
            as_type: Type to use for type-based resolution
        """
        registration = ServiceRegistration(
            name=name,
            factory=factory,
            lifecycle=lifecycle
        )

        self._registrations[name] = registration

        # Map type to name
        if as_type:
            self._type_map[as_type] = name
        elif isinstance(factory, type):
            self._type_map[factory] = name

        logger.debug(f"Registered service '{name}' ({lifecycle.value})")

    def register_singleton(self, name: str, instance: Any) -> None:
        """
        Register an already-created singleton instance.

        Args:
            name: Service name
            instance: The instance to register
        """
        registration = ServiceRegistration(
            name=name,
            factory=lambda: instance,
            lifecycle=ServiceLifecycle.SINGLETON,
            instance=instance,
            initialized=True
        )

        self._registrations[name] = registration

        if isinstance(instance, type):
            self._type_map[type(instance)] = name

    def register_factory(
        self,
        name: str,
        factory: Callable,
        lifecycle: ServiceLifecycle = ServiceLifecycle.SINGLETON
    ) -> None:
        """
        Register a factory function.

        Args:
            name: Service name
            factory: Factory function that creates the service
            lifecycle: Service lifecycle
        """
        self.register(name, factory, lifecycle)

    # =========================================================================
    # Resolution
    # =========================================================================

    def get(self, key: Union[str, Type]) -> Any:
        """
        Get a service by name or type.

        Args:
            key: Service name or type

        Returns:
            Service instance

        Raises:
            KeyError: Service not found
            RuntimeError: Circular dependency
        """
        # Resolve by type if needed
        if isinstance(key, type):
            name = self._type_map.get(key)
            if not name:
                raise KeyError(f"No service registered for type {key}")
        else:
            name = key

        registration = self._registrations.get(name)
        if not registration:
            raise KeyError(f"Service '{name}' not registered")

        # Circular dependency check
        if name in self._resolving:
            raise RuntimeError(f"Circular dependency detected for '{name}'")

        # Handle different lifecycles
        if registration.lifecycle == ServiceLifecycle.SINGLETON:
            if registration.initialized:
                return registration.instance

            self._resolving.add(name)
            try:
                instance = self._create_instance(registration)
                registration.instance = instance
                registration.initialized = True
                return instance
            finally:
                self._resolving.discard(name)

        elif registration.lifecycle == ServiceLifecycle.TRANSIENT:
            return self._create_instance(registration)

        elif registration.lifecycle == ServiceLifecycle.LAZY:
            if not registration.initialized:
                registration.instance = self._create_instance(registration)
                registration.initialized = True
            return registration.instance

        return registration.instance

    def _create_instance(self, registration: ServiceRegistration) -> Any:
        """Create an instance using the factory."""
        factory = registration.factory

        if inspect.isclass(factory):
            # Try to resolve constructor dependencies
            return self._resolve_class(factory)
        elif callable(factory):
            return factory()
        else:
            return factory

    def _resolve_class(self, cls: Type) -> Any:
        """Resolve dependencies from class constructor."""
        # Get constructor hints
        try:
            hints = get_type_hints(cls.__init__)
        except Exception:
            hints = {}

        # Build kwargs from registered services
        kwargs = {}
        for param_name, param_type in hints.items():
            if param_name == 'return':
                continue
            if param_type in self._type_map:
                kwargs[param_name] = self.get(param_type)

        return cls(**kwargs)

    # =========================================================================
    # Utilities
    # =========================================================================

    def has(self, key: Union[str, Type]) -> bool:
        """Check if service is registered."""
        if isinstance(key, type):
            return key in self._type_map
        return key in self._registrations

    def list_services(self) -> Dict[str, Dict[str, Any]]:
        """List all registered services."""
        return {
            name: {
                "lifecycle": reg.lifecycle.value,
                "initialized": reg.initialized,
                "type": isinstance(reg.factory, type)
            }
            for name, reg in self._registrations.items()
        }

    def clear(self) -> None:
        """Clear all registrations."""
        self._registrations.clear()
        self._type_map.clear()

    def reset_singletons(self) -> None:
        """Reset all singleton instances."""
        for reg in self._registrations.values():
            if reg.lifecycle == ServiceLifecycle.SINGLETON:
                reg.instance = None
                reg.initialized = False


# =============================================================================
# Decorator for Injection
# =============================================================================

def inject(func: Callable) -> Callable:
    """
    Decorator to inject dependencies into a function.

    Uses type hints to resolve services.

    Usage:
        @inject
        async def handler(event, search: SearchService, stats: StatsService):
            await search.query("test")
            stats.record(...)
    """
    hints = get_type_hints(func)

    async def wrapper(*args, **kwargs):
        # Get container
        container = get_container()

        # Inject missing params
        for param_name, param_type in hints.items():
            if param_name not in kwargs and container.has(param_type):
                kwargs[param_name] = container.get(param_type)

        if inspect.iscoroutinefunction(func):
            return await func(*args, **kwargs)
        return func(*args, **kwargs)

    return wrapper


def injectable(cls: Type) -> Type:
    """
    Class decorator to mark for injection.

    Usage:
        @injectable
        class MyService:
            def __init__(self, search: SearchService):
                self.search = search
    """
    cls._injectable = True
    return cls


# =============================================================================
# Global Instance
# =============================================================================

_container: Optional[ServiceContainer] = None


def get_container() -> ServiceContainer:
    """Get or create global container instance."""
    global _container
    if _container is None:
        _container = ServiceContainer()
        _register_defaults(_container)
    return _container


def reset_container() -> None:
    """Reset global container (for testing)."""
    global _container
    _container = None


def _register_defaults(container: ServiceContainer) -> None:
    """Register default services."""
    from services.search_service import get_search_service
    from services.cache_service import get_cache_service
    from services.stats_service import get_stats_service
    from services.index_service import get_index_service
    from services.progress_service import get_progress_service
    from services.index_stats_service import get_index_stats_service
    from api.dashboard import get_dashboard_api

    # Register lazy factories
    container.register("search_service", get_search_service, lifecycle=ServiceLifecycle.SINGLETON)
    container.register("cache_service", get_cache_service, lifecycle=ServiceLifecycle.SINGLETON)
    container.register("stats_service", get_stats_service, lifecycle=ServiceLifecycle.SINGLETON)
    container.register("index_service", get_index_service, lifecycle=ServiceLifecycle.SINGLETON)
    container.register("progress_service", get_progress_service, lifecycle=ServiceLifecycle.SINGLETON)
    container.register("index_stats_service", get_index_stats_service, lifecycle=ServiceLifecycle.SINGLETON)
    container.register("dashboard_api", get_dashboard_api, lifecycle=ServiceLifecycle.SINGLETON)
    container.register("event_bus", get_event_bus, lifecycle=ServiceLifecycle.SINGLETON)

    from core.eventbus import get_event_bus
    container.register("event_bus", get_event_bus, lifecycle=ServiceLifecycle.SINGLETON)
