from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal


@dataclass(frozen=True, slots=True)
class TelemetryEvent:
    event_type: Literal["turn", "ticket"]
    topic: Literal["paas", "cdn", "ssl", "dns", "other"]
    outcome: str
    model_calls: int
    created_at: datetime


class MemoryTelemetryStore:
    def __init__(self) -> None:
        self._events: list[TelemetryEvent] = []

    def record(
        self,
        *,
        event_type: Literal["turn", "ticket"],
        topic: Literal["paas", "cdn", "ssl", "dns", "other"],
        outcome: str,
        model_calls: int = 0,
        now: datetime | None = None,
    ) -> None:
        self._events.append(
            TelemetryEvent(
                event_type=event_type,
                topic=topic,
                outcome=outcome,
                model_calls=model_calls,
                created_at=now or datetime.now(UTC),
            )
        )

    def prune(self, *, now: datetime | None = None, retention_days: int = 30) -> int:
        cutoff = (now or datetime.now(UTC)) - timedelta(days=retention_days)
        before = len(self._events)
        self._events = [event for event in self._events if event.created_at >= cutoff]
        return before - len(self._events)

    def snapshot(self) -> tuple[TelemetryEvent, ...]:
        return tuple(self._events)
