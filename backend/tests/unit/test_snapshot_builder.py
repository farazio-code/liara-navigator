# ruff: noqa: RUF001
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest
from app.domain.errors import AppError
from app.retrieval.snapshot_builder import (
    build_records,
    build_snapshot,
    clean_mdx,
    collect_source_files,
)
from app.retrieval.snapshot_loader import validate_snapshot


def _write_page(root: Path, relative: str, title: str, body: str) -> None:
    path = root / "src" / "pages" / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        f'import Layout from "@/components/Layout";\n'
        f"<Head><title>{title}</title></Head>\n"
        f"# {title}\n"
        '<Section id="setup" title="راه‌اندازی" />\n'
        f"<p>{body}</p>\n",
        encoding="utf-8",
    )


def _fixture_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "docs"
    pages = {
        "paas/django/deploy.mdx": (
            "استقرار Django",
            "برای استقرار برنامه جنگو ابتدا تنظیمات برنامه و وابستگی‌ها را بررسی کنید.",
        ),
        "paas/static/deploy.mdx": (
            "استقرار Static",
            "فایل‌های خروجی برنامه استاتیک باید در پوشه خروجی صحیح قرار بگیرند.",
        ),
        "paas/domains/use-cdn.mdx": (
            "فعال‌سازی CDN",
            "برای فعال‌سازی شبکه توزیع محتوا ابتدا دامنه برنامه را متصل کنید.",
        ),
        "paas/domains/enable-ssl.mdx": (
            "فعال‌سازی SSL",
            "برای صدور گواهی امن باید رکورد دامنه به‌درستی تنظیم شده باشد.",
        ),
        "dns-management-system/add-record.mdx": (
            "مدیریت DNS",
            "رکورد موردنیاز را در سامانه مدیریت دامنه ایجاد و ذخیره کنید.",
        ),
        "overview/about.mdx": (
            "معرفی لیارا",
            "لیارا خدمات ابری گوناگون را برای میزبانی و اجرای برنامه‌ها ارائه می‌کند.",
        ),
    }
    for relative, (title, body) in pages.items():
        _write_page(repo, relative, title, body)
    subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "snapshot@test.invalid"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.name", "Snapshot Test"], cwd=repo, check=True)
    subprocess.run(["git", "add", "."], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-qm", "fixture"], cwd=repo, check=True)
    return repo


def test_clean_mdx_preserves_content_code_and_explicit_anchor() -> None:
    raw = """
import Layout from "@/components/Layout";
<Head><title>راهنمای Django</title><meta name="x" /></Head>
<Section id="liara-json" title="فایل liara.json" />
<p className="copy">تنظیمات برنامه را بررسی کنید.</p>
<Highlight className="json">{`{"platform":"django"}`}</Highlight>
"""

    title, cleaned = clean_mdx(raw)

    assert title == "راهنمای Django"
    assert "## فایل liara.json <!-- anchor:liara-json -->" in cleaned
    assert "تنظیمات برنامه را بررسی کنید." in cleaned
    assert '"platform":"django"' in cleaned
    assert "className" not in cleaned
    assert "import Layout" not in cleaned


def test_builder_keeps_static_platform_and_emits_runtime_schema(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)

    files = collect_source_files(repo)
    records = build_records(repo, max_chars=800)

    assert any("paas/static" in path.as_posix() for path in files)
    assert {record["topic"] for record in records} == {"paas", "cdn", "ssl", "dns", "other"}
    assert any(record["platform"] == "static" for record in records)
    assert all(
        set(record) == {"chunk_id", "title", "heading", "url", "topic", "platform", "content"}
        for record in records
    )
    assert all(str(record["url"]).startswith("https://docs.liara.ir/") for record in records)


def test_snapshot_is_versioned_hashed_valid_and_idempotent(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    output = tmp_path / "snapshots"

    first = build_snapshot(repo, output, max_chars=800, min_chunks=5)
    repeated = build_snapshot(repo, output, max_chars=800, min_chunks=5)
    manifest = validate_snapshot(first.directory)
    raw_manifest = json.loads((first.directory / "manifest.json").read_text())

    assert repeated.directory == first.directory
    assert manifest.version == first.version
    assert manifest.source_commit == first.source_commit
    assert raw_manifest["topic_counts"] == first.topic_counts


def test_snapshot_validator_rejects_wrong_chunk_schema(tmp_path: Path) -> None:
    repo = _fixture_repo(tmp_path)
    result = build_snapshot(repo, tmp_path / "snapshots", max_chars=800, min_chunks=5)
    chunks_path = result.directory / "chunks.jsonl"
    manifest_path = result.directory / "manifest.json"
    rows = [json.loads(line) for line in chunks_path.read_text().splitlines()]
    del rows[0]["heading"]
    chunks_text = "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows)
    manifest = json.loads(manifest_path.read_text())
    manifest["chunks_sha256"] = hashlib.sha256(chunks_text.encode()).hexdigest()
    chunks_path.write_text(chunks_text)
    manifest_path.write_text(json.dumps(manifest))

    with pytest.raises(AppError):
        validate_snapshot(result.directory)
