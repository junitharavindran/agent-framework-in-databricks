"""
Register the prompt versions used in Session 2 (run once; safe to re-run).

v1 asks for a long explanation (the weakness we will find with evaluation).
v2 asks for a short answer (the fix).
"""

from mlflow.genai import load_prompt, register_prompt, set_prompt_alias

from agent import PROMPT_NAME, PRODUCTION_URI, configure_mlflow

TOOLS_TEXT = """You are a proofreading assistant. Tools you can use:
- word_count(text): number of words
- spell_check(text): lists misspelled words with fixes
Reply with JSON only: either {"tool": "<name>", "args": {"text": "..."}} to use a tool, or {"answer": "<final answer>"} when done. Check spelling before answering."""

V1 = TOOLS_TEXT + "\nExplain your reasoning in detail in the answer."
V2 = TOOLS_TEXT + "\nAnswer in one short line: the corrections, or that there are none."


def setup(mlflow_uri=None):
    """Make `production` point at a prompt with the V1 text.

    If production already serves V1 it is reused, so re-running does not pile up duplicate versions. Otherwise V1 is registered as a new version.
    """
    configure_mlflow(mlflow_uri)
    try:
        current = load_prompt(PRODUCTION_URI)
    except Exception:  # no production alias yet
        current = None
    if current is not None and current.template == V1:
        return current
    v1 = register_prompt(PROMPT_NAME, V1, commit_message="v1: detailed answers")
    set_prompt_alias(PROMPT_NAME, "production", v1.version)
    return v1


def ensure_setup():
    """Register v1 and point `production` at it, but only if `production` doesn't exist yet in the current mode's database.

    Used by evaluate.py and lab.py so they work on a fresh checkout or after switching DEMO_OFFLINE on or off. An existing production alias (for example one you promoted) is left alone.
    """
    configure_mlflow()
    try:
        load_prompt(PRODUCTION_URI)
    except Exception:
        v1 = setup()
        print(f"[setup] no 'production' prompt found in this mode's database; registered v{v1.version} and pointed production at it")


def register_v2():
    return register_prompt(PROMPT_NAME, V2, commit_message="v2: short answers")


if __name__ == "__main__":
    v1 = setup()
    print(f"registered v{v1.version}; production -> v{v1.version}")