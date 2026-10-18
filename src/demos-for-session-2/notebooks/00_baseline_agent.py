# Databricks notebook source
# MAGIC %md
# MAGIC # Demo 0: Baseline agent
# MAGIC
# MAGIC **Concept**: an agent here is just *retrieve, then ask an LLM*. We build the simplest possible Python tutor and use it, with no tracing and no evaluation.
# MAGIC
# MAGIC **Goal of this demo**: feel the problem that the next demos solve. When an answer looks wrong, or even looks fine, can you tell *why* it came out that way?
# MAGIC
# MAGIC Notebook flow: concept -> code -> what to look at -> break it.

# COMMAND ----------

# MAGIC %pip install -U "mlflow[databricks]>=3.1" openai databricks-sdk
# MAGIC dbutils.library.restartPython()

# COMMAND ----------

import os
import sys

# Make `common/` importable (it lives one folder above `notebooks/`).
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), "..")))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. The ingredients
# MAGIC
# MAGIC - `common/wiki_pages.py`: a ten-page Python wiki (it deliberately has **no** page on exceptions or classes)
# MAGIC - `common/agent.py`: `search_wiki()` finds the best pages, `answer()` asks the LLM using them
# MAGIC - `common/config.py`: set `LLM_ENDPOINT` to a chat endpoint in your workspace **before running**

# COMMAND ----------

from common.wiki_pages import WIKI_PAGES

print(f"{len(WIKI_PAGES)} wiki pages: {', '.join(WIKI_PAGES)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Ask a few questions

# COMMAND ----------

from common.agent import answer

for q in [
    "How do I add an item to a list?",
    "How do I loop over the numbers 0 to 4?",
]:
    print(f"Q: {q}\nA: {answer(q)}\n{'-' * 60}")

# COMMAND ----------

# MAGIC %md
# MAGIC These look good. What you can see is the question and the answer, and nothing else.
# MAGIC
# MAGIC ## 3. Break it
# MAGIC
# MAGIC The wiki has **no** page on error handling. Ask about it anyway.

# COMMAND ----------

q = "How do I handle errors in Python?"
print(f"Q: {q}\nA: {answer(q)}")

# COMMAND ----------

# MAGIC %md
# MAGIC The answer is fluent and probably correct. But think about what you cannot tell from this output:
# MAGIC
# MAGIC - Which wiki pages did the agent retrieve?
# MAGIC - Did it use them, or answer from the model's memory?
# MAGIC - How long did retrieval take versus the LLM call? How many tokens did it use?
# MAGIC
# MAGIC The only thing you can inspect is the final string. **Next: demo 1 adds tracing so you can see inside.**
