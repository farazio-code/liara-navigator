from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.errors import ErrorCode


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ErrorResponse(StrictModel):
    code: ErrorCode
    message: str = Field(max_length=240)
    request_id: UUID
    retryable: bool


class SessionSummary(StrictModel):
    status: Literal["active"] = "active"
    connection_state: Literal["anonymous", "connected"]
    idle_expires_at: datetime
    absolute_expires_at: datetime


class CreateSessionResponse(StrictModel):
    session: SessionSummary
    csrf_token: str = Field(min_length=32, max_length=256)


class LivenessResponse(StrictModel):
    status: Literal["alive"] = "alive"
