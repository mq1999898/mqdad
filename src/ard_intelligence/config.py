"""Configuration helpers with no implicit secret loading."""
from __future__ import annotations
import os
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class Settings:
    provider: str = "ollama"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"
    remote_base_url: str = ""
    remote_model: str = ""
    remote_api_key: str = ""
    data_dir: Path = Path.home() / ".ard-intelligence"

    @classmethod
    def from_env(cls) -> "Settings":
        data = os.getenv("ARD_DATA_DIR", "").strip()
        provider = os.getenv("ARD_MODEL_PROVIDER", "ollama").strip().lower()
        if provider not in {"ollama", "openai_compatible", "offline"}:
            raise ValueError("ARD_MODEL_PROVIDER must be ollama, openai_compatible, or offline")
        return cls(
            provider=provider,
            ollama_url=os.getenv("ARD_OLLAMA_URL", "http://localhost:11434").rstrip("/"),
            ollama_model=os.getenv("ARD_OLLAMA_MODEL", "llama3.2"),
            remote_base_url=os.getenv("ARD_REMOTE_BASE_URL", "").rstrip("/"),
            remote_model=os.getenv("ARD_REMOTE_MODEL", ""),
            remote_api_key=os.getenv("ARD_REMOTE_API_KEY", ""),
            data_dir=Path(data).expanduser() if data else Path.home() / ".ard-intelligence",
        )
