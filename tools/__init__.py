"""
Unified tool interface: all tools are callable via tool.run(**args).
workspace_path is injected by the episode runner.
"""

from typing import Any, Callable, Dict, List, Optional

from tools import apply_patch, list_files, read_file, run_tests, search_text


def _normalize_result(result: Any) -> Any:
    """Convert tuple (e.g. run_tests) to a serializable form for traces."""
    if isinstance(result, tuple):
        return {"stdout": result[0], "stderr": result[1], "exit_code": result[2]}
    return result


class Tool:
    """Wrapper so each tool has a .run(**args) interface."""

    def __init__(self, name: str, fn: Callable[..., Any]):
        self.name = name
        self._fn = fn

    def run(self, workspace_path: str, **args: Any) -> Any:
        result = self._fn(workspace_path=workspace_path, **args)
        return _normalize_result(result)


# Registry: tool_name -> Tool
TOOLS: Dict[str, Tool] = {
    "list_files": Tool("list_files", list_files.run),
    "read_file": Tool("read_file", read_file.run),
    "search_text": Tool("search_text", search_text.run),
    "apply_patch": Tool("apply_patch", apply_patch.run),
    "run_tests": Tool("run_tests", run_tests.run),
}


def get_tool(name: str) -> Optional[Tool]:
    return TOOLS.get(name)


def list_tool_names() -> List[str]:
    return list(TOOLS.keys())
