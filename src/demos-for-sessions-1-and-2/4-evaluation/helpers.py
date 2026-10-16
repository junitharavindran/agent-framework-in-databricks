"""
Helpers for this demo only (LLM call + tools). Nothing outside this folder is used.

The demos call an LLM through `call_llm`. It works in 3 modes:

  live     GEMINI_API_KEY is set: call Gemini, and save every reply to cache/
  cached   a reply for this exact prompt is already in cache/: use it
  offline  DEMO_OFFLINE=1: a tiny rule-based stand-in, so the code can be rehearsed with no key and no network. Its answers are NOT real model output; never show them as such.

Order of use: offline if DEMO_OFFLINE=1, else cache hit, else live.

Logging: plain print() lines prefixed with [llm], [cache], [offline], [tool] or [json].
"""

import hashlib
import json
import os
import re
from pathlib import Path

CACHE = Path(__file__).parent / "cache" # results in a Path variable representing the path path <path-to-parent-directory>/cache, pointing to the folder for cached prompts and responses.
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")  # unconfirmed; see setup guide

# The demo "paragraph" used everywhere. Two deliberate misspellings.
PARAGRAPH = (
    "Our new refund policy lets customers return any item within thirty days. "
    "Refunds are issued to the orignal payment method and usually arrive in "
    "five business days. Gift purchases get store credit insted of cash."
)

# Seeded failing input for the Session 2 demos: it has no misspellings, so a careless agent that "fixes" something has invented a problem.
CLEAN_PARAGRAPH = "Refunds arrive in five business days. Gift purchases get store credit."


def _short(text: str, n: int = 80) -> str:
    '''Single-line, truncated version of text, for log lines.'''
    text = " ".join(str(text).split())
    return text if len(text) <= n else text[:n] + "..."


def _key(prompt: str) -> Path:
    '''
    - Creates a cache file corresponding to the given prompt by hashing the prompt and creating a JSON file of that name.
    - Returns a Path variable representing the path of the particular cached file for the given prompt (if it exists) in the cache folder.
    '''
    return CACHE / (hashlib.sha256(prompt.encode()).hexdigest()[:16] + ".json")


#================================================
# OFFLINE MODE

def _offline(prompt: str) -> str:
    """Rule-based stand-in so the demo can be rehearsed with no key. NOT model output."""

    # KEY IDEA: look for certain keywords in the prompt and act accordingly. Rules are checked from most to least specific, and every call returns valid JSON where the caller expects JSON (so parse_json never crashes).

    p = prompt.lower()

    # Rule 1: the LLM judge (scorers.py) asking for a verdict.
    if "strict judge" in p:
        answer = prompt.rsplit("ANSWER:", 1)[-1].strip()
        n = len(answer.split())
        ok = n <= 15  # stand-in for "short, no extra commentary"
        rationale = (
            f"Offline stand-in: answer has {n} words, "
            + ("short enough to count as concise." if ok else "too long to count as concise.")
        )
        print(f"[offline] rule matched: judge -> pass={ok} ({n} words)")
        return json.dumps({"pass": ok, "rationale": rationale})

    # Rule 2: the agent asking for its next step.
    if "reply with json" in p:
        # Look only at the part AFTER the paragraph, so the system prompt's own wording (e.g. "misspelled words") can never trigger a rule by accident.
        head, _, body = prompt.partition("PARAGRAPH:")
        body_l = body.lower()
        if "observation:" not in body_l:
            print("[offline] rule matched: no observation yet -> choose tool spell_check")
            return json.dumps({"tool": "spell_check", "args": {"text": _between(prompt)}})

        if "misspelled:" in body_l:
            print("[offline] rule matched: observation has misspellings -> answer with corrections")
            fixes = _after(body, "misspelled:")
            answer = "Corrections needed: " + fixes
            detail = (
                " Explanation: I ran the spell checker over the paragraph and it flagged the words above. "
                "Each one has a standard spelling, so I replaced it with the suggested fix. "
                "Every other word was spelled correctly, so no further edits are needed."
            )
        else:
            print("[offline] rule matched: observation is clean -> answer with no problems")
            answer = "No spelling problems found."
            detail = (
                " Explanation: I ran the spell checker over the paragraph and it reported no misspellings, "
                "so there is nothing to correct and the text should be left unchanged."
            )

        # Mimic the live behaviour: the agent's prompt asks for a detailed explanation, which is the weakness the 'concise' judge should catch. A fixed prompt (no "in detail") gets the short answer.
        if "in detail" in head.lower():
            print("[offline] prompt asks for detail -> verbose answer")
            answer += detail
        return json.dumps({"answer": answer})

    print("[offline] no rule matched -> returning 'ok'")
    return "ok"

# Helpers for offline mode.

def _between(prompt: str) -> str:
    '''Extract the paragraph to be spell-checked from the prompt.'''
    m = re.search(r"PARAGRAPH:\s*(.*?)\s*(?:\n|$)", prompt)
    return m.group(1) if m else ""

def _after(prompt: str, marker: str) -> str:
    '''Extract the substrings marked as misspelled in the prompt.'''
    i = prompt.lower().rfind(marker)
    return prompt[i + len(marker):].strip().splitlines()[0] if i >= 0 else ""

#================================================
# HARNESS FOR MODEL CALL

def call_llm(prompt: str) -> str:
    print(f"[llm] call_llm: prompt = {_short(prompt)!r} ({len(prompt)} chars)")

    # Offline mode:
    if os.environ.get("DEMO_OFFLINE") == "1":
        print("[llm] mode = OFFLINE (DEMO_OFFLINE=1); reply is NOT real model output")
        reply = _offline(prompt)
        print(f"[llm] reply = {_short(reply)}")
        return reply

    # If prompt has been cached with its response (cached mode):
    path = _key(prompt) # obtain the expected cache path given the prompt
    if path.exists():
        print(f"[cache] HIT  {path.name} -> mode = CACHED")
        reply = json.loads(path.read_text())["text"]
        print(f"[llm] reply = {_short(reply)}")
        return reply
    print(f"[cache] MISS {path.name}")

    # If prompt has not been cached with its response (live mode):
    key = os.environ.get("GEMINI_API_KEY")
    if not key:
        print("[llm] ERROR: no cached reply and GEMINI_API_KEY is not set")
        raise RuntimeError(
            "No cached reply and no GEMINI_API_KEY. Set the key, or run with DEMO_OFFLINE=1 to rehearse."
        )
    print(f"[llm] mode = LIVE, calling model {MODEL} ...")
    from google import genai

    client = genai.Client(api_key=key)
    text = (client.models.generate_content(model=MODEL, contents=prompt).text or "").strip()
    print(f"[llm] reply = {_short(text)}")
    CACHE.mkdir(exist_ok=True) # create cache directory if it does not exist
    path.write_text(json.dumps({"prompt": prompt, "text": text}, indent=2))
    print(f"[cache] SAVED {path.name}")
    return text

#================================================
# GENERAL HELPER FOR PARSING JSON

def parse_json(text: str) -> dict:
    """Models often wrap JSON in code fences; strip them."""
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"[json] ERROR parsing {_short(text)!r}: {e}")
        raise
    print(f"[json] parsed keys = {list(data) if isinstance(data, dict) else type(data).__name__}")
    return data

#================================================
# TOOLS

# The tools. Plain Python; no MLflow, no MCP.

KNOWN_MISSPELLINGS = {"orignal": "original", "insted": "instead", "recieve": "receive"}

def word_count(text: str) -> int:
    print(f"[tool] word_count({_short(text, 40)!r})")
    result = len(text.split())
    print(f"[tool] word_count -> {result}")
    return result

def spell_check(text: str) -> str:
    print(f"[tool] spell_check({_short(text, 40)!r})")
    words = re.findall(r"[a-zA-Z']+", text.lower())
    hits = [f"{w} -> {KNOWN_MISSPELLINGS[w]}" for w in words if w in KNOWN_MISSPELLINGS]
    result = "misspelled: " + ", ".join(hits) if hits else "no misspellings"
    print(f"[tool] spell_check -> {result}")
    return result