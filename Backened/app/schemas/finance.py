from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    category: str = Field(default="General", min_length=1, max_length=100)
    amount: float = Field(gt=0, allow_inf_nan=False)
    kind: Literal["income", "expense"]
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class TransactionPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    category: str | None = Field(default=None, min_length=1, max_length=100)
    amount: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    kind: Literal["income", "expense"] | None = None
    occurred_at: datetime | None = None


class TransactionResponse(TransactionCreate):
    id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None