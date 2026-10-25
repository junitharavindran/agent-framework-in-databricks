"""
Demo 1 onwards: the SAME agent as agent.py, with MLflow Tracing added.

Diff against agent.py (that is the whole lesson):
    1. mlflow.openai.autolog()                  -> LLM call becomes a span automatically
    2. @mlflow.trace(span_type="RETRIEVER")     -> retriever becomes a span
    3. mlflow.start_span(...)                   -> a manual span around prompt building
    4. @mlflow.trace(span_type="AGENT")         -> root span for the whole request
"""

import re

import mlflow
from databricks.sdk import WorkspaceClient
from mlflow.entities import Document

from common.config import LLM_ENDPOINT, SYSTEM_PROMPT_V1, TOP_K
from common.wiki_pages import WIKI_PAGES

mlflow.openai.autolog()  # (1) child span for every OpenAI-client call

_client = WorkspaceClient().serving_endpoints.get_open_ai_client()


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


def _words(text: str) -> set[str]: # return words in text, excluding stop words
    return set(re.findall(r"[a-z]+", text.lower())) - STOP_WORDS


@mlflow.trace(span_type="RETRIEVER")  # (2)
def search_wiki(query: str, top_k: int = TOP_K) -> list[Document]:
    q = _words(query)
    scored = []
    for name, text in WIKI_PAGES.items():
        matches = q & _words(f"{name} {text}")
        if len(matches) > 0:
            scored.append((len(matches), name, text, matches))
    scored.sort(reverse=True)
    # Returning `Document` objects lets retrieval judges (demo 2) read what was retrieved.
    return [
        Document(page_content=text, metadata={"doc_uri": f"wiki/{name}", "score": score, "matches": matches}, id=name)
        for score, name, text, matches in scored[:top_k]
    ]


@mlflow.trace(span_type="AGENT")  # (4)
def answer_question(question: str) -> dict:
    docs = search_wiki(question)

    with mlflow.start_span(name="build_prompt") as span:  # (3)
        context = "\n\n".join(f"[{d.id}] {d.page_content}" for d in docs)
        user_message = f"Wiki excerpts:\n{context}\n\nQuestion: {question}"
        span.set_inputs({"question": question, "pages": [d.id for d in docs]})
        span.set_outputs({"prompt_chars": len(user_message)})

    response = _client.chat.completions.create(
        model=LLM_ENDPOINT,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_V1},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )
    # Return a dict: later demos use this function directly as `predict_fn`.
    return {"response": response.choices[0].message.content}
