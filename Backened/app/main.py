"""FastAPI entry point for the AI Life Admin backend."""

from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from app.api.router import api_router
from app.core.config import settings
from app.db.session import close_mongo_connection, connect_to_mongo, db_instance, mongo_error_detail
from app.services.llm_service import LLMConfigurationError, LLMProviderError

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    await connect_to_mongo()
    try:
        yield
    finally:
        await close_mongo_connection()


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Manage tasks, documents, and calendar actions with AI assistance.",
    version="0.1.0",
    lifespan=lifespan,
)


@app.exception_handler(LLMConfigurationError)
async def llm_configuration_error_handler(_, exc: LLMConfigurationError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(LLMProviderError)
async def llm_provider_error_handler(_, exc: LLMProviderError):
    return JSONResponse(status_code=502, content={"detail": str(exc)})

origins = [
    origin.strip()
    for origin in settings.CORS_ORIGINS.split(",")
    if origin.strip() and origin.strip() != "*"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["health"])
async def root():
    return {"message": f"{settings.PROJECT_NAME} API is running", "docs": "/docs"}


@app.get("/health", tags=["health"])
async def health_check():
    client = db_instance.client
    if client is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="MongoDB client is not initialized")
    try:
        await client.admin.command("ping")
    except PyMongoError as exc:
        logger.exception("MongoDB health check failed")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=mongo_error_detail(exc),
        ) from exc
    return {"status": "ok", "database": "connected"}
