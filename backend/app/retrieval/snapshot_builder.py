from __future__ import annotations

import hashlib
import html
import json
import re
import subprocess
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from app.retrieval.source_policy import is_allowed_source

Topic = Literal["paas", "cdn", "ssl", "dns", "other"]

PLATFORMS = {
    "angular",
    "django",
    "docker",
    "dotnet",
    "flask",
    "go",
    "laravel",
    "nextjs",
    "nodejs",
    "php",
    "python",
    "react",
    "static",
    "vue",
}
SOURCE_REPOSITORY = "https://github.com/liara-cloud/docs"

IMPORT_RE = re.compile(r"(?ms)^\s*(?:import|export)\b.*?;\s*$")
COMMENT_RE = re.compile(r"\{/\*.*?\*/\}", re.DOTALL)
TITLE_RE = re.compile(r"<title>(.*?)</title>", re.IGNORECASE | re.DOTALL)
HEAD_RE = re.compile(r"<Head\b[^>]*>.*?</Head>", re.IGNORECASE | re.DOTALL)
SECTION_RE = re.compile(r"<Section\b.*?/>", re.IGNORECASE | re.DOTALL)
ATTRIBUTE_RE = re.compile(r"([\w-]+)\s*=\s*(['\"])(.*?)\2", re.DOTALL)
TEMPLATE_RE = re.compile(r"\{`(.*?)`\}", re.DOTALL)
TAG_RE = re.compile(r"</?[A-Za-z][^>]*>", re.DOTALL)
HEADING_RE = re.compile(
    r"^(#{1,6})\s+(.+?)(?:\s+<!--\s*anchor:([^\s]+)\s*-->)?$"
)
MARKDOWN_LINK_RE = re.compile(r"\[([^]]+)]\([^)]+\)")
MARKDOWN_IMAGE_RE = re.compile(r"!\[([^]]*)]\([^)]+\)")
SPACE_RE = re.compile(r"[ \t]+")


@dataclass(frozen=True, slots=True)
class SourceDocument:
    source_path: str
    title: str
    url: str
    topic: Topic
    platform: str | None
    content: str


@dataclass(frozen=True, slots=True)
class Section:
    heading: str
    anchor: str | None
    content: str


@dataclass(frozen=True, slots=True)
class SnapshotResult:
    directory: Path
    version: str
    chunk_count: int
    topic_counts: dict[str, int]
    source_commit: str


def get_source_commit(repo_path: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_path,
        check=True,
        capture_output=True,
        text=True,
    )
    commit = result.stdout.strip()
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("source repository did not return a full commit SHA")
    return commit


def collect_source_files(repo_path: Path, docs_subdir: str = "src/pages") -> list[Path]:
    root = (repo_path / docs_subdir).resolve()
    if not root.is_dir() or not root.is_relative_to(repo_path.resolve()):
        raise ValueError("docs_subdir must be an existing directory inside the repository")
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and path.suffix.lower() in {".md", ".mdx"}
        and not any(part in {"node_modules", ".git", "drafts"} for part in path.parts)
    )


def clean_mdx(raw: str) -> tuple[str, str]:
    title_match = TITLE_RE.search(raw)
    explicit_title = _plain_text(title_match.group(1)) if title_match else ""
    cleaned = COMMENT_RE.sub("", raw)
    cleaned = IMPORT_RE.sub("", cleaned)
    cleaned = _replace_sections(cleaned)
    cleaned = TEMPLATE_RE.sub(lambda match: f"\n```\n{match.group(1).strip()}\n```\n", cleaned)
    cleaned = HEAD_RE.sub("", cleaned)
    cleaned = MARKDOWN_IMAGE_RE.sub(lambda match: match.group(1), cleaned)
    cleaned = MARKDOWN_LINK_RE.sub(lambda match: match.group(1), cleaned)
    cleaned = TAG_RE.sub("\n", cleaned)
    cleaned = cleaned.replace("<>", "\n").replace("</>", "\n")
    cleaned = html.unescape(cleaned)

    lines: list[str] = []
    in_code = False
    for raw_line in cleaned.splitlines():
        line = SPACE_RE.sub(" ", raw_line).strip()
        if line.startswith("```"):
            in_code = not in_code
            lines.append("```")
            continue
        if not in_code and _is_jsx_noise(line):
            continue
        lines.append(line)
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    first_heading = next(
        (match.group(2).strip() for line in lines if (match := HEADING_RE.match(line))),
        "",
    )
    return explicit_title or first_heading or "مستندات لیارا", text


def classify_source(relative_path: Path) -> tuple[Topic, str | None]:
    parts = relative_path.with_suffix("").parts
    normalized = "/".join(parts).lower()
    platform = parts[1] if len(parts) > 1 and parts[0] == "paas" and parts[1] in PLATFORMS else None
    if "use-cdn" in normalized or "/cdn" in normalized:
        return "cdn", platform
    if any(term in normalized for term in ("enable-ssl", "/ssl", "acme-challenge")):
        return "ssl", platform
    if parts[0] == "dns-management-system" or "/dns" in normalized:
        return "dns", platform
    if parts[0] == "paas":
        return "paas", platform
    return "other", platform


def source_url(relative_path: Path, base_url: str = "https://docs.liara.ir") -> str:
    route = relative_path.with_suffix("").as_posix()
    if route.endswith("/index"):
        route = route[: -len("/index")]
    return f"{base_url.rstrip('/')}/{route.lstrip('/')}"


def split_sections(document: str, fallback_heading: str) -> list[Section]:
    sections: list[Section] = []
    heading = fallback_heading
    anchor: str | None = None
    body: list[str] = []
    in_code = False

    def flush() -> None:
        content = "\n".join(body).strip()
        if content:
            sections.append(Section(heading=heading, anchor=anchor, content=content))

    for line in document.splitlines():
        if line.startswith("```"):
            in_code = not in_code
        match = HEADING_RE.match(line) if not in_code else None
        if match:
            flush()
            heading = _plain_text(match.group(2))
            anchor = match.group(3)
            body = []
        else:
            body.append(line)
    flush()
    return sections


def chunk_section(section: Section, max_chars: int = 1600) -> list[str]:
    if not 400 <= max_chars <= 4000:
        raise ValueError("max_chars must be between 400 and 4000")
    paragraphs = _paragraphs(section.content)
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        for piece in _split_long_text(paragraph, max_chars):
            candidate = f"{current}\n\n{piece}".strip()
            if current and len(candidate) > max_chars:
                chunks.append(current)
                current = piece
            else:
                current = candidate
    if current:
        chunks.append(current)
    return [chunk for chunk in chunks if len(_plain_text(chunk)) >= 40]


def build_records(
    repo_path: Path,
    *,
    docs_subdir: str = "src/pages",
    base_url: str = "https://docs.liara.ir",
    max_chars: int = 1600,
) -> list[dict[str, object]]:
    docs_root = repo_path / docs_subdir
    records: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for path in collect_source_files(repo_path, docs_subdir):
        relative = path.relative_to(docs_root)
        title, cleaned = clean_mdx(path.read_text(encoding="utf-8"))
        topic, platform = classify_source(relative)
        page_url = source_url(relative, base_url)
        if not is_allowed_source(page_url):
            raise ValueError(f"generated URL is outside the source allowlist: {page_url}")
        for section in split_sections(cleaned, title):
            for index, content in enumerate(chunk_section(section, max_chars), start=1):
                content_fingerprint = hashlib.sha256(_normalize(content).encode()).hexdigest()
                dedupe_key = (relative.as_posix(), content_fingerprint)
                if dedupe_key in seen:
                    continue
                seen.add(dedupe_key)
                identity = (
                    f"{relative.as_posix()}\0{section.heading}\0"
                    f"{index}\0{content_fingerprint}"
                )
                anchor = f"#{section.anchor}" if section.anchor else ""
                records.append(
                    {
                        "chunk_id": hashlib.sha256(identity.encode()).hexdigest()[:20],
                        "title": title,
                        "heading": section.heading,
                        "url": f"{page_url}{anchor}",
                        "topic": topic,
                        "platform": platform,
                        "content": content,
                    }
                )
    return records


def build_snapshot(
    repo_path: Path,
    output_root: Path,
    *,
    docs_subdir: str = "src/pages",
    base_url: str = "https://docs.liara.ir",
    max_chars: int = 1600,
    min_chunks: int = 100,
) -> SnapshotResult:
    source_commit = get_source_commit(repo_path)
    version = f"liara-docs-{source_commit[:12]}"
    records = build_records(
        repo_path,
        docs_subdir=docs_subdir,
        base_url=base_url,
        max_chars=max_chars,
    )
    if len(records) < min_chunks:
        raise ValueError(f"snapshot has only {len(records)} chunks; expected at least {min_chunks}")
    topic_counts = dict(sorted(Counter(str(record["topic"]) for record in records).items()))
    required_topics = {"paas", "cdn", "ssl", "dns", "other"}
    if not required_topics.issubset(topic_counts):
        missing = ", ".join(sorted(required_topics - topic_counts.keys()))
        raise ValueError(f"snapshot is missing required topics: {missing}")

    chunks_text = "".join(
        json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
        for record in records
    )
    manifest = {
        "schema_version": 1,
        "version": version,
        "chunk_count": len(records),
        "chunks_sha256": hashlib.sha256(chunks_text.encode()).hexdigest(),
        "source_repository": SOURCE_REPOSITORY,
        "source_commit": source_commit,
        "created_at": datetime.now(UTC).isoformat(),
        "topic_counts": topic_counts,
    }
    output_directory = output_root / version
    if output_directory.exists():
        existing_chunks = output_directory / "chunks.jsonl"
        existing_manifest = output_directory / "manifest.json"
        if (
            existing_chunks.is_file()
            and existing_manifest.is_file()
            and existing_chunks.read_text(encoding="utf-8") == chunks_text
        ):
            return SnapshotResult(
                output_directory, version, len(records), topic_counts, source_commit
            )
        raise FileExistsError(
            f"immutable snapshot already exists with different content: {output_directory}"
        )

    output_directory.mkdir(parents=True)
    (output_directory / "chunks.jsonl").write_text(chunks_text, encoding="utf-8")
    (output_directory / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return SnapshotResult(output_directory, version, len(records), topic_counts, source_commit)


def _replace_sections(text: str) -> str:
    def replace(match: re.Match[str]) -> str:
        attributes = {key: value for key, _, value in ATTRIBUTE_RE.findall(match.group(0))}
        title = attributes.get("title", "بخش مستندات").strip()
        anchor = attributes.get("id", "").strip()
        marker = f" <!-- anchor:{anchor} -->" if anchor else ""
        return f"\n## {title}{marker}\n"

    return SECTION_RE.sub(replace, text)


def _is_jsx_noise(line: str) -> bool:
    if not line:
        return False
    lowered = line.lower()
    if line in {"{", "}", "[", "]", "([", "])", "]},", "});", "/>"}:
        return True
    prefixes = (
        "tabs={",
        "content={",
        "className=",
        "classname=",
        "src=",
        "width=",
        "height=",
        "controls=",
        "property=",
        "target=",
        "alt=",
        "link:",
        "title:",
        "platform:",
    )
    if lowered.startswith(prefixes):
        return True
    if re.fullmatch(r"[\s{}()[\],;:.<>/=\"']+", line):
        return True
    return bool(re.match(r"^(?:const|let|var)\s+\w+\s*=", line))


def _paragraphs(text: str) -> list[str]:
    paragraphs: list[str] = []
    current: list[str] = []
    in_code = False
    for line in text.splitlines():
        if line.startswith("```"):
            in_code = not in_code
        if not line and not in_code:
            if current:
                paragraphs.append("\n".join(current).strip())
                current = []
            continue
        current.append(line)
    if current:
        paragraphs.append("\n".join(current).strip())
    return [paragraph for paragraph in paragraphs if paragraph]


def _split_long_text(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]
    lines = text.splitlines()
    pieces: list[str] = []
    current = ""
    for line in lines:
        sentences = re.split(r"(?<=[.!؟])\s+", line) if len(line) > max_chars else [line]
        for sentence in sentences:
            while len(sentence) > max_chars:
                if current:
                    pieces.append(current)
                    current = ""
                pieces.append(sentence[:max_chars])
                sentence = sentence[max_chars:]
            candidate = f"{current}\n{sentence}".strip()
            if current and len(candidate) > max_chars:
                pieces.append(current)
                current = sentence
            else:
                current = candidate
    if current:
        pieces.append(current)
    return pieces


def _plain_text(value: str) -> str:
    return SPACE_RE.sub(" ", TAG_RE.sub("", value)).strip()


def _normalize(value: str) -> str:
    return " ".join(value.lower().replace("ي", "ی").replace("ك", "ک").split())
