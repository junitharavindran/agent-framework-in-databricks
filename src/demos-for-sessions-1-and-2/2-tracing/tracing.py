"""
Block 1.4 (demo): MLflow tracing, from nothing to a full span tree.

Run it, then open the UI: mlflow ui --port 5001 (or 5000)

    python tracing.py

Change the variable STEP provided below to do the following:
    
STEP = 1 => 1 decorator on the agent: a trace with a single span
STEP = 2 => Decorators on the LLM call and the tools: a span tree (default)
STEP = 3 => The same, plus a tool that raises: find the error span
"""

STEP = 2

import mlflow

from helpers import PARAGRAPH, call_llm, parse_json, spell_check, word_count

#================================================
# SET UP MLFLOW EXPERIMENT

mlflow.set_tracking_uri("sqlite:///mlflow.db") # local store; no server needed
mlflow.set_experiment("session1-tracing")

#================================================
# TRACED FUNCTIONS

@mlflow.trace(span_type="LLM", name="ask_model")
def ask_model(transcript: str) -> dict:
    return parse_json(call_llm(transcript))


@mlflow.trace(span_type="TOOL", name="word_count")
def t_word_count(text: str) -> int:
    return word_count(text)


@mlflow.trace(span_type="TOOL", name="spell_check")
def t_spell_check(text: str) -> str:
    if STEP == 3:
        raise ValueError("spell-check service unavailable")  # the seeded error
    return spell_check(text)

#================================================
# TOOL AND PROMPT DEFINITIONS

TOOLS = {"word_count": t_word_count, "spell_check": t_spell_check}
SYSTEM = """
You are a proofreading assistant. Tools you can use:
- word_count(text): number of words
- spell_check(text): lists misspelled words with fixes
Reply with JSON only: either {"tool": "<name>", "args": {"text": "..."}} to use a tool, or {"answer": "<short final answer>"} when done. Check spelling before answering.
"""

#================================================
# AGENT RUN

def run_agent(paragraph: str, max_steps: int = 4) -> str:
    transcript = f"{SYSTEM}\n\nPARAGRAPH: {paragraph}\n"
    for _ in range(max_steps):
        decision = ask_model(transcript) if STEP >= 2 else parse_json(call_llm(transcript))
        if "answer" in decision:
            return decision["answer"]
        name, args = decision["tool"], decision["args"]
        impl = TOOLS[name] if STEP >= 2 else {"word_count": word_count, "spell_check": spell_check}[name]
        transcript += f"\nObservation: {impl(**args)}\n"
    return "stopped: too many steps"


# Step 1 traces only this outer function. Steps 2-3 add the inner spans.
run_agent = mlflow.trace(span_type="AGENT", name="proofread_agent")(run_agent)

#================================================
# SHOW LAST TRACE OF AGENT RUN

def show_last_trace():
    mlflow.flush_trace_async_logging() # traces export asynchronously
    traces = mlflow.search_traces(max_results=1, return_type="list")
    trace = traces[0]
    print(f"\ntrace {trace.info.trace_id}  status={trace.info.status}")
    for span in trace.data.spans:
        marker = "  <-- ERROR" if span.status.status_code.name == "ERROR" else ""
        print(f"  {span.span_type or '-':<6} {span.name}{marker}")

#================================================
# RESULTS

if __name__ == "__main__":
    try:
        print(run_agent(PARAGRAPH))
    except Exception as exc:
        print(f"agent failed: {exc}")
    show_last_trace()
