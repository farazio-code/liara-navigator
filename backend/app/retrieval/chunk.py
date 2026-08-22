from __future__ import annotations

import re
from dataclasses import dataclass

HEADING = re.compile(r"^(#{1,6})\s+(.+)$")


@dataclass(frozen=True, slots=True)
class DocumentChunk:
    heading: str
    content: str


def chunk_markdown(document: str, *, max_chars: int = 1600) -> list[DocumentChunk]:
    sections: list[DocumentChunk] = []
    heading = "بدون عنوان"
    lines: list[str] = []
    in_code = False

    def flush() -> None:
        content = "\n".join(lines).strip()
        if not content:
            return
        if len(content) > max_chars:
            raise ValueError("A heading section exceeds max_chars; split the source heading first")
        sections.append(DocumentChunk(heading=heading, content=content))

    for raw_line in document.strip().splitlines():
        line = raw_line.strip()
        if line.startswith("```"):
            in_code = not in_code
        match = HEADING.match(line) if not in_code else None
        if match:
            flush()
            heading = match.group(2).strip()
            lines = []
            continue
        lines.append(line)
    flush()
    return sections
