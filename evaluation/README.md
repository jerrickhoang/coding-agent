# Evaluation

Benchmarking for the coding agent project.

## HumanEval (model-level)

- **Script:** [`../scripts/run_evalplus_humaneval.sh`](../scripts/run_evalplus_humaneval.sh)
- **Details:** [docs/EVAL_PLAN.md](../docs/EVAL_PLAN.md) — EvalPlus setup, base vs finetuned models, HF vs vLLM backends, results under `evalplus_results/humaneval/`.

## Agent-level eval

- **Harness:** `agent_eval/run_agent_eval.py` (mini agent benchmark).
