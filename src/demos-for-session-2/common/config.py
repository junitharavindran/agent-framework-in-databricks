"""Shared settings for all demos."""

# TODO: set to a chat endpoint available in your workspace
LLM_ENDPOINT = "databricks-meta-llama-3-3-70b-instruct"

# TODO: set to a workspace path you own, e.g. /Users/<you>/python-wiki-agent
# NOTE: if demo 6 will store traces in Unity Catalog, create this experiment WITH a UC trace location now. Binding is only possible at experiment creation.
EXPERIMENT_PATH = "/Users/<you>/python-wiki-agent"

TOP_K = 2  # number of wiki pages the retriever returns

# v1 prompt is deliberately loose, so the agent can hallucinate on topics the wiki does not cover. Tightening it later is the "fix" we measure with evaluation.
SYSTEM_PROMPT_V1 = (
    "You are a friendly Python tutor for beginners. "
    "Use the wiki excerpts to answer the question."
)
