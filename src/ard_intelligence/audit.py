"""Audit logging configuration."""
import logging
from pathlib import Path

def configure_logging(data_dir: Path) -> None:
    data_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s", handlers=[logging.FileHandler(data_dir / "ard.log", encoding="utf-8"), logging.StreamHandler()])
