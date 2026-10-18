<h1>Demos for Session 2</h1>

---

**Contents**:

- [Demo plan](#demo-plan)
- [The agent](#the-agent)
  - [Demos](#demos)
  - [Practical notes](#practical-notes)

---

# Demo plan
**See**: ["Session 2", `docs/demo-plan/demo-plan-v5.md`](/docs/demo-plan/demo-plan-v5.md#session2)

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
| D5 | Governance intro | UC (catalog/schema, register the agent as a UC model, grant/revoke, lineage), then Unity Gateway (guardrails, rate limit, usage tracking, `use_ai_gateway=True`) | Trip the rate limit; a guardrail blocks the adversarial prompt |
| D6 | Production | Traces in UC Delta tables, production monitoring (`register()` then `start()`), backfill, archival, inference tables, production failures feed back into the eval dataset | A production failure becomes a new eval row |

> **NOTE**: D1 comes before D2 (the reverse of the key-ideas order above), because learners need to see a trace before an evaluation makes sense.

## Practical notes

- **Deployment**: develop in notebooks; deploy to Model Serving for D5-D6 (automatic tracing, clearest path through Unity Gateway)
- **UC trace location**: if D6 stores traces in UC, create the experiment with the trace location **at creation**. Binding cannot be added or changed later.
- **Availability checks** before D5-D6:
  - Production monitoring, backfill and archival are Beta
  - UC trace storage needs MLflow >= 3.14, a SQL warehouse with `CAN USE`, a supported region, and an existing catalog and schema
- **Gateway caveat**: legacy AI Gateway does not support rate limiting or guardrails on Databricks *agents* endpoints. Run the gateway demo against the model endpoint the agent calls, not the agent endpoint.
