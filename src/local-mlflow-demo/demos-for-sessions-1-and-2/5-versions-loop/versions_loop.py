"""
Block 2.3 + 2.4 (demo): the small evaluation-driven loop, locally.

    python setup_prompts.py      # once: registers v1, production -> v1
    python versions_loop.py

Steps (each prints a header, so you can pause between them):
  1. Evaluate v1 (production): it fails the "concise" guideline
  2. Fix the prompt: register v2
  3. Re-run the same evaluation on v2 and compare the two
  4. Promote: point `production` at the better version
  5. Serving code is unchanged: answer() now behaves like v2
  6. Roll back: flip the alias to v1 and back
  7. Find a failing trace through its version tag
"""

import mlflow
from mlflow.genai import load_prompt, set_prompt_alias

from agent import PROMPT_NAME, answer
from helpers import PARAGRAPH
from evaluate import evaluate_version
from setup_prompts import register_v2, setup


def header(text: str) -> None:
    print(f"\n=== {text}")


def concise_rate(result) -> float:
    return result.metrics["concise/mean"]


if __name__ == "__main__":
    v1 = setup()

    header("1. Evaluate v1 (production)")
    r1 = evaluate_version(f"prompts:/{PROMPT_NAME}/{v1.version}")
    print("v1 concise:", concise_rate(r1), " corrections:", r1.metrics["contains_corrections/mean"])

    header("2. Fix the prompt: register v2")
    v2 = register_v2()
    print(f"registered v{v2.version}")

    header("3. Re-run the same evaluation on v2 and compare")
    r2 = evaluate_version(f"prompts:/{PROMPT_NAME}/{v2.version}")
    print(f"{'':<27}{'v1':>6}{'v2':>6}")
    for metric in ("concise/mean", "contains_corrections/mean", "used_spell_check/mean"):
        print(f"{metric:<27}{r1.metrics[metric]:>6.2f}{r2.metrics[metric]:>6.2f}")

    header("4. Promote: production -> better version")
    better = v2.version if concise_rate(r2) >= concise_rate(r1) else v1.version
    set_prompt_alias(PROMPT_NAME, "production", better)
    print(f"production -> v{load_prompt(f'prompts:/{PROMPT_NAME}@production').version}")

    header("5. Serving code unchanged: answer() uses whatever production points to")
    print(answer(PARAGRAPH))

    header("6. Roll back: flip the alias, no code change")
    set_prompt_alias(PROMPT_NAME, "production", v1.version)
    print(f"production -> v{load_prompt(f'prompts:/{PROMPT_NAME}@production').version}:", answer(PARAGRAPH))
    set_prompt_alias(PROMPT_NAME, "production", better)
    print(f"flipped back -> v{load_prompt(f'prompts:/{PROMPT_NAME}@production').version}:", answer(PARAGRAPH))

    header("7. Find a trace through the version that produced it")
    mlflow.flush_trace_async_logging()
    for t in mlflow.search_traces(filter_string=f"tag.prompt_version = '{v1.version}'", max_results=3, return_type="list"):
        print(f"  {t.info.trace_id}  prompt_version={t.info.tags['prompt_version']}")
