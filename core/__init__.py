"""
Core Module

Central infrastructure for CINE3600:
- Event Bus: Decoupled pub/sub messaging
- Service Container: Dependency injection
- Configuration: Single source of truth
"""

from core.eventbus import (
    EventBus,
    Event,
    Events,
    get_event_bus,
    reset_event_bus,
)

from core.container import (
    ServiceContainer,
    ServiceLifecycle,
    get_container,
    reset_container,
    inject,
    injectable,
)

from core.config import (
    Config,
    DatabaseConfig,
    TelegramConfig,
    IndexConfig,
    SearchConfig,
    FeatureFlags,
    MonitoringConfig,
    DashboardConfig,
    LimitsConfig,
    NotificationConfig,
    get_config,
    reload_config,
    config,
)

__all__ = [
    # Event Bus
    "EventBus",
    "Event",
    "Events",
    "get_event_bus",
    "reset_event_bus",
    # Container
    "ServiceContainer",
    "ServiceLifecycle",
    "get_container",
    "reset_container",
    "inject",
    "injectable",
    # Config
    "Config",
    "DatabaseConfig",
    "TelegramConfig",
    "IndexConfig",
    "SearchConfig",
    "FeatureFlags",
    "MonitoringConfig",
    "DashboardConfig",
    "LimitsConfig",
    "NotificationConfig",
    "get_config",
    "reload_config",
    "config",
]
