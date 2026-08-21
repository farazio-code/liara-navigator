from __future__ import annotations

import hashlib
import hmac
import secrets
from uuid import UUID

from app.domain.errors import AppError, ErrorCode
from app.domain.sessions import AnonymousSession


class MemorySessionVault:
    def __init__(self, *, hmac_secret: str) -> None:
        self._hmac_secret = hmac_secret.encode()
        self._sessions: dict[str, AnonymousSession] = {}
        self._resource_refs: dict[str, dict[str, tuple[str, str]]] = {}

    def _csrf_digest(self, csrf_token: str) -> str:
        return hmac.new(self._hmac_secret, csrf_token.encode(), hashlib.sha256).hexdigest()

    def create_anonymous(self) -> tuple[AnonymousSession, str]:
        csrf_token = secrets.token_urlsafe(32)
        session = AnonymousSession.create(csrf_token_hash=self._csrf_digest(csrf_token))
        self._sessions[str(session.session_id)] = session
        self._resource_refs[str(session.session_id)] = {}
        return session, csrf_token

    def get(self, session_id: str | None) -> AnonymousSession:
        if session_id is None:
            raise AppError(ErrorCode.SESSION_INVALID)
        try:
            normalized = str(UUID(session_id))
        except ValueError as error:
            raise AppError(ErrorCode.SESSION_INVALID) from error
        session = self._sessions.get(normalized)
        if session is None:
            raise AppError(ErrorCode.SESSION_INVALID)
        return session

    def bind_resource(self, session_id: str, *, kind: str, resource_id: str) -> str:
        digest = hmac.new(
            self._hmac_secret,
            f"{session_id}:{kind}:{resource_id}".encode(),
            hashlib.sha256,
        ).hexdigest()[:24]
        resource_ref = f"ref_{digest}"
        self._resource_refs[session_id][resource_ref] = (kind, resource_id)
        return resource_ref

    def resolve_resource(self, session_id: str, resource_ref: str, *, kind: str) -> str:
        binding = self._resource_refs.get(session_id, {}).get(resource_ref)
        if binding is None or binding[0] != kind:
            raise AppError(ErrorCode.RESOURCE_NOT_ALLOWED)
        return binding[1]

    def clear(self) -> None:
        self._sessions.clear()
        self._resource_refs.clear()
