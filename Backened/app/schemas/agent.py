from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class AgentPromptRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(min_length=1, max_length=20_000)


class AgentRunPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str = Field(min_length=1, max_length=20_000)


class AgentResponse(BaseModel):
    id: str
    agent_name: str
    prompt: str
    response: str
    created_at: datetime
    updated_at: datetime | None = None
