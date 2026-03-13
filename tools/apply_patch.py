"""
apply_patch: apply a unified diff patch to the repository.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Any


def run(patch_text: str, workspace_path: str = "", **kwargs: Any) -> str:
    """
    Apply a unified diff patch in the workspace.

    Args:
        patch_text: The patch content (unified diff format).
        workspace_path: Absolute path to the workspace root.

    Returns:
        Success or failure message.
    """
    base = Path(workspace_path)
    if not base.exists():
        return "Error: workspace does not exist."

    if not patch_text or not patch_text.strip():
        return "Error: empty patch."

    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".patch", delete=False
        ) as f:
            f.write(patch_text)
            patch_file = f.name
        try:
            result = subprocess.run(
                ["patch", "-p1", "-d", str(base), "-i", patch_file],
                capture_output=True,
                text=True,
                timeout=60,
            )
            if result.returncode == 0:
                return "Patch applied successfully."
            err = (result.stderr or result.stdout or "").strip()
            return f"Patch failed: {err}"
        finally:
            Path(patch_file).unlink(missing_ok=True)
    except Exception as e:
        return f"Error applying patch: {e}"
