import logging
from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pymongo.errors import DuplicateKeyError, PyMongoError
from starlette.concurrency import run_in_threadpool

from app.core.security import (
    InvalidTokenError,
    create_access_token,
    decode_access_token,
    get_jwt_secret,
    hash_password,
    verify_password,
)
from app.db.session import get_database, mongo_http_exception
from app.schemas.user import UserCreate, UserDelete, UserLogin, UserPatch, UserResponse
from app.utils.mongo import serialize_document

router = APIRouter()
logger = logging.getLogger(__name__)
bearer_scheme = HTTPBearer(auto_error=False)


def _require_jwt_secret() -> None:
    try:
        get_jwt_secret()
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db=Depends(get_database),
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bearer token required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        payload = decode_access_token(credentials.credentials)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except InvalidTokenError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    subject = payload.get("sub")
    if not isinstance(subject, str) or not ObjectId.is_valid(subject):
        raise HTTPException(status_code=401, detail="Invalid token subject")
    try:
        user = await db["users"].find_one({"_id": ObjectId(subject)})
    except PyMongoError as exc:
        logger.exception("MongoDB failed while loading authenticated user")
        raise mongo_http_exception(exc) from exc
    if user is None:
        raise HTTPException(status_code=401, detail="User no longer exists")
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db=Depends(get_database)):
    _require_jwt_secret()
    email = str(user.email).strip().lower()
    try:
        await db["users"].create_index("email", unique=True)
        password_hash = await run_in_threadpool(hash_password, user.password)
        document = {
            "email": email,
            "password": password_hash,
            "created_at": datetime.now(timezone.utc),
        }
        result = await db["users"].insert_one(document)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=409, detail="Email is already registered") from exc
    except PyMongoError as exc:
        logger.exception("MongoDB failed while registering a user")
        raise mongo_http_exception(exc) from exc

    document["_id"] = result.inserted_id
    return serialize_document(document)


@router.post("/login")
async def login(user: UserLogin, db=Depends(get_database)):
    _require_jwt_secret()
    email = str(user.email).strip().lower()
    try:
        db_user = await db["users"].find_one({"email": email})
    except PyMongoError as exc:
        logger.exception("MongoDB failed during login")
        raise mongo_http_exception(exc) from exc
    if db_user is None or not await run_in_threadpool(verify_password, user.password, db_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": str(db_user["_id"])})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def read_current_user(user=Depends(get_current_user)):
    return serialize_document(user)


@router.patch("/me", response_model=UserResponse)
async def update_current_user(
    changes: UserPatch,
    db=Depends(get_database),
    user=Depends(get_current_user),
):
    if changes.email is None and changes.new_password is None:
        raise HTTPException(status_code=422, detail="Provide a new email or new_password")
    if not await run_in_threadpool(verify_password, changes.current_password, user["password"]):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    updates = {}
    if changes.email is not None:
        updates["email"] = str(changes.email).strip().lower()
    if changes.new_password is not None:
        try:
            updates["password"] = await run_in_threadpool(hash_password, changes.new_password)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    try:
        result = await db["users"].update_one({"_id": user["_id"]}, {"$set": updates})
        updated_user = await db["users"].find_one({"_id": user["_id"]}) if result.matched_count else None
    except DuplicateKeyError as exc:
        raise HTTPException(status_code=409, detail="Email is already registered") from exc
    except PyMongoError as exc:
        logger.exception("MongoDB failed while updating the authenticated user")
        raise mongo_http_exception(exc) from exc
    if updated_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_document(updated_user)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_current_user(
    request: UserDelete,
    response: Response,
    db=Depends(get_database),
    user=Depends(get_current_user),
):
    if not await run_in_threadpool(verify_password, request.password, user["password"]):
        raise HTTPException(status_code=401, detail="Password is incorrect")
    try:
        result = await db["users"].delete_one({"_id": user["_id"]})
    except PyMongoError as exc:
        logger.exception("MongoDB failed while deleting the authenticated user")
        raise mongo_http_exception(exc) from exc
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    response.status_code = status.HTTP_204_NO_CONTENT
