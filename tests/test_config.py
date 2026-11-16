import pytest
from ard_intelligence.config import Settings
from ard_intelligence.providers import OpenAICompatibleProvider

def test_config_provider_validation(monkeypatch):
    monkeypatch.setenv("ARD_MODEL_PROVIDER", "unknown")
    with pytest.raises(ValueError):
        Settings.from_env()

def test_remote_provider_requires_endpoint_and_model():
    with pytest.raises(ValueError):
        OpenAICompatibleProvider("", "", "")
