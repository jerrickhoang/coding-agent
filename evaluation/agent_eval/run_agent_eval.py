import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import torch

# Project root on path
ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from agent_runtime import EpisodeRunner, run_episode
from agent_runtime.model_driver import ModelDriver

# Configuration
TASKS_FILE = "tasks/mini_agent_tasks.jsonl"
SAMPLE_REPO = "sample_repo"
RESULTS_FILE = "results/agent_eval/base_model.json"
MODEL_NAME = "Qwen/Qwen2.5-Coder-0.5B-Instruct"

def load_tasks(path: str) -> List[Dict[str, Any]]:
    tasks = []
    with open(path) as f:
        for line in f:
            tasks.append(json.loads(line))
    return tasks

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default=MODEL_NAME)
    args = parser.parse_args()
    
    os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)
    
    tasks = load_tasks(TASKS_FILE)
    print(f"Loaded {len(tasks)} tasks.")
    
    # Initialize driver (loads model once)
    driver = ModelDriver(model_name=args.model)
    
    results = []
    
    for task in tasks:
        task_id = task["id"]
        prompt = task["prompt"]
        print(f"\n--- Running Task: {task_id} ---")
        print(f"Prompt: {prompt}")
        
        driver.reset(prompt)
        
        # Define get_tool_calls for run_episode
        def get_tool_calls(context: Dict[str, Any], steps: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
            last_result = context.get("last_result")
            call = driver.get_tool_call(last_result)
            if call:
                # We need to return only tool and args for run_episode
                return {"tool": call.get("tool"), "args": call.get("args", {})}
            return None
        
        summary = run_episode(
            source_repo_path=SAMPLE_REPO,
            task_id=task_id,
            task_prompt=prompt,
            get_tool_calls=get_tool_calls
        )
        
        print(f"Task {task_id} complete. Success: {summary['success']}")
        results.append(summary)
        
    # Calculate metrics
    total_tasks = len(results)
    solved_tasks = sum(1 for r in results if r["success"] is True)
    total_steps = sum(len(r["steps"]) for r in results)
    
    # Analyze tool usage
    total_tool_calls = 0
    invalid_tool_calls = 0
    patch_attempts = 0
    patch_successes = 0
    
    for r in results:
        for step in r["steps"]:
            total_tool_calls += 1
            tool = step.get("tool")
            result = step.get("result")
            
            if tool == "apply_patch":
                patch_attempts += 1
                if isinstance(result, str) and "successfully" in result.lower():
                    patch_successes += 1
            
            if isinstance(result, str) and "Error: unknown tool" in result:
                invalid_tool_calls += 1
                
    metrics = {
        "model": MODEL_NAME,
        "total_tasks": total_tasks,
        "solved_tasks": solved_tasks,
        "solve_rate": solved_tasks / total_tasks if total_tasks > 0 else 0,
        "avg_steps": total_steps / total_tasks if total_tasks > 0 else 0,
        "invalid_tool_call_rate": invalid_tool_calls / total_tool_calls if total_tool_calls > 0 else 0,
        "patch_apply_rate": patch_successes / patch_attempts if patch_attempts > 0 else 0,
        "results": results
    }
    
    print("\n--- Summary ---")
    print(f"Solve Rate: {metrics['solve_rate']:.2%}")
    print(f"Avg Steps: {metrics['avg_steps']:.2f}")
    print(f"Invalid Tool Call Rate: {metrics['invalid_tool_call_rate']:.2%}")
    print(f"Patch Apply Rate: {metrics['patch_apply_rate']:.2%}")
    
    with open(RESULTS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)

if __name__ == "__main__":
    main()
