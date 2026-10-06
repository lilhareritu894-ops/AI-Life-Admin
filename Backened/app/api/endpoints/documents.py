import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile, status
from pymongo.errors import PyMongoError
from starlette.concurrency import run_in_threadpool

from app.api.endpoints.auth import get_current_user
from app.db.session import get_database, mongo_http_exception
from app.schemas.document import DocumentCreate, DocumentPatch, DocumentResponse
from app.services.doc_agent import doc_agent
from app.utils.file_parser import extract_text_from_file
from app.utils.mongo import parse_object_id, serialize_document

router = APIRouter()
logger = logging.getLogger(__name__)
MAX_UPLOAD_BYTES = 10 * 1024 * 1024


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(document: DocumentCreate, db=Depends(get_database), current_user=Depends(get_current_user)):
    record = document.model_dump()
    record.update(owner_id=current_user["_id"], created_at=datetime.now(timezone.utc))
    try:
        result = await db["documents"].insert_one(record)
    except PyMongoError as exc:
        logger.exception("MongoDB failed while creating a document")
        raise mongo_http_exception(exc) from exc
    record["_id"] = result.inserted_id
    return serialize_document(record)


@router.post("/scan", status_code=status.HTTP_201_CREATED)
async def scan_document(file: UploadFile = File(...), db=Depends(get_database), current_user=Depends(get_current_user)):
    filename = file.filename or "upload"
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="File must be 10 MB or smaller")
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    try:
        ai_summary = await run_in_threadpool(doc_agent.parse_uploaded_document, filename, content)
    except ValueError as exc:
        raise HTTPException(status_code=415, detail=str(exc)) from exc
    document = {
        "owner_id": current_user["_id"],
        "filename": filename,
        "doc_type": "document",
        "extracted_text": ai_summary,
        "created_at": datetime.now(timezone.utc),
    }
    try:
        result = await db["documents"].insert_one(document)
    except PyMongoError as exc:
        logger.exception("MongoDB failed while saving a scanned document")
        raise mongo_http_exception(exc) from exc
    document["_id"] = result.inserted_id
    return serialize_document(document)


@router.get("/", response_model=list[DocumentResponse])
async def list_documents(
    db=Depends(get_database),
    current_user=Depends(get_current_user),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    try:
        documents = await (
            db["documents"]
            .find({"owner_id": current_user["_id"]})
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
            .to_list(length=limit)
        )
    except PyMongoError as exc:
        logger.exception("MongoDB failed while listing documents")
        raise mongo_http_exception(exc) from exc
    return [serialize_document(document) for document in documents]


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: str, db=Depends(get_database), current_user=Depends(get_current_user)):
    object_id = parse_object_id(document_id, "Document")
    try:
        document = await db["documents"].find_one({"_id": object_id, "owner_id": current_user["_id"]})
    except PyMongoError as exc:
        logger.exception("MongoDB failed while fetching document %s", document_id)
        raise mongo_http_exception(exc) from exc
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return serialize_document(document)


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(document_id: str, document: DocumentPatch, db=Depends(get_database), current_user=Depends(get_current_user)):
    object_id = parse_object_id(document_id, "Document")
    updates = document.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=422, detail="Provide at least one document field to update")
    if any(value is None for value in updates.values()):
        raise HTTPException(status_code=422, detail="Document fields cannot be null")
    updates["updated_at"] = datetime.now(timezone.utc)
    try:
        document_filter = {"_id": object_id, "owner_id": current_user["_id"]}
        result = await db["documents"].update_one(document_filter, {"$set": updates})
        saved = await db["documents"].find_one(document_filter) if result.matched_count else None
    except PyMongoError as exc:
        logger.exception("MongoDB failed while updating document %s", document_id)
        raise mongo_http_exception(exc) from exc
    if saved is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return serialize_document(saved)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(document_id: str, response: Response, db=Depends(get_database), current_user=Depends(get_current_user)):
    object_id = parse_object_id(document_id, "Document")
    try:
        result = await db["documents"].delete_one({"_id": object_id, "owner_id": current_user["_id"]})
    except PyMongoError as exc:
        logger.exception("MongoDB failed while deleting document %s", document_id)
        raise mongo_http_exception(exc) from exc
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    response.status_code = status.HTTP_204_NO_CONTENT
