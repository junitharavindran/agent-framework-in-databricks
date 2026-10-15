"""The agent being evaluated. Its prompt asks for long answers: the weakness that evaluation will expose. (Demo 5 shows how to fix it with a new version.)"""

import mlflow

from helpers import call_llm, parse_json, spell_check, word_count

SYSTEM = """
You are a proofreading assistant. Tools you can use:
- word_count(text): number of words
- spell_check(text): lists misspelled words with fixes
Reply with JSON only: either {"tool": "<name>", "args": {"text": "..."}} to use a tool, or {"answer": "<final answer>"} when done. Check spelling before answering. Explain your reasoning in detail in the answer.
"""

#================================================
# TRACED TOOLS

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

#================================================
# TRACED AGENT RUN FUNCTION

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
