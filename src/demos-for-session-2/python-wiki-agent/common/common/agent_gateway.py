"""
Demo 5: the SAME agent, but the LLM call goes through Unity Gateway.

What changes compared with agent_traced.py (that is the whole lesson):
    1. The OpenAI client points at the gateway:  <workspace>/ai-gateway/mlflow/v1
    2. `model` is the model service's Unity Catalog name (e.g. system.ai.<model>), not a serving-endpoint name
Everything else (retriever, prompt, tracing) is reused as is.

Guardrails, rate limits and usage tracking are NOT in this file. They are configured on the model service, which is why the agent code does not change when policies change.
"""

import os

import mlflow
from databricks.sdk import WorkspaceClient
from openai import OpenAI

from common.agent_traced import search_wiki  # reuse the traced retriever
from common.config import SYSTEM_PROMPT_V1
from common.governance_config import GATEWAY_MODEL

mlflow.openai.autolog()

_w = WorkspaceClient()
_client = OpenAI(
    # In a notebook the SDK picks up a token. If this is None, set DATABRICKS_TOKEN yourself.
    api_key=os.environ.get("DATABRICKS_TOKEN") or _w.config.token,
    base_url=f"{_w.config.host.rstrip('/')}/ai-gateway/mlflow/v1",
)


@mlflow.trace(span_type="AGENT")
def answer_question_via_gateway(question: str) -> dict:
    docs = search_wiki(question)
    context = "\n\n".join(f"[{d.id}] {d.page_content}" for d in docs)
    response = _client.chat.completions.create(
        model=GATEWAY_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT_V1},
            {"role": "user", "content": f"Wiki excerpts:\n{context}\n\nQuestion: {question}"},
        ],
        temperature=0.2,
    )
    return {"response": response.choices[0].message.content}
