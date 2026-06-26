import asyncio
from aiohttp import web

from plugins import web_server
from info import PORT

from cinebot import Cine3600Bot
from cinebot.clients import initialize_clients


async def main():
    print("=" * 50)
    print("🚀 Starting CINE3600...")
    print("=" * 50)

    print("▶ Starting Telegram Bot...")
    await Cine3600Bot.start()

    print("▶ Initializing Clients...")
    await initialize_clients()

    print("▶ Starting Web Server...")

    # Create aiohttp application
    app = await web_server()

    runner = web.AppRunner(app)
    await runner.setup()

    site = web.TCPSite(
        runner,
        host="0.0.0.0",
        port=PORT
    )

    await site.start()

    print(f"✅ Web Server Running on Port {PORT}")
    print("✅ Bot is Online")
    print("=" * 50)

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        print("Shutting down...")

    finally:
        await runner.cleanup()
        await Cine3600Bot.stop()


if __name__ == "__main__":
    asyncio.run(main())