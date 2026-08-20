from __future__ import annotations

import hashlib
import hmac
import secrets

from app.domain.sessions import AnonymousSession


class MemorySessionVault:
    def __init__(self, *, hmac_secret: str) -> None:
        self._hmac_secret = hmac_secret.encode()
        self._sessions: dict[str, AnonymousSession] = {}

    def _csrf_digest(self, csrf_token: str) -> str:
        return hmac.new(self._hmac_secret, csrf_token.encode(), hashlib.sha256).hexdigest()

    def create_anonymous(self) -> tuple[AnonymousSession, str]:
        csrf_token = secrets.token_urlsafe(32)
        session = AnonymousSession.create(csrf_token_hash=self._csrf_digest(csrf_token))
        self._sessions[str(session.session_id)] = session
        return session, csrf_token

    def clear(self) -> None:
        self._sessions.clear()
