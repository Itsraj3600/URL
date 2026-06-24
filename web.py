import asyncio
from aiohttp import web

from plugins import web_server
from info import PORT

from cinebot import Cine3600Bot
from cinebot.clients import initialize_clients


async def main():
    print("Starting Cine client...")

    await Cine3600Bot.start()
    await initialize_clients()

    print("Starting web server...")

    app = web.AppRunner(await web_server())
    await app.setup()

    site = web.TCPSite(app, "0.0.0.0", PORT)
    await site.start()

    print("Web server started")

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())