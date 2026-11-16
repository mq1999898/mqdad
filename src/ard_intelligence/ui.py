"""Minimal PySide6 chat and health dashboard."""
from __future__ import annotations
from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel
from .config import Settings
from .orchestrator import Orchestrator

class _ReplyWorker(QThread):
    finished_text = Signal(str)
    def __init__(self, orchestrator: Orchestrator, prompt: str):
        super().__init__()
        self.orchestrator, self.prompt = orchestrator, prompt
    def run(self):
        self.finished_text.emit(self.orchestrator.handle(self.prompt))

class MainWindow(QMainWindow):
    def __init__(self, orchestrator: Orchestrator, settings: Settings):
        super().__init__()
        self.orchestrator = orchestrator
        self.setWindowTitle("ARD INTELLIGENCE")
        self.resize(900, 650)
        root = QWidget()
        layout = QVBoxLayout(root)
        self.status = QLabel(f"Provider: {settings.provider} | Memory: SQLite | Sensitive actions: approval required")
        self.chat = QTextEdit(); self.chat.setReadOnly(True)
        row = QHBoxLayout()
        self.input = QLineEdit(); self.input.setPlaceholderText("Ask ARD INTELLIGENCE…")
        self.send = QPushButton("Send")
        row.addWidget(self.input); row.addWidget(self.send)
        layout.addWidget(self.status); layout.addWidget(self.chat); layout.addLayout(row)
        self.setCentralWidget(root)
        self.send.clicked.connect(self.submit)
        self.input.returnPressed.connect(self.submit)

    def submit(self):
        prompt = self.input.text().strip()
        if not prompt:
            return
        self.input.clear(); self.send.setEnabled(False)
        self.chat.append(f"<b>You:</b> {prompt}")
        self.worker = _ReplyWorker(self.orchestrator, prompt)
        self.worker.finished_text.connect(self.reply)
        self.worker.start()

    def reply(self, text: str):
        self.chat.append(f"<b>ARD:</b> {text}")
        self.send.setEnabled(True)
