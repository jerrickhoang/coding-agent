"""
read_file: reads the contents of a file with a size limit.
"""

from pathlib import Path
from typing import Any

# Limit file size to prevent huge outputs (bytes)
MAX_FILE_SIZE = 256 * 1024  # 256 KB


def run(path: str, workspace_path: str = "", **kwargs: Any) -> str:
    """
    Read file contents. Returns error message if path is invalid or file too large.

    Args:
        path: Path relative to workspace (or absolute within workspace).
        workspace_path: Absolute path to the workspace root.

    Returns:
        File contents as string, or error message.
    """
    base = Path(workspace_path).resolve()
    full = (base / path).resolve()
    try:
        if not full.exists():
            return f"Error: file not found: {path}"
        if not full.is_file():
            return f"Error: not a file: {path}"
        if full.stat().st_size > MAX_FILE_SIZE:
            return f"Error: file too large (max {MAX_FILE_SIZE} bytes): {path}"
        # Ensure we don't escape workspace
        if not str(full).startswith(str(base)):
            return f"Error: path outside workspace: {path}"
        return full.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        return f"Error reading {path}: {e}"
