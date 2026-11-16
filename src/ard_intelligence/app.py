"""ARD desktop entry point. Core remains usable without the optional Qt dependency."""
from __future__ import annotations
import logging
from .config import Settings
from .memory import MemoryStore
from .orchestrator import Orchestrator
from .providers import OfflineProvider, OllamaProvider, OpenAICompatibleProvider
from .audit import configure_logging

def build_orchestrator(settings: Settings) -> Orchestrator:
    settings.data_dir.mkdir(parents=True, exist_ok=True)
    memory = MemoryStore(settings.data_dir / "memory.sqlite3")
    if settings.provider == "ollama":
        provider = OllamaProvider(settings.ollama_url, settings.ollama_model)
    elif settings.provider == "openai_compatible":
        provider = OpenAICompatibleProvider(settings.remote_base_url, settings.remote_model, settings.remote_api_key)
    else:
        provider = OfflineProvider()
    return Orchestrator(provider, memory)

def main() -> int:
    settings = Settings.from_env()
    configure_logging(settings.data_dir)
    try:
        from PySide6.QtWidgets import QApplication
        from .ui import MainWindow
    except ImportError:
        logging.getLogger(__name__).error("PySide6 is not installed. Install with: pip install -e '.[desktop]'")
        return 2
    app = QApplication([])
    window = MainWindow(build_orchestrator(settings), settings)
    window.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
