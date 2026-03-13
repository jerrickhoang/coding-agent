"""
search_text: search for text across the repository using ripgrep or grep.
"""

import subprocess
from pathlib import Path
from typing import Any


def run(query: str, workspace_path: str = "", **kwargs: Any) -> str:
    """
    Search for query in repository files. Uses ripgrep if available, else grep.

    Args:
        query: Search string (literal, not regex by default for ripgrep -F).
        workspace_path: Absolute path to the workspace root.

    Returns:
        Matching lines with file paths, or error message.
    """
    base = Path(workspace_path)
    if not base.exists():
        return "Error: workspace does not exist."

    # Prefer ripgrep (rg), fallback to grep
    for cmd in [
        ["rg", "-n", "-F", query, "--no-heading", "."],  # ripgrep, literal
        ["grep", "-rn", query, "."],  # grep
    ]:
        try:
            result = subprocess.run(
                cmd,
                cwd=str(base),
                capture_output=True,
                text=True,
                timeout=30,
            )
            out = result.stdout or ""
            err = result.stderr or ""
            if result.returncode == 0:
                return out.strip() or "(no matches)"
            if result.returncode == 1:
                # No matches
                return "(no matches)"
            # Try next command on failure
        except FileNotFoundError:
            continue
        except subprocess.TimeoutExpired:
            return "Error: search timed out."

    return "Error: neither ripgrep (rg) nor grep found."
