# Coding Agent Runtime

Minimal runtime for a coding agent that interacts with a repository through structured tool calls. Used for training trajectories, SFT, RL, and benchmarking.

## Structure

```
coding_agent/
  agent_runtime/     # Episode loop and trace logging
  tools/             # list_files, read_file, search_text, apply_patch, run_tests
  sandbox/           # Temp workspace copy (original repo never modified)
  scripts/           # run_manual_agent.py, replay_episode.py
  logs/              # Saved traces
  sample_repo/       # Minimal repo for testing
```

## Tools (unified `tool.run(**args)`)

| Tool         | Args              | Returns                    |
|-------------|-------------------|----------------------------|
| list_files  | root (optional)   | list of file paths         |
| read_file   | path              | file contents (max 256KB)  |
| search_text | query             | matching lines + paths     |
| apply_patch | patch_text        | success/failure message    |
| run_tests   | —                 | stdout, stderr, exit_code  |

## Quick test

From project root:

```bash
# Manual flow: search → read → apply_patch → run_tests
python scripts/run_manual_agent.py sample_repo \
  --search-query "return a" \
  --read-path utils.py \
  --patch sample_repo/patch_add_to_subtract.patch

# Replay a saved trace
python scripts/replay_episode.py logs/trace_manual_*.json sample_repo

# Dry-run: print trace steps only
python scripts/replay_episode.py logs/trace_manual_*.json sample_repo --dry-run
```

## Episode constraints

- **max_steps**: 10  
- **max_patch_attempts**: 2  

Episode ends when tests pass, max steps are reached, or patch limit is hit.

## Trace format

Traces are JSON with `task_id` and `steps` (each step: `tool`, `args`, `result`), suitable for SFT and replay.

## Dependencies

- Python 3.10+
- For `run_tests`: **pytest** (in the target repo or environment)
- For `search_text`: **ripgrep** (`rg`) or **grep**
- For `apply_patch`: **patch**
