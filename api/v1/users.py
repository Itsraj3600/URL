"""
Users API Endpoints

GET /api/v1/users
    List users with optional filters.
    Params: limit, offset, search, banned_only, premium_only

GET /api/v1/users/:id
    Get single user details.

POST /api/v1/users/:id/ban
    Ban a user.
    Body: { "reason": "spam" }

POST /api/v1/users/:id/unban
    Unban a user.

POST /api/v1/users/:id/premium
    Grant premium access.
    Body: { "days": 30 }

DELETE /api/v1/users/:id/premium
    Remove premium access.
"""

from typing import Dict, Any, List, Optional


async def list_users(
    limit: int = 50,
    offset: int = 0,
    search: str = "",
    banned_only: bool = False,
    premium_only: bool = False
) -> List[Dict[str, Any]]:
    """List users with optional filters."""
    from api.dashboard import get_dashboard_api

    api = get_dashboard_api()
    users = await api.get_users(
        limit=limit,
        offset=offset,
        search=search,
        banned_only=banned_only,
        premium_only=premium_only
    )

    return [
        {
            "user_id": u.user_id,
            "username": u.username,
            "first_name": u.first_name,
            "search_count": u.search_count,
            "download_count": u.download_count,
            "is_premium": u.is_premium,
            "is_banned": u.is_banned,
            "ban_reason": u.ban_reason,
            "last_seen": u.last_seen.isoformat() if u.last_seen else None,
        }
        for u in users
    ]


async def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Get single user details."""
    from api.dashboard import get_dashboard_api

    api = get_dashboard_api()
    user = await api.get_user(user_id)

    if not user:
        return None

    return {
        "user_id": user.user_id,
        "username": user.username,
        "first_name": user.first_name,
        "is_premium": user.is_premium,
        "is_banned": user.is_banned,
        "ban_reason": user.ban_reason,
        "search_count": user.search_count,
        "download_count": user.download_count,
    }


async def ban_user(user_id: int, reason: str = "") -> Dict[str, Any]:
    """Ban a user."""
    from api.dashboard import get_dashboard_api
    from core import get_event_bus, Events

    api = get_dashboard_api()
    success = await api.ban_user(user_id, reason)

    if success:
        # Emit event
        bus = get_event_bus()
        await bus.publish(Events.USER_BANNED, user_id=user_id, reason=reason)

    return {"success": success, "user_id": user_id}


async def unban_user(user_id: int) -> Dict[str, Any]:
    """Unban a user."""
    from api.dashboard import get_dashboard_api
    from core import get_event_bus, Events

    api = get_dashboard_api()
    success = await api.unban_user(user_id)

    if success:
        bus = get_event_bus()
        await bus.publish(Events.USER_UNBANNED, user_id=user_id)

    return {"success": success, "user_id": user_id}


ENDPOINTS = {
    "GET /users": list_users,
    "GET /users/:id": get_user,
    "POST /users/:id/ban": ban_user,
    "POST /users/:id/unban": unban_user,
}
