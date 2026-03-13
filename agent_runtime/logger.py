"""
Trace logging: save episode traces for later SFT training and replay.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, List
import uuid


def create_trace(task_id: str, steps: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build a trace dict in the required format."""
    return {
        "task_id": task_id,
        "steps": steps,
    }


def save_trace(trace: Dict[str, Any], log_dir: str) -> str:
    """
    Save trace to log_dir. Filename includes task_id and a short unique suffix.
    Returns the path of the saved file.
    """
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    task_id = trace.get("task_id", "unknown")
    suffix = str(uuid.uuid4())[:8]
    path = os.path.join(log_dir, f"trace_{task_id}_{suffix}.json")
    with open(path, "w") as f:
        json.dump(trace, f, indent=2)
    return path


def load_trace(path: str) -> Dict[str, Any]:
    """Load a trace from a JSON file."""
    with open(path) as f:
        return json.load(f)
