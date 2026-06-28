"""
Index API Endpoints

GET /api/v1/index/jobs
    List all index jobs.

GET /api/v1/index/jobs/:id
    Get single job details.

POST /api/v1/index/start
    Start a new index job.
    Body: { "channel_id": -100123, "last_message_id": 50000 }

POST /api/v1/index/:id/pause
    Pause an index job.

POST /api/v1/index/:id/resume
    Resume a paused job.

POST /api/v1/index/:id/cancel
    Cancel an index job.

DELETE /api/v1/index/:id
    Delete job record.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


async def list_jobs() -> List[Dict[str, Any]]:
    """List all index jobs."""
    from api.dashboard import get_dashboard_api

    api = get_dashboard_api()
    jobs = await api.get_index_jobs()

    return [
        {
            "job_id": j.job_id,
            "channel_id": j.channel_id,
            "channel_name": j.channel_name,
            "status": j.status,
            "progress": {
                "percent": j.progress_percent,
                "processed": j.processed,
                "inserted": j.inserted,
                "duplicates": j.duplicates,
                "errors": j.errors,
            },
            "speed": j.speed,
            "eta": j.eta,
            "started_at": j.started_at.isoformat() if j.started_at else None,
        }
        for j in jobs
    ]


async def start_job(
    channel_id: int,
    last_message_id: int,
    requested_by: int = 0,
    priority: int = 0,
    batch_size: int = 500
) -> Dict[str, Any]:
    """Start a new index job."""
    from api.dashboard import get_dashboard_api
    from core import get_event_bus, Events

    api = get_dashboard_api()
    job_id = await api.start_index(
        channel_id=channel_id,
        last_message_id=last_message_id,
        requested_by=requested_by
    )

    if job_id:
        bus = get_event_bus()
        await bus.publish(
            Events.INDEX_STARTED,
            job_id=job_id,
            channel_id=channel_id
        )

    return {
        "success": bool(job_id),
        "job_id": job_id,
        "channel_id": channel_id,
    }


async def pause_job(job_id: str) -> Dict[str, Any]:
    """Pause an index job."""
    from api.dashboard import get_dashboard_api
    from core import get_event_bus, Events

    api = get_dashboard_api()
    success = await api.pause_index(job_id)

    if success:
        bus = get_event_bus()
        await bus.publish(Events.INDEX_PAUSED, job_id=job_id)

    return {"success": success, "job_id": job_id}


async def resume_job(job_id: str) -> Dict[str, Any]:
    """Resume a paused job."""
    from api.dashboard import get_dashboard_api
    from core import get_event_bus, Events

    api = get_dashboard_api()
    success = await api.resume_index(job_id)

    if success:
        bus = get_event_bus()
        await bus.publish(Events.INDEX_RESUMED, job_id=job_id)

    return {"success": success, "job_id": job_id}


async def cancel_job(job_id: str) -> Dict[str, Any]:
    """Cancel an index job."""
    from api.dashboard import get_dashboard_api
    from core import get_event_bus, Events

    api = get_dashboard_api()
    success = await api.cancel_index(job_id)

    if success:
        bus = get_event_bus()
        await bus.publish(Events.INDEX_CANCELLED, job_id=job_id)

    return {"success": success, "job_id": job_id}


ENDPOINTS = {
    "GET /index/jobs": list_jobs,
    "POST /index/start": start_job,
    "POST /index/:id/pause": pause_job,
    "POST /index/:id/resume": resume_job,
    "POST /index/:id/cancel": cancel_job,
}
