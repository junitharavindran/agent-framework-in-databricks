"""
Settings for demo 5 (and later demos): Unity Catalog and Unity Gateway.

Kept apart from config.py so the earlier demos stay untouched.
"""

# --- Unity Catalog ---------------------------------------------------------
# TODO: use a catalog you can create schemas in. The schema is created if missing.
CATALOG = "main"
SCHEMA = "new_python_wiki_agent"
UC_MODEL_NAME = f"{CATALOG}.{SCHEMA}.wiki_agent"  # catalog.schema.object: UC's 3-level namespace

# --- Unity Gateway -----------------------------------------------------------
# A model service, named by its Unity Catalog name. Databricks-provided foundation models live under `system.ai` (the docs show names like `system.ai.claude-sonnet-4-5`).
# TODO: set to a model service available in your workspace/region, or one you created.
GATEWAY_MODEL = "main.new_python_wiki_agent.wiki_agent_llm"
