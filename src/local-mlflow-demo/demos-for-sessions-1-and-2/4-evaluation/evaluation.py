"""
Block 2.2 (demo): evaluate the agent with three kinds of scorer.

    python evaluation.py

Open the MLflow UI from this folder to see per-row scores and judge rationales:
    mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001
"""

import mlflow

from agent import run_agent
from helpers import CLEAN_PARAGRAPH, PARAGRAPH
from scorers import CONCISE_GUIDELINE, contains_corrections, make_guideline_judge, used_spell_check

#================================================
# SET MLFLOW EXPERIMENT

mlflow.set_tracking_uri("sqlite:///mlflow.db")
mlflow.set_experiment("evaluation-demo")

#================================================
# DATA TO EVALUATE OVER

DATA = [
    {"inputs": {"paragraph": PARAGRAPH}, "expectations": {"corrections": ["original", "instead"]}},
    {"inputs": {"paragraph": "Please recieve your parcel at the orignal address."}, "expectations": {"corrections": ["receive", "original"]}},
    {"inputs": {"paragraph": CLEAN_PARAGRAPH}, "expectations": {"corrections": []}},
]

#================================================
# EVALUATION HARNESS USE

if __name__ == "__main__":
    result = mlflow.genai.evaluate(
        data=DATA,
        predict_fn=lambda paragraph: run_agent(paragraph),
        scorers=[contains_corrections, used_spell_check, make_guideline_judge("concise", CONCISE_GUIDELINE)],
    )
    mlflow.flush_trace_async_logging()
    print("\nmetrics:")
    for name, value in sorted(result.metrics.items()):
        print(f"  {name}: {value}")
