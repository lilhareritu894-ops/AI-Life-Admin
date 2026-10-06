from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class DocumentFields(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: str = Field(min_length=1, max_length=255)
    doc_type: str = Field(default="document", min_length=1, max_length=100)
    extracted_text: str = Field(default="", max_length=100_000)


class DocumentCreate(DocumentFields):
    pass


class DocumentPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    filename: str | None = Field(default=None, min_length=1, max_length=255)
    doc_type: str | None = Field(default=None, min_length=1, max_length=100)
    extracted_text: str | None = Field(default=None, max_length=100_000)


class DocumentResponse(DocumentFields):
    id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
