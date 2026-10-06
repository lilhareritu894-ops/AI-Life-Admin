import asyncio
import logging
from datetime import datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends
from pymongo.errors import PyMongoError

from app.api.endpoints.auth import get_current_user
from app.db.session import get_database, mongo_http_exception

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/summary")
async def get_analytics_summary(db=Depends(get_database), current_user=Depends(get_current_user)):
    owner_id = current_user["_id"]
    today = datetime.now(timezone.utc).date()
    first_day = today - timedelta(days=6)
    activity = {
        (first_day + timedelta(days=offset)).isoformat(): {
            "date": (first_day + timedelta(days=offset)).isoformat(),
            "tasks_created": 0,
            "tasks_completed": 0,
            "agent_runs": 0,
        }
        for offset in range(7)
    }
    first_day_start = datetime.combine(first_day, time.min, tzinfo=timezone.utc)
    try:
        tasks_collection = db["tasks"]
        tasks_total, tasks_completed, events_total, documents_total, agent_runs_total = await asyncio.gather(
            tasks_collection.count_documents({"owner_id": owner_id}),
            tasks_collection.count_documents({"owner_id": owner_id, "is_completed": True}),
            db["calendar_events"].count_documents({"owner_id": owner_id}),
            db["documents"].count_documents({"owner_id": owner_id}),
            db["agent_runs"].count_documents({"owner_id": owner_id}),
        )
        recent_tasks, recent_runs = await asyncio.gather(
            tasks_collection.find(
                {
                    "owner_id": owner_id,
                    "$or": [{"created_at": {"$gte": first_day_start}}, {"updated_at": {"$gte": first_day_start}}],
                }
            ).to_list(length=5000),
            db["agent_runs"].find({"owner_id": owner_id, "created_at": {"$gte": first_day_start}}).to_list(length=5000),
        )
    except PyMongoError as exc:
        logger.exception("MongoDB failed while calculating analytics")
        raise mongo_http_exception(exc) from exc

    for task in recent_tasks:
        created_at = task.get("created_at")
        if isinstance(created_at, datetime) and created_at.date().isoformat() in activity:
            activity[created_at.date().isoformat()]["tasks_created"] += 1
        updated_at = task.get("updated_at")
        if task.get("is_completed") and isinstance(updated_at, datetime) and updated_at.date().isoformat() in activity:
            activity[updated_at.date().isoformat()]["tasks_completed"] += 1
    for run in recent_runs:
        created_at = run.get("created_at")
        if isinstance(created_at, datetime) and created_at.date().isoformat() in activity:
            activity[created_at.date().isoformat()]["agent_runs"] += 1

    return {
        "tasks_total": tasks_total,
        "tasks_completed": tasks_completed,
        "tasks_pending": tasks_total - tasks_completed,
        "calendar_events": events_total,
        "documents": documents_total,
        "agent_runs": agent_runs_total,
        "daily_activity": list(activity.values()),
    }