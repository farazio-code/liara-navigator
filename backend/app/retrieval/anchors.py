from urllib.parse import unquote, urlparse

from app.retrieval.source_policy import is_allowed_source


def validate_rendered_anchor(url: str, *, rendered_anchors: set[str]) -> None:
    if not is_allowed_source(url):
        raise ValueError("source is not on the official allowlist")
    anchor = unquote(urlparse(url).fragment)
    if anchor and anchor not in rendered_anchors:
        raise ValueError("broken source anchor")
