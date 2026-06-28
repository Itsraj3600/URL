"""
Startup Validator - Pre-flight checks before bot initialization.
"""

import logging
from typing import Tuple, List
from motor.motor_asyncio import AsyncIOMotorClient
from os import environ

logger = logging.getLogger(__name__)


class StartupValidator:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    async def validate_all(self) -> Tuple[bool, List[str], List[str]]:
        self.errors.clear()
        self.warnings.clear()

        self._validate_env_vars()
        await self._validate_database()
        self._validate_telegram()

        self._log_results()

        return len(self.errors) == 0, self.errors, self.warnings

    def _validate_env_vars(self):
        required = {
            "BOT_TOKEN": "Telegram Bot Token",
            "API_ID": "Telegram API ID",
            "API_HASH": "Telegram API HASH",
            "DATABASE_URI": "MongoDB URI",
            "LOG_CHANNEL": "Log Channel",
            "ADMINS": "Admin IDs",
        }

        optional = {
            "CHANNELS": "Auto Index Channels",
            "OPENAI_API": "OpenAI API Key",
        }

        for key, desc in required.items():
            value = environ.get(key, "").strip()

            if not value:
                self.errors.append(f"Missing {key} ({desc})")

        for key, desc in optional.items():
            value = environ.get(key, "").strip()

            if not value:
                self.warnings.append(f"{key} not configured ({desc})")

    async def _validate_database(self):
        uri = environ.get("DATABASE_URI", "").strip()

        if not uri:
            return

        try:
            logger.info("Checking MongoDB connection...")

            client = AsyncIOMotorClient(
                uri,
                serverSelectionTimeoutMS=5000,
                connectTimeoutMS=5000,
                socketTimeoutMS=10000,
            )

            await client.admin.command("ping")

            logger.info("MongoDB connection successful")

            client.close()

        except Exception as e:
            self.errors.append(f"MongoDB connection failed: {e}")

    def _validate_telegram(self):
        api_id_str = environ.get("API_ID", "").strip()
        api_hash = environ.get("API_HASH", "").strip().lower()
        bot_token = environ.get("BOT_TOKEN", "").strip()

        if api_id_str:
            try:
                api_id = int(api_id_str)

                if api_id <= 0:
                    self.errors.append("API_ID must be greater than 0")

            except ValueError:
                self.errors.append("API_ID must be numeric")

        if api_hash:

            if len(api_hash) != 32:
                self.errors.append(
                    f"API_HASH must be 32 characters (got {len(api_hash)})"
                )

            elif not all(c in "0123456789abcdef" for c in api_hash):
                self.errors.append("API_HASH contains invalid characters")

        if bot_token:

            if ":" not in bot_token:
                self.errors.append("BOT_TOKEN format is invalid")

    def _log_results(self):

        logger.info("=" * 60)
        logger.info("Startup Validation Report")
        logger.info("=" * 60)

        if self.errors:

            logger.error("Errors Found: %s", len(self.errors))

            for err in self.errors:
                logger.error("❌ %s", err)

        else:
            logger.info("No validation errors")

        if self.warnings:

            logger.warning("Warnings Found: %s", len(self.warnings))

            for warn in self.warnings:
                logger.warning("⚠️ %s", warn)

        else:
            logger.info("No warnings")

        logger.info("=" * 60)


async def validate_startup() -> bool:
    validator = StartupValidator()

    valid, errors, warnings = await validator.validate_all()

    if not valid:

        logger.error("")
        logger.error("BOT STARTUP ABORTED")
        logger.error("Fix the above configuration errors and restart.")
        logger.error("")

        return False

    logger.info("All startup checks passed successfully.")

    return True