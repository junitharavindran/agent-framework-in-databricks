<h1>Demos for Session 2</h1>

---

**Contents**:

- [Demo plan](#demo-plan)
- [The agent](#the-agent)
  - [Demos](#demos)

---

# Demo plan
**See**: ["Session 2", `docs/demo-plan/demo-plan-v5.md`](/docs/demo-plan/demo-plan-v5.md#session-2)

**Demo plan** (Python wiki agent):

> **Approach**: One small agent, one new concept per demo. Each demo ends with a "break it" moment that motivates the next. Notebook flow: concept -> code -> what to look at in the UI -> break it.


# The agent

- **Task**: <br> Answer beginner Python questions from a wiki of about 10 short pages
- **Tool**: <br> `search_wiki(query)`
  - Giving `RETRIEVER` and `TOOL` spans
  - Without being overwhelming
- **LLM**: <br> A Databricks-hosted foundation model via a serving endpoint
- **Shared eval questions** (about 10, reused in every demo):
  - Covered by the wiki
  - Not covered by the wiki (triggers an ungrounded answer)
  - Out of scope (e.g. Java generics)
  - Adversarial ("ignore your instructions...")

> **WHY**: Reusing the same agent and questions lets learners compare results across demos.

## Demos

| Code | Demo | What it shows | "Break it" moment |
| --- | --- | --- | --- |
| D0 | Baseline agent | Plain agent, no tracing | You cannot tell *why* an answer came out as it did |
| D1 | Tracing | `@mlflow.trace`, auto spans from the LLM client, a manual span, reading the span tree | The retriever returned no pages, so the answer is ungrounded |
| D2 | First evaluation | Eval dataset, `predict_fn`, `mlflow.genai.evaluate()`, built-in judges (`Correctness`, `Safety`, `RetrievalGroundedness`), `Feedback` rationales | Built-ins cannot check that answers include a runnable code example |
| D3 | Custom scorers | Guideline judge, deterministic `@scorer`, `make_judge()` in one `evaluate()` call | Do the judges agree with a human? |
| D4 | Judge iteration | Human feedback on traces, trace tags for failure modes, judge alignment | Why judges need validation |

> **NOTE**: D1 comes before D2 (the reverse of the key-ideas order above), because learners need to see a trace before an evaluation makes sense.