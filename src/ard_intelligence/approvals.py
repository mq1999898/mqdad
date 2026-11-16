"""Approval tokens are scoped, expiring, and consumed once."""
from __future__ import annotations
from dataclasses import dataclass
import secrets
import time

@dataclass
class _Grant:
    scope: str
    expires: float

class ApprovalManager:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._grants: dict[str, _Grant] = {}

    def issue(self, scope: str, *, user_confirmed: bool) -> str:
        if not user_confirmed or not scope.strip():
            raise PermissionError("Explicit user confirmation and a non-empty scope are required")
        token = secrets.token_urlsafe(24)
        self._grants[token] = _Grant(scope, time.monotonic() + self.ttl_seconds)
        return token

    def consume(self, token: str, scope: str) -> bool:
        grant = self._grants.pop(token, None)
        return bool(grant and grant.scope == scope and grant.expires >= time.monotonic())
