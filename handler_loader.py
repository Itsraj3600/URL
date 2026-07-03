import logging
from importlib import import_module

logger = logging.getLogger(__name__)

HANDLER_MODULES = [
    "plugins.ai",
    "plugins.banned",
    "plugins.broadcast",
    "plugins.channel",
    "plugins.commands",
    "plugins.connection",
    "plugins.files_delete",
    "plugins.filters",
    "plugins.genlink",
    "plugins.gfilters",
    "plugins.index",
    "plugins.inline",
    "plugins.join_req",
    "plugins.misc",
    "plugins.pmfilter",
    "plugins.Premium",
    "plugins.p_ttishow",
    "plugins.rlazyRenamer",
    "plugins.rlazy_cpption",
    "plugins.rlazy_filedetect",
    "plugins.rlazy_thumbnail",
]


def load_handlers():
    """
    Import every handler manually.

    Any file imported here will automatically register
    its @Client.on_message handlers.
    """

    logger.info("Loading handlers...")

    for module_name in HANDLER_MODULES:
        import_module(module_name)
        logger.info("Loaded handler module: %s", module_name)

    logger.info("All handlers loaded successfully.")