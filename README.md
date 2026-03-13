# Coding Agent

Train and evaluate a small open-weight coding agent with SFT + RL; measure improvement via HumanEval and a custom mini agent benchmark. See [docs/](docs/) for scope and evaluation plan.

## Setup

```bash
# Virtual environment (Python 3.10+)
python3 -m venv .venv --without-pip   # if needed: --without-pip then bootstrap pip
source .venv/bin/activate

# Dependencies for agent runtime (see Quick test below)
# For HumanEval evaluation: evalplus, torch, transformers, accelerate (see Evaluation)
```

## Structure

```
agent_runtime/   # Episode loop and trace logging
tools/            # list_files, read_file, search_text, apply_patch, run_tests
sandbox/         # Temp workspace copy (original repo never modified)
evaluation/      # Agent eval harness; HumanEval via script below
scripts/         # run_manual_agent.py, replay_episode.py, run_evalplus_humaneval.sh
tasks/           # Task definitions (JSONL)
sample_repo/     # Minimal repo for testing
docs/            # PROJECT_SCOPE.md, EVAL_PLAN.md
evalplus_results/  # HumanEval results (created by run_evalplus_humaneval.sh)
```

## Evaluation (HumanEval)

[EvalPlus](https://github.com/evalplus/evalplus) HumanEval — same script for base model and finetuned checkpoints:

```bash
# Base or Hub model (default: Qwen/Qwen2.5-Coder-0.5B-Instruct)
./scripts/run_evalplus_humaneval.sh

# Finetuned checkpoint
./scripts/run_evalplus_humaneval.sh /path/to/checkpoint
```

Uses HuggingFace backend with a single GPU. Results under `evalplus_results/humaneval/`. Details: [docs/EVAL_PLAN.md](docs/EVAL_PLAN.md).

## Agent runtime

### Tools (unified `tool.run(**args)`)

| Tool         | Args              | Returns                    |
|-------------|-------------------|----------------------------|
| list_files  | root (optional)   | list of file paths         |
| read_file   | path              | file contents (max 256KB)  |
| search_text | query             | matching lines + paths     |
| apply_patch | patch_text        | success/failure message    |
| run_tests   | —                 | stdout, stderr, exit_code  |

### Quick test

From project root (with venv activated):

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

### Episode constraints

- **max_steps**: 10  
- **max_patch_attempts**: 2  

Episode ends when tests pass, max steps are reached, or patch limit is hit.

### Trace format

Traces are JSON with `task_id` and `steps` (each step: `tool`, `args`, `result`), suitable for SFT and replay.

## Dependencies

- Python 3.10+
- For `run_tests`: **pytest** (in the target repo or environment)
- For `search_text`: **ripgrep** (`rg`) or **grep**
- For `apply_patch`: **patch**
- For HumanEval: **evalplus**, **torch**, **transformers**, **accelerate** (install in `.venv` as needed)
