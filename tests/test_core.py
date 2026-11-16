from pathlib import Path

import pytest

from ard_intelligence.approvals import ApprovalManager
from ard_intelligence.config import Settings
from ard_intelligence.memory import MemoryStore
from ard_intelligence.orchestrator import Orchestrator
from ard_intelligence.providers import OfflineProvider
from ard_intelligence.sandbox import CodeSandbox
from ard_intelligence.tools import Tool, ToolRegistry


def test_settings_reject_unknown_provider(monkeypatch):
    monkeypatch.setenv("ARD_MODEL_PROVIDER", "unknown")
    with pytest.raises(ValueError):
        Settings.from_env()


def test_memory_round_trip_and_empty_search(tmp_path):
    memory = MemoryStore(tmp_path / "memory.sqlite3")
    memory.add_message("user", "hello")
    memory.add_knowledge("project", "ARD INTELLIGENCE")
    assert memory.history() == [("user", "hello")]
    assert memory.search("") == []
    assert memory.search("ARD") == [("project", "ARD INTELLIGENCE")]


def test_approval_is_scoped_and_single_use():
    approvals = ApprovalManager(ttl_seconds=30)
    token = approvals.issue("deploy", user_confirmed=True)
    assert approvals.consume(token, "other") is False
    # Tokens are consumed even when the scope does not match.
    assert approvals.consume(token, "deploy") is False


def test_approval_requires_confirmation():
    approvals = ApprovalManager()
    with pytest.raises(PermissionError):
        approvals.issue("deploy", user_confirmed=False)


def test_tool_registry_enforces_scope_and_approval():
    approvals = ApprovalManager()
    registry = ToolRegistry(approvals)
    registry.register(Tool("read", "knowledge:read", False, lambda value: value))
    assert registry.invoke("read", scopes={"knowledge:read"}, value="ok") == "ok"
    with pytest.raises(PermissionError):
        registry.invoke("read", scopes=set(), value="no")

    registry.register(Tool("write", "files:write", True, lambda: "written"))
    token = approvals.issue("files:write", user_confirmed=True)
    assert registry.invoke("write", scopes={"files:write"}, approval_token=token) == "written"
    with pytest.raises(PermissionError):
        registry.invoke("write", scopes={"files:write"}, approval_token=token)


def test_sandbox_stages_python_without_executing(tmp_path):
    sandbox = CodeSandbox(tmp_path / "staging")
    target = sandbox.stage("sample.py", "answer = 42\n")
    assert target.read_text(encoding="utf-8") == "answer = 42\n"
    with pytest.raises(ValueError):
        sandbox.stage("../outside.py", "bad = True")


def test_sandbox_rejects_invalid_python(tmp_path):
    sandbox = CodeSandbox(tmp_path / "staging")
    with pytest.raises(SyntaxError):
        sandbox.stage("broken.py", "def broken(:\n")


def test_orchestrator_routes_and_offline_response(tmp_path):
    memory = MemoryStore(tmp_path / "memory.sqlite3")
    orchestrator = Orchestrator(OfflineProvider(), memory)
    assert orchestrator.route("Please review this Python bug") == "developer"
    answer = orchestrator.handle("hello")
    assert "No model provider" in answer
    assert memory.history()[-2][0] == "user"
    assert memory.history()[-1][0] == "assistant"
