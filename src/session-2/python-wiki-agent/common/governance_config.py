"""
Settings for demo 5 (and later demos): Unity Catalog and Unity Gateway.

Kept apart from config.py so the earlier demos stay untouched.
"""

# --- Unity Catalog ---------------------------------------------------------
# TODO: use a catalog you can create schemas in. The schema is created if missing.
CATALOG = "main"
SCHEMA = "python_wiki_agent"
UC_MODEL_NAME = f"{CATALOG}.{SCHEMA}.wiki_agent"  # catalog.schema.object: UC's three-level namespace

# --- Unity Gateway -----------------------------------------------------------
# A model service, named by its Unity Catalog name. Databricks-provided foundation models live under `system.ai` (the docs show names like `system.ai.claude-sonnet-4-5`).
# TODO: set to a model service available in your workspace/region, or one you created.
GATEWAY_MODEL = f"{CATALOG}.{SCHEMA}.wiki_agent_service" # for this to be valid, you have to ensure the model service you create is given the name wiki_agent_service and is deployed in the specified catalog and schema
# "<catalog>.<schema>.<model service name>"
