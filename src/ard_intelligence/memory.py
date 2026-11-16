"""Persistent conversation and searchable knowledge memory."""
from __future__ import annotations
import sqlite3
from pathlib import Path

class MemoryStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, role TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            db.execute("CREATE TABLE IF NOT EXISTS knowledge (id INTEGER PRIMARY KEY, title TEXT NOT NULL, content TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
            try:
                db.execute("CREATE VIRTUAL TABLE IF NOT EXISTS knowledge_fts USING fts5(title, content, content='knowledge', content_rowid='id')")
                db.executescript("CREATE TRIGGER IF NOT EXISTS knowledge_ai AFTER INSERT ON knowledge BEGIN INSERT INTO knowledge_fts(rowid,title,content) VALUES(new.id,new.title,new.content); END; CREATE TRIGGER IF NOT EXISTS knowledge_ad AFTER DELETE ON knowledge BEGIN INSERT INTO knowledge_fts(knowledge_fts,rowid,title,content) VALUES('delete',old.id,old.title,old.content); END;")
            except sqlite3.OperationalError:
                pass

    def _connect(self):
        return sqlite3.connect(self.path)

    def add_message(self, role: str, content: str) -> None:
        with self._connect() as db:
            db.execute("INSERT INTO messages(role,content) VALUES(?,?)", (role, content))

    def add_knowledge(self, title: str, content: str) -> int:
        with self._connect() as db:
            cur = db.execute("INSERT INTO knowledge(title,content) VALUES(?,?)", (title, content))
            return int(cur.lastrowid)

    def search(self, query: str, limit: int = 10) -> list[tuple[str, str]]:
        if not query.strip():
            return []
        with self._connect() as db:
            try:
                rows = db.execute("SELECT k.title,k.content FROM knowledge_fts f JOIN knowledge k ON k.id=f.rowid WHERE knowledge_fts MATCH ? LIMIT ?", (query, limit)).fetchall()
            except sqlite3.OperationalError:
                rows = db.execute("SELECT title,content FROM knowledge WHERE title LIKE ? OR content LIKE ? LIMIT ?", (f"%{query}%", f"%{query}%", limit)).fetchall()
        return [(str(a), str(b)) for a, b in rows]

    def history(self, limit: int = 50) -> list[tuple[str, str]]:
        with self._connect() as db:
            rows = db.execute("SELECT role,content FROM messages ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [(str(a), str(b)) for a, b in reversed(rows)]
