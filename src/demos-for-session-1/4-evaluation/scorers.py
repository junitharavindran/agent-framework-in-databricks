"""The 3 scorer kinds used in Session 2."""

from mlflow.entities import Feedback
from mlflow.genai.scorers import scorer

from helpers import call_llm, parse_json


# 1. Deterministic custom scorer: plain code, no LLM.
@scorer
def contains_corrections(outputs, expectations) -> bool:
    """Every expected correction must appear in the answer."""
    wanted = expectations.get("corrections", [])
    return all(fix in outputs for fix in wanted)


# 2. Trace-based scorer: looks at HOW the agent got there, not just the answer.
@scorer
def used_spell_check(trace) -> bool:
    """The agent must have called the spell_check tool."""
    return any(span.name == "spell_check" for span in trace.data.spans)


# 3. LLM judge with a guideline: for qualities code cannot check.
CONCISE_GUIDELINE = "The answer is short: it lists the corrections or says there are none, with no extra commentary."


def make_guideline_judge(name: str, guideline: str):
    @scorer(name=name)
    def judge(outputs) -> Feedback:
        prompt = (
            "You are a strict judge. Return JSON only: "
            '{"pass": true or false, "rationale": "one sentence"}.\n'
            f"Guideline: {guideline}\nANSWER: {outputs}"
        )
        verdict = parse_json(call_llm(prompt))
        return Feedback(value="yes" if verdict["pass"] else "no", rationale=verdict["rationale"])

    return judge
