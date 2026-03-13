"""
Sandbox environment: copies a repository into a temporary workspace.
The agent never modifies the original repository.
"""

import shutil
import tempfile
import uuid
from pathlib import Path
from typing import Optional


class RepoEnvironment:
    """Manages a temporary copy of a repository for agent episodes."""

    def __init__(self, source_repo_path: str):
        self.source_repo_path = Path(source_repo_path).resolve()
        if not self.source_repo_path.is_dir():
            raise ValueError(f"Source repo not found: {self.source_repo_path}")
        self._workspace_path: Optional[Path] = None

    def reset(self) -> str:
        """
        Copy the source repo into a new temporary workspace.
        Returns the absolute path to the workspace root.
        """
        self.close()
        # Use a unique path that does not exist yet so copytree can create it
        name = f"coding_agent_{uuid.uuid4().hex[:12]}"
        self._workspace_path = Path(tempfile.gettempdir()) / name
        shutil.copytree(
            self.source_repo_path,
            self._workspace_path,
            dirs_exist_ok=False,
            ignore=shutil.ignore_patterns(".git", "__pycache__", "*.pyc", ".venv", "venv"),
        )
        return str(self._workspace_path)

    @property
    def workspace_path(self) -> Optional[str]:
        """Current workspace root path, or None if not reset."""
        return str(self._workspace_path) if self._workspace_path else None

    def close(self) -> None:
        """Remove the temporary workspace if it exists."""
        if self._workspace_path and self._workspace_path.exists():
            shutil.rmtree(self._workspace_path, ignore_errors=True)
            self._workspace_path = None

    def __enter__(self) -> "RepoEnvironment":
        self.reset()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()
