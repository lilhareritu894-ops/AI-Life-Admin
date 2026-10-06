import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pymongo.errors import PyMongoError
from starlette.concurrency import run_in_threadpool

from app.api.endpoints.auth import get_current_user
from app.db.session import get_database, mongo_http_exception
from app.schemas.calendar import (
    CalendarEventCreate,
    CalendarEventPatch,
    CalendarEventResponse,
)
from app.services.calendar_agent import calendar_agent
from app.utils.mongo import parse_object_id, serialize_document


router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=CalendarEventResponse, status_code=status.HTTP_201_CREATED)
async def create_calendar_event(event: CalendarEventCreate, db=Depends(get_database), current_user=Depends(get_current_user)):
    record = event.model_dump()
    record.update(owner_id=current_user["_id"], created_at=datetime.now(timezone.utc))
    try:
        result = await db["calendar_events"].insert_one(record)
    except PyMongoError as exc:
        logger.exception("MongoDB failed while creating a calendar event")
        raise mongo_http_exception(exc) from exc
    record["_id"] = result.inserted_id
    return serialize_document(record)


@router.get("/", response_model=list[CalendarEventResponse], tags=["Calendar"])
async def get_calendar_events(
    db=Depends(get_database),
    current_user=Depends(get_current_user),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    try:
        events = await (
            db["calendar_events"]
            .find({"owner_id": current_user["_id"]})
            .sort("time_slot", 1)
            .skip(skip)
            .limit(limit)
            .to_list(length=limit)
        )
    except PyMongoError as exc:
        logger.exception("MongoDB failed while listing calendar events")
        raise mongo_http_exception(exc) from exc
    return [serialize_document(event) for event in events]


@router.get("/optimize")
async def optimize_schedule(db=Depends(get_database), current_user=Depends(get_current_user)):
    try:
        events = await db["calendar_events"].find({"owner_id": current_user["_id"]}).to_list(length=500)
    except PyMongoError as exc:
        logger.exception("MongoDB failed while loading events for optimization")
        raise mongo_http_exception(exc) from exc
    if not events:
        return {"recommendation": "No calendar events found to optimize."}

    events_text = "\n".join(
        f"{event.get('title', 'Untitled')} — {event.get('time_slot', 'time not set')}"
        for event in events
    )
    recommendation = await run_in_threadpool(calendar_agent.resolve_schedule_conflict, events_text)
    return {"recommendation": recommendation}


@router.get("/{event_id}", response_model=CalendarEventResponse)
async def get_calendar_event(event_id: str, db=Depends(get_database), current_user=Depends(get_current_user)):
    object_id = parse_object_id(event_id, "Calendar event")
    try:
        event = await db["calendar_events"].find_one({"_id": object_id, "owner_id": current_user["_id"]})
    except PyMongoError as exc:
        logger.exception("MongoDB failed while fetching calendar event %s", event_id)
        raise mongo_http_exception(exc) from exc
    if event is None:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    return serialize_document(event)


@router.patch("/{event_id}", response_model=CalendarEventResponse)
async def update_calendar_event(event_id: str, event: CalendarEventPatch, db=Depends(get_database), current_user=Depends(get_current_user)):
    object_id = parse_object_id(event_id, "Calendar event")
    updates = event.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=422, detail="Provide at least one event field to update")
    if any(value is None for value in updates.values()):
        raise HTTPException(status_code=422, detail="Calendar event fields cannot be null")
    updates["updated_at"] = datetime.now(timezone.utc)
    try:
        event_filter = {"_id": object_id, "owner_id": current_user["_id"]}
        result = await db["calendar_events"].update_one(event_filter, {"$set": updates})
        saved = await db["calendar_events"].find_one(event_filter) if result.matched_count else None
    except PyMongoError as exc:
        logger.exception("MongoDB failed while updating calendar event %s", event_id)
        raise mongo_http_exception(exc) from exc
    if saved is None:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    return serialize_document(saved)


@router.delete("/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_calendar_event(event_id: str, response: Response, db=Depends(get_database), current_user=Depends(get_current_user)):
    object_id = parse_object_id(event_id, "Calendar event")
    try:
        result = await db["calendar_events"].delete_one({"_id": object_id, "owner_id": current_user["_id"]})
    except PyMongoError as exc:
        logger.exception("MongoDB failed while deleting calendar event %s", event_id)
        raise mongo_http_exception(exc) from exc
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Calendar event not found")
    response.status_code = status.HTTP_204_NO_CONTENT
