<h1>Demos for Session 3</h1>

---

**Contents**:

- [Demo plan](#demo-plan)
- [The agent](#the-agent)
  - [Demos](#demos)

---

# Demo plan
**See**: ["Session 3", `docs/demo-plan/demo-plan-v5.md`](/docs/demo-plan/demo-plan-v5.md#session-3)

**Demo plan** (Python wiki agent):

> **Approach**: One small agent, one new concept per demo. Each demo ends with a "break it" moment that motivates the next. Notebook flow: concept -> code -> what to look at in the UI -> break it.

# The agent
For D5:

- **Task**: <br> Answer beginner Python questions from a wiki of about 10 short pages
- **Tool**: <br> `search_wiki(query)`
  - Giving `RETRIEVER` and `TOOL` spans
  - Without being overwhelming
- **LLM**: <br> A Databricks-hosted foundation model via a serving endpoint
- **Shared eval questions** (about 10, reused in every demo):
  - Covered by the wiki
  - Not covered by the wiki (triggers an ungrounded answer)
  - Out of scope (e.g. Java generics)

For D6:

- **Tasks**:
  - Answer beginner Python questions from a wiki of about 10 short pages
  - Provide Python exercises from a dataset of concept-related exercises
- **Tools**:
  - `search_wiki(query)`
  - `get_exercise(query)`
- **LLM**: <br> A Databricks-hosted foundation model via a serving endpoint
- **Shared eval questions** (about 10, reused in every demo):
  - Covered by the wiki
  - Not covered by the wiki (triggers an ungrounded answer)
  - Covered by exercises
  - Not covered by exercises
  - Out of scope (e.g. Java generics)
  - Adversarial ("ignore your instructions...")

> **WHY**: Reusing the same agent and questions lets learners compare results across demos.

## Demos

| Code | Demo | What it shows | "Break it" moment |
| --- | --- | --- | --- |
| D5 | Governance intro | UC (catalog/schema, register the agent as a UC model, grant/revoke, lineage), then Unity Gateway (guardrails, rate limit, usage tracking, `use_ai_gateway=True`) | Trip the rate limit; a guardrail blocks the adversarial prompt |
| D6 | Tool integration intro | Tool creation + use without UC, tools as UC functions + governance | Vague tool description |