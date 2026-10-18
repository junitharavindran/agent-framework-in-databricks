"""
Demo 0: the plain agent. No tracing, no evaluation. Just retrieve, then answer.

Flow (kept deliberately simple and deterministic):
    question -> search_wiki() -> build prompt -> LLM -> answer
The retriever is a toy keyword matcher so beginners can read all of it.
"""

import re

from databricks.sdk import WorkspaceClient

from common.config import LLM_ENDPOINT, SYSTEM_PROMPT_V1, TOP_K
from common.wiki_pages import WIKI_PAGES

_client = WorkspaceClient().serving_endpoints.get_open_ai_client()


def _words(text: str) -> set[str]:
    return set(re.findall(r"[a-z]+", text.lower()))


def search_wiki(query: str, top_k: int = TOP_K) -> list[dict]:
    """Rank wiki pages by how many query words they share. Returns the best `top_k`."""
    q = _words(query)
    scored = [
        (len(q & _words(f"{name} {text}")), name, text)
        for name, text in WIKI_PAGES.items()
    ]
    scored.sort(reverse=True)
    # NOTE: Pages with a score of 0 still get returned. That is the weakness that demo 1 exposes.
    return [{"page": name, "text": text} for _, name, text in scored[:top_k]]


def answer(question: str) -> str:
    pages = search_wiki(question)
    context = "\n\n".join(f"[{p['page']}] {p['text']}" for p in pages)
    response = _client.chat.completions.create(
        model=LLM_ENDPOINT,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_V1},
            {"role": "user", "content": f"Wiki excerpts:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content
