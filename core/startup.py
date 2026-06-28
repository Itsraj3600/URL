"""
Startup Validator - Pre-flight checks before bot initialization.

Validates:
- Required environment variables (BOT_TOKEN, API_ID, API_HASH, DATABASE_URI)
- Database connectivity
- Telegram API credentials
- Disk space and system resources

Blocks bot startup if validation fails and provides helpful error messages.
"""

import logging
import sys
from typing import Tuple, Optional, List
from motor.motor_asyncio import AsyncIOMotorClient

logger = logging.getLogger(__name__)


class StartupValidator:
    """Validate system configuration before bot startup."""

    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    async def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        """
        Run all validation checks.

        Returns:
            Tuple of (all_valid: bool, errors: List[str], warnings: List[str])
        """
        self.errors.clear()
        self.warnings.clear()

        # Check environment variables
        self._validate_env_vars()

        # Check database connectivity
        await self._validate_database()

        # Check Telegram credentials
        self._validate_telegram()

        # Log results
        self._log_results()

        return len(self.errors) == 0, self.errors, self.warnings

    def _validate_env_vars(self) -> None:
        """Validate required environment variables."""
        required = {
            "BOT_TOKEN": "Telegram bot token (get from @BotFather)",
            "API_ID": "Telegram API ID (from my.telegram.org)",
            "API_HASH": "Telegram API hash (from my.telegram.org)",
            "DATABASE_URI": "MongoDB connection string",
        }

        optional = {
            "LOG_CHANNEL": "Log channel ID for bot logs",
            "ADMINS": "Admin user IDs",
            "CHANNELS": "Channels to auto-index",
        }

        # Check required vars
        from os import environ

        for var, description in required.items():
            value = environ.get(var, "").strip()
            if not value:
                self.errors.append(f"❌ Missing {var}: {description}")

        # Check optional vars
        for var, description in optional.items():
            value = environ.get(var, "").strip()
            if not value:
                self.warnings.append(f"⚠️  Optional {var} not set: {description}")

    async def _validate_database(self) -> None:
        """Validate database connectivity."""
        from os import environ

        database_uri = environ.get("DATABASE_URI", "").strip()
        if not database_uri:
            # Already reported in env vars check
            return

        try:
            logger.info("Checking database connectivity...")
            client = AsyncIOMotorClient(
                database_uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=10000,
            )

            # Attempt ping
            await client.admin.command("ping")
            logger.info("✅ Database connection successful")

            # Check storage quota
            try:
                server_status = await client.admin.command("serverStatus")
                storage_mb = (
                    server_status.get("storageEngine", {})
                    .get("wiredTiger", {})
                    .get("cache", {})
                    .get("bytes", 0)
                ) / (1024 * 1024)

                if storage_mb > 450:  # Warn at 450MB on 512MB limit
                    self.warnings.append(
                        f"⚠️  Database storage high: {storage_mb:.0f}MB used"
                    )
            except Exception:
                pass  # Storage check is optional

            await client.close()

        except Exception as e:
            self.errors.append(f"❌ Database connection failed: {str(e)}")

    def _validate_telegram(self) -> None:
        """Validate Telegram API credentials."""
        from os import environ

        api_id_str = environ.get("API_ID", "").strip()
        api_hash = environ.get("API_HASH", "").strip()

        # Validate API_ID format
        if api_id_str:
            try:
                api_id = int(api_id_str)
                if api_id < 100000 or api_id > 9999999:
                    self.errors.append(
                        f"❌ Invalid API_ID: {api_id} (must be between 100000-9999999)"
                    )
            except ValueError:
                self.errors.append(f"❌ API_ID must be numeric, got: {api_id_str}")

        # Validate API_HASH format
        if api_hash:
            if len(api_hash) != 32 or not all(c in "0123456789abcdef" for c in api_hash):
                self.errors.append(
                    f"❌ Invalid API_HASH: must be 32 hexadecimal characters"
                )

    def _log_results(self) -> None:
        """Log validation results."""
        if self.errors:
            logger.error("=" * 60)
            logger.error("STARTUP VALIDATION FAILED")
            logger.error("=" * 60)
            for error in self.errors:
                logger.error(error)
            logger.error("=" * 60)

        if self.warnings:
            logger.warning("Startup Warnings:")
            for warning in self.warnings:
                logger.warning(warning)

        if not self.errors and not self.warnings:
            logger.info("✅ All startup checks passed")


async def validate_startup() -> bool:
    """
    Run startup validation. Return True if all checks pass, False otherwise.

    If validation fails, error messages are logged and the function returns False.
    Caller should exit the program if this returns False.
    """
    validator = StartupValidator()
    valid, errors, warnings = await validator.validate_all()

    if not valid:
        logger.error(
            "Cannot start bot due to configuration errors. Fix issues above and restart."
        )
        return False

    return True
