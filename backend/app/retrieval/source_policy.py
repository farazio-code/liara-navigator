from urllib.parse import urlparse


def is_allowed_source(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        return False
    if parsed.netloc == "docs.liara.ir":
        return True
    if parsed.netloc != "github.com":
        return False
    path = parsed.path.rstrip("/")
    if not path.startswith("/liara-cloud/docs/"):
        return False
    forbidden = ("/issues/", "/pull/", "/pulls/", "/discussions/", "/forks/")
    return not any(fragment in f"{path}/" for fragment in forbidden)
