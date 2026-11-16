"""Minimal PySide6 chat and health dashboard."""
from __future__ import annotations

import logging

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .config import Settings
from .orchestrator import Orchestrator

log = logging.getLogger(__name__)


class _ReplyWorker(QThread):
    finished_text = Signal(str)

    def __init__(self, orchestrator: Orchestrator, prompt: str):
        super().__init__()
        self.orchestrator, self.prompt = orchestrator, prompt

    def run(self):
        try:
            reply = self.orchestrator.handle(self.prompt)
        except Exception:
            log.exception("Unexpected error while handling a chat message")
            reply = "An unexpected internal error occurred. Check the application log."
        self.finished_text.emit(reply)


class MainWindow(QMainWindow):
    def __init__(self, orchestrator: Orchestrator, settings: Settings):
        super().__init__()
        self.orchestrator = orchestrator
        self.setWindowTitle("ARD INTELLIGENCE")
        self.resize(900, 650)
        root = QWidget()
        layout = QVBoxLayout(root)
        self.status = QLabel(
            f"Provider: {settings.provider} | Memory: SQLite | Sensitive actions: approval required"
        )
        self.chat = QTextEdit()
        self.chat.setReadOnly(True)
        row = QHBoxLayout()
        self.input = QLineEdit()
        self.input.setPlaceholderText("Ask ARD INTELLIGENCE…")
        self.send = QPushButton("Send")
        row.addWidget(self.input)
        row.addWidget(self.send)
        layout.addWidget(self.status)
        layout.addWidget(self.chat)
        layout.addLayout(row)
        self.setCentralWidget(root)
        self.send.clicked.connect(self.submit)
        self.input.returnPressed.connect(self.submit)

    def _append_plain_message(self, speaker: str, message: str) -> None:
        # setPlainText prevents user/model text from being interpreted as rich HTML.
        current = self.chat.toPlainText()
        line = f"{speaker}: {message}"
        self.chat.setPlainText(f"{current}\n{line}" if current else line)
        cursor = self.chat.textCursor()
        cursor.movePosition(cursor.End)
        self.chat.setTextCursor(cursor)

    def submit(self):
        prompt = self.input.text().strip()
        if not prompt:
            return
        self.input.clear()
        self.send.setEnabled(False)
        self._append_plain_message("You", prompt)
        self.worker = _ReplyWorker(self.orchestrator, prompt)
        self.worker.finished_text.connect(self.reply)
        self.worker.start()

    def reply(self, text: str):
        self._append_plain_message("ARD", text)
        self.send.setEnabled(True)
