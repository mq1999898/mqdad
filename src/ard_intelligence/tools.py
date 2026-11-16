"""Scoped tool registry. Sensitive tools require one-time human approval."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any
from .approvals import ApprovalManager

@dataclass(frozen=True)
class Tool:
    name: str
    scope: str
    sensitive: bool
    handler: Callable[..., Any]

class ToolRegistry:
    def __init__(self, approvals: ApprovalManager):
        self.approvals = approvals
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        if tool.name in self._tools:
            raise ValueError(f"Tool already registered: {tool.name}")
        self._tools[tool.name] = tool

    def invoke(self, name: str, *, scopes: set[str], approval_token: str | None = None, **kwargs):
        tool = self._tools[name]
        if tool.scope not in scopes:
            raise PermissionError(f"Missing authorization scope: {tool.scope}")
        if tool.sensitive and not (approval_token and self.approvals.consume(approval_token, tool.scope)):
            raise PermissionError("A valid user approval token is required")
        return tool.handler(**kwargs)

    def names(self) -> tuple[str, ...]:
        return tuple(sorted(self._tools))
