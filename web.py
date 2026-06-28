"""
Web Server Process

This process runs the HTTP dashboard and API.
It does NOT connect to Telegram - that's the worker's job.

Architecture:
    Worker (bot.py)          Web (web.py)
         ↓                        ↓
    Telegram API             HTTP Dashboard
         ↓                        ↓
    Shared State ←--------→ Shared State
    (MongoDB/Supabase)
         ↓
    Both processes can read/write shared state

Startup:
    web.py starts HTTP server on PORT
    Dashboard reads bot status from shared state
    No duplicate Telegram connections
"""

import asyncio
import logging
from aiohttp import web

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def create_app() -> web.Application:
    """Create and configure the aiohttp application."""
    from plugins import web_server

    # Initialize web server routes
    app = await web_server()

    # Add middleware for CORS
    async def cors_middleware(app, handler):
        async def middleware_handler(request):
            if request.method == "OPTIONS":
                response = web.Response()
            else:
                response = await handler(request)

            response.headers["Access-Control-Allow-Origin"] = "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            return response
        return middleware_handler

    return app


async def start_http_server():
    """Start the HTTP server."""
    from info import PORT
    from core import get_config

    config = get_config()

    print("=" * 60)
    print("🎬 CINE3600 Dashboard Server")
    print("=" * 60)

    # Create application
    app = await create_app()

    # Setup runner
    runner = web.AppRunner(app)
    await runner.setup()

    # Start site
    site = web.TCPSite(
        runner,
        host="0.0.0.0",
        port=PORT
    )
    await site.start()

    logger.info(f"✅ Dashboard API running on port {PORT}")
    logger.info(f"✅ Environment: {config.environment}")
    logger.info("=" * 60)

    # Initialize shared state reader (sets up connection to read bot status)
    await initialize_shared_state_reader()

    return runner


async def initialize_shared_state_reader():
    """Initialize connection to shared state (MongoDB/Supabase)."""
    # Connect to MongoDB for reading shared state
    from database.client import connect_all

    try:
        await connect_all()
        logger.info("✅ Connected to MongoDB for shared state")
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        logger.warning("Running in degraded mode (no shared state)")

    # Connect to Supabase if available
    from core import get_config
    config = get_config()

    if config.database.supabase_url:
        logger.info("✅ Supabase available for shared state")


async def main():
    """Main entry point for web server."""
    runner = None

    try:
        # Start HTTP server
        runner = await start_http_server()

        # Keep running
        logger.info("Dashboard server started. Press Ctrl+C to stop.")
        while True:
            await asyncio.sleep(3600)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except SystemExit:
        logger.info("System exit received...")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
    finally:
        if runner:
            await runner.cleanup()
        logger.info("Goodbye.")


if __name__ == "__main__":
    asyncio.run(main())
