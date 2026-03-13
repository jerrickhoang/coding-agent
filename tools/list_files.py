"""
list_files: returns a list of files in the repository.
"""

from pathlib import Path
from typing import Any, List, Optional


# Default max depth and ignore patterns for listing
DEFAULT_IGNORE = {".git", "__pycache__", ".venv", "venv", "node_modules", ".pytest_cache", "*.pyc"}


def run(root: Optional[str] = None, workspace_path: str = "", **kwargs: Any) -> List[str]:
    """
    List files in the repository (or under root if provided).

    Args:
        root: Optional subdirectory relative to workspace. If None, list from workspace root.
        workspace_path: Absolute path to the workspace root.

    Returns:
        List of relative file paths (relative to workspace).
    """
    base = Path(workspace_path)
    if root:
        base = base / root
    if not base.exists():
        return []

    out: List[str] = []
    try:
        base_resolved = base.resolve()
        ws_resolved = Path(workspace_path).resolve()
        for path in base_resolved.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(ws_resolved)
            parts = rel.parts
            if any(p in DEFAULT_IGNORE or p.startswith(".") for p in parts):
                continue
            if parts[-1].endswith(".pyc"):
                continue
            out.append(str(rel))
    except Exception:
        pass
    return sorted(out)
