import logging
import pkgutil
from importlib import import_module

logger = logging.getLogger(__name__)

IGNORED_MODULES = {"__init__", "route"}


def load_handlers():
    """
    Import every handler manually.

    Any file imported here will automatically register
    its @Client.on_message handlers.
    """

    logger.info("Loading handlers...")

    import plugins

    for module_info in pkgutil.iter_modules(plugins.__path__):
        if module_info.name in IGNORED_MODULES or module_info.name.startswith("_"):
            continue

        module_name = f"plugins.{module_info.name}"
        import_module(module_name)
        logger.info("Loaded handler module: %s", module_name)

    logger.info("All handlers loaded successfully.")