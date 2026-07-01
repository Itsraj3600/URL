import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from os import getenv

DATABASE_URI = getenv("DATABASE_URI")

async def main():
    if not DATABASE_URI:
        print("DATABASE_URI is not set.")
        return

    try:
        client = AsyncIOMotorClient(
            DATABASE_URI,
            serverSelectionTimeoutMS=5000
        )

        await client.admin.command("ping")
        print("✅ Database connected successfully!")

    except Exception as e:
        print(f"❌ Connection failed:\n{e}")

asyncio.run(main())