"""
The Session 2 agent: the proofreading agent, with its system prompt kept in the MLflow prompt registry so it can be versioned and re-pointed by alias.

`answer()` is the "serving code". It never names a version: it loads whatever the `production` alias points to, so flipping the alias changes what runs.
"""

import mlflow
from mlflow.genai import load_prompt

from helpers import (
    call_llm,
    experiment_name,
    mlflow_uri,
    offline_enabled,
    parse_json,
    spell_check,
    word_count,
)

PROMPT_NAME = "proofread-system"
PRODUCTION_URI = f"prompts:/{PROMPT_NAME}@production"


def configure_mlflow(uri: str | None = None, experiment: str | None = None) -> None:
    """Point MLflow at the demo's store and experiment (offline runs get their own, see helpers.py).

    Safe to call repeatedly. Called when this module is imported, so `answer()` also works when used on its own.
    """
    mlflow.set_tracking_uri(uri or mlflow_uri())
    mlflow.set_experiment(experiment or experiment_name())


configure_mlflow()


@mlflow.trace(span_type="LLM", name="ask_model")
def ask_model(transcript: str) -> dict:
    return parse_json(call_llm(transcript))


@mlflow.trace(span_type="TOOL", name="word_count")
def t_word_count(text: str) -> int:
    return word_count(text)


@mlflow.trace(span_type="TOOL", name="spell_check")
def t_spell_check(text: str) -> str:
    return spell_check(text)


TOOLS = {"word_count": t_word_count, "spell_check": t_spell_check}


@mlflow.trace(span_type="AGENT", name="proofread_agent")
def run_agent(paragraph: str, prompt_uri: str = PRODUCTION_URI, max_steps: int = 4) -> str:
    try:
        prompt = load_prompt(prompt_uri)
    except Exception as e:
        raise RuntimeError(
            f"Could not load prompt {prompt_uri!r} from {mlflow_uri()} "
            f"({'offline' if offline_enabled() else 'live'} mode). Offline and live runs use separate databases, "
            "so run `python setup_prompts.py` with the same DEMO_OFFLINE setting as this command."
        ) from e
    # Tag the trace with the version that produced it, so a bad trace can be traced back to a version later.
    if mlflow.get_current_active_span() is not None:
        mlflow.update_current_trace(
            tags={
                "prompt_version": str(prompt.version),
                # "offline" traces come from the rule-based stand-in, not a real model.
                "llm_mode": "offline" if offline_enabled() else "real",
            }
        )
    transcript = f"{prompt.template}\n\nPARAGRAPH: {paragraph}\n"
    for _ in range(max_steps):
        decision = ask_model(transcript)
        if "answer" in decision:
            return decision["answer"]
        name, args = decision["tool"], decision["args"]
        transcript += f"\nObservation: {TOOLS[name](**args)}\n"
    return "stopped: too many steps"


def answer(paragraph: str) -> str:
    """The serving entry point. Unchanged across versions."""
    return run_agent(paragraph)