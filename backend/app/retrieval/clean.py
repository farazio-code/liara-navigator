import re

BLOCK_PATTERN = re.compile(r"<(script|style|nav)[^>]*>.*?</\1>", re.IGNORECASE | re.DOTALL)
IMPORT_PATTERN = re.compile(r"^[ \t]*(?:import|export)\s+.*$", re.MULTILINE)
JSX_PATTERN = re.compile(r"</?[A-Z][^>]*>")
SPACE_PATTERN = re.compile(r"[ \t]+")


def clean_document(raw: str) -> str:
    cleaned = BLOCK_PATTERN.sub("", raw)
    cleaned = IMPORT_PATTERN.sub("", cleaned)
    cleaned = JSX_PATTERN.sub("", cleaned)
    cleaned = "\n".join(SPACE_PATTERN.sub(" ", line).strip() for line in cleaned.splitlines())
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()
