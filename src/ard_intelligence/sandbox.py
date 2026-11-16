"""Safe code staging: validates paths and parses Python but never executes it."""
from __future__ import annotations
import ast
from pathlib import Path

class CodeSandbox:
    """A staging and syntax-check area, not an OS-level execution sandbox."""
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def stage(self, relative_path: str, content: str) -> Path:
        target = (self.root / relative_path).resolve()
        if target == self.root or self.root not in target.parents:
            raise ValueError("Path must stay inside the staging directory")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        if target.suffix == ".py":
            ast.parse(content, filename=str(target))
        return target

    def approve_for_manual_review(self, relative_path: str, *, user_approved: bool) -> Path:
        if not user_approved:
            raise PermissionError("Explicit human approval is required")
        target = (self.root / relative_path).resolve()
        if self.root not in target.parents or not target.is_file():
            raise ValueError("Staged file not found")
        return target
