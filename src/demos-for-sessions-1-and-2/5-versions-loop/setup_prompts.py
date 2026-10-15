"""
Register the prompt versions used in Session 2 (run once; safe to re-run).

v1 asks for a long explanation (the weakness we will find with evaluation).
v2 asks for a short answer (the fix).
"""

import mlflow
from mlflow.genai import register_prompt, set_prompt_alias

from agent import PROMPT_NAME

TOOLS_TEXT = """You are a proofreading assistant. Tools you can use:
- word_count(text): number of words
- spell_check(text): lists misspelled words with fixes
Reply with JSON only: either {"tool": "<name>", "args": {"text": "..."}} to use a tool,
or {"answer": "<final answer>"} when done. Check spelling before answering."""

V1 = TOOLS_TEXT + "\nExplain your reasoning in detail in the answer."
V2 = TOOLS_TEXT + "\nAnswer in one short line: the corrections, or that there are none."


def setup(mlflow_uri="sqlite:///mlflow.db"):
    mlflow.set_tracking_uri(mlflow_uri)
    mlflow.set_experiment("versions-demo")
    v1 = register_prompt(PROMPT_NAME, V1, commit_message="v1: detailed answers")
    set_prompt_alias(PROMPT_NAME, "production", v1.version)
    return v1


def register_v2():
    return register_prompt(PROMPT_NAME, V2, commit_message="v2: short answers")


if __name__ == "__main__":
    v1 = setup()
    print(f"registered v{v1.version}; production -> v{v1.version}")
