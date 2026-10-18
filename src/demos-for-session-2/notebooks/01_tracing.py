# Databricks notebook source
# MAGIC %md
# MAGIC # Demo 1: Tracing
# MAGIC
# MAGIC **Concept**: MLflow Tracing records every request as a **trace**, a tree of **spans**. Each span is one operation and captures its inputs, outputs, timing, type and status. Databricks' managed MLflow supports the standard MLflow SDK and is OpenTelemetry-compatible.
# MAGIC
# MAGIC **We change very little**: same agent, plus four small additions (see `common/agent_traced.py`).
# MAGIC
# MAGIC | Addition | What it gives you |
# MAGIC |---|---|
# MAGIC | `mlflow.openai.autolog()` | A `CHAT_MODEL` span for the LLM call, with no extra code |
# MAGIC | `@mlflow.trace(span_type="RETRIEVER")` | A span showing which wiki pages were retrieved |
# MAGIC | `mlflow.start_span(...)` | A manual span for our own logic (prompt building) |
# MAGIC | `@mlflow.trace(span_type="AGENT")` | A root span for the whole request |

# COMMAND ----------

# MAGIC %pip install -U "mlflow[databricks]>=3.1" openai databricks-sdk
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))

import mlflow

from common.config import EXPERIMENT_PATH

mlflow.set_tracking_uri("databricks")
# Traces are logged to an MLflow Experiment. It is the hub for everything in later demos.
# Set EXPERIMENT_PATH in common/config.py first. (If demo 6 will store traces in Unity Catalog, create the experiment with a UC trace location at creation time, not later.)
mlflow.set_experiment(EXPERIMENT_PATH)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Run the traced agent
# MAGIC
# MAGIC In a Databricks notebook the trace is rendered right under the cell. Expand the tree.

# COMMAND ----------

from common.agent_traced import answer_question

result = answer_question("How do I add an item to a list?")
print(result["response"])

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. What to look at in the trace
# MAGIC
# MAGIC A typical trace looks like this (the root is the agent, the children are the steps):
# MAGIC
# MAGIC ```
# MAGIC answer_question          AGENT        <- whole request, total latency
# MAGIC ├── search_wiki          RETRIEVER    <- which pages, with scores
# MAGIC ├── build_prompt         (manual)     <- our own step
# MAGIC └── Completions          CHAT_MODEL   <- prompt, response, tokens
# MAGIC ```
# MAGIC
# MAGIC Click each span and check:
# MAGIC 1. **Inputs / outputs**: what went in and came out
# MAGIC 2. **Duration**: retrieval versus the LLM call
# MAGIC 3. **Span type** and **status**
# MAGIC
# MAGIC You can also open the experiment's **Traces** tab to see all requests in one list.

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Break it
# MAGIC
# MAGIC Now the question the wiki cannot answer. In demo 0 we could only see a fluent answer.

# COMMAND ----------

result = answer_question("How do I handle errors in Python?")
print(result["response"])

# COMMAND ----------

# MAGIC %md
# MAGIC Open the **`search_wiki`** span of this trace:
# MAGIC
# MAGIC - It returned `TOP_K` pages anyway, with a **score of 0** (no overlap with the question).
# MAGIC - The prompt therefore contained irrelevant pages, and the model answered from its own memory.
# MAGIC
# MAGIC The answer may be correct, but it is **not grounded in the wiki**, and now we can *see* that. We found the failure by hand-inspecting one trace. For ten questions that is fine; for ten thousand it is not.
# MAGIC
# MAGIC **Next: demo 2 turns "is this answer good?" into an automated, repeatable measurement.**
