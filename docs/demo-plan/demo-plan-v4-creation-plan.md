<h1>Plan for Creating the Beginner Demo Plan</h1>

> AI-generated based on human prompt about approach.

> Creating [`demo-plan-v4.md`](./demo-plan-v4.md)

> **Context**:
> 
> - Source: Demo Plan V3 (V3) ([`demo-plan-v3.md`](./demo-plan-v3.md))
> - Audience: Beginners with basic Databricks + Python knowledge

---

**Contents**:

- [Approach](#approach)
- [Why this approach works for beginners](#why-this-approach-works-for-beginners)
- [Locked constraints](#locked-constraints)
- [Steps](#steps)
  - [1. Write learning outcomes per session](#1-write-learning-outcomes-per-session)
  - [2. Triage V3 into a table](#2-triage-v3-into-a-table)
  - [3. Fix the spiral and the promise ledger](#3-fix-the-spiral-and-the-promise-ledger)
  - [4. Build per-session time budgets and sum them](#4-build-per-session-time-budgets-and-sum-them)
  - [5. Draft each block from one template](#5-draft-each-block-from-one-template)
  - [6. Design the lab tasks and the cross-session devices](#6-design-the-lab-tasks-and-the-cross-session-devices)
  - [7. Write per-session pre-staging checklists](#7-write-per-session-pre-staging-checklists)
  - [8. Verify and check coverage](#8-verify-and-check-coverage)
  - [9. Write the document in stages](#9-write-the-document-in-stages)
- [First review point](#first-review-point)
- [Open question](#open-question)

---

# Approach
The course runs as four sessions over two weekends (Saturday and Sunday each, one session per day, a week between the pairs, same group throughout). The structure is a spiral: preview the destination, deep-dive the foundations, then return to the destination and build it properly.

**Sessions 1-2: Overview, then deep dive**:

Session 1 opens with a recorded overview of a finished system. It touches on agent deployment and governance and relates them to MCP, the agent framework and MLflow. This motivates the second half of the material rather than teaching it. The rest of Sessions 1-2 deep-dives the framework topics (tracing, MCP, evaluation, versions and aliases). Each topic is taught as theory first, then demo, with hands-on labs. ***All of this runs locally.***

**Sessions 3-4: Deployment and governance**:

These build on the previous weekend and get into agent deployment and governance on a live Databricks workspace. Concepts are built iteratively through increasingly complex demos. Each rung of the ladder adds exactly one new idea to the app from the rung before.

**Sessions at a glance**:

| Session | Focus | Where |
| --- | --- | --- |
| 1 | Recorded overview, then tracing, then MCP architecture (tools, resources, prompts) | Local |
| 2 | Recap, then evaluation, then versions and aliases, then a "put it together" run | Local |
| 3 | Deploy and govern: Apps, Unity Gateway, UC trace tables, skyjet deployed | Databricks |
| 4 | MCP server types, governance test, evaluation-driven loop, lifecycle view | Databricks |

**Overview pauses and where each is answered**:

| Pause in the recorded run | Question raised | Answered in |
| --- | --- | --- |
| The agent calls a tool | What exactly did it do, and in what order? | Session 1: tracing |
| It gives a wrong answer | How do we know it is good, and how do we catch this? | Session 2: evaluation |
| A new prompt makes things worse | Which version is running, and can we go back? | Session 2: versioning |
| It calls a tool through a server | How do tools get plugged in? | Session 1: MCP |
| Two users get different results | Who is allowed to call what? | Sessions 3-4: governance |
| It runs as a deployed app | Where does it live, and how does it get there? | Sessions 3-4: deployment |

**Sessions 3-4 ladder**:

| Rung | Adds | Session |
| --- | --- | --- |
| 1 | Deploy the simple paragraph-analysis app on Databricks Apps (no MLflow, no MCP) | 3 |
| 2 | Route it through Unity Gateway: rate limit, usage, payload log (Run A vs Run B) | 3 |
| 3 | Bridge: same MLflow instrumentation, now with traces in UC; short legacy contrast (Model Serving) | 3 |
| 4 | Deploy skyjet: multi-agent, traced, behind the gateway (capstone Act 0) | 3 end / 4 start |
| 5 | MCP server types: custom, external, then managed | 4 |
| 6 | Governance: the two-user test on managed MCP | 4 |
| 7 | The loop: evaluation, fix, new version, compare, backfill, alias rollback | 4 |

# Why this approach works for beginners

- **Motivation before mechanics.** Beginners meet tracing, evaluation and versioning as answers to questions they have already seen raised, not as a list of tools. A concept with a reason attached is retained better than one without.
- **Preview, deep dive, return.** Seeing the destination first gives the foundations a purpose. Returning to it in Sessions 3-4 lets participants recognise concepts they were promised, which reinforces both halves.
- **Local before platform.** Sessions 1-2 show MLflow and MCP with nothing else in the way. In Session 3, participants can tell what is MLflow and what is Databricks, because they have already seen the instrumentation work on its own.
- **Theory then demo, at topic level.** Each topic gets a short theory block followed straight away by its demo. One long theory block followed by one long demo block would lose people, so the alternation is kept small.
- **Labs where they are cheap.** Local work needs no workspace, so hands-on practice is realistic in Sessions 1-2. Doing something themselves is what makes the ideas stick.
- **A ladder of single ideas.** In Sessions 3-4 each rung adds one new concept to a working app, so complexity builds in steps a beginner can follow. A failure on any rung can be traced to the one thing that changed.
- **A recorded overview.** It is safe because the opening session does not depend on Databricks or an LLM key working, and it can be paused at exactly the right moments.
- **The weekend and weekly rhythm.** Back-to-back days keep Sessions 1-2 fresh in memory, and the week's gap before Session 3 is time to pre-stage the live workspace. The same group means each session can build on the last.

# Locked constraints

- Overview is recorded
- Same group for all 4 sessions
- 2 weekend sessions (one per day), 1 week between the pairs
- Hands-on labs in Sessions 1-2
- Live workspace for Sessions 3-4
  > With the Gateway and UC prerequisites in place.
- Theory and demo roughly 50%-50%
- 2-3 hours per session

# Steps
## 1. Write learning outcomes per session
Session 1 gets 2 tiers:

- "recognise" for the overview
- "explain" for the deep dive.

Each outcome is phrased as "participants can...".

> **Why**: Outcomes make every later cut defensible, and the recognise/explain split keeps the overview from being held to deep-dive standards.

## 2. Triage V3 into a table
Tag each concept as:

- Overview-only
- Deep dive
- Ladder rung (with the rung number), plus a one-line reason

> **Why**: This is where a 10-hour plan becomes 4 sessions. It also gives you something to review and push back on before any detail is written.

## 3. Fix the spiral and the promise ledger
- Map the 6 overview pauses to the sessions that answer them
- List:
  - Every promise made in the overview
    > UC, OBO, Gateway, rollback.
  - The session that pays it off

> **Why**: The spiral only works if every raised question gets answered. The ledger makes unpaid promises visible.

## 4. Build per-session time budgets and sum them
- Each budget has a theory/demo/lab split, breaks and buffer
- Column totals are computed, not eyeballed

## 5. Draft each block from one template
Fields:

- Question it answers
- Objective
- Theory beats
- Demo or lab steps
- Check-for-understanding
- Cached fallback
- Carry-over from the last session
- Set-up for the next

> **Why**: A single template keeps blocks comparable and makes the fallback and carry-over mandatory, which matters for Gemini rate limits and the weekly gap.

## 6. Design the lab tasks and the cross-session devices
- **Labs**:
  - Session 1 adds `@mlflow.trace` and finds your span
  - Session 2 writes and breaks a guideline
- **Devices**:
  - A parking lot of questions
    > Revisited at the start of Session 3.
  - A 10-minute recap at each session start
  - The bridge slide
    > "same instrumentation, what changes in Databricks"
  - A glossary + each acronym intro'd only when a demo needs it
  - Optional homework between the pairs

> **Why**: For beginners, the labs and devices carry more of the learning than any single demo, so they are designed on purpose.

## 7. Write per-session pre-staging checklists
- Cover:
  - Seeded failures
  - Grants
  - 2 test users
  - Pre-registered scorers
  - The deployed apps
- Add a recorded backup for each Databricks demo
  > Plus a rehearsal schedule.

> **Why**: The main risk is setup, not content. Sessions 3-4 on a live workspace depend on many prerequisites, and the checklist also tells you what to prepare during the week's gap.

## 8. Verify and check coverage
- Re-check only the V3 items still in scope:
  - Gateway availability
  - OBO status
  - Payload-log table name
  - Alias API names
- Confirm every outcome is covered by at least one block.
- Run a timed dry run per block.

> **Why**: Most of V3's verification log covers features that are cut, so re-checking all of it would waste effort. The coverage check gives the same guarantee as V3's coverage map.

## 9. Write the document in stages
Format: Markdown in V3's style. Order:

1. Outcomes and triage (for your review)
2. Time budgets
3. Blocks
4. Checklists, handout map and change log

> **Why**: Staging lets you fix the structure before effort goes into detail.

# First review point
Send the...

- **per-session outcomes**
- **the triage table and the time budgets** (Steps 1-4)

... for review before the blocks are drafted.

# Open question
"Does "agent framework" in Sessions 1-2 include a short "what is an agent and tool calling" opener, or can that be assumed? The default is a 20-minute opener in Session 1."

> Response: Yes, assume no knowledge, include the above opener.