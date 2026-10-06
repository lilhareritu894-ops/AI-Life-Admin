import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pymongo.errors import PyMongoError

from app.api.endpoints.auth import get_current_user
from app.db.session import get_database, mongo_http_exception
from app.schemas.finance import TransactionCreate, TransactionPatch, TransactionResponse
from app.utils.mongo import parse_object_id, serialize_document

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/summary")
async def get_finance_summary(db=Depends(get_database), current_user=Depends(get_current_user)):
    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    pipeline = [
        {"$match": {"owner_id": current_user["_id"]}},
        {
            "$group": {
                "_id": None,
                "income": {"$sum": {"$cond": [{"$eq": ["$kind", "income"]}, "$amount", 0]}},
                "expenses": {"$sum": {"$cond": [{"$eq": ["$kind", "expense"]}, "$amount", 0]}},
                "month_income": {
                    "$sum": {
                        "$cond": [
                            {"$and": [{"$eq": ["$kind", "income"]}, {"$gte": ["$occurred_at", month_start]}]},
                            "$amount",
                            0,
                        ]
                    }
                },
                "month_expenses": {
                    "$sum": {
                        "$cond": [
                            {"$and": [{"$eq": ["$kind", "expense"]}, {"$gte": ["$occurred_at", month_start]}]},
                            "$amount",
                            0,
                        ]
                    }
                },
            }
        },
    ]
    try:
        totals = await db["transactions"].aggregate(pipeline).to_list(length=1)
    except PyMongoError as exc:
        logger.exception("MongoDB failed while calculating finance summary")
        raise mongo_http_exception(exc) from exc
    totals = totals[0] if totals else {}
    income = float(totals.get("income", 0))
    expenses = float(totals.get("expenses", 0))
    return {
        "currency": "USD",
        "balance": income - expenses,
        "income": income,
        "expenses": expenses,
        "month_income": float(totals.get("month_income", 0)),
        "month_expenses": float(totals.get("month_expenses", 0)),
    }


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction: TransactionCreate, db=Depends(get_database), current_user=Depends(get_current_user)):
    record = transaction.model_dump()
    record.update(owner_id=current_user["_id"], created_at=datetime.now(timezone.utc))
    try:
        result = await db["transactions"].insert_one(record)
    except PyMongoError as exc:
        logger.exception("MongoDB failed while creating a transaction")
        raise mongo_http_exception(exc) from exc
    record["_id"] = result.inserted_id
    return serialize_document(record)


@router.get("/", response_model=list[TransactionResponse])
async def list_transactions(
    db=Depends(get_database),
    current_user=Depends(get_current_user),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    try:
        records = await (
            db["transactions"]
            .find({"owner_id": current_user["_id"]})
            .sort("occurred_at", -1)
            .skip(skip)
            .limit(limit)
            .to_list(length=limit)
        )
    except PyMongoError as exc:
        logger.exception("MongoDB failed while listing transactions")
        raise mongo_http_exception(exc) from exc
    return [serialize_document(record) for record in records]


@router.patch("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    transaction: TransactionPatch,
    db=Depends(get_database),
    current_user=Depends(get_current_user),
):
    object_id = parse_object_id(transaction_id, "Transaction")
    updates = transaction.model_dump(exclude_unset=True)
    if not updates or any(value is None for value in updates.values()):
        raise HTTPException(status_code=422, detail="Provide valid transaction fields to update")
    updates["updated_at"] = datetime.now(timezone.utc)
    transaction_filter = {"_id": object_id, "owner_id": current_user["_id"]}
    try:
        result = await db["transactions"].update_one(transaction_filter, {"$set": updates})
        record = await db["transactions"].find_one(transaction_filter) if result.matched_count else None
    except PyMongoError as exc:
        logger.exception("MongoDB failed while updating transaction %s", transaction_id)
        raise mongo_http_exception(exc) from exc
    if record is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return serialize_document(record)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: str,
    response: Response,
    db=Depends(get_database),
    current_user=Depends(get_current_user),
):
    object_id = parse_object_id(transaction_id, "Transaction")
    try:
        result = await db["transactions"].delete_one({"_id": object_id, "owner_id": current_user["_id"]})
    except PyMongoError as exc:
        logger.exception("MongoDB failed while deleting transaction %s", transaction_id)
        raise mongo_http_exception(exc) from exc
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")
    response.status_code = status.HTTP_204_NO_CONTENT