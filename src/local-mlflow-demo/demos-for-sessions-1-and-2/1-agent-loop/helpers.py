"""
Helpers for this demo only (LLM call + tools). Nothing outside this folder is used.

The demos call an LLM through `call_llm`. It works in 3 modes:

  live     GEMINI_API_KEY is set: call Gemini, and save every reply to cache/
  cached   a reply for this exact prompt is already in cache/: use it
  offline  DEMO_OFFLINE=1: a tiny rule-based stand-in, so the code can be rehearsed with no key and no network. Its answers are NOT real model output; never show them as such.

Order of use: offline if DEMO_OFFLINE=1, else cache hit, else live.
"""

import hashlib
import json
import os
import re
from pathlib import Path

CACHE = Path(__file__).parent / "cache" # results in a Path variable representing the path path <path-to-parent-directory>/cache, pointing to the folder for cached prompts and responses.
MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.5-flash")  # unconfirmed; see setup guide

# The demo "paragraph" used everywhere. Two deliberate misspellings.
PARAGRAPH = (
    "Our new refund policy lets customers return any item within thirty days. "
    "Refunds are issued to the orignal payment method and usually arrive in "
    "five business days. Gift purchases get store credit insted of cash."
)


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
    
    # KEY IDEA:Lok for certain keywords in the prompt and act accordingly.

    p = prompt.lower()
    if "reply with json" in p: # the agent asking for its next step
        if "observation:" not in p:
            return json.dumps({"tool": "spell_check", "args": {"text": _between(prompt)}})
        if "misspelled:" in p:
            answer = "Corrections needed: " + _after(prompt, "misspelled:")
        else:
            answer = "No spelling problems found."
        return json.dumps({"answer": answer})
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
    # Offline mode:
    if os.environ.get("DEMO_OFFLINE") == "1":
        return _offline(prompt)

    # If prompt has been cached with its response (cached mode):
    path = _key(prompt) # obtain the expected cache path given the prompt
    if path.exists():
        return json.loads(path.read_text())["text"]
    
    # If prompt has not been cached with its response (live mode):
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        raise RuntimeError(
            "No cached reply and no GEMINI_API_KEY. Set the key, or run with DEMO_OFFLINE=1 to rehearse."
        )
    from google import genai

    client = genai.Client(api_key=key)
    text = (client.models.generate_content(model=MODEL, contents=prompt).text or "").strip()
    CACHE.mkdir(exist_ok=True) # create cache directory if it does not exist
    path.write_text(json.dumps({"prompt": prompt, "text": text}, indent=2))
    return text

#================================================
# GENERAL HELPER FOR PARSING JSON

def parse_json(text: str) -> dict:
    """Models often wrap JSON in code fences; strip them."""
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(text)

#================================================
# TOOLS

# The tools. Plain Python; no MLflow, no MCP.

KNOWN_MISSPELLINGS = {"orignal": "original", "insted": "instead", "recieve": "receive"}

def word_count(text: str) -> int:
    return len(text.split())

def spell_check(text: str) -> str:
    words = re.findall(r"[a-zA-Z']+", text.lower())
    hits = [f"{w} -> {KNOWN_MISSPELLINGS[w]}" for w in words if w in KNOWN_MISSPELLINGS]
    return "misspelled: " + ", ".join(hits) if hits else "no misspellings"
