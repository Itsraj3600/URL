"""
Channels API Endpoints

GET /api/v1/channels
    List all connected channels.

POST /api/v1/channels
    Add a channel.
    Body: { "channel_id": -100123, "last_message_id": 50000 }

DELETE /api/v1/channels/:id
    Remove a channel.

POST /api/v1/channels/:id/sync
    Trigger sync for a channel.

POST /api/v1/channels/:id/reindex
    Trigger full reindex.
"""

from typing import Dict, Any, List


async def list_channels() -> List[Dict[str, Any]]:
    """List all connected channels."""
    from api.dashboard import get_dashboard_api

    api = get_dashboard_api()
    channels = await api.get_channels()

    return [
        {
            "channel_id": c.channel_id,
            "channel_name": c.channel_name,
            "channel_username": c.channel_username,
            "connected": c.connected,
            "files_count": c.files_count,
            "last_sync": c.last_sync.isoformat() if c.last_sync else None,
            "status": c.status,
        }
        for c in channels
    ]


async def add_channel(
    channel_id: int,
    last_message_id: int = 0,
    auto_index: bool = False
) -> Dict[str, Any]:
    """Add a channel to watch."""
    from core import get_event_bus, Events

    # Emit event for channel added
    bus = get_event_bus()
    await bus.publish(
        Events.CHANNEL_ADDED,
        channel_id=channel_id,
        auto_index=auto_index
    )

    return {
        "success": True,
        "channel_id": channel_id,
    }


async def sync_channel(channel_id: int) -> Dict[str, Any]:
    """Trigger sync for a channel."""
    from core import get_event_bus, Events

    bus = get_event_bus()
    await bus.publish(Events.CHANNEL_SYNC_STARTED, channel_id=channel_id)

    return {
        "success": True,
        "channel_id": channel_id,
        "status": "syncing",
    }


ENDPOINTS = {
    "GET /channels": list_channels,
    "POST /channels": add_channel,
    "POST /channels/:id/sync": sync_channel,
}
