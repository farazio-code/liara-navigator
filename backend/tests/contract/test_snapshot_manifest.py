from pathlib import Path

from app.retrieval.snapshot_loader import validate_snapshot

FIXTURE = Path(__file__).parents[3] / "knowledge" / "snapshots" / "test-fixture"


def test_fixture_snapshot_manifest_hash_and_sources_are_valid() -> None:
    manifest = validate_snapshot(FIXTURE)

    assert manifest.version == "test-fixture"
    assert manifest.chunk_count == 6
    assert manifest.schema_version == 1
