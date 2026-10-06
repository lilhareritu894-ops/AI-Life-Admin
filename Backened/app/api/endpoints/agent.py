import asyncio
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pymongo.errors import PyMongoError

from app.api.endpoints.auth import get_current_user
from app.db.session import get_database, mongo_http_exception
from app.schemas.agent import AgentPromptRequest, AgentResponse, AgentRunPatch
from app.services.llm_service import llm_service
from app.utils.mongo import parse_object_id, serialize_document

router = APIRouter()
logger = logging.getLogger(__name__)
AGENT_NAME = "Executive Orchestrator Agent"


@router.post("/query", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def execute_master_agent(request: AgentPromptRequest, db=Depends(get_database), current_user=Depends(get_current_user)):
    response_text = await asyncio.to_thread(llm_service.generate_completion, request.prompt)
    run = {
        "agent_name": AGENT_NAME,
        "owner_id": current_user["_id"],
        "prompt": request.prompt,
        "response": response_text,
        "created_at": datetime.now(timezone.utc),
    }
    try:
        result = await db["agent_runs"].insert_one(run)
    except PyMongoError as exc:
        logger.exception("MongoDB failed while saving an agent run")
        raise mongo_http_exception(exc) from exc
    run["_id"] = result.inserted_id
    return serialize_document(run)


@router.get("/runs", response_model=list[AgentResponse])
async def list_agent_runs(
    db=Depends(get_database),
    current_user=Depends(get_current_user),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    try:
        runs = await (
            db["agent_runs"]
            .find({"owner_id": current_user["_id"]})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
            .to_list(length=limit)
        )
    except PyMongoError as exc:
        logger.exception("MongoDB failed while listing agent runs")
        raise mongo_http_exception(exc) from exc
    return [serialize_document(run) for run in runs]


@router.get("/runs/{run_id}", response_model=AgentResponse)
async def get_agent_run(run_id: str, db=Depends(get_database), current_user=Depends(get_current_user)):
    object_id = parse_object_id(run_id, "Agent run")
    try:
        run = await db["agent_runs"].find_one({"_id": object_id, "owner_id": current_user["_id"]})
    except PyMongoError as exc:
        logger.exception("MongoDB failed while fetching agent run %s", run_id)
        raise mongo_http_exception(exc) from exc
    if run is None:
        raise HTTPException(status_code=404, detail="Agent run not found")
    return serialize_document(run)


@router.patch("/runs/{run_id}", response_model=AgentResponse)
async def update_agent_run(run_id: str, request: AgentRunPatch, db=Depends(get_database), current_user=Depends(get_current_user)):
    object_id = parse_object_id(run_id, "Agent run")
    response_text = await asyncio.to_thread(llm_service.generate_completion, request.prompt)
    updates = {
        "prompt": request.prompt,
        "response": response_text,
        "updated_at": datetime.now(timezone.utc),
    }
    try:
        run_filter = {"_id": object_id, "owner_id": current_user["_id"]}
        result = await db["agent_runs"].update_one(run_filter, {"$set": updates})
        run = await db["agent_runs"].find_one(run_filter) if result.matched_count else None
    except PyMongoError as exc:
        logger.exception("MongoDB failed while updating agent run %s", run_id)
        raise mongo_http_exception(exc) from exc
    if run is None:
        raise HTTPException(status_code=404, detail="Agent run not found")
    return serialize_document(run)


@router.delete("/runs/{run_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent_run(run_id: str, response: Response, db=Depends(get_database), current_user=Depends(get_current_user)):
    object_id = parse_object_id(run_id, "Agent run")
    try:
        result = await db["agent_runs"].delete_one({"_id": object_id, "owner_id": current_user["_id"]})
    except PyMongoError as exc:
        logger.exception("MongoDB failed while deleting agent run %s", run_id)
        raise mongo_http_exception(exc) from exc
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Agent run not found")
    response.status_code = status.HTTP_204_NO_CONTENT
