"""
Wiki search as a plain function, for the tool demos (06_tools.py onwards).

Same matching logic as `search_wiki` in the traced agent, with two differences:
    1. No MLflow: the agent loop traces every tool call itself (a TOOL span), and the MCP server (T2) runs in a different process, where it would not join that trace.
    2. JSON-safe output: plain dicts, with `matches` as a list (a `set` cannot be sent over MCP or to the model).
"""

import os
import re

try:  # in the repo
    from common.config import TOP_K
    from common.wiki_pages import WIKI_PAGES
except ModuleNotFoundError as e:  # in the MCP server's app folder, where the modules sit side by side
    if not (e.name or "").startswith("common"):
        raise
    from wiki_pages import WIKI_PAGES

    TOP_K = int(os.environ.get("WIKI_TOP_K", "3"))

# Common words to exclude from query search matches (so the focus is more on keyword matches)...
STOP_WORDS = {
    # articles and determiners
    "a", "an", "the", "this", "that", "these", "those", "some", "any",
    # pronouns
    "i", "me", "my", "you", "your", "it", "its", "we", "they",
    # prepositions and conjunctions
    "in", "of", "to", "on", "at", "by", "into", "than", "so", "but", "then",
    # auxiliary and common verbs
    "is", "are", "was", "be", "do", "does", "did", "can", "could", "should", "will", "would",
    # question words
    "how", "what", "why", "which", "when", "where", "who",
    # filler that appears on many pages
    "use", "using", "make", "get", "just", "like", "also", "python",
}


def _words(text: str) -> set[str]:  # return words in text, excluding stop words
    return set(re.findall(r"[a-z]+", text.lower())) - STOP_WORDS


def search_wiki(query: str, top_k: int = TOP_K) -> list[dict]:
    """Best-matching wiki pages for `query`, as [{id, page_content, score, matches}]."""
    q = _words(query)
    scored = []
    for name, text in WIKI_PAGES.items():
        matches = q & _words(f"{name} {text}")
        if len(matches) > 0:
            scored.append((len(matches), name, text, matches))
    scored.sort(key=lambda s: (s[0], s[1]), reverse=True)  # same order as the original (names are unique)
    return [
        {"id": name, "page_content": text, "score": score, "matches": sorted(matches)}
        for score, name, text, matches in scored[:top_k]
    ]