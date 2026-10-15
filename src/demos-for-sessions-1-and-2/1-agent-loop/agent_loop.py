"""
Block 1.3 (shown practice): the smallest agent loop.

An agent is a loop: ask the model what to do next, run the tool it picks, feed the result back, repeat until it gives an answer. No MLflow, no MCP yet.

    python agent_loop.py # live or cached
    DEMO_OFFLINE=1 python agent_loop.py
"""

from helpers import PARAGRAPH, call_llm, parse_json, spell_check, word_count

TOOLS = {"word_count": word_count, "spell_check": spell_check}

SYSTEM = """You are a proofreading assistant. Tools you can use:
- word_count(text): number of words
- spell_check(text): lists misspelled words with fixes
Reply with JSON only: either {"tool": "<name>", "args": {"text": "..."}} to use a tool,
or {"answer": "<short final answer>"} when done. Check spelling before answering."""


def run_agent(paragraph: str, max_steps: int = 4) -> str:
    transcript = f"{SYSTEM}\n\nPARAGRAPH: {paragraph}\n"
    for step in range(1, max_steps + 1):
        decision = parse_json(call_llm(transcript))          # 1. the model decides
        if "answer" in decision:                              # 4. done
            print(f"step {step}: ANSWER -> {decision['answer']}")
            return decision["answer"]
        name, args = decision["tool"], decision["args"]
        result = TOOLS[name](**args)                          # 2. we run the tool
        print(f"step {step}: TOOL   -> {name}({args['text'][:30]!r}...) = {result}")
        transcript += f"\nObservation: {result}\n"            # 3. feed the result back
    return "stopped: too many steps"


if __name__ == "__main__":
    run_agent(PARAGRAPH)
