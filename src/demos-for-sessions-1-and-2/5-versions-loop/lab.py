"""
Lab L3 (15 min): create a version and compare.

Starting state: v1 is registered and `production` points to it (run `python setup_prompts.py` if not).

  1. Change ONE line of NEW_PROMPT below (for example the last sentence).
  2. Run this file. It registers v2 and evaluates both versions.
  3. Read the comparison. Does the metric you care about improve?
  4. Edit the last lines so `production` points to the better version. No other code should change: answer() in agent.py stays as it is.

Stretch: flip the alias back and call answer() to confirm the old behaviour returns.

Offline note: with DEMO_OFFLINE=1 the stand-in only reacts to the wording of the prompt (concise cues like "short" or "one line" vs verbose cues like "explain" or "in detail"), so it is good for rehearsing the flow, not for judging prompt quality. Run setup_prompts.py with the same DEMO_OFFLINE setting.
"""

import mlflow
from mlflow.genai import load_prompt, register_prompt, set_prompt_alias

from agent import PRODUCTION_URI, PROMPT_NAME, configure_mlflow
from evaluate import evaluate_version
from setup_prompts import TOOLS_TEXT, ensure_setup

NEW_PROMPT = TOOLS_TEXT + "\nAnswer in one short line."   # <- change the last line

configure_mlflow()
ensure_setup()  # registers v1 + production alias if this mode's database has none yet

# The baseline is whatever `production` serves right now (normally v1), not a hardcoded version number.
baseline = load_prompt(PRODUCTION_URI)
v2 = register_prompt(PROMPT_NAME, NEW_PROMPT, commit_message="lab L3")
old = evaluate_version(f"prompts:/{PROMPT_NAME}/{baseline.version}")
new = evaluate_version(f"prompts:/{PROMPT_NAME}/{v2.version}")
mlflow.flush_trace_async_logging()

for metric in sorted(old.metrics):
    print(f"{metric:<28} v{baseline.version}={old.metrics[metric]:.2f}  v{v2.version}={new.metrics[metric]:.2f}")

# TODO: point production at the better version, e.g. set_prompt_alias(PROMPT_NAME, "production", v2.version)