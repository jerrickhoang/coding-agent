#!/usr/bin/env bash
# Run EvalPlus HumanEval with HuggingFace backend (single GPU).
# Usage: ./scripts/run_evalplus_humaneval.sh [model_name]
set -e
cd "$(dirname "$0")/.."
MODEL="${1:-Qwen/Qwen2.5-Coder-0.5B-Instruct}"
# Use single GPU to avoid "tensors on different devices" errors
export CUDA_VISIBLE_DEVICES=0
.venv/bin/python -m evalplus.evaluate \
  --model "$MODEL" \
  --dataset humaneval \
  --backend hf \
  --greedy
