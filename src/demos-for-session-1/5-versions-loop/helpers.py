"""
Helpers for this demo only (LLM call + tools). Nothing outside this folder is used.

The demos call an LLM through `call_llm`. It works in 3 modes:

  live     GEMINI_API_KEY is set: call Gemini, and save every reply to cache/
  cached   a reply for this exact prompt is already in cache/: use it
  offline  DEMO_OFFLINE=1 (also true/yes/on): a tiny rule-based stand-in, so the code can be rehearsed with no key and no network. Its answers are NOT real model output; never show them as such.

Order of use: offline if DEMO_OFFLINE is on, else cache hit, else live.

Offline runs are kept apart from real ones: they use their own MLflow database and experiment (see `mlflow_uri()` / `experiment_name()`), and agent traces get an `llm_mode=offline` tag. Run setup_prompts.py with the same DEMO_OFFLINE setting you use for everything else, because the prompt registry lives in that database.

What the offline stand-in reacts to (it is a heuristic, not a model):
  - the agent prompt's wording: concise cues (short, one line, brief, ...) give a short answer, verbose cues (explain, in detail, reasoning, ...) give a long one, and concise wins if both appear. With neither, the answer is short.
  - DEMO_OFFLINE_FAULT=skip_tool: the agent answers without calling spell_check, so the used_spell_check and contains_corrections scorers can be seen to fail.

Logging: plain print() lines prefixed with [llm], [cache], [offline], [tool] or [json].
"""

import hashlib
import json
import os
import re
from pathlib import Path

CACHE = Path(__file__).parent / "cache" # results in a Path variable representing the path path <path-to-parent-directory>/cache, pointing to the folder for cached prompts and responses.
MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite")  # unconfirmed; see setup guide


def offline_enabled() -> bool:
    '''True when DEMO_OFFLINE is set to 1, true, yes or on (case-insensitive).'''
    return os.environ.get("DEMO_OFFLINE", "").strip().lower() in {"1", "true", "yes", "on"}


def mlflow_uri() -> str:
    '''Tracking/registry store. Offline runs get their own database so stand-in results never mix with real ones. An explicit MLFLOW_TRACKING_URI always wins.'''
    explicit = os.environ.get("MLFLOW_TRACKING_URI")
    if explicit:
        return explicit
    return "sqlite:///mlflow_offline.db" if offline_enabled() else "sqlite:///mlflow.db"


def experiment_name() -> str:
    '''MLflow experiment name, suffixed with "-offline" for offline runs.'''
    return "versions-demo-offline" if offline_enabled() else "versions-demo"

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

# Wording cues the stand-in uses to decide between a short and a verbose answer.
_CONCISE_CUES = re.compile(
    r"\b(short|shortly|one[- ]line|one sentence|brief|briefly|concise|concisely|terse|"
    r"no explanation|without explanation|(?:do not|don't|dont) explain)\b",
    re.I,
)
_VERBOSE_CUES = re.compile(r"\b(explain|explanation|in detail|detailed|step[- ]by[- ]step|reasoning)\b", re.I)

# Offline judge: corrections like "orignal -> original" are the content of a good answer, so they are not counted as commentary.
_FIX_PAIR = re.compile(r"[\w']+\s*->\s*[\w']+")
MAX_COMMENTARY_WORDS = 8


def _wants_verbose(template: str) -> bool:
    '''Heuristic: does the prompt text ask for a long answer? Concise cues win over verbose cues; neither means short.'''
    if _CONCISE_CUES.search(template):
        return False
    return bool(_VERBOSE_CUES.search(template))


def _commentary_words(answer: str) -> int:
    '''Words in the answer left over after removing the "Corrections needed:" label and the "x -> y" fixes.'''
    text = re.sub(r"^\s*corrections needed:", "", answer, flags=re.I)
    text = _FIX_PAIR.sub(" ", text)
    return len(re.findall(r"[A-Za-z0-9']+", text))


def _offline_judge(prompt: str) -> str:
    answer = prompt.rsplit("ANSWER:", 1)[-1].strip()
    n = _commentary_words(answer)
    ok = n <= MAX_COMMENTARY_WORDS  # stand-in for "short, no extra commentary"
    rationale = (
        f"Offline stand-in: {n} words of commentary beyond the corrections, "
        + ("short enough to count as concise." if ok else "too much to count as concise.")
    )
    print(f"[offline] rule matched: judge -> pass={ok} ({n} commentary words)")
    return json.dumps({"pass": ok, "rationale": rationale})


def _offline_agent(prompt: str) -> str:
    # The agent prompt is always "<template>\n\nPARAGRAPH: <text>\n" plus "\nObservation: ..." lines (agent.py), so split on that, not on words that could occur anywhere.
    template, _, body = prompt.partition("PARAGRAPH:")
    observations = re.findall(r"^Observation: (.*)$", body, flags=re.M)

    if not observations:
        if os.environ.get("DEMO_OFFLINE_FAULT", "").strip().lower() == "skip_tool":
            print("[offline] fault skip_tool: answering without calling spell_check")
            return json.dumps({"answer": "No spelling problems found."})
        print("[offline] rule matched: no observation yet -> choose tool spell_check")
        return json.dumps({"tool": "spell_check", "args": {"text": _paragraph(body)}})

    last = observations[-1].strip()
    if last.lower().startswith("misspelled:"):
        print("[offline] rule matched: observation has misspellings -> answer with corrections")
        answer = "Corrections needed: " + last[len("misspelled:"):].strip()
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

    # Mimic the live behaviour: a prompt that asks for detail gets a long answer, which is the weakness the 'concise' judge should catch.
    if _wants_verbose(template):
        print("[offline] prompt asks for detail -> verbose answer")
        answer += detail
    return json.dumps({"answer": answer})


def _offline(prompt: str) -> str:
    """Rule-based stand-in so the demo can be rehearsed with no key. NOT model output."""

    # KEY IDEA: recognise which caller is asking from the SHAPE of the prompt (not from words that might appear in user text), and always return valid JSON so parse_json never crashes.

    # Rule 1: the LLM judge (scorers.py) asking for a verdict. Its prompt starts with a fixed sentence.
    if prompt.lstrip().lower().startswith("you are a strict judge"):
        return _offline_judge(prompt)

    # Rule 2: the agent asking for its next step. agent.py always adds a "PARAGRAPH:" marker, even if the prompt text was edited.
    if "PARAGRAPH:" in prompt:
        return _offline_agent(prompt)

    # Fallthrough: still valid JSON, and shaped like an agent final answer, so nothing downstream crashes.
    print("[offline] no rule matched -> returning a placeholder JSON answer")
    return json.dumps({"answer": "offline: no rule matched"})


def _paragraph(body: str) -> str:
    '''The paragraph to spell-check: everything after "PARAGRAPH:" up to the first observation (or the end). Keeps multi-line paragraphs intact.'''
    return re.split(r"\nObservation:", body, maxsplit=1)[0].strip()

#================================================
# HARNESS FOR MODEL CALL

def call_llm(prompt: str) -> str:
    print(f"[llm] call_llm: prompt = {_short(prompt)!r} ({len(prompt)} chars)")

    # Offline mode:
    if offline_enabled():
        print("[llm] mode = OFFLINE (DEMO_OFFLINE is on); reply is NOT real model output")
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