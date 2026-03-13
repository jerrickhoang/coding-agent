#!/usr/bin/env python3
"""
Replay an episode from a saved trace: run the same tool sequence in a fresh workspace
and optionally compare results. Used to verify traces and debug.
"""

import argparse
import json
import sys
from pathlib import Path

# Project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_runtime import EpisodeRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="Replay a saved episode trace")
    parser.add_argument("trace_path", type=str, help="Path to trace JSON file")
    parser.add_argument("repo_path", type=str, help="Path to source repository (for fresh workspace)")
    parser.add_argument("--dry-run", action="store_true", help="Only print trace, do not run tools")
    parser.add_argument("--log-dir", default=None, help="Log dir for new trace (default: ./logs)")
    args = parser.parse_args()

    trace_path = Path(args.trace_path)
    if not trace_path.exists():
        print(f"Error: trace file not found: {trace_path}")
        sys.exit(1)

    with open(trace_path) as f:
        trace = json.load(f)

    task_id = trace.get("task_id", "replay")
    steps = trace.get("steps", [])
    print(f"Task ID: {task_id}")
    print(f"Steps: {len(steps)}\n")

    if args.dry_run:
        for i, s in enumerate(steps):
            print(f"  {i+1}. {s.get('tool')} {s.get('args')}")
            print(f"     result: {str(s.get('result'))[:200]}...")
        return

    repo_path = Path(args.repo_path).resolve()
    if not repo_path.is_dir():
        print(f"Error: not a directory: {repo_path}")
        sys.exit(1)

    log_dir = args.log_dir or str(ROOT / "logs")
    runner = EpisodeRunner(source_repo_path=str(repo_path), log_dir=log_dir)
    try:
        runner.reset(task_id=f"{task_id}_replay")
        print(f"Workspace: {runner.workspace_path}\n")

        for i, s in enumerate(steps):
            tool = s.get("tool")
            args = s.get("args", {})
            out = runner.step(tool, args)
            print(f"[{i+1}] {tool} {args}")
            print(f"  result: {str(out['result'])[:300]}...")
            if out.get("done"):
                print("  (done)")
                break

        new_trace_path = runner.save_trace(f"{task_id}_replay")
        print(f"\nReplay trace saved: {new_trace_path}")
    finally:
        runner.close()


if __name__ == "__main__":
    main()
