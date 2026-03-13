#!/usr/bin/env python3
"""
Manual agent: runs the fixed flow search_text -> read_file -> apply_patch -> run_tests
against a repository. Used to verify the runtime and produce a trace.
"""

import argparse
import sys
from pathlib import Path

# Project root on path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent_runtime import EpisodeRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="Run manual agent flow (search -> read -> patch -> tests)")
    parser.add_argument("repo_path", type=str, help="Path to source repository (will be copied to temp workspace)")
    parser.add_argument("--task-id", default="manual", help="Task ID for the trace")
    parser.add_argument("--log-dir", default=None, help="Log directory (default: <repo_path>/../logs or ./logs)")
    parser.add_argument("--search-query", default="def ", help="Query for search_text")
    parser.add_argument("--read-path", default=None, help="Path to read after search (default: first match or prompt)")
    parser.add_argument("--patch", default=None, help="Path to patch file, or patch content; if not set, skip apply_patch")
    args = parser.parse_args()

    repo_path = Path(args.repo_path).resolve()
    if not repo_path.is_dir():
        print(f"Error: not a directory: {repo_path}")
        sys.exit(1)

    log_dir = args.log_dir or str(ROOT / "logs")
    runner = EpisodeRunner(source_repo_path=str(repo_path), log_dir=log_dir)

    try:
        runner.reset(task_id=args.task_id)
        print(f"Workspace: {runner.workspace_path}\n")

        # 1. search_text
        out = runner.step("search_text", {"query": args.search_query})
        print(f"[search_text] query={args.search_query}")
        print(f"  result (first 500 chars): {str(out['result'])[:500]}...\n")
        if out.get("done"):
            trace_path = runner.save_trace(args.task_id)
            print(f"Trace saved: {trace_path}")
            return

        # 2. read_file — use first file from search if --read-path not set
        read_path = args.read_path
        if not read_path and isinstance(out.get("result"), str):
            first_line = out["result"].strip().split("\n")[0]
            if ":" in first_line:
                read_path = first_line.split(":", 1)[0].strip()
        if not read_path:
            read_path = "README.md"  # fallback
        out = runner.step("read_file", {"path": read_path})
        print(f"[read_file] path={read_path}")
        print(f"  result (first 400 chars): {str(out['result'])[:400]}...\n")
        if out.get("done"):
            trace_path = runner.save_trace(args.task_id)
            print(f"Trace saved: {trace_path}")
            return

        # 3. apply_patch (optional)
        if args.patch:
            patch_content = Path(args.patch).read_text() if Path(args.patch).exists() else args.patch
            out = runner.step("apply_patch", {"patch_text": patch_content})
            print(f"[apply_patch]")
            print(f"  result: {out['result']}\n")
            if out.get("done"):
                trace_path = runner.save_trace(args.task_id)
                print(f"Trace saved: {trace_path}")
                return

        # 4. run_tests
        out = runner.step("run_tests", {})
        result = out["result"]
        if isinstance(result, dict):
            print(f"[run_tests] exit_code={result.get('exit_code')}")
            print(result.get("stdout", "")[-1500:] or result.get("stderr", ""))
        else:
            print(f"[run_tests] {result}")
        print()

        trace_path = runner.save_trace(args.task_id)
        print(f"Trace saved: {trace_path}")
        print(f"Done. success={out.get('success')}")
    finally:
        runner.close()


if __name__ == "__main__":
    main()
