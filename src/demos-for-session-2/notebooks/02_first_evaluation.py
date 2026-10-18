# Databricks notebook source
# MAGIC %md
# MAGIC # Demo 2: First evaluation
# MAGIC
# MAGIC **Concept**: `mlflow.genai.evaluate()` runs your agent over every row of a dataset, then scores each
# MAGIC output with **scorers**. It has three ingredients:
# MAGIC
# MAGIC ```
# MAGIC data  (inputs + expectations) ---+
# MAGIC scorers (built-in judges)     ---+--> mlflow.genai.evaluate() --> results (aggregate + per row)
# MAGIC predict_fn (our traced agent) ---+
# MAGIC ```
# MAGIC
# MAGIC Why demo 1 came first: evaluation runs the agent, creates a trace per row, and some judges (e.g.
# MAGIC `RetrievalGroundedness`) read the **retriever span** of that trace.
# MAGIC
# MAGIC Note: this uses `mlflow.genai.evaluate()`. The older `mlflow.evaluate` is deprecated for LLM apps.

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
mlflow.set_experiment(EXPERIMENT_PATH)

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. The dataset
# MAGIC
# MAGIC Each row has `inputs` (keys match the `predict_fn` arguments) and `expectations` (ground truth). Our 10 questions include: 6 covered by the wiki, 2 **not** in the wiki, 1 out of scope, 1 adversarial.

# COMMAND ----------

from common.eval_data import EVAL_DATA, KIND_BY_QUESTION

print(f"{len(EVAL_DATA)} rows. Example row:\n{EVAL_DATA[0]}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. The predict function
# MAGIC
# MAGIC Rules for `predict_fn`: accept the keys of `inputs` as keyword arguments, return something JSON-serialisable, be traced, and emit exactly one trace per call. Our `answer_question` already does all of that, so the wrapper is trivial.

# COMMAND ----------

from common.agent_traced import answer_question


def predict_fn(question: str) -> dict:
    return answer_question(question)


# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Choose scorers (built-in LLM judges)
# MAGIC
# MAGIC | Judge | Question it answers | Needs |
# MAGIC |---|---|---|
# MAGIC | `Correctness` | Does the response match the expected facts? | `expected_facts` |
# MAGIC | `Safety` | Is the response free of harmful content? | nothing |
# MAGIC | `RetrievalGroundedness` | Is the response supported by what was retrieved? | a `RETRIEVER` span in the trace |
# MAGIC
# MAGIC Judges are LLMs. By default they use a Databricks-hosted judge model. To pick your own, pass `model="databricks:/<endpoint-name>"` to each scorer.

# COMMAND ----------

from mlflow.genai.scorers import Correctness, RetrievalGroundedness, Safety

scorers = [Correctness(), Safety(), RetrievalGroundedness()]

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Run the evaluation
# MAGIC
# MAGIC One call runs the agent on every row, creates a trace per row, and applies all scorers.

# COMMAND ----------

results = mlflow.genai.evaluate(
    data=EVAL_DATA,
    predict_fn=predict_fn,
    scorers=scorers,
)

print(f"run_id: {results.run_id}")
results.metrics

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. What to look at
# MAGIC
# MAGIC Open the **Evaluations** tab of the experiment (the run link printed above). For each row, every judge returns a **`Feedback`** object with:
# MAGIC
# MAGIC - `value`: pass/fail (or a score)
# MAGIC - `rationale`: *why*. Read these. They tell you what failed, not just that it failed.
# MAGIC - `source`: `LLM_JUDGE` here (`CODE` for `@scorer` functions, which is demo 3)
# MAGIC
# MAGIC Click into a row's trace to jump from a failing score to the exact span that caused it.
# MAGIC
# MAGIC Things to check:
# MAGIC 1. Which of the 10 questions fail `RetrievalGroundedness`? (Likely the two **not_in_wiki** rows, but LLM judges vary, so check.)
# MAGIC 2. Do those same rows still *pass* `Correctness`? Correct but ungrounded is exactly what demo 1 hinted at.
# MAGIC 3. What does `Safety` say about the adversarial prompt?

# COMMAND ----------

# Optional: the same data as a table, grouped by question kind. Handy for slicing results.
# Best-effort: column names returned by `search_traces` can differ across MLflow versions, so adjust "request" / "assessments" below if this cell errors. The UI shows the same data.
import pandas as pd

traces = mlflow.search_traces(run_id=results.run_id)
rows = []
for _, t in traces.iterrows():
    question = t["request"]["question"] if isinstance(t["request"], dict) else str(t["request"])
    for a in t["assessments"]:
        rows.append(
            {
                "kind": KIND_BY_QUESTION.get(question, "?"),
                "question": question,
                "judge": a.name,
                "value": a.feedback.value if a.feedback else None,
            }
        )

display(pd.DataFrame(rows).pivot_table(index=["kind", "question"], columns="judge", values="value", aggfunc="first"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Break it
# MAGIC
# MAGIC Our tutor should give **beginners a runnable code example** with each answer. Look at the judge list again:  no built-in judge checks that. `Correctness` can pass an answer that explains the idea in prose only.
# MAGIC
# MAGIC Built-in judges cover common criteria. Your product has *specific* ones.
# MAGIC
# MAGIC **Next: demo 3 adds custom scorers (a guideline judge, a deterministic `@scorer`, and `make_judge()`) to check this and run them all in a single `evaluate()` call.**
