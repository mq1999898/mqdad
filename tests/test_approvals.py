from ard_intelligence.approvals import ApprovalManager
import pytest

def test_approval_is_scoped_and_one_time():
    manager = ApprovalManager()
    token = manager.issue("read:kali", user_confirmed=True)
    assert manager.consume(token, "write:kali") is False
    assert manager.consume(token, "read:kali") is False
    token = manager.issue("read:kali", user_confirmed=True)
    assert manager.consume(token, "read:kali") is True
    assert manager.consume(token, "read:kali") is False

def test_approval_requires_confirmation():
    with pytest.raises(PermissionError):
        ApprovalManager().issue("sensitive", user_confirmed=False)
