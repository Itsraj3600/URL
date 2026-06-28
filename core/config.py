"""
Central Configuration

Single source of truth for all CINE3600 configuration.

All settings are loaded from environment variables with sensible defaults.
This module should be the only place that reads from os.environ directly.

Usage:
    from core.config import config

    # Access settings
    print(config.database.url)
    print(config.bot.token)
    print(config.index.batch_size)

    # Check feature flags
    if config.features.auto_index:
        ...

    # Get all settings
    settings = config.to_dict()
"""

import os
import logging
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from functools import lru_cache

logger = logging.getLogger(__name__)


# =============================================================================
# Configuration Sections
# =============================================================================

@dataclass
class DatabaseConfig:
    """Database connection settings."""
    # MongoDB
    mongo_url: str = ""
    mongo_db_name: str = "CineBot"
    mongo_max_pool_size: int = 100
    mongo_min_pool_size: int = 10
    mongo_timeout_ms: int = 30000

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""

    # Redis (optional)
    redis_url: str = ""
    redis_enabled: bool = False

    def __post_init__(self):
        # Load from environment if not set
        if not self.mongo_url:
            self.mongo_url = os.environ.get("DATABASE_URL", "")
        if not self.supabase_url:
            self.supabase_url = os.environ.get("SUPABASE_URL", "")
        if not self.supabase_anon_key:
            self.supabase_anon_key = os.environ.get("SUPABASE_ANON_KEY", "")
        if not self.supabase_service_role_key:
            self.supabase_service_role_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
        if not self.redis_url:
            self.redis_url = os.environ.get("REDIS_URL", "")


@dataclass
class TelegramConfig:
    """Telegram bot settings."""
    api_id: int = 0
    api_hash: str = ""
    bot_token: str = ""
    owner_id: int = 0
    admin_ids: List[int] = field(default_factory=list)

    # Bot settings
    log_channel: int = 0
    index_req_channel: int = 0
    force_sub_channel: int = 0
    force_sub_channel2: int = 0

    # Channels to watch for auto-index
    monitored_channels: List[int] = field(default_factory=list)

    def __post_init__(self):
        if not self.api_id:
            self.api_id = int(os.environ.get("API_ID", "0"))
        if not self.api_hash:
            self.api_hash = os.environ.get("API_HASH", "")
        if not self.bot_token:
            self.bot_token = os.environ.get("BOT_TOKEN", "")
        if not self.owner_id:
            self.owner_id = int(os.environ.get("OWNER_ID", "0"))
        admins_str = os.environ.get("ADMINS", "")
        if not self.admin_ids and admins_str:
            self.admin_ids = [int(x.strip()) for x in admins_str.split(",") if x.strip()]


@dataclass
class IndexConfig:
    """Indexing settings."""
    batch_size: int = 500
    max_batch_size: int = 1000
    checkpoint_interval: int = 100
    max_workers: int = 3

    # Progress
    progress_update_interval: int = 30

    # Duplicate detection
    check_by_file_id: bool = True
    check_by_unique_id: bool = True
    check_by_normalized_title: bool = True
    check_by_content_hash: bool = False

    # Auto-indexing
    auto_index_enabled: bool = False
    auto_index_batch_size: int = 50
    auto_index_delay_seconds: int = 5

    def __post_init__(self):
        self.batch_size = int(os.environ.get("INDEX_BATCH_SIZE", str(self.batch_size)))
        self.max_workers = int(os.environ.get("INDEX_MAX_WORKERS", str(self.max_workers)))


@dataclass
class SearchConfig:
    """Search settings."""
    # Cache
    cache_ttl_seconds: int = 600
    cache_max_entries: int = 1000
    pagination_cache_ttl_seconds: int = 900

    # Results
    max_results_per_page: int = 10
    max_results_total: int = 100

    # Ranking
    enable_ranking: bool = True
    exact_match_score: int = 100
    starts_with_score: int = 80
    contains_score: int = 60
    year_match_score: int = 40
    fuzzy_match_score: int = 20

    # Suggestions
    suggestion_limit: int = 5
    enable_suggestions: bool = True

    def __post_init__(self):
        self.cache_ttl_seconds = int(os.environ.get("SEARCH_CACHE_TTL", str(self.cache_ttl_seconds)))


@dataclass
class FeatureFlags:
    """Feature flags for enabling/disabling functionality."""
    auto_index: bool = False
    spell_check: bool = True
    imdb_integration: bool = True
    url_shortener: bool = False
    premium_required: bool = False
    broadcast_enabled: bool = True
    filter_enabled: bool = True
    inline_search: bool = True
    join_requests: bool = True
    custom_thumbnail: bool = True
    stats_tracking: bool = True
    error_reporting: bool = True

    def __post_init__(self):
        self.auto_index = os.environ.get("FEATURE_AUTO_INDEX", "").lower() == "true"
        self.spell_check = os.environ.get("FEATURE_SPELL_CHECK", "true").lower() == "true"


@dataclass
class MonitoringConfig:
    """Monitoring and logging settings."""
    log_level: str = "INFO"
    log_file: str = "logs/cinebot.log"
    log_rotation: str = "10 MB"
    log_backup_count: int = 5

    # Health checks
    health_check_interval: int = 60
    alert_on_high_cpu: bool = True
    alert_on_high_memory: bool = True
    alert_on_db_disconnect: bool = True
    alert_on_worker_error: bool = True

    # Thresholds
    high_cpu_threshold: float = 80.0
    high_memory_threshold: float = 80.0
    low_disk_threshold: float = 10.0

    # Metrics
    track_search_times: bool = True
    track_index_times: bool = True
    track_user_activity: bool = True

    def __post_init__(self):
        self.log_level = os.environ.get("LOG_LEVEL", self.log_level)


@dataclass
class DashboardConfig:
    """Dashboard settings."""
    enabled: bool = True
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False

    # Authentication
    require_auth: bool = True
    jwt_secret: str = ""
    jwt_ttl_hours: int = 24
    session_ttl_hours: int = 12

    # CORS
    cors_origins: List[str] = field(default_factory=lambda: ["*"])

    def __post_init__(self):
        self.port = int(os.environ.get("DASHBOARD_PORT", str(self.port)))
        self.jwt_secret = os.environ.get("JWT_SECRET", os.environ.get("SECRET_KEY", ""))


@dataclass
class LimitsConfig:
    """Rate limiting and usage limits."""
    # Search limits
    max_searches_per_minute: int = 30
    max_searches_per_day: int = 500

    # Download limits
    max_downloads_per_day: int = 50
    max_downloads_per_day_premium: int = 200

    # File size limits
    max_file_size_mb: int = 2000

    # Flood wait
    flood_wait_cooldown: int = 30

    def __post_init__(self):
        self.max_searches_per_minute = int(os.environ.get("MAX_SEARCHES_PER_MINUTE", str(self.max_searches_per_minute)))


@dataclass
class NotificationConfig:
    """Notification settings."""
    # Telegram notifications
    notify_on_index_complete: bool = True
    notify_on_index_error: bool = True
    notify_on_worker_error: bool = True
    notify_on_db_error: bool = True
    notify_on_new_user: bool = False
    notify_on_ban: bool = True
    notify_on_premium: bool = True

    # Notification targets
    notification_channel: int = 0
    admin_notification_channel: int = 0

    # Email (optional)
    email_enabled: bool = False
    email_smtp_host: str = ""
    email_smtp_port: int = 587
    email_from: str = ""
    email_password: str = ""


# =============================================================================
# Main Config Class
# =============================================================================

@dataclass
class Config:
    """Main configuration container."""
    app_name: str = "CINE3600"
    version: str = "2.0.0"
    environment: str = "production"

    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    telegram: TelegramConfig = field(default_factory=TelegramConfig)
    index: IndexConfig = field(default_factory=IndexConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    features: FeatureFlags = field(default_factory=FeatureFlags)
    monitoring: MonitoringConfig = field(default_factory=MonitoringConfig)
    dashboard: DashboardConfig = field(default_factory=DashboardConfig)
    limits: LimitsConfig = field(default_factory=LimitsConfig)
    notifications: NotificationConfig = field(default_factory=NotificationConfig)

    def __post_init__(self):
        self.environment = os.environ.get("ENV", os.environ.get("ENVIRONMENT", "production"))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "app_name": self.app_name,
            "version": self.version,
            "environment": self.environment,
            "database": asdict(self.database),
            "telegram": {
                "api_id": self.telegram.api_id,
                "owner_id": self.telegram.owner_id,
                "admin_ids": self.telegram.admin_ids,
                # Exclude sensitive data
            },
            "index": asdict(self.index),
            "search": asdict(self.search),
            "features": asdict(self.features),
            "monitoring": asdict(self.monitoring),
            "dashboard": {
                "enabled": self.dashboard.enabled,
                "port": self.dashboard.port,
                "require_auth": self.dashboard.require_auth,
            },
            "limits": asdict(self.limits),
        }

    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"

    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"


# =============================================================================
# Global Instance
# =============================================================================

_config: Optional[Config] = None


def get_config() -> Config:
    """Get or create global Config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def reload_config() -> Config:
    """Reload configuration from environment."""
    global _config
    _config = Config()
    return _config


# Shorthand
config = property(get_config)


# =============================================================================
# Convenience Access
# =============================================================================

# Quick access to common settings
def get_database_url() -> str:
    return get_config().database.mongo_url


def get_bot_token() -> str:
    return get_config().telegram.bot_token


def get_admin_ids() -> List[int]:
    return get_config().telegram.admin_ids


def get_owner_id() -> int:
    return get_config().telegram.owner_id


def is_feature_enabled(feature: str) -> bool:
    """Check if a feature flag is enabled."""
    cfg = get_config()
    return getattr(cfg.features, feature, False)
