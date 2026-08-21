from __future__ import annotations

import re
from dataclasses import dataclass

CONTROL_CHARACTERS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
SECRET_ASSIGNMENT = re.compile(
    r"(?i)\b(password|passwd|token|api[_-]?key|secret)\s*[=:]\s*[^\s,;]+"
)
CONNECTION_CREDENTIALS = re.compile(r"(?i)([a-z][a-z0-9+.-]*://[^:/\s]+:)[^@\s]+(@)")
INSTRUCTION_INJECTION = re.compile(
    r"(?i).*(ignore|disregard|forget).*(instructions?|system prompt).*$"
)


@dataclass(frozen=True, slots=True)
class SanitizedLogLine:
    timestamp: str
    stream: str
    message: str


@dataclass(frozen=True, slots=True)
class SanitizedLogBatch:
    lines: list[SanitizedLogLine]
    truncated: bool

    def render_for_model(self) -> str:
        body = "\n".join(
            f"[{line.timestamp}] {line.stream}: {line.message}" for line in self.lines
        )
        return f"<UNTRUSTED_SERVICE_LOGS>\n{body}\n</UNTRUSTED_SERVICE_LOGS>"


def sanitize_logs(
    lines: list[dict[str, str]], *, max_lines: int = 100, max_line_chars: int = 500
) -> SanitizedLogBatch:
    selected = lines[-max_lines:]
    sanitized: list[SanitizedLogLine] = []
    for line in selected:
        message = CONTROL_CHARACTERS.sub("", line["message"])
        message = SECRET_ASSIGNMENT.sub(lambda match: f"{match.group(1)}=[REDACTED]", message)
        message = CONNECTION_CREDENTIALS.sub(r"\1[REDACTED]\2", message)
        if INSTRUCTION_INJECTION.match(message):
            message = "[UNTRUSTED_INSTRUCTION_REMOVED]"
        message = message[:max_line_chars]
        sanitized.append(
            SanitizedLogLine(
                timestamp=line["timestamp"], stream=line["stream"], message=message
            )
        )
    truncated = len(lines) > max_lines or any(
        len(line["message"]) > max_line_chars for line in selected
    )
    return SanitizedLogBatch(lines=sanitized, truncated=truncated)
