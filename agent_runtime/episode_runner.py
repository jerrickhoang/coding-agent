"""
Episode runner: reset env, provide task to model, execute tool calls, repeat until
tests pass, max steps, or patch submitted. Records trace for each episode.
"""

from typing import Any, Callable, Dict, List, Optional

from sandbox.repo_environment import RepoEnvironment
from tools import get_tool, list_tool_names

from .logger import create_trace, save_trace


MAX_STEPS = 10
MAX_PATCH_ATTEMPTS = 2


class EpisodeRunner:
    """
    Runs one episode: task -> model -> tool call -> result -> ... -> done.
    Agent logic is separate: the runner only executes tool calls from a driver.
    """

    def __init__(
        self,
        source_repo_path: str,
        log_dir: str = "logs",
        max_steps: int = MAX_STEPS,
        max_patch_attempts: int = MAX_PATCH_ATTEMPTS,
    ):
        self.env = RepoEnvironment(source_repo_path)
        self.log_dir = log_dir
        self.max_steps = max_steps
        self.max_patch_attempts = max_patch_attempts
        self._workspace_path: Optional[str] = None
        self._steps: List[Dict[str, Any]] = []
        self._patch_attempts = 0

    def reset(self, task_id: str = "default") -> Dict[str, Any]:
        """
        Reset environment (new temp workspace) and state.
        Returns initial context for the model: task_id, workspace_path, tool list.
        """
        self._workspace_path = self.env.reset()
        self._steps = []
        self._patch_attempts = 0
        return {
            "task_id": task_id,
            "workspace_path": self._workspace_path,
            "tools": list_tool_names(),
            "max_steps": self.max_steps,
            "max_patch_attempts": self.max_patch_attempts,
        }

    def step(self, tool_name: str, args: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute one tool call. args must not contain workspace_path (injected here).
        Returns {"result": ..., "done": bool, "success": bool?, "step": ...}.
        """
        if self._workspace_path is None:
            return {"result": "Error: environment not reset.", "done": True, "success": False}

        tool = get_tool(tool_name)
        if tool is None:
            step_record = {"tool": tool_name, "args": args or {}, "result": "Error: unknown tool."}
            self._steps.append(step_record)
            return {"result": step_record["result"], "done": False, "step": step_record}

        args = dict(args or {})
        args.pop("workspace_path", None)
        result = tool.run(workspace_path=self._workspace_path, **args)

        step_record = {"tool": tool_name, "args": args, "result": result}
        self._steps.append(step_record)

        done = False
        success = None
        if tool_name == "apply_patch":
            self._patch_attempts += 1
            if isinstance(result, str) and "successfully" in result.lower():
                success = True
            else:
                success = False
        if tool_name == "run_tests":
            exit_code = result.get("exit_code", result[2] if isinstance(result, (list, tuple)) else -1)
            if exit_code == 0:
                done = True
                success = True
            else:
                success = False

        if len(self._steps) >= self.max_steps:
            done = True
        if self._patch_attempts >= self.max_patch_attempts and not success:
            done = True

        return {"result": result, "done": done, "success": success, "step": step_record}

    def get_trace(self, task_id: str = "default") -> Dict[str, Any]:
        """Return the current trace (task_id + steps)."""
        return create_trace(task_id, self._steps)

    def save_trace(self, task_id: str = "default") -> str:
        """Save current trace to log_dir and return the file path."""
        trace = self.get_trace(task_id)
        return save_trace(trace, self.log_dir)

    def close(self) -> None:
        """Release the temporary workspace."""
        self.env.close()
        self._workspace_path = None

    @property
    def workspace_path(self) -> Optional[str]:
        return self._workspace_path

    @property
    def steps(self) -> List[Dict[str, Any]]:
        return self._steps.copy()


def run_episode(
    source_repo_path: str,
    task_id: str,
    task_prompt: str,
    get_tool_calls: Callable[[Dict[str, Any], List[Dict[str, Any]]], Optional[Dict[str, Any]]],
    log_dir: str = "logs",
    max_steps: int = MAX_STEPS,
    max_patch_attempts: int = MAX_PATCH_ATTEMPTS,
) -> Dict[str, Any]:
    """
    Run a full episode with a driver that produces tool calls from context and history.

    get_tool_calls(context, steps) -> {"tool": name, "args": {...}} or None to stop.

    Returns summary: task_id, steps, trace_path, done, success.
    """
    runner = EpisodeRunner(
        source_repo_path=source_repo_path,
        log_dir=log_dir,
        max_steps=max_steps,
        max_patch_attempts=max_patch_attempts,
    )
    try:
        context = runner.reset(task_id=task_id)
        context["task_prompt"] = task_prompt
        steps = []
        done = False
        success = None

        while not done and len(steps) < max_steps:
            call = get_tool_calls(context, steps)
            if call is None:
                break
            tool_name = call.get("tool")
            args = call.get("args", {})
            if not tool_name:
                break
            out = runner.step(tool_name, args)
            steps = runner.steps
            done = out.get("done", False)
            if out.get("success") is not None:
                success = out["success"]
            context["last_result"] = out.get("result")
            context["last_step"] = out.get("step")

        trace_path = runner.save_trace(task_id)
        return {
            "task_id": task_id,
            "steps": runner.steps,
            "trace_path": trace_path,
            "done": done,
            "success": success,
        }
    finally:
        runner.close()
