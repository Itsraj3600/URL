"""
API v1

Versioned API endpoints for CINE3600.

Structure:
    api/
    ├── v1/                    # Version 1
    │   ├── __init__.py
    │   ├── overview.py        # Dashboard overview
    │   ├── users.py           # User management
    │   ├── index.py           # Index job management
    │   ├── search.py          # Search operations
    │   ├── channels.py        # Channel management
    │   ├── analytics.py       # Analytics data
    │   └── health.py          # Health checks
    ├── __init__.py
    └── base.py                # Shared API utilities

This structure allows introducing api/v2 without breaking v1.
"""

# Version info
API_VERSION = "1.0.0"
API_PREFIX = "/api/v1"

# Import endpoints
from api.v1 import overview, users, index, search, channels, analytics, health

__all__ = [
    "API_VERSION",
    "API_PREFIX",
    "overview",
    "users",
    "index",
    "search",
    "channels",
    "analytics",
    "health",
]
