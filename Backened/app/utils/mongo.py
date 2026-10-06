from bson import ObjectId
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder


def parse_object_id(value: str, resource_name: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{resource_name} not found",
        )
    return ObjectId(value)


def serialize_document(document: dict) -> dict:
    serialized = dict(document)
    serialized["id"] = str(serialized.pop("_id"))
    serialized.pop("owner_id", None)
    return jsonable_encoder(serialized, custom_encoder={ObjectId: str})
