from __future__ import annotations

import hashlib
import json
from collections.abc import AsyncIterator
from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Header, Request
from fastapi.responses import StreamingResponse
from pydantic import Field

from app.api.schemas import StrictModel
from app.application.router import Topic
from app.security.log_sanitizer import sanitize_logs


class TurnRequest(StrictModel):
    client_request_id: str = Field(min_length=8, max_length=64, pattern=r"^[a-zA-Z0-9_-]+$")
    topic: Topic
    message: str = Field(min_length=4, max_length=4000)
    service_ref: str | None = Field(default=None, min_length=8, max_length=80)


router = APIRouter(prefix="/turns", tags=["Turns"])


def _event(name: str, payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
    return f"event: {name}\ndata: {encoded}\n\n"


@router.post("/stream", response_class=StreamingResponse)
async def stream_turn(
    request: Request,
    body: TurnRequest,
    csrf_token: Annotated[str | None, Header(alias="X-CSRF-Token")] = None,
) -> StreamingResponse:
    session = request.app.state.session_vault.get(request.cookies.get("ln_session"))
    session_id = str(session.session_id)
    request.app.state.session_vault.verify_csrf(session_id, csrf_token)
    digest = hashlib.sha256(body.model_dump_json().encode()).hexdigest()
    cached = request.app.state.session_vault.get_cached_turn(
        session_id, body.client_request_id, digest
    )
    if cached is None:
        request.app.state.rate_limiter.check(
            session_id, "turn", limit=20, window_seconds=600
        )
        stream = _event("request.accepted", {"request_id": body.client_request_id})
        runtime_evidence = None
        if body.topic == "paas" and body.service_ref is not None:
            service_id = request.app.state.session_vault.resolve_resource(
                session_id, body.service_ref, kind="service"
            )
            stream += _event("agent.fetching_logs", {"service_ref": body.service_ref})
            raw_lines, upstream_truncated = request.app.state.fake_liara.logs(
                user_id="demo-user", service_id=service_id, limit=100
            )
            sanitized = sanitize_logs(raw_lines)
            runtime_evidence = sanitized.render_for_model()
            stream += _event(
                "agent.sanitizing_logs",
                {
                    "lines": len(sanitized.lines),
                    "truncated": upstream_truncated or sanitized.truncated,
                },
            )
        result = await request.app.state.agent.run(
            topic=body.topic, message=body.message, runtime_evidence=runtime_evidence
        )
        if result.status != "clarification":
            stream += _event("agent.searching", {"topic": body.topic})
        if result.read_chunks:
            stream += _event("agent.reading", {"chunks": result.read_chunks})
        stream += _event(
            "request.completed",
            {
                "status": result.status,
                "message": result.message,
                "claims": [asdict(claim) for claim in result.claims],
                "model_calls": result.model_calls,
            },
        )
        request.app.state.session_vault.cache_turn(
            session_id, body.client_request_id, digest, stream
        )
        request.app.state.telemetry.record(
            event_type="turn",
            topic=body.topic,
            outcome=result.status,
            model_calls=result.model_calls,
        )
    else:
        stream = cached

    async def body_stream() -> AsyncIterator[str]:
        yield stream

    return StreamingResponse(
        body_stream(),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no"},
    )
