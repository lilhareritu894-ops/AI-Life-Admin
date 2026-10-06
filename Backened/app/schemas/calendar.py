from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CalendarEventFields(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    time_slot: str = Field(min_length=1, max_length=100)
    status: str = Field(default="Scheduled", min_length=1, max_length=50)


class CalendarEventCreate(CalendarEventFields):
    pass


class CalendarEventPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    time_slot: str | None = Field(default=None, min_length=1, max_length=100)
    status: str | None = Field(default=None, min_length=1, max_length=50)


class CalendarEventResponse(CalendarEventFields):
    id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None
