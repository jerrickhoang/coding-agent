"""
run_tests: run the repository's test suite using pytest.
"""

import subprocess
from pathlib import Path
from typing import Any, Tuple


def run(workspace_path: str = "", **kwargs: Any) -> Tuple[str, str, int]:
    """
    Run pytest in the workspace. Returns (stdout, stderr, exit_code).

    Args:
        workspace_path: Absolute path to the workspace root.

    Returns:
        (stdout, stderr, exit_code). exit_code == 0 means tests passed.
    """
    base = Path(workspace_path)
    if not base.exists():
        return ("", "Error: workspace does not exist.", 1)

    try:
        result = subprocess.run(
            ["pytest", "-v", "--tb=short"],
            cwd=str(base),
            capture_output=True,
            text=True,
            timeout=120,
        )
        return (
            result.stdout or "",
            result.stderr or "",
            result.returncode,
        )
    except subprocess.TimeoutExpired:
        return ("", "Error: tests timed out.", -1)
    except FileNotFoundError:
        return ("", "Error: pytest not found. Install with: pip install pytest", 1)
    except Exception as e:
        return ("", f"Error running tests: {e}", 1)
