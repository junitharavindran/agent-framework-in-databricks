"""Evaluate one prompt version on the small dataset (used by the loop and lab L3).

    python setup_prompts.py     # once
    python evaluate.py

Scores the production prompt (v1) on a small dataset. Open the MLflow UI,
experiment "versions-demo", to see per-row scores and judge rationales.
"""
import mlflow

from agent import PRODUCTION_URI, run_agent
from helpers import CLEAN_PARAGRAPH, PARAGRAPH
from scorers import CONCISE_GUIDELINE, contains_corrections, make_guideline_judge, used_spell_check

DATA = [
    {"inputs": {"paragraph": PARAGRAPH}, "expectations": {"corrections": ["original", "instead"]}},
    {"inputs": {"paragraph": "Please recieve your parcel at the orignal address."}, "expectations": {"corrections": ["receive", "original"]}},
    {"inputs": {"paragraph": CLEAN_PARAGRAPH}, "expectations": {"corrections": []}},
]


def evaluate_version(prompt_uri: str, guideline: str = CONCISE_GUIDELINE):
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("versions-demo")
    return mlflow.genai.evaluate(
        data=DATA,
        predict_fn=lambda paragraph: run_agent(paragraph, prompt_uri=prompt_uri),
        scorers=[contains_corrections, used_spell_check, make_guideline_judge("concise", guideline)],
    )


if __name__ == "__main__":
    result = evaluate_version(PRODUCTION_URI)
    mlflow.flush_trace_async_logging()
    print("\nmetrics:")
    for name, value in sorted(result.metrics.items()):
        print(f"  {name}: {value}")
