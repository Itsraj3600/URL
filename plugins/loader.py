"""
Plugin Protection - Safe plugin loading with error isolation.

Wraps plugin initialization in try/catch to prevent one failing plugin
from crashing the entire bot. Failed plugins are logged and skipped,
while the bot continues running.

Features:
- Try/catch wrapper for each plugin
- Full traceback logging
- Disabled plugin registry
- Admin notifications
- EventBus PLUGIN_FAILED event publication
"""

import logging
import importlib
import sys
import os
from typing import List, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Registry of disabled plugins
DISABLED_PLUGINS: Dict[str, str] = {}  # {plugin_name: error_reason}


class PluginProtection:
    """Manages safe plugin loading."""

    @staticmethod
    async def load_all_plugins(plugins_dir: str = "plugins") -> List[str]:
        """
        Load all plugins with error protection.

        Args:
            plugins_dir: Directory containing plugins

        Returns:
            List of successfully loaded plugin names
        """
        DISABLED_PLUGINS.clear()
        loaded_plugins = []

        logger.info(f"Loading plugins from {plugins_dir}...")

        # Find all plugin files
        if not os.path.isdir(plugins_dir):
            logger.warning(f"Plugins directory not found: {plugins_dir}")
            return loaded_plugins

        plugin_files = [
            f[:-3]  # Remove .py extension
            for f in os.listdir(plugins_dir)
            if f.endswith(".py") and not f.startswith("_")
        ]

        logger.info(f"Found {len(plugin_files)} plugin files: {plugin_files}")

        # Load each plugin safely
        for plugin_name in plugin_files:
            success = await PluginProtection.load_plugin(plugin_name, plugins_dir)
            if success:
                loaded_plugins.append(plugin_name)

        # Log summary
        logger.info(
            f"✅ Plugins loaded: {len(loaded_plugins)}/{len(plugin_files)} successful"
        )

        if DISABLED_PLUGINS:
            logger.warning(f"❌ Disabled plugins: {list(DISABLED_PLUGINS.keys())}")

        return loaded_plugins

    @staticmethod
    async def load_plugin(plugin_name: str, plugins_dir: str = "plugins") -> bool:
        """
        Load a single plugin with error protection.

        Args:
            plugin_name: Name of plugin (without .py extension)
            plugins_dir: Directory containing plugins

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            logger.debug(f"Loading plugin: {plugin_name}")

            # Import plugin module
            module_path = f"{plugins_dir}.{plugin_name}"
            module = importlib.import_module(module_path)

            logger.info(f"✅ Plugin loaded: {plugin_name}")
            return True

        except ImportError as e:
            reason = f"Import error: {str(e)}"
            logger.error(f"❌ Failed to load plugin {plugin_name}: {reason}")
            DISABLED_PLUGINS[plugin_name] = reason
            logger.exception(f"Full traceback for {plugin_name}:")

            # Publish event
            await PluginProtection._publish_plugin_failed_event(plugin_name, reason)

            return False

        except SyntaxError as e:
            reason = f"Syntax error in {e.filename} line {e.lineno}: {e.msg}"
            logger.error(f"❌ Plugin {plugin_name} has syntax error: {reason}")
            DISABLED_PLUGINS[plugin_name] = reason
            logger.exception(f"Full traceback for {plugin_name}:")

            await PluginProtection._publish_plugin_failed_event(plugin_name, reason)
            return False

        except Exception as e:
            reason = f"{type(e).__name__}: {str(e)}"
            logger.error(f"❌ Failed to load plugin {plugin_name}: {reason}")
            DISABLED_PLUGINS[plugin_name] = reason
            logger.exception(f"Full traceback for {plugin_name}:")

            # Publish event
            await PluginProtection._publish_plugin_failed_event(plugin_name, reason)

            return False

    @staticmethod
    async def _publish_plugin_failed_event(plugin_name: str, reason: str) -> None:
        """Publish PLUGIN_FAILED event to event bus."""
        try:
            from core import get_event_bus, Events

            event_bus = get_event_bus()
            await event_bus.publish(
                Events.PLUGIN_FAILED,
                source="plugin_loader",
                data={
                    "plugin_name": plugin_name,
                    "reason": reason,
                    "timestamp": datetime.utcnow(),
                },
            )
        except Exception as e:
            logger.debug(f"Could not publish PLUGIN_FAILED event: {e}")

    @staticmethod
    def get_disabled_plugins() -> Dict[str, str]:
        """Get registry of disabled plugins."""
        return dict(DISABLED_PLUGINS)

    @staticmethod
    async def notify_admin(bot_client, admin_id: int) -> None:
        """
        Notify admin of disabled plugins.

        Args:
            bot_client: Pyrogram bot client
            admin_id: Admin user ID
        """
        if not DISABLED_PLUGINS:
            return

        try:
            message = "⚠️ Plugin Errors Detected:\n\n"
            for plugin_name, reason in DISABLED_PLUGINS.items():
                message += f"❌ {plugin_name}\n"
                message += f"   {reason}\n\n"

            message += (
                "Fix the issues and restart the bot to enable these plugins."
            )

            await bot_client.send_message(admin_id, message)
            logger.info(f"Notified admin {admin_id} of disabled plugins")

        except Exception as e:
            logger.warning(f"Could not notify admin: {e}")
