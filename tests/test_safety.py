from ard_intelligence.sandbox import CodeSandbox
from ard_intelligence.kali_ssh import ALLOWED_DIAGNOSTICS, KaliSSH
import pytest

def test_stage_python_without_execution(tmp_path):
    sandbox = CodeSandbox(tmp_path / "stage")
    path = sandbox.stage("sample.py", "print('safe to parse')\n")
    assert path.is_file()
    with pytest.raises(SyntaxError):
        sandbox.stage("broken.py", "if:")

def test_rejects_path_traversal(tmp_path):
    sandbox = CodeSandbox(tmp_path / "stage")
    with pytest.raises(ValueError):
        sandbox.stage("../escape.txt", "no")

def test_manual_approval_gate(tmp_path):
    sandbox = CodeSandbox(tmp_path / "stage")
    sandbox.stage("ok.txt", "ready")
    with pytest.raises(PermissionError):
        sandbox.approve_for_manual_review("ok.txt", user_approved=False)
    assert sandbox.approve_for_manual_review("ok.txt", user_approved=True).is_file()

def test_ssh_is_fixed_command_and_approval_gated():
    ssh = KaliSSH("localhost", "user", "known_hosts", "key")
    with pytest.raises(PermissionError):
        ssh.run_diagnostic("system_info", approved=False)
    with pytest.raises(ValueError):
        ssh.run_diagnostic("uname -a; malicious", approved=True)
    assert set(ALLOWED_DIAGNOSTICS) == {"system_info", "network_interfaces", "listening_sockets"}
