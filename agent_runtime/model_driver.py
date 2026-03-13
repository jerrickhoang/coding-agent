import json
import re
from typing import Any, Dict, List, Optional
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class ModelDriver:
    """
    Wraps a language model to act as a coding agent.
    Handles prompt construction, tool call parsing, and history management.
    """

    SYSTEM_PROMPT = """You are a coding agent that can interact with a repository using tools.
Your goal is to solve the provided task by inspecting the code, applying patches, and running tests.

Available tools:
1. list_files(root: str = None) -> List[str]
   Lists files in the repository or a subdirectory.
2. read_file(path: str) -> str
   Reads the contents of a file.
3. search_text(query: str) -> str
   Searches for text across the repository. Returns matching lines and paths.
4. apply_patch(patch_text: str) -> str
   Applies a unified diff patch to the repository. The patch MUST be in a valid unified diff format (starts with --- a/path and +++ b/path).
5. run_tests() -> Dict[str, Any]
   Runs the test suite using pytest. Returns stdout, stderr, and exit_code (0 means success).

Output your next action as a JSON object with 'thought', 'tool', and 'args' keys.
Example for apply_patch:
{
  "thought": "I will fix the bug by changing addition to subtraction.",
  "tool": "apply_patch",
  "args": {
    "patch_text": "--- a/utils.py\n+++ b/utils.py\n@@ -3,3 +3,3 @@\n def add(a, b):\n-    return a + b\n+    return a - b"
  }
}

Only output ONE tool call at a time. Wait for the result before proceeding.
"""

    def __init__(
        self,
        model_name: str = "Qwen/Qwen2.5-Coder-0.5B-Instruct",
        model: Optional[Any] = None,
        tokenizer: Optional[Any] = None,
        device: str = "auto"
    ):
        self.model_name = model_name
        if model and tokenizer:
            self.model = model
            self.tokenizer = tokenizer
        else:
            print(f"Loading model {model_name}...")
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                device_map=device,
                torch_dtype=torch.float16 if torch.cuda.is_available() or torch.backends.mps.is_available() else torch.float32,
                trust_remote_code=True
            )
        
        self.history: List[Dict[str, str]] = []

    def reset(self, task_prompt: str):
        """Reset history with a new task."""
        self.history = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": f"Task: {task_prompt}"}
        ]

    def get_tool_call(self, last_result: Optional[Any] = None) -> Optional[Dict[str, Any]]:
        """
        Ask the model for the next tool call based on history and last result.
        Returns {"tool": name, "args": {...}} or None.
        """
        if last_result is not None:
            # Format result for the model
            result_str = str(last_result)
            if len(result_str) > 5000:
                result_str = result_str[:2500] + "\n... (truncated) ...\n" + result_str[-2500:]
            
            self.history.append({"role": "user", "content": f"Observation: {result_str}"})

        # Generate response
        text = self.tokenizer.apply_chat_template(
            self.history,
            tokenize=False,
            add_generation_prompt=True
        )
        
        inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.0,  # Greedy for agent consistency
                do_sample=False,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        generated_ids = [
            output_ids[len(input_ids):] for input_ids, output_ids in zip(inputs.input_ids, outputs)
        ]
        response = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
        print(f"DEBUG: Model response: {response}")
        
        # Add to history
        self.history.append({"role": "assistant", "content": response})
        
        # Parse JSON
        return self._parse_json(response)

    def _parse_json(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract JSON tool call from model response."""
        # Try to find JSON block
        json_match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
        if not json_match:
            json_match = re.search(r"(\{.*?\})", text, re.DOTALL)
        
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass
        
        # Fallback: try to find keys manually or just return None
        return None
