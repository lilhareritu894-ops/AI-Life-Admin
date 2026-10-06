from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskFields(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    due_date: str | None = None


class TaskCreate(TaskFields):
    pass


class TaskPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=5000)
    due_date: str | None = None
    is_completed: bool | None = None


class TaskInDB(TaskFields):
    id: str | None = None
    is_completed: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
