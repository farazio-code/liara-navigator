from dataclasses import fields
from datetime import UTC, datetime, timedelta

from app.telemetry.store import MemoryTelemetryStore, TelemetryEvent


def test_telemetry_schema_cannot_accept_content_or_resource_identity() -> None:
    assert {field.name for field in fields(TelemetryEvent)} == {
        "event_type",
        "topic",
        "outcome",
        "model_calls",
        "created_at",
    }


def test_memory_telemetry_prunes_events_older_than_thirty_days() -> None:
    store = MemoryTelemetryStore()
    now = datetime(2026, 8, 21, tzinfo=UTC)
    store.record(
        event_type="turn",
        topic="dns",
        outcome="answer",
        model_calls=1,
        now=now - timedelta(days=31),
    )
    store.record(event_type="ticket", topic="other", outcome="accepted_mock", now=now)

    removed = store.prune(now=now)

    assert removed == 1
    assert len(store.snapshot()) == 1
