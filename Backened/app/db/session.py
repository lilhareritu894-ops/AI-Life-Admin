"""MongoDB client lifecycle and FastAPI dependency."""

from urllib.parse import urlparse

from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException, status
from pymongo.errors import PyMongoError

from app.core.config import settings


class Database:
    client: AsyncIOMotorClient | None = None
    db = None


db_instance = Database()


def should_use_tls(database_url: str) -> bool:
    """Only enforce TLS for Atlas-style or remote MongoDB URIs."""
    parsed = urlparse(database_url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme.lower() == "mongodb+srv":
        return True
    if host in {"localhost", "127.0.0.1", "::1"}:
        return False
    return True


def mongo_error_detail(exc: PyMongoError) -> str:
    """Give API callers a safe, actionable hint without exposing the URI."""
    message = str(exc).lower()
    if "localhost:27017" in message or "127.0.0.1:27017" in message:
        return (
            "Local MongoDB connection was refused. Start the local MongoDB server or set DATABASE_URL "
            "to a reachable MongoDB Atlas URI in the backend .env file."
        )
    if "ssl handshake failed" in message or "tlsv1 alert internal error" in message:
        return (
            "MongoDB TLS handshake failed. Check the Atlas cluster hostname in "
            "DATABASE_URL and verify that your network, proxy, or firewall allows "
            "TLS connections to Atlas on port 27017."
        )
    if "authentication failed" in message or "bad auth" in message:
        return "MongoDB authentication failed. Check the Atlas database username and password in DATABASE_URL."
    if "timed out" in message or "serverselectiontimeouterror" in message:
        return (
            "MongoDB did not respond. Check DATABASE_URL, database status, network access, "
            "and outbound access to port 27017."
        )
    return f"MongoDB request failed ({type(exc).__name__}). See the API process log for details."


def mongo_http_exception(exc: PyMongoError) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail=mongo_error_detail(exc),
    )


async def connect_to_mongo() -> None:
    """Create the client; Motor connects lazily on the first database operation."""
    client_kwargs = {
        "serverSelectionTimeoutMS": 10000,
        "connectTimeoutMS": 10000,
    }
    if should_use_tls(settings.DATABASE_URL):
        client_kwargs["tls"] = True

    db_instance.client = AsyncIOMotorClient(settings.DATABASE_URL, **client_kwargs)
    db_instance.db = db_instance.client[settings.DATABASE_NAME]


async def close_mongo_connection() -> None:
    if db_instance.client is not None:
        db_instance.client.close()
        db_instance.client = None
        db_instance.db = None


def get_database():
    """Return the initialized database or a useful service-unavailable error."""
    if db_instance.db is None:
        from fastapi import HTTPException

        raise HTTPException(status_code=503, detail="Database is not initialized")
    return db_instance.db
