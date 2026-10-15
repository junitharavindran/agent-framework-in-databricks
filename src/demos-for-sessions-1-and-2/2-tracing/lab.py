"""
Lab L1 (15 min): trace your function.

Goal: make the `spell_check` tool show up as its own span, under the agent.

  1. Run this file. Open the MLflow UI (mlflow ui --port 5001) and find the experiment "lab-tracing". You should see AGENT and LLM spans, but no spell_check.
  2. Add @mlflow.trace(span_type="TOOL") above `t_spell_check`.
  3. Run again. Find your span: it should sit under proofread_agent and show the text going in and the corrections coming out.

Stretch: make t_spell_check raise an error and find the error span.
"""

import mlflow

from helpers import PARAGRAPH, call_llm, parse_json, spell_check, word_count

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("lab-tracing")


@mlflow.trace(span_type="LLM", name="ask_model")
def ask_model(transcript: str) -> dict:
    return parse_json(call_llm(transcript))


@mlflow.trace(span_type="TOOL", name="word_count")
def t_word_count(text: str) -> int:
    return word_count(text)


# TODO (step 2): add the decorator here
def t_spell_check(text: str) -> str:
    return spell_check(text)


TOOLS = {"word_count": t_word_count, "spell_check": t_spell_check}
SYSTEM = """You are a proofreading assistant. Tools you can use:
- word_count(text): number of words
- spell_check(text): lists misspelled words with fixes
Reply with JSON only: either {"tool": "<name>", "args": {"text": "..."}} to use a tool,
or {"answer": "<short final answer>"} when done. Check spelling before answering."""


@mlflow.trace(span_type="AGENT", name="proofread_agent")
def run_agent(paragraph: str, max_steps: int = 4) -> str:
    transcript = f"{SYSTEM}\n\nPARAGRAPH: {paragraph}\n"
    for _ in range(max_steps):
        decision = ask_model(transcript)
        if "answer" in decision:
            return decision["answer"]
        name, args = decision["tool"], decision["args"]
        transcript += f"\nObservation: {TOOLS[name](**args)}\n"
    return "stopped: too many steps"


if __name__ == "__main__":
    print(run_agent(PARAGRAPH))
    mlflow.flush_trace_async_logging()  # traces export in the background
    print("Done. Open the MLflow UI and look at the newest trace.")
