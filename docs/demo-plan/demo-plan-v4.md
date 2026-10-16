<h1>Demo Plan V4</h1>

> Mostly AI-generated with human feedback + edits.

> **Status**: Draft for review. Covers Steps 1-9 of [`demo-plan-v4-creation-plan.md`](./demo-plan-v4-creation-plan.md): outcomes, triage, promise ledger, time budgets, blocks, labs, assignments, devices, pre-staging checklists, verification, the handout map and the change log. Not yet done: the starter files for the labs, a live Gemini call, and the timed dry runs.

> **Context**:
>
> - Source: Demo Plan V3 ([`demo-plan-v3.md`](./demo-plan-v3.md))
> - Audience: beginners with basic Databricks + Python knowledge
>   > Assumed to know nothing about agents.
> - Format:
>   - 4 sessions of about 3 hours
>   - Over 2 weekends (Sat + Sun each)
>   - Same cohort

---

**Contents**:

- [1. Learning outcomes](#1-learning-outcomes)
- [2. Triage of V3](#2-triage-of-v3)
- [3. Spiral and promise ledger](#3-spiral-and-promise-ledger)
- [4. Time budgets](#4-time-budgets)
- [Resolved decisions](#resolved-decisions)
- [5. Blocks](#5-blocks)
- [6. Labs, assignments and cross-session devices](#6-labs-assignments-and-cross-session-devices)
- [7. Pre-staging checklists](#7-pre-staging-checklists)
- [8. Verification and coverage](#8-verification-and-coverage)
- [9. Handout map](#9-handout-map)
- [Change log (V3 to V4)](#change-log-v3-to-v4)
- [Open items for review](#open-items-for-review)

---

# 1. Learning outcomes

Each outcome reads "Participants can...".

## Session 1: Overview, agents, tracing, MCP

**Recognise** (recorded overview):

- R1. Say in one sentence what tracing, evaluation, versioning, governance and deployment are each for.
- R2. Point to where a tool call, a wrong answer, a version change and a permission difference show up in a running agent.

**Explain** (deep dive):

- E1. Explain what an agent is and how tool calling works, and read a tiny agent loop.
- E2. Explain trace vs span, the span types, and automatic vs custom spans. *(Lab: add `@mlflow.trace` to a function and find your span.)*
- E3. Describe host, client and server, the three MCP primitives (tools, resources, prompts), and the two transports (STDIO, Streamable HTTP).

## Session 2: Evaluation and versions

- E4. Name the kinds of scorer (built-in judge, guideline judge, deterministic custom scorer, custom LLM judge) and choose between them.
- E5. Use a trace-based scorer, and explain why LLM judges need calibration against human labels. *(Lab: write a guideline, then break it and watch the score.)*
- E6. Define a "version" (prompt versions plus the app snapshot that used them), compare two versions, and explain how flipping an alias rolls back with no serving-code change.
- E7. Trace, evaluate and version a small local agent that has an MCP tool. *(Lab.)*

## Session 3: Deploy and observe on Databricks

- E8. Explain why Databricks Apps is the current pattern for agents and why Model Serving agents are legacy.
- E9. Explain what Unity Gateway governs, and show rate limiting, usage tracking and payload logging, stating the endpoint type each time.
- E10. Explain what Unity Catalog (UC) is and what it governs, and say what changes when the same MLflow instrumentation runs on Databricks.
- E11. Read a trace and the matching gateway usage row for a deployed multi-agent app (skyjet).

## Session 4: Govern and iterate

- E12. Compare custom, external and managed MCP servers on who hosts them, who governs access, setup effort, fitting use-case, and trust exposure.
- E13. Explain on-behalf-of-user (OBO) authorization and why two users get different results from a managed tool.
- E14. Walk the evaluation-driven loop: failing case, fix, new version, re-run, compare, promote or roll back.

> **Why outcomes first**: Every cut in Step 2 is defended by an outcome it serves. A topic with no outcome is a candidate for the handout.

# 2. Triage of V3

Tags:

- **Overview** (seen only in the recording)
- **Deep dive**, **Rung n** (Sessions 3-4 ladder)
- **Name only** (one slide or table row)
- **Handout**

| V3 concept | Tag | Session | Reason |
| --- | --- | --- | --- |
| Agent basics and tool-calling loop | Deep dive | 1 | Not in V3. Needed because no prior knowledge is assumed |
| Skyjet system running end to end | Overview | 1 | Recorded; raises the six questions (see ["Overview pauses" in this document](#overview-pauses)) |
| MLflow tracing: spans, span types, autolog vs custom, error span | Deep dive | 1 | Answers "what did the agent do?" |
| MCP architecture, tools/resources/prompts, STDIO vs HTTP | Deep dive | 1 | Gives the agent tools to trace and evaluate |
| MCP stateless data layer, `server/discover` | Name only | 1 | SDK-version risk in dry runs; low beginner value |
| MCP sampling, roots, logging, legacy SSE | Not shown | | V3 already excludes these |
| MLflow evaluation: scorer kinds, trace-based scorer, global vs row-wise guidelines | Deep dive | 2 | Answers "is it good?" |
| Judge calibration | Deep dive | 2 | Teaches why a judge's score is not ground truth |
| Multi-turn judges | Handout | | Experimental; needs session IDs and extra setup |
| Versions, aliases, promote and roll back, debug via version record | Deep dive | 2 | Answers "which version is running?" |
| Apps-based deploy (Agent Bricks CLI) | Rung 1 | 3 | Current Databricks pattern |
| Other deploy routes (DAB, Git, direct upload) | Name only | 3 | One slide with the options |
| Unity Gateway on/off, rate limit, usage, payload log | Rung 2 | 3 | Simplest governance win; Run A vs Run B contrast |
| Gateway guardrails, traffic splitting, fallbacks | Name only | 3 | Support varies by endpoint type |
| Same MLflow instrumentation on Databricks (bridge) | Rung 3 | 3 | Connects Sessions 1-2 to Session 3 |
| UC primer | Rung 3 | 3 | Needed before trace tables and grants |
| Model Serving agent pattern (legacy) | Rung 3 | 3 | Short contrast only |
| Skyjet deployed behind the gateway (capstone Act 0) | Rung 4 | 3 | Realistic app for Session 4 |
| Custom MCP server (Databricks App) | Rung 5 | 4 | Short demo |
| External MCP server (UC connection, MCP Service) | Rung 5 | 4 | Short demo; Beta or preview requirements |
| Managed MCP (UC function) | Rung 5 | 4 | Deepest demo; carries the governance lesson |
| Two-user governance test (OBO) | Rung 6 | 4 | Most memorable moment of the course |
| Production monitoring, evaluation loop, backfill | Rung 7 | 4 | The iterative loop |
| Lifecycle view, alias rollback on Databricks | Rung 7 | 4 | Closes the "can we go back?" promise |
| Interpretability table | Name only | 4 | Recap in the final wrap |
| Context hygiene (concept) | Name only | 4 | Discussion in the wrap, with pre-computed numbers if available |
| Context hygiene (20+ question experiment) | Handout | | Large setup; result may fall either way |
| Flexibility and scalability items | Name only | 4 | Discussion only: trace limits, cost, runtime scaling |
| Dev-to-prod promotion with DAB targets | Handout | | Out of scope for beginners |

> **Why triage as a table**: It turns the 10-hour V3 into four sessions, and each tag is a reviewable decision. Disagree with a row and only that row changes.

# 3. Spiral and promise ledger
## Overview pauses
The six questions the Skyjet app recording raises:

| Pause in the recorded run | Question raised | Answered in |
| --- | --- | --- |
| The agent calls a tool | What exactly did it do, and in what order? | Session 1: tracing |
| It gives a wrong answer | How do we know it is good, and how do we catch this? | Session 2: evaluation |
| A new prompt makes things worse | Which version is running, and can we go back? | Session 2: versioning |
| It calls a tool through a server | How do tools get plugged in? | Session 1: MCP |
| Two users get different results | Who is allowed to call what? | Sessions 3-4: governance |
| It runs as a deployed app | Where does it live, and how does it get there? | Sessions 3-4: deployment |

## Promise ledger
Anything said in the overview but not taught there is a debt.

> Each is checked off in the session shown.

| Promise (made in the overview) | Paid off in | Rung or block |
| --- | --- | --- |
| "Unity Gateway sits in front of every LLM call" | Session 3 | Rung 2 |
| "UC controls access to data and functions" | Session 3 (primer), Session 4 (grants in action) | Rung 3, Rung 6 |
| "The app acts on behalf of the user" (OBO) | Session 4 | Rung 6 |
| "You can roll back to the previous version" | Session 2 (local), Session 4 (Databricks) | Versions block, Rung 7 |
| "The app is deployed on Databricks" | Session 3 | Rung 1, Rung 4 |
| "Tools plug in through MCP servers" | Session 1 (concept), Session 4 (server types) | MCP block, Rung 5 |

> **NOTE**: A parking lot of unanswered questions is kept on screen in Sessions 1-2 and revisited at the start of Session 3.

> **Why a ledger**: The spiral only works if every raised question gets answered. The ledger makes unpaid promises visible, so nothing is left dangling.

# 4. Time budgets
- Each session
  - 160 minutes of content
  - 10 minutes break
  - 10 minutes buffer
  - 180 minutes in total
- Columns are summed
- Demo means presenter-led
- Lab means participants do it themselves

## Session 1

| Block | Min | Theory | Demo | Lab |
| --- | --- | --- | --- | --- |
| Course map and expectations | 10 | 10 | 0 | 0 |
| Recorded overview (6 pauses) | 40 | 10 | 30 | 0 |
| Opener: agents and tool calling | 20 | 12 | 8 | 0 |
| Tracing (lab: `@mlflow.trace`) | 45 | 20 | 10 | 15 |
| *Break* | *10* | | | |
| MCP architecture | 45 | 28 | 17 | 0 |
| **Content total** | **160** | **80** | **65** | **15** |
| *Buffer* | *10* | | | |

> **Drop first if short**:
> 
> The STDIO vs Streamable HTTP contrast demo.

## Session 2

| Block | Min | Theory | Demo | Lab |
| --- | --- | --- | --- | --- |
| Recap and parking lot | 10 | 10 | 0 | 0 |
| Evaluation (lab: write and break a guideline) | 70 | 35 | 20 | 15 |
| *Break* | *10* | | | |
| Versions and aliases | 40 | 25 | 15 | 0 |
| Put it together: local agent with an MCP tool, traced, evaluated, versioned | 30 | 0 | 15 | 15 |
| Look ahead to Session 3 | 10 | 10 | 0 | 0 |
| **Content total** | **160** | **80** | **50** | **30** |
| *Buffer* | *10* | | | |

> **Drop first if short**:
> 
> The judge calibration demo (keep the theory).

## Session 3

| Block | Min | Theory | Demo | Lab |
| --- | --- | --- | --- | --- |
| Recap, bridge slide ("same instrumentation, what changes"), parking lot | 15 | 15 | 0 | 0 |
| Rung 1: deploy the paragraph-analysis app on Databricks Apps | 30 | 15 | 15 | 0 |
| Rung 2: Unity Gateway, Run A vs Run B (rate limit, usage, payload log) | 45 | 15 | 30 | 0 |
| *Break* | *10* | | | |
| Rung 3: MLflow on Databricks, UC primer, legacy Model Serving contrast | 40 | 20 | 20 | 0 |
| Rung 4: deploy skyjet behind the gateway | 20 | 5 | 15 | 0 |
| Wrap, ledger check, homework | 10 | 10 | 0 | 0 |
| **Content total** | **160** | **80** | **80** | **0** |
| *Buffer* | *10* | | | |

> **Drop first if short**:
> 
> The legacy Model Serving demo (keep the slide).

## Session 4

| Block | Min | Theory | Demo | Lab |
| --- | --- | --- | --- | --- |
| Recap; register the production scorer | 15 | 5 | 10 | 0 |
| Rung 5a: custom MCP | 12 | 4 | 8 | 0 |
| Rung 5b: external MCP | 12 | 4 | 8 | 0 |
| Rung 5c: managed MCP | 30 | 10 | 20 | 0 |
| Rung 5 wrap: comparison table | 6 | 6 | 0 | 0 |
| *Break* | *10* | | | |
| Rung 6: two-user governance test (OBO) | 25 | 7 | 18 | 0 |
| Rung 7: the loop (evaluate, fix, new version, compare, backfill, roll back) | 45 | 15 | 30 | 0 |
| Wrap: interpretability recap, context hygiene and scalability discussion, handout | 15 | 15 | 0 | 0 |
| **Content total** | **160** | **66** | **94** | **0** |
| *Buffer* | *10* | | | |

> **Why the scorer is registered first**: Production monitoring takes 15-20 minutes to produce results, so it arrives during the MCP blocks and is ready for Rung 7.
>
> **Drop first if short**:
> 
> The custom and external demos (keep their comparison-table rows).

## Course totals

| Session | Theory | Demo + Lab | Content min |
| --- | --- | --- | --- |
| 1 | 80 | 80 | 160 |
| 2 | 80 | 80 | 160 |
| 3 | 80 | 80 | 160 |
| 4 | 66 | 94 | 160 |
| **Total** | **306** | **334** | **640** |

- That is about 48% theory and 52% demo and lab
- Session 4 runs demo-heavy by design
  > Because it is a build-up of live demos.

> **Why sum the columns**: An earlier draft of a 3-hour plan claimed 50-50 but was not. Totalling every column catches this before it ends up in the document.

# Resolved decisions

| Question | Decision |
| --- | --- |
| Session 4 theory share (41%) | Accepted. Part of that theory is already covered in Sessions 1-2 |
| Tracing at 45 minutes including the lab | Accepted as enough |
| Context hygiene | Discussion only (Session 4 wrap) |
| Labs in Sessions 3-4 | None live. Presenter demos, plus assignments done outside the session |
| Drop-first list | Accepted as written |
| Participant setup | Own machines, own Gemini key. Setup guide ([`participant-setup-guide.md`](./participant-setup-guide.md)) and smoke test ([`smoke_test.py`](./smoke_test.py)) drafted. Sent at least 2 days before Session 1 |
| Overview recording | Recorded the day before, or run live. Recommended: record it the day before even if you go live, so a fallback exists |
| Assignments | Submitted by email or a shared folder. A2 and A3 handouts drafted |
| Class size | 8-10 students |

---

# 5. Blocks
Template:

- Every block uses the same fields
- Light blocks (recaps, wraps) use only the ones that apply

- **Question**: The question it answers
- **Outcomes**: IDs from section 1
- **Theory**: The beats, in order
- **Demo / Lab**: The steps
- **Check**: One question to ask the room before moving on
- **Fallback**: What to use if the live step fails
- **Carry-over**: What the block reuses from earlier
- **Set-up**: What the block leaves ready for the next one

> **Common fallback rules**:
> 
> - Keep cached outputs of every LLM-backed step
>   > Gemini's free tier is rate-limited.
> - For every Databricks demo, keep a screen recording and screenshots
> - Beta or preview features are marked where used

## Session 1: Overview, agents, tracing, MCP (local)
### 1.1 Course map and expectations
> 10 min.

- **Question**: What are we doing, and why in this order?
- **Theory**:
  - The 4 sessions and where each runs
  - The spiral: preview, foundations, build
  - How labs and the parking lot work
- **Check**: "Which session will tell us who may call which tool?" (Sessions 3-4)
- **Set-up**:
  - Parking lot visible on screen
  - Recording ready to play

### 1.2 Recorded overview
> 40 min: 10 theory, 30 demo.

- **Question**:
  - What does a finished agentic system look like?
  - What will we learn to build and control?
- **Outcomes**: R1, R2
- **Theory** (10):
  - About 5 minutes framing the skyjet app (a policy agent and a flight agent)
  - About 1 minute at each pause:
    - State the question
    - Add it to the parking lot
    - Make a one-sentence promise
      > E.g.: "UC controls access to data and functions, more in Session 3."
- **Demo** (30):
  - The recording or a live run, paused at the 6 points in section 3
    > The recording is made the day before. Make it even if you plan to go live: it doubles as the rehearsal and the fallback.
  - Databricks parts get one sentence each
- **Check**: Ask 2 participants to restate a parking-lot question in their own words
- **Fallback**:
  - The recording from the day before
  - Keep a transcript and screenshots in case playback fails
- **Set-up**: Parking lot filled with the 6 questions

### 1.3 Opener: agents and tool calling
> 20 min: 12 theory, 8 demo.

- **Question**: What is an agent, really?
- **Outcomes**: E1
- **Theory** (12):
  - A single LLM call vs an agent that loops
  - The loop:
    - The model decides to call a tool
    - The app runs it
    - The result goes back
    - The model decides again
  - A tool is a function plus a description and a schema; the model never runs it
  - Why this loop is what we trace, evaluate, version and govern
- **Demo** (8):
  - A roughly 30-line agent loop with one tool, calling Gemini
  - Print the message list at each step
- **Check**: "In the loop, who actually runs the tool?"
- **Fallback**: Cached message transcript
- **Carry-over**: The paragraph-analysis use-case from V3, kept as the running local example
- **Set-up**: This agent is traced in 1.4

### 1.4 Tracing
> 45 min: 20 theory, 10 demo, 15 lab.

- **Question**: What did the agent do, and in what order?
- **Outcomes**: E2
- **Theory** (20):
  - What a trace is
  - A span as one unit of work, with inputs, outputs and timing
  - The parent-child span tree
  - Span types: LLM, TOOL, RETRIEVER, CHAIN
  - Automatic (autologged) vs custom spans
  - Error spans
  - Where traces live locally, and the MLflow UI
- **Demo** (10), 3 mini-demos of about 3 minutes each:
  1. A recursive factorial, to show the span tree
  2. One LLM call, autologged
  3. A small typed-span pipeline (retriever, tool, LLM) where the tool raises, so the error span shows in the tree
- **Lab** (15): See L1 in section 6
- **Check**: "Where in the span tree would you look to find which tool failed?"
- **Fallback**:
  - Screenshots of the UI
  - Cached LLM output
- **Carry-over**: The opener's agent loop now gets traced
- **Set-up**: Participants have traces in their local MLflow store

> **Moved to handout**:
> 
> The selection vs bubble sort demo. It adds no concept beyond factorial.

*Break (10 min)*

### 1.5 MCP architecture
> 45 min: 28 theory, 17 demo.

- **Question**: How do tools get plugged in?
- **Outcomes**: E3
- **Theory** (28):
  - The problem: every agent wiring every tool its own way
  - Host, client and server
    - One host with many clients
    - A dedicated client-server connection each
  - The 3 primitives:
    - Tools (the model decides to call them)
    - Resources (data fetched by URI)
    - Prompts (reusable templates)
  - Transports: STDIO and Streamable HTTP
  - One slide, name only: in the current spec the data layer is stateless (no handshake; `server/discover`)
- **Demo** (17), paragraph analysis with 2 small servers:
  - Server A over STDIO: tools for word count and spell-check
  - Server B over Streamable HTTP:
    - A `search_documents` tool
    - A resource opened by URI (`doc://<id>`)
    - An "analyse this paragraph" prompt
  - Log each client's connection to show the dedicated pairing
  - *Drop first*: The STDIO vs Streamable HTTP contrast
- **Check**:
  - "Which primitive fits a read-only document?"
  - "Which fits an action the model decides to take?"
- **Fallback**:
  - Cached outputs
  - A recording of both servers running
- **Carry-over**: The opener's tool now arrives through MCP
- **Set-up**: Session 2 starts from a traced agent that calls an MCP tool

> **Build-time check**: Pin `mcp==2.3.0` (verified 14 Oct 2026) and dry-run. In SDK v2 the server class is `MCPServer` (`from mcp.server.mcpserver import MCPServer`), not `FastMCP`, and `from mcp import Client` can connect to a server in-process. v2 serves both spec eras.
>
> **Moved to handout**:
> 
> - The sentiment and keyword tools that use a server-side LLM
> - They blur who is calling the LLM (a distraction for beginners)

## Session 2: Evaluation and versions (local)
### 2.1 Recap and parking lot
> 10 min.

- **Theory**:
  - 3-sentence recap: the agent loop, traces, MCP
  - Walk the parking lot, marking:
    - Which questions are answered
    - Which questions are pending
- **Check**: Ask 1 participant to explain what a span is

### 2.2 Evaluation
> 70 min: 35 theory, 20 demo, 15 lab.

- **Question**: Is it any good?
- **Outcomes**: E4, E5
- **Theory** (35):
  - Why eyeballing outputs does not scale: dataset, scorer, results
  - Scorer kinds:
    - Built-in judge
    - Guideline judge
    - Deterministic custom scorer
    - Custom LLM judge
  - Global vs row-wise guidelines
  - A judge is an LLM, so it can be wrong
    > Calibration against human labels.
  - Trace-based scorers
    > E.g.: Which tools were called.
  - The older `mlflow.metrics` API is legacy
    > Say it once and move on.
- **Demo** (20), on a small dataset for the paragraph-analysis app:
  1. A deterministic scorer on its own
  2. A guideline judge on its own, showing the rationale
  3. A trace-based scorer on the traces from Session 1
  4. All of them together in one run, viewed in the UI
  5. *Drop first*:
     1. One human label that disagrees with a judge
     2. A revised guideline
- **Lab** (15): See L2 in section 6
- **Check**:
  - "A judge gives 5/5 and a human says the answer is wrong => <br> Which do you trust, and what do you change?"
- **Fallback**: Cached judge outputs for the full dataset
- **Carry-over**: Session 1 traces and the traced agent
- **Set-up**:
  - An evaluation dataset
  - A seeded failing input for the versions block

> **Build-time check**: Use built-in judges that run on open-source MLflow, and set the judge model to Gemini explicitly.

*Break (10 min)*

### 2.3 Versions and aliases
> 40 min: 25 theory, 15 demo.

- **Question**: Which version is running, and can we go back?
- **Outcomes**: E6
- **Theory** (25):
  - What lifecycle management is, beyond experiment and run IDs:
    - Versioning what was deployed
    - Comparing versions
    - Promoting and rolling back
    - Tying a failure to a version
  - A "version" is the pair of prompt versions and the app snapshot that used them; "deploy" means serving a version
  - The uses:
    - Reusing an older high-performing version
    - Debugging a failure that belongs to one version
  - An alias is a movable label
    > Flipping it changes what runs without touching serving code.
- **Demo** (15), 2 versions with different guideline prompts and the same task prompts:
  1. Compare them in the UI and programmatically
  2. Send the seeded input that fails on one version only... <br> ... *and find it through that version's record*
  3. Point `production` at the better version, then:
     1. Flip to the other and back
     2. Show the serving code did not change
- **Check**: "The alias was flipped => <br> What changed, and what did not?"
- **Fallback**:
  - Both versions pre-registered
  - Cached outputs
- **Carry-over**: The evaluation results from 2.2, now compared per version
- **Set-up**: v1 registered for the lab in 2.4

> **Build-time check**: The prompt-registry and alias calls were verified on MLflow 3.17.1 (14 Oct 2026): `mlflow.genai.register_prompt`, `set_prompt_alias`, and `load_prompt("prompts:/<name>@production")`. Flipping an alias from version 1 to 2 changed what loaded, and loading by version still worked. Re-run on the version you pin.

### 2.4 Put it together
> 30 min: 15 demo, 15 lab.

- **Question**: Do tracing, evaluation and versions work as one loop?
- **Outcomes**: E7
- **Demo** (15), on the local agent with an MCP tool:
  1. Send a request and show the trace with the MCP tool span
  2. Run the evaluation with the trace-based scorer
  3. Register v1
- **Lab** (15): See L3 in section 6
- **Check**: "For a failed request, which do you open first: the trace, the evaluation, or the version?"
- **Fallback**: A starter state with v1 already registered

### 2.5 Look ahead
> 10 min.

- **Theory**:
  - Preview Session 3: Apps, Unity Gateway, UC
  - What to bring
  - The parking-lot questions still open
- **Set-up**: Hand out assignment A1 (section 6)

## Session 3: Deploy and observe (Databricks, live demos)
### 3.1 Recap, bridge slide, parking lot
> 15 min.

- **Question**: What stays the same on Databricks?
- **Theory**:
  - A compressed recap
    > A week has passed.
  - The bridge slide (section 6)
  - Revisit the parking lot and tick off answered questions
  - Frame it as open-source MLflow vs managed MLflow
- **Check**: "Name 2 things that stay the same and 2 that change."
- **Carry-over**: Sessions 1-2

### 3.2 Rung 1: deploy the paragraph-analysis app
> 30 min: 15 theory, 15 demo.

- **Question**: Where does the agent live, and how does it get there?
- **Outcomes**: E8
- **Theory** (15):
  - What Databricks Apps provides:
    - Hosting
    - Identity
    - Scaling
  - App-based vs the Model Serving agent pattern
    > Databricks lists the Model Serving pattern as legacy.
  - Deploy routes:
    - The Agent Bricks CLI (recommended for new agents)
    - DABs
    - Git
    - Direct upload
    > Show one, name the rest.
  - The app has its own identity (a service principal)
  - The MLflow `AgentServer` is legacy
    > Mention it once.
- **Demo** (15):
  1. The paragraph-analysis app, with no MLflow and no MCP
  2. Deploy it from a prepared repo with the Agent Bricks CLI
  3. Show the running app
- **Check**: "What does an app give you that a notebook does not?"
- **Fallback**:
  - Pre-deployed copy of the app
  - Recording
- **Carry-over**: The use-case from the Session 1 MCP demo
- **Set-up**: A gateway endpoint exists for an LLM

### 3.3 Rung 2: Unity Gateway
> 45 min: 15 theory, 30 demo.

- **Question**: Who may use the model, how much, and can we see it?
- **Outcomes**: E9
- **Theory** (15):
  - What the gateway is: a governance layer in front of LLM endpoints
    > Unity Gateway (Beta); an account admin enables it.
  - Features shown:
    - Rate limiting
    - Usage tracking
    - Payload logging (inference tables)
  - Features named only:
    - Guardrails
    - Traffic splitting
    - Fallbacks
  - Support varies by endpoint type
    > State the type before each feature.
- **Demo** (30):
  1. Run A: a direct LLM call, no gateway
  2. Run B: the same call routed through the gateway
     > Pass the gateway endpoint name as the model and set `use_ai_gateway=True`. The parameter keeps the old name... <br> ... *but the product is Unity Gateway*
  3. Rate limit:
     1. Set a very low limit
     2. Send requests through B until one is rejected
  4. Usage:
     1. Show B's call in usage tracking
     2. Show A's is absent
  5. Payload log:
     1. Find B's request and response
     2. Show A has no record
- **Check**: "Run A worked => <br> Why does it appear nowhere in usage tracking?"
- **Fallback**:
  - Screenshots of the usage and payload tables
  - Recording
- **Set-up**: Raise or remove the low rate limit before the next block

> **Build-time check**:
>
> - Usage: `system.ai_gateway.usage` is confirmed in the docs (token counts, latency, requester identity, request tags)
> - Payload log: there is no fixed table name. You choose the catalog, schema and prefix, and the full name is shown in the endpoint config. Read it from there and put it on the slide
> - Run B must go through the endpoint query API. `ai_query` only gets usage tracking, so it would not show the payload log
> - Confirm the gateway is enabled for the account (Beta, Previews page, supported region, UC-enabled workspace). Docs name it "Unity AI Gateway" in places; the plan uses "Unity Gateway"

*Break (10 min)*

### 3.4 Rung 3: MLflow on Databricks, UC primer, legacy contrast
> 40 min: 20 theory, 20 demo.

- **Question**: Where do traces go, and who can see them?
- **Outcomes**: E10
- **Theory** (20):
  - UC primer (10):
    - What UC is
    - Catalog, schema, then tables and functions
    - Permissions through grants
    - What it governs here: data, functions, connections, trace tables
  - Traces in UC (5):
    - An experiment created with a UC trace location
      > It cannot be reassigned later.
    - Explicit grants
    - A SQL warehouse
  - The legacy Model Serving pattern (5):
    - Why it is legacy
    - Where the migration path is documented
- **Demo** (20):
  1. Run the same traced code from Sessions 1-2, now with a UC trace location
  2. Show:
     1. A trace in the Databricks MLflow UI
     2. The trace table
     3. The grants on the trace schema
  3. *Drop first*: A short look at a pre-built Model Serving endpoint for the legacy contrast
     > Keep the slide.
- **Check**: "When we moved here, did the code change or the configuration?"
- **Fallback**:
  - Screenshots
  - Recording

> **Build-time check**:
> 
> - MLflow 3.14 or later
> - `ALL_PRIVILEGES` is not sufficient for trace tables

### 3.5 Rung 4: deploy skyjet
> 20 min: 5 theory, 15 demo.

- **Question**: What does a realistic agent look like?
- **Outcomes**: E11
- **Theory** (5): Skyjet has:
  - A policy agent and a flight agent
  - At least 1 MCP-based tool
  - MLflow tracing
  - Every LLM call routed through the gateway
- **Demo** (15):
  1. Deploy skyjet behind the gateway
  2. Ask one question
  3. Show the trace (span tree, tool span) and the matching gateway usage row
- **Check**: "Find which agent handled the policy question in the trace."
- **Fallback**:
  - Recording
  - Pre-deployed instance
- **Set-up**: Skyjet left running for Session 4

> **Build-time check**:
> 
> - Skyjet's runtime (Agent Bricks CLI or the legacy MLflow `AgentServer`) is stated
> - The V3 acceptance checklist is complete

### 3.6 Wrap, ledger check, homework
> 10 min.

- **Theory**:
  - Tick the ledger: Gateway, deployment, UC primer
  - Name what remains: OBO, server types, the loop
- **Set-up**: Hand out assignment A2

## Session 4: Govern and iterate (Databricks, live demos)
### 4.1 Recap and register the production scorer
> 15 min: 5 theory, 10 demo.

- **Question**: What should already be running while we talk?
- **Theory** (5):
  - A short recap
  - Production monitoring takes 15-20 minutes to produce results... <br> ... *so we start it now*
- **Demo** (10):
  1. From a notebook, register a scorer on skyjet's experiment
     > Only `@scorer` functions work, and they must be registered from a notebook.
  2. Send a few requests to generate traces
- **Check**: "Why register it now rather than at the end?"
- **Fallback**: A scorer registered in advance, with results already present

> **Build-time check**:
> 
> - The experiment has the SQL warehouse tag
> - At most 20 scorers per experiment
> - Production monitoring is Beta

### 4.2 Rung 5a: custom MCP
> 12 min: 4 theory, 8 demo.

- **Question**: How do I add my own tools?
- **Outcomes**: E12
- **Theory** (4):
  - You host it as a Databricks App
  - Access is governed by app permissions
  - Limits:
    - OAuth only
    - No personal access tokens
    - No OBO
- **Demo** (8):
  1. A small MCP server already deployed as an app
  2. The agent connects at `https://<app-url>/mcp`
  3. Show:
     1. The call in a trace
     2. The "Can Use" permission for the agent's service principal
- **Check**: "Who decides whether the agent may call this server?"
- **Fallback**: Screenshots
- **Carry-over**: The same MCP primitives from Session 1, now hosted

### 4.3 Rung 5b: external MCP
> 12 min: 4 theory, 8 demo.

- **Question**: How do I use a third-party server safely?
- **Outcomes**: E12
- **Theory** (4):
  - A third-party server, reached through:
    - A UC HTTP connection
    - Registration as an MCP Service
  - Governed by:
    - An `EXECUTE` grant in UC
    - The gateway
  - The exposure from untrusted tool descriptions and responses (prompt injection)
  - The Beta and preview requirements
- **Demo** (8):
  1. A pre-registered MCP Service
  2. A call passing through the gateway
  3. The `EXECUTE` grant
- **Check**: "Why is this the highest-exposure option?"
- **Fallback**:
  - Screenshots
  - Recording

### 4.4 Rung 5c: managed MCP
> 30 min: 10 theory, 20 demo.

- **Question**: How do I expose my governed functions as tools?
- **Outcomes**: E12
- **Theory** (10):
  - Databricks hosts it on serverless compute
  - A UC function exposed as an MCP tool
    > Per-function URL `/api/2.0/mcp/functions/{catalog}/{schema}/{function_name}`; the schema-level URL lists every function in the schema.
  - Governed by:
    - UC permissions
    - The gateway
  - Other managed servers (AI Search, Genie Agents, Databricks SQL) are named, not demoed
- **Demo** (20):
  1. Create a UC function
  2. Grant `EXECUTE`
  3. Have the agent call it as a managed tool
  4. Show the tool span in a trace
- **Check**: "What must a user have been granted to call this function?"
  > `EXECUTE`, plus the catalog and schema privileges.
- **Fallback**:
  - A pre-created function
  - Recording
- **Set-up**: The function and grants are ready for the governance test

### 4.5 Rung 5 wrap: comparison table
> 6 min theory.

- Participants fill 1 table (custom, external, managed) on:
  - Who hosts it
  - Who governs access
  - Setup effort
  - A fitting use-case
  - Trust and security exposure
- They try one cell before the reference answers are shown
- **Check**: Compare against the answers participants prepared in assignment A2

*Break (10 min)*

### 4.6 Rung 6: two-user governance test
> 25 min: 7 theory, 18 demo.

- **Question**: Who is allowed to call what?
- **Outcomes**: E13
- **Theory** (7):
  - OBO means the app calls a resource with the end user's identity... <br> ... *rather than its own*
  - With only the app's service principal, both users get the same result
  - UC checks the user's grants
  - The app needs OBO enabled with the `unity-catalog` scope
- **Demo** (18):
  1. Call the managed function as a user with access (success)
  2. Call it as a user without access (denial)
  3. Optional: show the same call through the app's service principal
     > Both users get the same result.

  > Do not attempt this on the custom server, which has no OBO.
- **Check**: "If OBO were off, what would the second user see?"
- **Fallback**:
  - Recording of both calls
  - Screenshots of the denial

> **Build-time check**:
> 
> - OBO (user authorization) was announced GA on 7 Oct 2026, but some doc pages still say Public Preview. Say "GA" only after you see it in your workspace
> - A workspace admin sets the maximum scopes, and existing apps must be restarted after OBO is enabled
> - Grants go to the users or a group, not only to the service principal

### 4.7 Rung 7: the evaluation-driven loop
> 45 min: 15 theory, 30 demo.

- **Question**: How do we improve the agent safely?
- **Outcomes**: E14
- **Theory** (15):
  - Evaluation as the driver of agent development
  - The 3 phases:
    - Pre-deployment validation
      > `mlflow.genai.evaluate` on a fixed dataset.
    - Production monitoring on sampled live traces
    - Iterating on the judges
  - Backfill: running a new scorer over historical traces
    > Beta. The default window is 7 days; register and start the scorer first, and give an explicit start time.
  - The lifecycle view
    > Version, traces and evaluation results in one place.
- **Demo** (30), in order:
  1. Evaluation exposes the seeded failing case
  2. Change the agent (a prompt or a tool) and deploy it as a new version
  3. Re-run the same evaluation and compare the 2 runs
  4. Promote the better version
  5. Show the production-monitoring results from 4.1
  6. Create a new scorer and backfill with an explicit start time
  7. Open the lifecycle view, then:
     1. Flip the alias back to roll back
     2. Tie 1 failing trace to the version that produced it
- **Check**: "A trace failed in production => <br> How do you find which version produced it?"
- **Fallback**:
  - Pre-run evaluation runs and monitoring results
  - If Beta features are unavailable:
    - Keep traces in the experiment
    - Run `mlflow.genai.evaluate` over exported traces

> **Timing note**: This is the tightest block. Pre-stage each step's starting state so none takes more than about 4 minutes.

### 4.8 Wrap
> 15 min theory.

- **Theory**:
  - Interpretability recap: each artifact answers one question
    > Span tree, tool-call span, judge rationale, payload log, version record.
  - Discussion:
    - Context hygiene
      > Sub-agents may lower the peak input per call but add orchestration overhead. Share pre-computed numbers if available.
    - Trace ingestion limits
    - Cost
    - Runtime scaling
  - Close the promise ledger
  - Point to the handout
- **Check**: Ask participants which parking-lot question they found most useful to have answered
- **Set-up**: Hand out assignment A3

---

# 6. Labs, assignments and cross-session devices
## Labs (local, Sessions 1-2)

| Lab | When | Starter state | Steps | Success looks like | Stretch |
| --- | --- | --- | --- | --- | --- |
| L1: trace your function | 1.4, 15 min | A short agent script with one untraced function | Add `@mlflow.trace`; run; open the UI; find your span with its inputs and outputs | Your span appears in the tree under the right parent | Make the function raise and find the error span |
| L2: write and break a guideline | 2.2, 15 min | The small dataset and a working guideline judge setup | Write a guideline for the paragraph-analysis app; run it; make it vague or contradictory; re-run; compare scores and rationales | You can point to a rationale that changed because the guideline did | Add a second, row-wise guideline |
| L3: create a version and compare | 2.4, 15 min | v1 registered and evaluated | Change one prompt line; register v2; re-run the evaluation; compare v1 and v2; point `production` at the better one | The alias points where the scores say it should, with no code change | Flip it back and confirm |

> **Gemini keys**: Each participant creates a key in their own Google project. Google applies free-tier limits per project, not per key, so keys that share a project share a limit. Labs use live calls, with cached outputs as the fallback for anyone who hits a limit.
>
> **Trace export**: Traces are exported asynchronously. In every script that reads traces back, call `mlflow.flush_trace_async_logging()` before `mlflow.search_traces()`.

## Assignments (outside the session, not live)

| Assignment | Between | Time | Task | Output |
| --- | --- | --- | --- | --- |
| A1 | Session 2 and 3 (one week) | About 45 min, optional | Extend the local agent: add 1 MCP tool or 1 guideline; register a new version; evaluate; flip the alias. Write down which parking-lot question is still unanswered for you | A screenshot of the version comparison, plus 1-2 sentences |
| A2 | Session 3 and 4 (overnight) | About 20 min | Screenshots of a usage table and a payload log are provided. Answer: which call went through the gateway, who made it, what endpoint type it was. Then choose custom, external or managed for 3 scenarios and say why | Short answers, used in 4.5 |
| A3 | After Session 4 | 60-90 min | Pick a scenario (e.g. an HR-policy bot). Write 1 page: how you would split the agents, which MCP server type each tool uses and why, the UC grants 2 roles would need, 3 evaluation cases with their scorers, and what you would version | A one-page plan |

- A2 and A3 work with screenshots and paper, so they do not need workspace access
  > Participants who do have access can implement part of A3 as an option.
- All assignments are submitted by email or the shared folder, and feedback comes back the same way
- Handouts:
  - A2: [`assignment-a2.md`](./assignment-a2.md), with the presenter's [`assignment-a2-key.md`](./assignment-a2-key.md)
  - A3: [`assignment-a3.md`](./assignment-a3.md)

## Cross-session devices
- **Parking lot**: A visible list of open questions
  - Filled in 1.2
  - Reviewed at the start of Session 2
  - Revisited at the start of Sessions 3 and 4
- **Recaps**:
  - 10 minutes at the start of Session 2
  - 15 minutes at the start of Sessions 3 and 4
    > Longer because of the gap and the context switch.
  - A one-line recap at each block boundary
- **Bridge slide** (3.1), 2 columns:
  - *Stays the same*: `@mlflow.trace`, autologging, scorers and judges, versions and aliases
  - *Changes*:
    - The tracking URI and experiment path
    - Where traces are stored (a UC trace location instead of the local store)
    - Who can see them (UC permissions)
- **Check-for-understanding**: 1 question per block, listed above
- **Glossary**: A one-page handout
  > Acronyms are introduced only when a demo needs them.

| Term | First said | Defined in |
| --- | --- | --- |
| Trace, span | 1.2 | 1.4 |
| MCP | 1.2 | 1.5 |
| Scorer, judge | 1.2 | 2.2 |
| Version, alias | 1.2 | 2.3 |
| Unity Gateway | 1.2 (one sentence) | 3.3 |
| UC | 1.2 (one sentence) | 3.4 |
| Service principal (SP) | 3.2 | 4.2 |
| OBO | 1.2 ("acts as the user") | 4.6 |
| DAB | 3.2 (name only) | handout |

---

# 7. Pre-staging checklists
> The main risk is setup, not content. Sessions 3-4 depend on many Databricks prerequisites, so each has an owner moment below.

## Recorded backups
| ID | Covers | Recorded | Used if |
| --- | --- | --- | --- |
| B1 | Overview (1.2) | Day before Session 1 | Always played; or the fallback if you run it live |
| B2 | Tracing and MCP demos (1.4, 1.5) | Rehearsal week | A live step fails or Gemini rate-limits |
| B3 | Evaluation, versions, put-it-together (2.2-2.4) | Rehearsal week | Same |
| B4 | Rungs 1-4 (3.2-3.5), with screenshots of each result | Gap week, after the full workspace run | The workspace or a Beta feature misbehaves |
| B5 | Rungs 5-7 (4.2-4.7), with screenshots of the denial and the loop | Gap week | Same |

> Record with synthetic data only, and blur names, emails and workspace IDs.

## Before the course
- [ ] Send the setup guide and `smoke_test.py` at least 1 week before Session 1
- [ ] Collect every participant's smoke-test output at least 2 days before Session 1
  > Fix any FAIL by email. Anyone still failing joins the labs as a pair with a neighbour.
- [ ] Build the starter files for L1-L3 (not built yet)
- [ ] Cache the output of every LLM-backed step
- [ ] Confirm the live Gemini call and the default model name
  > The sandbox could not reach Gemini, so `gemini-3.5-flash-lite` is unconfirmed. Run `python smoke_test.py` on a real machine with a real key.
- [ ] Confirm the skyjet acceptance checklist (needed before B1 is recorded)
- [ ] Ask the account admin to enable Unity Gateway (Beta) on the Previews page
- [ ] Confirm the workspace is UC-enabled and in a supported region

## Day before Session 1
- [ ] Record B1
- [ ] Timed run of 1.3-1.5, with the labs
- [ ] Open the setup guide on a clean machine and follow it once

## Morning of each session
- [ ] Join 30 minutes early; check the screen share, audio and recording
- [ ] Parking lot visible on screen
- [ ] Cached outputs and the matching recording open in other tabs
- [ ] Sessions 1-2: `mlflow ui` runs; Gemini key works
- [ ] Sessions 3-4: the workspace opens, the apps are running and the gateway endpoint responds

## Between Sessions 1 and 2 (same evening)
- [ ] Register v1 of the prompts for the lab in 2.4
- [ ] Add unanswered parking-lot questions to the 2.1 slide

## Gap week (before Session 3)
Stage everything in the order the rungs use it.

- [ ] Rung 1: the paragraph-analysis app deployed once end to end, so you know the steps
- [ ] Rung 2: gateway endpoint created; Run A and Run B tested; low rate limit tested, then raised
- [ ] Rung 3: the experiment created with its UC trace location (fixed at creation); grants given explicitly
  > `ALL_PRIVILEGES` is not enough for trace tables.
- [ ] Rung 4: skyjet deployed behind the gateway, with the seeded failing case
- [ ] Rung 5: custom MCP app deployed; UC HTTP connection and MCP Service for the external server; managed MCP function created
- [ ] Rung 6: 2 test users (or volunteers), one with access and one without; grants given to the users or a group
- [ ] Rung 7: scorers prepared, 2 agent versions registered, a pre-run evaluation, and monitoring results
- [ ] A2 screenshot set captured (S1-S5) in the Session 3 rehearsal
- [ ] Record B4 and B5

## Between Sessions 3 and 4 (same evening)
- [ ] Insert the A2 screenshots and send A2
- [ ] Raise or remove the low rate limit
- [ ] Start the production scorer early if it is not already registered
  > First monitoring results take 15-20 minutes; 4.1 registers it so 4.7 has results to show.

## Rehearsal schedule
| Run | When | What |
| --- | --- | --- |
| R1 | The week before Session 1 | Full local run of Sessions 1-2, timed per block |
| R2 | Gap week | Full workspace run of Sessions 3-4, timed per block |
| R3 | The evening before Sessions 3 and 4 | Tightest blocks only: 3.3, 4.6, 4.7 |

# 8. Verification and coverage
## Re-verification of V3 items still in scope (14 Oct 2026)
| Item | Result | Where it landed |
| --- | --- | --- |
| Unity Gateway: Beta, admin enables, region, UC | Confirmed. Naming differs: "Unity AI Gateway" on AWS and GCP docs, "Unity Gateway" or "Enhanced Unity Gateway" on some Azure pages | 3.3 |
| Apps agents route LLM traffic through the gateway | Confirmed | 3.3 |
| Gateway features (usage, rate limits, traffic splitting) | Confirmed in the new gateway docs; the payload-log doc sits under the serving-endpoints gateway | 3.3 |
| Usage table | `system.ai_gateway.usage` confirmed | 3.3, A2 key |
| Payload-log table name | Not fixed; chosen by catalog, schema and prefix, read from the endpoint config | 3.3 |
| `ai_query` | Usage tracking only, so Run B uses the endpoint query API | 3.3 |
| OBO status | Announced GA on 7 Oct 2026; some doc pages lag | 4.6 |
| Prompt and alias APIs | Verified locally on MLflow 3.17.1 | 2.3 |
| Deterministic and trace-based scorers with `mlflow.genai.evaluate` | Verified locally | 2.2 |
| Trace export timing | Needs `mlflow.flush_trace_async_logging()` before `search_traces()` | Section 6 |
| Agent Bricks CLI | Confirmed (`agentbricks init/dev/deploy`, `ab`, needs `uv`). PyPI describes it as experimental, so say so in 3.2 | 3.2 |
| MCP Python SDK | v2.0.0 stable 28 Jul 2026; 2.3.0 latest; `MCPServer` replaces `FastMCP` | 1.5 |
| MLflow telemetry opt-out | `MLFLOW_DISABLE_TELEMETRY=true` verified in the package | Setup guide |

## Still unverified
- The gateway Fallbacks row of the support table (inferred in V3; flagged in the A2 key)
- The human-feedback API names, used for judge calibration in 2.2
- The skyjet repository contents (github.com/Platformatory/generative-ai, Module 5B)
- A live Gemini call and the default model name
- Timed dry runs per block

## Coverage check
Every outcome has at least one block.

| Outcome | Block |
| --- | --- |
| R1, R2 | 1.2 |
| E1 | 1.3 |
| E2 | 1.4 |
| E3 | 1.5 |
| E4, E5 | 2.2 |
| E6 | 2.3 |
| E7 | 2.4 |
| E8 | 3.2 |
| E9 | 3.3 |
| E10 | 3.4 |
| E11 | 3.5 |
| E12 | 4.2, 4.3, 4.4, 4.5 |
| E13 | 4.6 |
| E14 | 4.7 |

## Re-summed totals
| Session | Theory | Demo | Lab | Content min |
| --- | --- | --- | --- | --- |
| 1 | 80 | 65 | 15 | 160 |
| 2 | 80 | 50 | 30 | 160 |
| 3 | 80 | 80 | 0 | 160 |
| 4 | 66 | 94 | 0 | 160 |
| **Total** | **306** | **289** | **45** | **640** |

- Theory 306 of 640 minutes is 47.8%
- Demo and lab is 334 minutes, or 52.2%

# 9. Handout map
What was cut from V3 and where the participant can find it.

| V3 content | Where it goes | Note |
| --- | --- | --- |
| Multi-turn judges | Handout | Experimental; needs session IDs |
| Context hygiene experiment (20+ questions) | Handout | Large setup; discussion only in 4.8 |
| Dev-to-prod promotion with DAB targets | Handout | Out of scope for beginners |
| Sentiment and keyword tools using a server-side LLM | Handout | Blur who calls the LLM |
| Deploy routes (DAB, Git, direct upload) | One slide in 3.2, then the handout | |
| Gateway guardrails, traffic splitting, fallbacks | One slide in 3.3, then the handout | Support varies by endpoint type |
| MCP sampling, roots, logging, legacy SSE | Not shown | Already excluded in V3 |
| Glossary | Handout | Table in section 6 |
| Setup guide and smoke test | Handout, sent before Session 1 | |
| A1-A3 | Handouts | A2 and A3 drafted, A2 has a presenter key |

# Change log (V3 to V4)
- **Audience**: Beginners with basic Databricks and Python; no agent knowledge assumed
- **Structure**: 4 sessions of about 3 hours over 2 weekends, replacing the single 10-hour plan
- **Spiral**: A recorded overview, then a local deep dive (Sessions 1-2), then a ladder of 7 live Databricks rungs (Sessions 3-4)
- **Added**: Agent and tool-calling opener; labs L1-L3; assignments A1-A3; promise ledger; parking lot; bridge slide; glossary; setup guide and smoke test
- **Cut or moved**: Items in section 9
- **Changed**:
  - MCP is taught with 2 small servers instead of the full V3 set
  - Gateway is split into a Run A vs Run B contrast
  - Model Serving agents are a short legacy contrast
  - Context hygiene is discussion only
- **Corrected after verification**:
  - Payload-log table name is user-chosen
  - `FastMCP` is `MCPServer` in MCP SDK v2
  - OBO is announced GA
  - Gemini free-tier limits are per project
- **Time**: 640 content minutes, 47.8% theory

# Open items for review
1. **Two-user governance test**
   > Use 2 pre-made test users (the default), or 2 volunteers from the class? With 8-10 students, volunteers are feasible, but they need workspace accounts and the grants in place.
2. **Participant workspace access**
   > Do participants have any workspace access? It decides whether volunteers are possible and whether A3 can be implemented as an option.
3. **Skyjet acceptance checklist**
   > The recording is made the day before Session 1, so the checklist has to be confirmed by then.
4. **Assignment deadlines**
   > Due dates and feedback turnaround for A1-A3. Suggested: A1 before Session 3, A2 before Session 4 starts, A3 within a week of Session 4.
5. **Starter files**
   > L1-L3 starter files are not built yet.
6. **Live Gemini call**
   > Not tested from the sandbox. The default model name `gemini-3.5-flash-lite` needs confirming on a real key.
7. **Agent Bricks CLI**
   > PyPI describes it as experimental. Decide whether to say so in 3.2 or keep a fallback deploy route.