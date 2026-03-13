# Evaluation Plan: Coding Agent

## Overview
The evaluation plan consists of three levels of benchmarking to measure the performance of the base model, the SFT (Supervised Fine-Tuned) model, and the RL (Reinforcement Learning) model.

## Level 1: Model-Level (HumanEval)

### HumanEval (EvalPlus) Setup
- **Tool:** [EvalPlus](https://github.com/evalplus/evalplus) for HumanEval (and optional MBPP).
- **Script:** `scripts/run_evalplus_humaneval.sh` — runs EvalPlus with the HuggingFace backend, single GPU, greedy decoding.
- **Usage:**
  - **Base or Hub model:** `./scripts/run_evalplus_humaneval.sh` (default: `Qwen/Qwen2.5-Coder-0.5B-Instruct`) or `./scripts/run_evalplus_humaneval.sh "Qwen/Qwen2.5-Coder-7B-Instruct"`.
  - **Finetuned checkpoint:** `./scripts/run_evalplus_humaneval.sh /path/to/checkpoint` (e.g. `./scripts/run_evalplus_humaneval.sh ./training/sft/sft_v1`).
- **Backends:** `--backend hf` (default in script). For multi-GPU, use `--backend vllm` with `--tp 2` (requires `pip install vllm`); with `hf`, use a single GPU (`CUDA_VISIBLE_DEVICES=0` or the script) to avoid device-mismatch errors.
- **Results:** Written under `evalplus_results/humaneval/` (e.g. `*_eval_results.json`). Same script is used for baseline, post-SFT, and post-RL; only the model path/name changes.

### Metrics & goal
- **Primary Benchmark:** HumanEval (Python).
- **Metrics:** `pass@1`, syntax error rate, token usage.
- **Goal:** Ensure the base model's coding capability is preserved or improved after SFT and RL.

## Level 2: Mini Agent Benchmark (Custom)
- **Primary Benchmark:** Custom set of bug fixes, TODO implementations, and refactors.
- **Metrics:** 
  - Solve rate (tests passed).
  - Patch apply rate.
  - Average tool calls per episode.
  - Invalid tool call rate.
- **Implementation:** Run the agent in the current `EpisodeRunner` harness on a fixed task set.

## Level 3: Stretch (SWE-bench style)
- **Primary Benchmark:** Small subset of SWE-bench or similar repo-level issues.
- **Metrics:** Issue resolution rate.
- **Goal:** Evaluate the agent's ability to handle complex, multi-file repository issues.

## Evaluation Schedule
- **Baseline (Week 3):** Run benchmarks on the base model (`Qwen2.5-Coder-7B-Instruct`).
- **Post-SFT (Weeks 6–7):** Run benchmarks on the best SFT checkpoint.
- **Post-RL (Weeks 9–11):** Run benchmarks on RL-trained models.
- **Final (Week 12):** Final report and comparison.

## Results Storage
- **HumanEval (EvalPlus):** `evalplus_results/humaneval/` — model-specific subdirs and `*_eval_results.json` per run.
- **Other benchmarks:** `results/` directory, organized by benchmark and model version (e.g., `results/humaneval/base_model.json`, agent-eval outputs).
