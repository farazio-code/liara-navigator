from __future__ import annotations

import re
import secrets
from typing import Annotated, Literal

from fastapi import APIRouter, Header, Request, status
from pydantic import Field

from app.api.schemas import StrictModel
from app.domain.errors import AppError, ErrorCode

SECRET_PATTERN = re.compile(
    r"(?i)\b(password|passwd|token|api[_-]?key|secret)\s*[=:]\s*[^\s,;]+"
)


class TicketRequest(StrictModel):
    topic: Literal["paas", "cdn", "ssl", "dns", "other"]
    subject: str = Field(min_length=10, max_length=120)
    description: str = Field(min_length=20, max_length=2000)
    handoff_summary: str | None = Field(default=None, max_length=1500)


class TicketResponse(StrictModel):
    ticket_ref: str
    status: Literal["accepted_mock"] = "accepted_mock"


router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=TicketResponse, status_code=status.HTTP_201_CREATED)
async def submit_ticket(
    request: Request,
    body: TicketRequest,
    csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> TicketResponse:
    session = request.app.state.session_vault.get(request.cookies.get("ln_session"))
    session_id = str(session.session_id)
    request.app.state.session_vault.verify_csrf(session_id, csrf_token)
    request.app.state.rate_limiter.check(
        session_id, "ticket", limit=10, window_seconds=600
    )
    content = "\n".join(
        value for value in (body.subject, body.description, body.handoff_summary) if value
    )
    if SECRET_PATTERN.search(content):
        raise AppError(ErrorCode.VALIDATION_FAILED)
    request.app.state.telemetry.record(
        event_type="ticket", topic=body.topic, outcome="accepted_mock"
    )
    return TicketResponse(ticket_ref=f"tkt_{secrets.token_hex(6)}")
