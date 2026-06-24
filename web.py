import asyncio

from aiohttp import web

from plugins import web_server
from info import PORT


async def main():
    app = web.AppRunner(await web_server())
    await app.setup()
    site = web.TCPSite(app, "0.0.0.0", PORT)
    await site.start()
    print("Web server started")

    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())