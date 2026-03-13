# Project Scope: Coding Agent Training

## Objective
Train a small open-weight model (Qwen2.5-Coder-7B) to act as a coding agent. The agent should be able to:
1. Read a task description.
2. Inspect a repository (list files, read contents, search).
3. Edit code via patches.
4. Run tests and interpret results.
5. Retry after failure and submit a final patch.

The goal is to measure improvement through SFT (Supervised Fine-Tuning) and RL (Reinforcement Learning) using standardized benchmarks.

## In Scope
- **Agent Tools:** `list_files`, `read_file`, `search_text`, `apply_patch`, `run_tests`.
- **Episode Constraints:** 
  - Max steps: 10
  - Max patch attempts: 2
  - Max files modified: 1–3
- **Environment:** Dockerized or local sandbox (no external internet, no package installs during episode).
- **Language:** Python.
- **Model:** Qwen2.5-Coder-7B.

## Out of Scope
- Multi-repo tasks.
- Non-Python languages (initially).
- External network access or package installation during agent episodes.
- Training models other than the chosen base (for the primary experiment).

## Tech Choices
- **Base Model:** `Qwen/Qwen2.5-Coder-7B-Instruct`
- **Inference Stack:** TBD (Shortlist: `vLLM`, `transformers` + `bitsandbytes`)
- **Training Framework:** TBD (Shortlist: `Unsloth`, `Axolotl`, `Hugging Face PEFT/QLoRA`)

## Target Repo Structure
```
datasets/        # Training/dev/eval datasets
tasks/           # Task definitions (JSONL)
trajectories/    # Collected agent traces
training/        # SFT and RL training scripts/configs
evaluation/      # Benchmark implementations (HumanEval, Agent Eval)
runtime/         # Agent loop and tool implementations
results/         # Benchmark results and reports
docs/            # Documentation and plans
```
