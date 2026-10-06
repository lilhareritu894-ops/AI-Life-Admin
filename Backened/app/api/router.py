from fastapi import APIRouter
from app.api.endpoints import analytics, auth, calendar, documents, finance, agent, tasks

api_router = APIRouter()

api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])
api_router.include_router(calendar.router, prefix="/calendar", tags=["Calendar"])
api_router.include_router(agent.router, prefix="/agent", tags=["Master Agent"])
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(finance.router, prefix="/finance", tags=["Finance"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
