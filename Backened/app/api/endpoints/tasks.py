import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pymongo.errors import PyMongoError

from app.api.endpoints.auth import get_current_user
from app.db.session import get_database, mongo_http_exception
from app.schemas.task import TaskCreate, TaskInDB, TaskPatch
from app.utils.mongo import parse_object_id, serialize_document

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=TaskInDB, status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db=Depends(get_database), current_user=Depends(get_current_user)):
    document = task.model_dump()
    document.update(owner_id=current_user["_id"], is_completed=False, created_at=datetime.now(timezone.utc))
    try:
        result = await db["tasks"].insert_one(document)
    except PyMongoError as exc:
        logger.exception("MongoDB failed while creating a task")
        raise mongo_http_exception(exc) from exc

    document["_id"] = result.inserted_id
    return serialize_document(document)


@router.get("/", response_model=list[TaskInDB])
async def get_tasks(
    db=Depends(get_database),
    current_user=Depends(get_current_user),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    try:
        documents = await db["tasks"].find({"owner_id": current_user["_id"]}).sort("created_at", -1).skip(skip).limit(limit).to_list(length=limit)
    except PyMongoError as exc:
        logger.exception("MongoDB failed while fetching tasks")
        raise mongo_http_exception(exc) from exc
    return [serialize_document(document) for document in documents]


@router.get("/{task_id}", response_model=TaskInDB)
async def get_task(task_id: str, db=Depends(get_database), current_user=Depends(get_current_user)):
    object_id = parse_object_id(task_id, "Task")
    try:
        document = await db["tasks"].find_one({"_id": object_id, "owner_id": current_user["_id"]})
    except PyMongoError as exc:
        logger.exception("MongoDB failed while fetching task %s", task_id)
        raise mongo_http_exception(exc) from exc
    if document is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return serialize_document(document)


@router.patch("/{task_id}", response_model=TaskInDB)
async def update_task(task_id: str, task: TaskPatch, db=Depends(get_database), current_user=Depends(get_current_user)):
    object_id = parse_object_id(task_id, "Task")
    updates = task.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=422, detail="Provide at least one task field to update")
    if any(updates.get(field) is None for field in ("title", "is_completed") if field in updates):
        raise HTTPException(status_code=422, detail="title and is_completed cannot be null")
    updates["updated_at"] = datetime.now(timezone.utc)
    try:
        task_filter = {"_id": object_id, "owner_id": current_user["_id"]}
        result = await db["tasks"].update_one(task_filter, {"$set": updates})
        document = await db["tasks"].find_one(task_filter) if result.matched_count else None
    except PyMongoError as exc:
        logger.exception("MongoDB failed while updating task %s", task_id)
        raise mongo_http_exception(exc) from exc
    if document is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return serialize_document(document)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, response: Response, db=Depends(get_database), current_user=Depends(get_current_user)):
    object_id = parse_object_id(task_id, "Task")
    try:
        result = await db["tasks"].delete_one({"_id": object_id, "owner_id": current_user["_id"]})
    except PyMongoError as exc:
        logger.exception("MongoDB failed while deleting task %s", task_id)
        raise mongo_http_exception(exc) from exc
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Task not found")
    response.status_code = status.HTTP_204_NO_CONTENT
