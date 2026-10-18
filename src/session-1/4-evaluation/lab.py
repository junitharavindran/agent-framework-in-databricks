"""
Lab L2 (15 min): write a guideline, then break it.

  1. Run this file. Read the rationale for each row.
  2. Edit GOOD_GUIDELINE if you want it sharper, and run again.
  3. Now set GUIDELINE = VAGUE (or write a contradictory one, for example "The answer must be long and also under ten words"). Run again.
  4. Compare the scores and rationales between runs in the MLflow UI (experiment "evaluation-demo"). Which rationale changed because the guideline changed?

Stretch: add a second guideline judge and pass both to `scorers`.
"""

import mlflow

from agent import run_agent
from helpers import PARAGRAPH, CLEAN_PARAGRAPH
from scorers import make_guideline_judge

GOOD_GUIDELINE = "The answer is short: it lists the corrections or says there are none, with no extra commentary."
VAGUE = "The answer is good."

GUIDELINE = GOOD_GUIDELINE # <- change me

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("evaluation-demo")

result = mlflow.genai.evaluate(
    data=[{"inputs": {"paragraph": PARAGRAPH}}, {"inputs": {"paragraph": CLEAN_PARAGRAPH}}],
    predict_fn=lambda paragraph: run_agent(paragraph),
    scorers=[make_guideline_judge("my_guideline", GUIDELINE)],
)
mlflow.flush_trace_async_logging()
print("score:", result.metrics)
