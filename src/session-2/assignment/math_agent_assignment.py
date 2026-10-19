# Databricks notebook source
# MAGIC %md
# MAGIC # Assignment: Build, Trace and Evaluate a Maths Agent
# MAGIC
# MAGIC You get a small, working maths agent that has **no observability at all**.
# MAGIC
# MAGIC Over 12 steps you will:
# MAGIC
# MAGIC - make it observable (tracing)
# MAGIC - measure it (evaluation)
# MAGIC - build your own judges
# MAGIC - check those judges against human opinion
# MAGIC - label question types
# MAGIC
# MAGIC **How this notebook works**
# MAGIC - Cells marked **PROVIDED** run as they are.
# MAGIC - Cells marked with `TODO`s: replace them with your work.
# MAGIC - Markdown cells with `✏️ Your answer` are for your written observations.
# MAGIC - Work top to bottom, and re-run a cell after you edit it.
# MAGIC - Some PROVIDED cells have `# STEP n` comments showing where you will edit them later.
# MAGIC
# MAGIC **You need**:
# MAGIC
# MAGIC - A Databricks workspace
# MAGIC - A chat model serving endpoint that supports tool calling
# MAGIC
# MAGIC > Nothing else: 1 notebook, no extra files.
# MAGIC
# MAGIC **Ground rule**:
# MAGIC
# MAGIC Never clean up the model's output (for example, stripping code fences).
# MAGIC
# MAGIC > The scorers must see exactly what the model said.
# MAGIC
# MAGIC | Step | You will |
# MAGIC |---|---|
# MAGIC | 1-2 | Trace every model call and tool call, with sensible span names and types |
# MAGIC | 3 | Add custom spans inside the error-handling blocks |
# MAGIC | 4 | Run the built-in judges `Correctness` and `RetrievalGroundedness` and record what you see |
# MAGIC | 5-7 | Check "is the output valid JSON?" two ways (a guideline judge, a deterministic scorer) and compare them |
# MAGIC | 8 | Write a custom judge (`make_judge`) for the quality of the `procedure` field |
# MAGIC | 9-11 | Add human feedback, measure judge-human agreement |
# MAGIC | 12 | Tag traces with the question type `irrelevant_question` |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Setup (PROVIDED)

# COMMAND ----------

# MAGIC %pip install -U "mlflow[databricks]>=3.1" openai databricks-sdk

# COMMAND ----------

dbutils.library.restartPython()  # Databricks only. Skip this line elsewhere.

# COMMAND ----------

import json

import mlflow
from databricks.sdk import WorkspaceClient

# TODO (YOUR TURN): set these two values.
LLM_ENDPOINT = "databricks-meta-llama-3-3-70b-instruct" # a chat endpoint that supports tool calling
# NOTE: You can continue to use the above endpoint, which is a Databricks foundational model endpoint; learn more:
# Ref: https://docs.databricks.com/aws/en/machine-learning/model-serving/foundation-model-overview
# Ref: https://docs.databricks.com/aws/en/machine-learning/foundation-model-apis/supported-models#meta-llama-3-3-70b-instruct
EXPERIMENT_PATH = "..."
# E.g.: /Shared/math-agent-assignment

JUDGE_MODEL = f"databricks:/{LLM_ENDPOINT}"  # model used by the custom judges you write later

mlflow.set_tracking_uri("databricks")
mlflow.set_experiment(EXPERIMENT_PATH)  # nothing is recorded here until you add tracing

client = WorkspaceClient().serving_endpoints.get_open_ai_client()
# STEP 1: enable automatic tracing of model calls on the line below this one.

# COMMAND ----------

# MAGIC %md
# MAGIC # Part A: The agent (PROVIDED)
# MAGIC
# MAGIC The agent answers natural-language maths questions by calling **tools**. Read the code before you run it.
# MAGIC
# MAGIC - **Tools**: `add`, `subtract`, `multiply`, `divide`, `factorial`.
# MAGIC - **Error handling**: Tools never crash. They:
# MAGIC   - Catch problems
# MAGIC     > E.g.: Zero division, wrong types, negative or non-whole factorials, too-large factorials.
# MAGIC   - Return `{"error": "..."}` so the model can report them.
# MAGIC - **Agent loop**:
# MAGIC   - Ask the model
# MAGIC   - Run any tool calls it requests
# MAGIC   - Send the results back
# MAGIC   - Repeat until it gives a final answer
# MAGIC - **Output contract**: The final answer must be one JSON object in the following format: <br> `  {"input": "What is 15 plus 27?", "output": 42, "procedure": "Called add with a=15 and b=27, which returned 42."}`
# MAGIC   > This contract is what steps 5-8 check.
# MAGIC
# MAGIC | Field | Rule |
# MAGIC |---|---|
# MAGIC | `input` | A non-empty string: the user's question, copied exactly |
# MAGIC | `output` | A number (the final result) **or** a non-empty string (an error or refusal message). Not null, not a boolean |
# MAGIC | `procedure` | A non-empty string explaining the steps taken and the tools used, in order |
# MAGIC | whole reply | A single JSON object with exactly these three fields, with no code fences and no text outside the JSON |

# COMMAND ----------

# --- Tools ---
import math
import operator

MAX_FACTORIAL = 100


def _num(x):
    """Return x if it is a real number, otherwise raise TypeError."""
    if isinstance(x, bool) or not isinstance(x, (int, float)):
        raise TypeError(f"expected a number, got {type(x).__name__}: {x!r}")
    return x


def _arith(op_name, fn, a, b):
    arith_input = {"op_name": op_name, "arguments": [a, b]}
    try:
        arith_result = {"result": fn(_num(a), _num(b))}
    except TypeError as e:
        arith_result = {"error": f"TypeError: {e}"}
    except ZeroDivisionError:
        arith_result = {"error": "ZeroDivisionError: cannot divide by zero"}
    return arith_result

# STEP 1-2: trace this tool (give it a name and a span type)
@mlflow.trace(span_type="TOOL", name="add")
def add(a, b):
    return _arith("add", operator.add, a, b)


# STEP 1-2: TODO: trace this tool
def subtract(a, b):
    return _arith("subtract", operator.sub, a, b)


# STEP 1-2: TODO: trace this tool
def multiply(a, b):
    return _arith("multiply", operator.mul, a, b)


# STEP 1-2: TODO: trace this tool
def divide(a, b):
    return _arith("divide", operator.truediv, a, b)

# STEP 1-2: TODO: trace this tool
def factorial(n):
    factorial_input = {"n": n}
    try:
        n = _num(n)
        if isinstance(n, float):
            if not n.is_integer():
                raise TypeError(f"factorial needs a whole number, got {n}")
            n = int(n)
        if n < 0:
            raise ValueError("factorial is not defined for negative numbers")
        if n > MAX_FACTORIAL:
            raise OverflowError(f"n is too large (limit is {MAX_FACTORIAL})")
        factorial_result = {"result": math.factorial(n)}
    except TypeError as e:
        factorial_result = {"error": f"TypeError: {e}"}
        # STEP 3: TODO: add a custom span here
    except ValueError as e:
        factorial_result = {"error": f"ValueError: {e}"}
        # STEP 3: TODO: add a custom span here
    except OverflowError as e:
        factorial_result = {"error": f"OverflowError: {e}"}
        # STEP 3: TODO: add a custom span here
    return factorial_result

# COMMAND ----------

# --- Tool descriptions the model sees, and the dispatcher ---
def _spec(name, description, params):
    return {
        "type": "function", "function": {
        "name": name, "description": description,
        "parameters": {
            "type": "object",
            "properties": {p: {"type": "number", "description": d} for p, d in params.items()},
            "required": list(params)
            }
        }
    }


TOOLS_SPEC = [
    _spec("add", "Add two numbers.", {"a": "first number", "b": "second number"}),
    _spec("subtract", "Subtract b from a.", {"a": "first number", "b": "second number"}),
    _spec("multiply", "Multiply two numbers.", {"a": "first number", "b": "second number"}),
    _spec("divide", "Divide a by b.", {"a": "numerator", "b": "denominator"}),
    _spec("factorial", "Factorial of a non-negative whole number.", {"n": "the number"}),
]
TOOL_FUNCS = {"add": add, "subtract": subtract, "multiply": multiply, "divide": divide, "factorial": factorial}

# COMMAND ----------

# --- The agent ---
SYSTEM_PROMPT = """
You are a careful maths assistant. You can ONLY do arithmetic.
Use the provided tools for every calculation (add, subtract, multiply, divide, factorial). Never calculate in your head.
For multi-step questions, call the tools one after another.
If a tool returns an error, do not retry with made-up numbers: report the error.
If the question is not about arithmetic, say that you can only help with arithmetic.

Your FINAL reply must be a single JSON object and nothing else: no markdown, no code fences, no text before or after it.
It must have exactly these fields:
  "input":     the user's question, copied exactly (a string)
  "output":    the final numeric answer (a number), or a short error/refusal message (a string)
  "procedure": an explanation of the steps you took and the tools you used, in order (a string)
Example: {"input": "What is 2 plus 3?", "output": 5, "procedure": "Called add with a=2 and b=3, which returned 5."}
"""


# STEP 1-2: TODO: trace the agent entry point (name + span type)
def run_agent(question: str, max_steps: int = 6) -> dict:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": question}]
    for _ in range(max_steps):
        response = client.chat.completions.create(
            model=LLM_ENDPOINT, messages=messages, tools=TOOLS_SPEC, temperature=0
        )
        msg = response.choices[0].message
        if not msg.tool_calls:
            return {"response": msg.content}  # the raw final text: do NOT clean it
        messages.append(
            {
                "role": "assistant",
                "content": msg.content or "", "tool_calls": [
                    {
                        "id": c.id,
                        "type": "function",
                        "function": {"name": c.function.name, "arguments": c.function.arguments}
                    }
                    for c in msg.tool_calls
                ]
            }
        )
        for call in msg.tool_calls:
            fn = TOOL_FUNCS.get(call.function.name)
            if fn is None:
                result = {"error": f"unknown tool: {call.function.name}"}
            try:
                result = fn(**json.loads(call.function.arguments))
            except (json.JSONDecodeError, TypeError) as e:  # malformed or wrongly named arguments
                return {"error": f"bad tool call: {e}"}
            messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
    return {"response": json.dumps(
            {
                "input": question,
                "output": "error: too many steps",
                "procedure": "The agent reached its step limit."
            }
        )
    }

# COMMAND ----------

# Smoke test (no tracing yet): you can see the answer, but not *how* it was produced.
for q in ["What is 15 plus 27?", "Divide 10 by 0.", "What is (3 + 4) times 5?", "Give me the factorial of 5.1."]:
    print(q, "->", run_agent(q)["response"], "\n")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Evaluation dataset (PROVIDED)
# MAGIC
# MAGIC Each row has the question (`inputs`) and `expected_facts` that a correct answer must contain (`expectations`).

# COMMAND ----------

def _row(question, *facts):
    return {"inputs": {"question": question}, "expectations": {"expected_facts": list(facts)}}


EVAL_DATA = [
    _row("What is 15 plus 27?", "The result is 42"),
    _row("Multiply 12 by 8.", "The result is 96"),
    _row("What is 100 divided by 4?", "The result is 25"),
    _row("What is 10 minus 25?", "The result is -15"),
    _row("What is 5 factorial?", "The result is 120"),
    _row("What is 10 factorial?", "The result is 3628800"),
    _row("Divide 10 by 0.", "Division by zero is not possible and the agent reports an error"),
    _row("What is the factorial of -3?", "Factorial is not defined for negative numbers"),
    _row("What is the factorial of 2.5?", "Factorial requires a whole number"),
    _row("What is (3 + 4) times 5?", "The result is 35"),
    _row("What is the capital of France?", "The agent says it can only help with arithmetic and does not answer the geography question"),
]
print(len(EVAL_DATA), "questions")


def predict_fn(question: str) -> dict:
    """What mlflow.genai.evaluate() calls for every row."""
    return run_agent(question)

# COMMAND ----------

# MAGIC %md
# MAGIC # Part 1: Tracing
# MAGIC
# MAGIC ## Steps 1-2: Trace every model call and tool call
# MAGIC > With proper span names and types.
# MAGIC
# MAGIC **Step 1.** Add tracing:
# MAGIC 1. Model calls: in the setup cell:
# MAGIC     - Enable OpenAI autologging (`mlflow.openai.autolog()`).
# MAGIC       > Every model call becomes a span automatically.
# MAGIC 2. Tool calls and the agent:
# MAGIC     - Add the `@mlflow.trace(...)` decorator at each `# STEP 1-2` marker (5 tools and `run_agent`).
# MAGIC
# MAGIC **Step 2.** Give every span a clear **name** and the right **span type**.
# MAGIC
# MAGIC > **NOTE**:
# MAGIC > 
# MAGIC > - Read the documentation and choose.
# MAGIC > - MLflow also supports custom span types.
# MAGIC > - You are not limited to what is in the documentation.
# MAGIC > - But the documentation contains well-defined span types.
# MAGIC > - Hence, it is good practice to use them where appropriate.
# MAGIC
# MAGIC - Span concepts: https://mlflow.org/docs/latest/genai/concepts/span/
# MAGIC - Manual and custom tracing (decorator parameters): https://docs.databricks.com/aws/en/mlflow3/genai/tracing/manual-tracing
# MAGIC - Tracing overview: https://mlflow.org/docs/latest/genai/tracing/
# MAGIC - API reference (look for `SpanType`): https://mlflow.org/docs/latest/api_reference/index.html
# MAGIC
# MAGIC Decorator shape: `@mlflow.trace(name="...", span_type=...)`
# MAGIC
# MAGIC **✏️ Your answer.** Fill in the table after reading the docs. (Hint: our agent has no retriever, so consider which listed types do *not* apply, too.)
# MAGIC
# MAGIC | Span | Name I gave it | Span type I chose | Why this type |
# MAGIC |---|---|---|---|
# MAGIC | Agent entry point (`run_agent`) | TODO | TODO | TODO |
# MAGIC | Calculator tools (`add` ... `factorial`) | TODO | TODO | TODO |
# MAGIC | Model call (set by autolog) | (automatic) | TODO | TODO |

# COMMAND ----------

# TODO: Enable MLflow OpenAI autologging

# COMMAND ----------

# CHECK (PROVIDED): run once, then print the spans MLflow recorded.
def span_report(trace_id):
    trace = mlflow.get_trace(trace_id)
    for s in trace.data.spans:
        print(f"{s.name:<30} {str(s.span_type):<12} parent={s.parent_id}")
    return trace


run_agent("What is 6 plus 7?")
trace = span_report(mlflow.get_last_active_trace_id())

types = {str(s.span_type) for s in trace.data.spans}
assert "CHAT_MODEL" in types, "No model-call span found: did you enable mlflow.openai.autolog()?"
assert "TOOL" in types, "No tool span found: did you trace the tools, with the right span type?"
print("\nOK. Now open the experiment's Traces tab and click into this trace.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3: Custom spans in factorial error-handling blocks
# MAGIC
# MAGIC Tool errors are returned as data, so a trace looks "successful" even when a tool failed.
# MAGIC
# MAGIC > Make failures visible: at each `# STEP 3` marker in the factorial function, open a custom span inside the `except` block.
# MAGIC
# MAGIC Pattern (worked example, choose your own span type):
# MAGIC
# MAGIC ```py
# MAGIC except OverflowError as e:
# MAGIC     # --- ADDING CUSTOM SPAN...
# MAGIC     with mlflow.start_span(name="error_overflow", span_type=<your choice>) as span:
# MAGIC         span.set_inputs({"n": n})
# MAGIC         span.set_outputs({"error": str(e)})
# MAGIC     # ... ADDED CUSTOM SPAN ---
# MAGIC     ...
# MAGIC ```
# MAGIC
# MAGIC Rules: Every span name must contain `error`, and each should record the relevant inputs and the error message.
# MAGIC
# MAGIC **✏️ Your answer.** Which span type did you use for error spans, and why?
# MAGIC > TODO

# COMMAND ----------

# CHECK (PROVIDED). If the model answered without calling a tool, just re-run the cell.
for q in ["What is the factorial of -3?", "What is the factorial of 5.1?"]:
    run_agent(q)
    t = span_report(mlflow.get_last_active_trace_id())
    assert any("error" in s.name.lower() for s in t.data.spans), f"No error span for: {q}"
    # NOTE:
    # - You may get assertion errors if the model does not even call the factorial tool.
    # - If that is the case, do not debug further, just note the issue as an issue with the agent.
    print()
print("OK: error spans found.")

# COMMAND ----------

# MAGIC %md
# MAGIC # Part 2: Evaluation with built-in judges
# MAGIC
# MAGIC ## Step 4: `Correctness` and `RetrievalGroundedness`
# MAGIC
# MAGIC Instantiate both judges and run the evaluation. Import them from `mlflow.genai.scorers`.
# MAGIC
# MAGIC Then open the run in MLflow (**Experiments > your experiment > Evaluations**), look at each row, and fill in the table below.
# MAGIC Read the judges' **rationales**, not just the scores.

# COMMAND ----------

from mlflow.genai.scorers import Correctness, RetrievalGroundedness

builtin_scorers = [
    # TODO: instantiate Correctness and RetrievalGroundedness
]
assert len(builtin_scorers) == 2, "Add both judges"

results_builtin = mlflow.genai.evaluate(data=EVAL_DATA, predict_fn=predict_fn, scorers=builtin_scorers)
RUN_BUILTIN = results_builtin.run_id
print("run_id:", RUN_BUILTIN)
results_builtin.metrics

# COMMAND ----------

# MAGIC %md
# MAGIC **✏️ Your answer** (copy what you see in MLflow):
# MAGIC
# MAGIC | Judge | Rows passed / total | Rows that failed (questions) | What the rationale said |
# MAGIC |---|---|---|---|
# MAGIC | Correctness | TODO | TODO | TODO |
# MAGIC | RetrievalGroundedness | TODO | TODO | TODO |
# MAGIC
# MAGIC Questions:
# MAGIC 1. Does `Correctness` agree with your own reading of the outputs? Name one row where it is right and one where it surprised you.
# MAGIC    > TODO
# MAGIC 2. What did `RetrievalGroundedness` report for this agent, and **why**? (Hint: what does this judge need to find in a trace? Look at your span types.)
# MAGIC    > TODO
# MAGIC 3. Given your answer to 2, is this judge useful for this agent? What kind of agent would it suit?
# MAGIC    > TODO

# COMMAND ----------

# MAGIC %md
# MAGIC # Part 3: Is the output valid JSON? 2 ways to check
# MAGIC
# MAGIC All three steps below use the **output spec** table from Part A.
# MAGIC
# MAGIC ## Step 5: A guideline judge
# MAGIC
# MAGIC A guideline judge checks a rule written in plain English. Write the rule(s) so that a judge can decide pass or fail from the reply.
# MAGIC
# MAGIC > **TIP**: Refer to the input as **"the request"** and the output as **"the response"**. Be specific: cover *all* the spec's rules (single JSON object, exactly three fields, each field's valid values, nothing outside the JSON).

# COMMAND ----------

from mlflow.genai.scorers import Guidelines

valid_json_guideline = Guidelines(
    name="valid_json_output",
    guidelines=[
        # TODO: one plain-English rule per line, e.g. "The response must be ..."
        "..."
    ],
)
assert valid_json_guideline.guidelines, "Write at least one guideline"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6: A deterministic scorer
# MAGIC
# MAGIC Write the same check as plain Python with the `@scorer` decorator. Return a `Feedback` with a `value` (True/False) and a helpful `rationale` that names the first rule that failed.
# MAGIC
# MAGIC Keep imports **inside** the function, and do not use type hints (this is what lets a scorer be registered for production monitoring later).

# COMMAND ----------

from mlflow.genai.scorers import scorer


@scorer
def valid_json_format(outputs):
    import json

    from mlflow.entities import Feedback

    text = outputs["response"] if isinstance(outputs, dict) else str(outputs)

    # Check 1 (worked example): can the text be read as JSON at all?
    try:
        data = json.loads(text)
    except (json.JSONDecodeError):
        return Feedback(value=False, rationale="Not valid JSON (this includes text around the JSON or code fences).")

    # Check 2 - TODO: the JSON must be a dict (a {...} object), not a list, string or number.
    # HINT: if not isinstance(data, dict) ...

    # Check 3 - TODO: the keys must be EXACTLY "input", "output", "procedure" (no missing, no extra).
    # HINT: compare `set(data)` with `{"input", "output", "procedure"}` (you can use regular logical operators).
    
    # Check 4 - TODO: output field cannot be null (represented as None in Python)
    # HINT: if data["output"] is None

    # Check 5 - TODO: output field cannot be boolean
    # HINT: if isinstance(data["output"], bool) ...

    # Check 6 - TODO: procedure cannot be an empty or blankspace string
    # HINT: if data["procedure"].strip() == "" ...

    return Feedback(value=True, rationale="Valid JSON with valid fields.")

# COMMAND ----------

# SELF-TEST (PROVIDED): your scorer must pass these before you move on.
good = '{"input": "2+3", "output": 5, "procedure": "Called add."}'
good_str = '{"input": "capital?", "output": "I can only do arithmetic.", "procedure": "No tool needed."}'
bad = {
    "plain text": "The answer is 5",
    "code fence": '```json\n{"input": "q", "output": 5, "procedure": "p"}\n```',
    "missing field": '{"input": "q", "output": 5}',
    "extra field": '{"input": "q", "output": 5, "procedure": "p", "note": "x"}',
    "null output": '{"input": "q", "output": null, "procedure": "p"}',
    "bool output": '{"input": "q", "output": true, "procedure": "p"}',
    "empty procedure": '{"input": "q", "output": 5, "procedure": ""}',
    "not an object": '[1, 2, 3]',
}
assert valid_json_format(outputs={"response": good}).value is True, "should accept good JSON"
assert valid_json_format(outputs={"response": good_str}).value is True, "should accept a string output"
for label, text in bad.items():
    assert valid_json_format(outputs={"response": text}).value is False, f"should reject: {label}"
print("Self-test passed.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 7: Compare the two approaches
# MAGIC
# MAGIC Run both on the same agent outputs, then compare.

# COMMAND ----------

def as_bool(v):
    return str(v).lower() in ("true", "yes")


def outputs_by_question(run_id):
    """question -> (trace_id, raw model reply) for every trace of an evaluation run."""
    out = {}
    for t in mlflow.search_traces(run_id=run_id, return_type="list"):
        try:
            q = json.loads(t.data.request)["question"]
            r = json.loads(t.data.response)
            out[q] = (t.info.trace_id, r["response"] if isinstance(r, dict) else r)
        except TypeError:
            continue # in case t.data.request and t.data.response are not a string or bytestring or bytearray, for some reason
    return out


results_format = mlflow.genai.evaluate(
    data=EVAL_DATA, predict_fn=predict_fn, scorers=[valid_json_guideline, valid_json_format])
RUN_FORMAT = results_format.run_id

import pandas as pd

rows = []
for q, (_, text) in outputs_by_question(RUN_FORMAT).items():
    det = valid_json_format(outputs={"response": text})
    gl = valid_json_guideline(inputs={"question": q}, outputs={"response": text})
    rows.append(
        {
            "question": q,
            "deterministic": as_bool(det.value),
            "guideline": as_bool(gl.value),
            "raw reply (start)": text[:70]
        }
    )
comparison = pd.DataFrame(rows)
comparison

# COMMAND ----------

# MAGIC %md
# MAGIC Look at the rows where the two **disagree** (and at the rationales in MLflow), then fill in:
# MAGIC
# MAGIC **✏️ Your answer**
# MAGIC
# MAGIC | | Deterministic `@scorer` | Guideline judge |
# MAGIC |---|---|---|
# MAGIC | Rows flagged invalid | TODO | TODO |
# MAGIC | Cost and speed | TODO | TODO |
# MAGIC | Same answer every time? | TODO | TODO |
# MAGIC | Strictness on exact fields and types | TODO | TODO |
# MAGIC | Can it judge "meaning" (e.g. is `output` plausible for `input`)? | TODO | TODO |
# MAGIC | Quality of failure explanation | TODO | TODO |
# MAGIC | One concrete mistake I observed | TODO | TODO |
# MAGIC
# MAGIC 1. Describe one row where they disagreed, who was right, and why.
# MAGIC    > TODO (if they never disagreed, say so, and describe an input that *could* make them disagree)
# MAGIC 2. For this check, which would you run on every production request, and why?
# MAGIC    > TODO

# COMMAND ----------

# MAGIC %md
# MAGIC # Part 4: A custom judge for the `procedure` field
# MAGIC
# MAGIC ## Step 8: `make_judge`
# MAGIC
# MAGIC Write a judge named **`procedure_clarity`** that returns **true** when the `procedure` field shows **clear logic without excessive content**, otherwise false. Your instructions must define both ideas concretely, so that two different people (or models) would reach the same verdict. For example, consider:
# MAGIC
# MAGIC - *Clear logic*:
# MAGIC   - Do the steps follow the order the calculation was done?
# MAGIC   - Do they name the tools actually used?
# MAGIC   - Do they explain how the result was reached?
# MAGIC - *Excessive content*:
# MAGIC   - Repetition, restating the question
# MAGIC   - Unrelated commentary
# MAGIC   - Steps that did not happen
# MAGIC   - More text than the calculation needs (decide what "too long" means for this agent)
# MAGIC
# MAGIC Use the `{{ inputs }}` and `{{ outputs }}` placeholders.
# MAGIC
# MAGIC Keep the name exactly `procedure_clarity`: human feedback is matched to the judge by name.

# COMMAND ----------

from mlflow.genai.judges import make_judge

procedure_judge = make_judge(
    name="procedure_clarity",
    # TODO: write your instructions.
    # - The request is in {{ inputs }}
    # - The response is in {{ outputs }}.
    # - State what makes the `procedure` field clear and what makes it excessive.
    # - Then say to answer true only when it is clear and not excessive.
    instructions="""
    ...
    """,
    feedback_value_type=bool,  # if your MLflow version rejects this argument, remove it
    model=JUDGE_MODEL,
)

# COMMAND ----------

results_procedure = mlflow.genai.evaluate(data=EVAL_DATA, predict_fn=predict_fn, scorers=[procedure_judge])
RUN_PROCEDURE = results_procedure.run_id
outs = outputs_by_question(RUN_PROCEDURE)  # question -> (trace_id, raw reply)
print("run_id:", RUN_PROCEDURE)

# COMMAND ----------

# MAGIC %md
# MAGIC **✏️ Your answer.** Open the run in MLflow and read the `procedure_clarity` rationales.
# MAGIC
# MAGIC - Rows judged **not clear / excessive**: TODO
# MAGIC - Does the judge's reasoning look right to you for at least two of them? TODO

# COMMAND ----------

# MAGIC %md
# MAGIC # Part 5: Humans vs. the judge
# MAGIC
# MAGIC ## Step 9: Provide human feedback
# MAGIC
# MAGIC Read the model's replies for the six questions below, then give your own verdict using the **same definition** as your judge
# MAGIC (clear logic, not excessive): `True` = the procedure is good, `False` = it is not. Add a one-line reason. Fill in `HUMAN_REVIEW` exactly in this structure (do not rename or remove questions):

# COMMAND ----------

QUESTIONS_FOR_HUMAN_REVIEW = [
    "What is 15 plus 27?",
    "What is 5 factorial?",
    "Divide 10 by 0.",
    "What is the factorial of -3?",
    "What is (3 + 4) times 5?",
    "What is the capital of France?",
]

for q in QUESTIONS_FOR_HUMAN_REVIEW:  # read these first
    print(f"Q: {q}\nREPLY: {outs[q][1]}\n{'-' * 70}")

# COMMAND ----------

REVIEWER = "student@example.com" # put your own email so the feedback has a traceable source

# TODO: replace each (None, "") with (True or False, "one-line reason").
HUMAN_REVIEW = {
    "What is 15 plus 27?":            (None,  ""),
    "What is 5 factorial?":           (None,  ""),
    "Divide 10 by 0.":                (None,  ""),
    "What is the factorial of -3?":   (None,  ""),
    "What is (3 + 4) times 5?":       (None,  ""),
    "What is the capital of France?": (None,  ""),
}

# COMMAND ----------

# PROVIDED: logs your verdicts on the traces. Re-running it adds duplicates, so run it once after filling in.
from mlflow.entities import AssessmentSource, AssessmentSourceType

assert all(v is not None for v, _ in HUMAN_REVIEW.values()), "Fill in every verdict first"

for q, (value, why) in HUMAN_REVIEW.items():
    mlflow.log_feedback(
        trace_id=outs[q][0],
        name="procedure_clarity", # same name as the judge, so the two can be compared
        value=value,
        rationale=why,
        source=AssessmentSource(source_type=AssessmentSourceType.HUMAN, source_id=REVIEWER),
    )
print("Logged", len(HUMAN_REVIEW), "human verdicts. Open a trace in the UI to see them next to the judge's.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 10: Compare judge and human agreement
# MAGIC
# MAGIC Complete the loop below: for each reviewed question, get the judge's verdict on the *same stored reply* and compare it with the human's.

# COMMAND ----------

def measure(judge, verbose=True):
    """Agreement between `judge` and HUMAN_REVIEW, on the stored replies."""
    rows = []
    for q, (human_value, _) in HUMAN_REVIEW.items():
        fb = judge(inputs={"question": q}, outputs={"response": outs[q][1]})
        judge_value = as_bool(fb.value)
        rows.append({
            "question": q,
            "human": human_value,
            "judge": judge_value,
            "agree": human_value == judge_value, # TODO: True when the human and the judge gave the same verdict, False otherwise
        })
    df = pd.DataFrame(rows)
    rate = df["agree"].mean()
    if verbose:
        print(f"Agreement: {rate:.0%} ({int(df['agree'].sum())}/{len(df)})")
    return rate, df


rate_v1, df_v1 = measure(procedure_judge)
df_v1

# COMMAND ----------

# MAGIC %md
# MAGIC **✏️ Your answer**
# MAGIC
# MAGIC - Agreement rate: TODO
# MAGIC - Disagreements: for each one, say whether the judge was too **strict** or too **lenient**, and quote the part of its rationale that explains it.
# MAGIC   > TODO
# MAGIC - Six labelled rows is a tiny sample. What can and can't you conclude from it?
# MAGIC   > TODO

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 11: Alignment (if needed)
# MAGIC
# MAGIC **Decide**: if every verdict agreed, say so below and skip to step 12. Otherwise, align the judge.
# MAGIC
# MAGIC **Option A: manual alignment (do this one).** Use your disagreements to rewrite the instructions (make the vague parts concrete: lengths, what counts as a step, what to ignore),
# MAGIC create `procedure_judge_v2` (same name!), and re-measure.

# COMMAND ----------

procedure_judge_v2 = make_judge(
    name="procedure_clarity",
    # TODO: your improved instructions ({{ inputs }}, {{ outputs }}).
    instructions="""
    ...
    """,
    feedback_value_type=bool,
    model=JUDGE_MODEL,
)

rate_v2, df_v2 = measure(procedure_judge_v2)
print(f"v1: {rate_v1:.0%}  ->  v2: {rate_v2:.0%}")
df_v2

# COMMAND ----------

# MAGIC %md
# MAGIC **✏️ Your answer**
# MAGIC
# MAGIC - Decision (skip alignment / align) and why: TODO
# MAGIC - What did you change in the instructions, and which disagreement did each change target? TODO
# MAGIC - Did v2 fix the disagreements without breaking any agreement? Be honest about overfitting to six rows. TODO
# MAGIC
# MAGIC **Option B: automatic alignment (optional stretch).** (not given)
# MAGIC
# MAGIC Check the docs: https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/alignment/

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 12: Tag the traces for the irrelevant questions
# MAGIC
# MAGIC Tag the trace for the irrelevant questions (e.g. "What is the capital of France") with:
# MAGIC
# MAGIC - Key: question_type
# MAGIC - Value: irrelevant_question

# COMMAND ----------

# TODO: find and place the trace IDs for questions containing irrelevant questions in this list
trace_ids = []

tagged = 0
for trace_id in trace_ids:
    mlflow.set_trace_tag(trace_id=trace_id, key="question_type", value="irrelevant_question")
    tagged += 1

# COMMAND ----------

# CHECK (PROVIDED): read the tags back by searching for them.
found = mlflow.search_traces(
    run_id=RUN_PROCEDURE,
    filter_string="tags.question_type = 'irrelevant_question'",
    return_type="list")
print(f"Found {len(found)} traces with the tag (you tagged {tagged}).")

# COMMAND ----------

# MAGIC %md
# MAGIC **✏️ Your answer**
# MAGIC
# MAGIC 1. Open the Traces tab and filter by this tag. What do the tagged traces have in common?
# MAGIC    > TODO
# MAGIC 2. Was every failure really *verbosity*? If a trace failed for a different reason, what tag would you give it?
# MAGIC    > TODO
# MAGIC 3. If you now wanted to fix the agent, what single change would you try first (prompt, tool output, or something else), and which metric would you watch to confirm it worked?
# MAGIC    > TODO
# MAGIC
# MAGIC ---
# MAGIC ### What to hand in
# MAGIC This notebook with all `TODO`s filled, **run top to bottom**, and the `✏️ Your answer` cells completed.