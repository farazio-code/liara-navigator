from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from uuid import UUID, uuid4


class SessionStatus(StrEnum):
    ACTIVE = "active"
    DISCONNECTED = "disconnected"
    EXPIRED = "expired"


class ConnectionState(StrEnum):
    ANONYMOUS = "anonymous"
    VALIDATING = "validating"
    CONNECTED = "connected"


@dataclass(frozen=True, slots=True)
class AnonymousSession:
    session_id: UUID
    created_at: datetime
    last_activity_at: datetime
    idle_expires_at: datetime
    absolute_expires_at: datetime
    csrf_token_hash: str
    status: SessionStatus = SessionStatus.ACTIVE
    connection_state: ConnectionState = ConnectionState.ANONYMOUS

    @classmethod
    def create(cls, *, csrf_token_hash: str, now: datetime | None = None) -> AnonymousSession:
        created_at = now or datetime.now(UTC)
        return cls(
            session_id=uuid4(),
            created_at=created_at,
            last_activity_at=created_at,
            idle_expires_at=created_at + timedelta(minutes=30),
            absolute_expires_at=created_at + timedelta(hours=2),
            csrf_token_hash=csrf_token_hash,
        )
