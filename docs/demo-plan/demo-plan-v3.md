<h1>Demo Plan V3</h1>

> AI-enhanced.

---

**Contents**:

- [Key abbreviations](#key-abbreviations)
- [About](#about)
- [How to read this plan](#how-to-read-this-plan)
  - [Coverage map](#coverage-map)
  - [Tiers and time](#tiers-and-time)
  - [Layering map](#layering-map)
  - [Demo hygiene](#demo-hygiene)
- [Core concepts](#core-concepts)
  - [MLflow as a deployment lifecycle manager](#mlflow-as-a-deployment-lifecycle-manager)
  - [MLflow as an observability framework](#mlflow-as-an-observability-framework)
  - [MLflow as an evaluation framework](#mlflow-as-an-evaluation-framework)
  - [MCP architecture and tooling](#mcp-architecture-and-tooling)
  - [Agentic app deployment in Databricks - 1](#agentic-app-deployment-in-databricks---1)
  - [Agentic app deployment in Databricks - 2 (capstone)](#agentic-app-deployment-in-databricks---2-capstone)
    - [Act 0: Deploy and observe](#act-0-deploy-and-observe)
    - [Act 1: MCP server types](#act-1-mcp-server-types)
    - [Act 2: Evaluation-driven loop](#act-2-evaluation-driven-loop)
    - [Act 3: Lifecycle view](#act-3-lifecycle-view)
    - [Legacy contrast (optional)](#legacy-contrast-optional)
- [Agentic app dev/deployment principles](#agentic-app-devdeployment-principles)
  - [Evaluation-driven development](#evaluation-driven-development)
  - [Context hygiene](#context-hygiene)
- [Interpretability](#interpretability)
- [Flexibility and scalability](#flexibility-and-scalability)
- [Change log (V2 to V3)](#change-log-v2-to-v3)
- [Verification log](#verification-log)
- [Sources](#sources)

---

# Key abbreviations

| Abbreviation | Full form |
| --- | --- |
| UC | Unity Catalog |
| DAB | Declarative Automation Bundles (formerly Databricks Asset Bundles) |
| MCP | Model Context Protocol |
| OBO | On-behalf-of-user authorization (the app calls a resource with the end user's identity, not its own) |
| SP | Service principal |

> **NOTE: Naming**: The governance layer is called **Unity Gateway**. Some Databricks pages shorten it to "Unity Gateway", which is the name we shall be using in this plan. The earlier product is "AI Gateway (legacy)" and is not used.

# About
The demo plan is meant to organise the practical demonstration of the deployment of agentic applications in Databricks such that the core concepts are clarified (in terms of what they mean in practice), the principles behind agentic application development and deployment are clarified (e.g. evaluation-driven development, context hygiene (i.e. keeping agent context well-scoped and preventing context rot), interpretability (of the agentic application's processes and outcomes), etc.), flexibility and scalability are addressed, and practical components are clarified (e.g. tooling, governance, etc.).

> In essence: the demo plan is to clarify theory via realistic practice.

# How to read this plan
## Coverage map
Each intent in "About" is closed by at least one demo:

| Intent | Where it is demonstrated |
| --- | --- |
| Core concepts | The 6 sections under "Core concepts" (the capstone expands into three MCP-server-type acts) |
| Evaluation-driven development | Capstone, Act 2 ("Evaluation-driven development" holds the principle and points there) |
| Context hygiene | "Context hygiene" (reuses the capstone app) |
| Interpretability | "Interpretability" (artifact map over earlier demos) |
| Flexibility and scalability | "Flexibility and scalability" (each item labelled demo or discussion) |
| Tooling | MLflow, MCP, Databricks demos |
| Governance | Unity Gateway (Databricks - 1 and capstone), UC (capstone: managed and external MCP acts; trace tables) |

## Tiers and time
> **NOTE**:
> 
> - Audience: engineers comfortable with Python + basic Databricks
> - Times are defaults to tune to your session length

| Tier | Demos | Suggested time each |
| --- | --- | --- |
| Spine | MLflow lifecycle; MLflow observability; MLflow evaluation; MCP architecture; Capstone (Acts 0-3); Context hygiene | 30-45 min (capstone: 90-120 min in total) |
| Short | Databricks - 1; capstone Acts 1a (custom MCP) and 1b (external MCP) | 15-25 min |
| Optional | Capstone legacy-contrast demo; flexibility and scalability items | 5-15 min |

> If time is cut, drop from the bottom up.
> 
> *The capstone's managed-MCP act (1c) and Acts 2-3 are never dropped.*

## Layering map
Which layer each demo exercises.

> X = used; blank = deliberately absent.

| Demo | Apps | Model Serving | MLflow | Unity Gateway | MCP | UC (tool access) | UC (trace tables) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MLflow lifecycle | | | X | | | | |
| MLflow observability | | | X | | | | |
| MLflow evaluation | | | X | | | | |
| MCP architecture | | | | | X | | |
| Databricks - 1 (app-based) | X | | | optional | | | |
| Databricks - 1 (model-serving, legacy contrast) | | X | X | optional | | | |
| Capstone Act 1a (custom MCP) | X | X | X | X | X | | X |
| Capstone Act 1b (external MCP) | X | X | X | X | X | X | X |
| Capstone Act 1c (managed MCP) | X | X | X | X | X | X | X |
| Capstone Acts 2-3 (eval loop, lifecycle view) | X | X | X | X | X | X | X |
| Capstone legacy-contrast (model-serving endpoint) | | X | X | X | X | X | |
| Context hygiene | X | X | X | X | X | X | X |

> **NOTE**:
>
> **Model Serving** = a Model Serving endpoint is part of the demo, either as the deployed agent (legacy pattern) or as the LLM backend behind the gateway. **UC (tool access)** = UC governs the tool or data access path. **UC (trace tables)** = traces are stored in UC Delta tables. The 2 are separate on purpose. Custom MCP leaves UC (tool access) blank because access is governed by Databricks Apps permissions. External MCP is governed through UC (a UC HTTP connection, registered as an MCP Service), so it is marked. If your custom app reads UC tables, mark it. Finally, context hygiene reuses the capstone app, so its row mirrors the capstone.

## Demo hygiene
- Use synthetic data only
- Gemini's free tier is rate-limited
  > Keep cached outputs of each LLM-backed demo as a fallback.
- Several Databricks features used here are Beta, preview or experimental. Each is marked where used:
  - Unity Gateway (Beta; an account admin must enable it from the Previews page; supported regions only)
  - MCP Services for external servers (needs the Unity Gateway Beta and the Managed MCP Servers preview)
  - Production monitoring (Beta)
  - Scorer backfill (Beta)
  - Multi-turn evaluation (experimental)
- Release-sensitive claims were checked on 14 Oct 2026
  > - See the [Verification log](#verification-log)
  > - Re-check the items marked "re-check" the day before the demo

> **NOTE: Deferred**: Fallbacks beyond those already written in V2 are not implemented in V3. The V2 fallback lines are kept as they were.

# Core concepts
Keep each demo:

- As concise and bare-bones as possible
- As direct about the concept as possible

## MLflow as a deployment lifecycle manager
Clarify:

- What lifecycle management concretely consists of
  > Beyond the generic "tracking" via experiments/run IDs.
  >
  > Concretely:
  > 
  > - Versioning what was deployed
  > - Comparing versions
  > - Promoting/rolling back
  > - Tying a failure to a version
- **What is actually versioned**
  > State it explicitly in the demo:
  > 
  > - The guideline prompts (prompt versions)
  > - The app/model snapshot that used them
- What are the uses of such management
  > E.g.:
  > 
  > - Reusing an older high-performing deployment
  > - Debugging unique failures within a certain deployment

Suggested demo:

- Deploy 2 simple AI-based experiments
- Ensure both have:
  - Different guideline prompts
  - The same task prompts
- Compare deployments:
  - Through MLflow UI
  - Programmatically
- Test case 1 (reuse):
  - Pick the better version
  - Load/serve it again
- Test case 2 (debug):
  - Send 1 input that fails on one version only
  - Locate the failure through that version's record.
- Test case 3 (promote and roll back):
  - Point an alias (e.g. `production`) at the better version
  - Flip the alias to the other version and back
  - Show that the serving code did not change

> **Build-time check**: For the MLflow version you use, confirm:
> 
> - Exact prompt-registry
> - Alias API names 

> **Suggested deployment mode**:
> 
> - Locally-hosted
> - Externally-connected LLM
>   > Preferably Gemini, as it is free.

## MLflow as an observability framework
Clarify:

- How MLflow Tracing is actually used by code components
- The different kinds of spans and traces we can create
  > Including span types (e.g. LLM, TOOL, RETRIEVER, CHAIN) and error spans.
- Automatically-created vs. custom spans/traces

Suggested demos (in order):

1. Perform tracing for a recursive function
    > E.g.: Factorial calculation.
2. Perform tracing for 2 sorting functions
    > E.g.: Selection sort vs. bubble sort.
3. Perform tracing for 1 LLM call
    > Automatically-created (autologged) span, shown next to the custom spans above.
4. Perform tracing for a small typed-span pipeline
    > - A mock retriever (RETRIEVER span) feeds a tool (TOOL span)
    > - This feeds an LLM call (LLM span), where 1 tool call raises
    > - Show the error span inside the span tree

> **Suggested deployment mode**: Locally-hosted

## MLflow as an evaluation framework
Clarify:

- The different kinds of MLflow scorers
  > E.g.:
  > 
  > - Built-in judge
  > - Guideline judge
  > - Custom scorer (deterministic)
  > - Custom LLM judge
  > 
  > **Suggested**: Also demonstrate:
  > 
  > - Multi-turn scorers/judges
  > - Global vs. row-wise guidelines in guideline judge
- Combination of MLflow Tracing and MLflow Evaluation
  > Via a trace-based scorer.
  > 
  > E.g.: A scorer that checks which tools were called.
- Why scorers need calibration against human judgement

> **NOTE**: The older `mlflow.metrics` API is legacy.
> 
> *Use scorers instead.*
>
> **NOTE: Multi-turn judges**: Multi-turn judges need session IDs on the traces (the `mlflow.trace.session` tag/metadata), so tracing is a prerequisite for them. Multi-turn evaluation is experimental and works on pre-collected traces.
>
> **NOTE: Databricks-specific built-in judges**: Some built-in judges (e.g. Safety, RetrievalRelevance) may exist only in Databricks managed MLflow. For the locally-hosted demo, pick built-in judges that run on open-source MLflow. Built-in multi-turn judges default to OpenAI, so set the judge model to Gemini explicitly.

Suggested demo:

Part 0: Capture

- 1 chatbot, traced, with a session ID on every turn
- 1 scripted conversation for the main demo
- 8-10 short conversations for Part 3

Part 1: Scorer taxonomy

- Apply a suite of judges + custom scorers on the main conversation:
  - Individually first
  - Together next

Part 2: Tracing + evaluation

- Apply 1 trace-based scorer to the captured traces

Part 3: Judge calibration

- Attach human assessments (labels/expectations) to the short conversations
- Compare each judge's verdict with the human label
- Show 1 disagreement and revise the guideline accordingly

> **Suggested deployment mode**:
> 
> - Locally-hosted
> - Externally-connected LLM
>   > Preferably Gemini, as it is free.

## MCP architecture and tooling
Clarify:

- MCP client-server architecture in action:
  - 1-to-many host-server connection
  - Host hosting 1+ MCP clients
  - Dedicated client-server connection
- MCP primitives shown in practice
  > Tools, resources and prompts. The demo must contain at least one real resource (fetched by URI) and one prompt, not tools only.
- MCP protocol layers in action:
  - Data layer
    > Stateless in the current spec (2026-07-28):
    > 
    > - No initialization handshake and no session header
    > - Protocol version, client info and capabilities travel with each request (in `_meta`)
    > - `server/discover` returns server capabilities on demand. Servers must implement it; clients may call it.
  - Transport layer
    > STDIO and Streamable HTTP.

Suggested demo:

- 1 AI application as host
  > AI model + wrapper code.
- Multiple clients
- 1 orchestration logic to make MCP server calls
- Multiple MCP servers for:
  - Tools (deterministic and AI)
  - Resources
  - Prompts
- Use-case: Paragraph analysis; e.g.:
  - Check word and character count (tool)
  - Check spelling, without AI (tool)
  - Evaluate sentiment, with AI but not the host (tool; the server uses its own LLM client)
  - Identify keywords for tags, with AI but not the host (tool)
  - Find externally-stored documents with the same keywords (tool: `search_documents`)
  - Open one found document by URI, e.g. `doc://<id>` (resource)
  - A reusable "analyse this paragraph" template (prompt)
- Test case 1 (architecture):
  - Log each client's connection to its server
  - Thereby show the dedicated client-server pairing
- Test case 2 (transport):
  - Run 1 server over STDIO
  - Run 1 server over Streamable HTTP
- Test case 3 (data layer):
  - Call `server/discover` on 1 server
  - Show a tool call with no prior handshake
  - Point at the protocol version and capabilities carried in `_meta`

> **NOTE: Do not show**: MCP sampling (the server-side LLM calls use the server's own client), roots, logging, and the legacy HTTP+SSE transport. The 2026-07-28 spec deprecates them.

> **Caveat**: Test case 3 needs an SDK that implements the 2026-07-28 spec. The official TypeScript SDK v2 is stable. For Python, sources disagree on whether v2 or v1.x is the default install, so pin an exact version and dry-run beforehand. Use the same spec era on the client and the server: a modern server with a legacy client is the combination that fails. Python SDK v2 also renamed the in-SDK `FastMCP` class to `MCPServer`.

> **Suggested deployment mode**:
> 
> - Locally-hosted
> - Self-managed (locally-hosted) MCP servers
> - Externally-connected LLM
>   > Preferably Gemini, as it is free.

## Agentic app deployment in Databricks - 1
Clarify:

- App-based pattern of deployment
  - Using the Agent Bricks CLI (`agentbricks deploy`)
    > Databricks' recommended route for new agents: `DurableAgentServer` on Agent Runtime (which runs on Databricks Apps).
  - Using DAB (Declarative Automation Bundles)
  - Using externally-hosted source code (e.g. Git repo)
  - Using direct code upload
- Model-serving pattern of deployment (without app)
  > **Legacy**. Databricks lists "Custom Agent on Model Serving" among legacy offerings and advises moving to Apps. Show it for contrast only.
- Unity Gateway as governance (optional in both patterns):
  - Show in this demo:
    - Rate limiting
    - Usage tracking
    - Payload logging (inference tables)
  - Name only (support varies by endpoint type, see the table below):
    - Guardrails
    - Traffic splitting
    - Fallbacks

Gateway feature support by endpoint type:

> Serving-endpoint surface; confirm on your endpoint.

| Feature | External model | FMAPI pay-per-token | FMAPI provisioned | Databricks agents | Custom model |
| --- | --- | --- | --- | --- | --- |
| Guardrails | Yes | Yes | Yes | No | No |
| Traffic splitting | Yes | No | Yes | No | Yes |
| Fallbacks | Yes | No | No | No | No |

> **NOTE**: The Fallbacks row is inferred from:
> 
> - A flattened docs table
> - A note that fallbacks work only on external models
> 
> Re-check it.

> **Suggestion**: Do not include the following:
>
> - MLflow (for app-based pattern)
> - MCP
>
> This ensures the demo is tightly-scoped.
>
> **NOTE**:
> 
> - MLflow is unavoidable for model-serving pattern
> - App-based pattern can use Model Serving, but need not
> - Unity Gateway is the governance layer used throughout
>   > The earlier AI Gateway (legacy) is not used.
>
> **Why this app differs from the capstone's**: This demo isolates deployment and the gateway on the simplest app (the paragraph-analysis use-case from the MCP demo). The capstone adds everything else on a realistic multi-agent app.

Prerequisites:

- Unity Gateway enabled for the account
  > Previews page, by an account admin.
- A workspace in a supported region
  > Not available on AWS GovCloud or Azure Government.
- One gateway endpoint created for an LLM

Suggested demo:

- For app-based pattern:
  - Same use-case as ["MCP architecture and tooling" above](#mcp-architecture-and-tooling)
    > But deployed in Databricks, and without MCP tooling.
  - Avoid Model Serving and MLflow
  - Run twice to show Unity Gateway is optional:
    - Run A: direct LLM call, no gateway
    - Run B: the same call routed through Unity Gateway
      > The code change is only the routing step::
      > 
      > - Pass the gateway endpoint name as the model
      > - Set `use_ai_gateway=True` on the Databricks LLM client
      > - The parameter keeps the old name... <br> ... *but the product is Unity Gateway*
  - Test case 1 (rate limit):
    - Set a very low limit on the gateway endpoint
    - Send requests through Run B's route until 1 is rejected
  - Test case 2 (usage):
    - Show Run B's call in usage tracking
    - Show that Run A's call is absent
  - Test case 3 (payload log):
    - Find Run B's request and response in the gateway's payload log (inference table)
    - Show that Run A has no record
- For model-serving pattern (legacy contrast):
  - Create backend for the same demo as above
  - Show the necessity of MLflow for this case
  - State:
    - Why it is legacy
    - Where the migration path to Apps is documented

> **Build-time check**: Name the exact usage and payload-log tables in your workspace before the demo. Docs name `system.ai_gateway.usage` for usage; the payload-log table name was not verified.

> **NOTE 1**: Not every gateway feature applies to every endpoint type (see the table above). State the endpoint type before showing each feature.

> **NOTE 2**: For new agents, Databricks recommends the Agent Bricks CLI and runtime. The MLflow `AgentServer` (and `LongRunningAgentServer`) is legacy. Mention this, and use whichever the demo's source code already uses.

> **Required deployment mode**: In Databricks.

## Agentic app deployment in Databricks - 2 (capstone)
> **Why one app**: V2 had a separate Databricks - 2 app and an Evaluation-driven development app, with identical layering rows. They are merged. The skyjet app is deployed once and exercised across 4 acts.

Clarify:

- Everything from ["Agentic app deployment in Databricks - 1"](#agentic-app-deployment-in-databricks---1)
- MCP servers in Databricks:
  > Also talk about the use-cases/merits/demerits of each.
  - Custom
    > Hosted by you as a Databricks App.
  - External
    > Third-party server, reached through a UC HTTP connection and registered as an MCP Service.
  - Managed
    > E.g.: A UC function exposed as an MCP tool.
- UC for data governance
  > Especially: what IS UC and how does it govern?
- How MLflow actually manages agent lifecycle in specifics
- The iterative nature of agent deployment and evaluation
  > See ["Evaluation-driven development"](#evaluation-driven-development).

**The app**: [`Module 5B/skyjet-app`, `Platformatory`, **github.com**](https://github.com/Platformatory/generative-ai/tree/main/Module%205B/skyjet-app) (unchanged from V2).

> **Acceptance checklist** Confirm  before the demo:
>
> - A policy agent and a flight agent
> - At least 1 MCP-based tool
> - MLflow tracing on the agents
> - A runnable evaluation dataset
> - A stated agent runtime: <be> Agent Bricks CLI (recommended) or the legacy MLflow `AgentServer`

How the local demos carry over:

| Local demo | Capstone equivalent |
| --- | --- |
| MLflow lifecycle: version record, alias flip | Act 3: the same record in the Databricks MLflow UI, with traces and evaluation results beside it |
| MLflow observability: span tree, tool spans | Acts 0-1: traces in UC trace tables |
| MLflow evaluation: scorers, judges | Act 2: `mlflow.genai.evaluate`, production monitoring, backfill |
| MCP architecture: primitives, transports | Act 1: the same primitives behind three Databricks server types |
| Databricks - 1: gateway on/off | Act 0: every LLM call goes through Unity Gateway |

Prerequisites:

- Unity Gateway enabled, in a supported region
  > See Databricks - 1.
- A SQL warehouse
  > - UC-stored traces are read through it
  > - Monitoring jobs fail... <b> ... *without the `mlflow.monitoring.sqlWarehouseId` experiment tag*
- MLflow 3.14 or later (`mlflow[databricks]>=3.14.0`) for traces in UC
- An experiment created **with** a UC trace location
  > The binding can only be made at creation; cannot be reassigned.
- Explicit UC grants on the trace schema (`USE_CATALOG`, `USE_SCHEMA`, `CREATE TABLE`, then table privileges)
  > `ALL_PRIVILEGES` is not sufficient for trace tables.
- A Databricks notebook for registering monitoring scorers
  > Only `@scorer` functions work, and they must be defined and registered from a notebook (no class-based scorers).
- 2 human users for the governance test, plus the app's SP
- OBO (user authorization) enabled on the app, with the `unity-catalog` scope for UC-function MCP
- 1+ UC functions to expose, with grants
- For external MCP:
  - The MCP Services preview
  - A marketplace server or a UC connection
- For custom MCP:
  - A small MCP server deployed as a Databricks App
  - The agent's SP granted "Can Use"

> **NOTE**: Production monitoring allows at most 20 scorers per experiment.

### Act 0: Deploy and observe
- Deploy skyjet as an app, by the method chosen in Databricks - 1
- Route every LLM call through Unity Gateway
- Set up observability via MLflow Tracing + Unity Gateway
  > In the gateway, focus on the payload log (inference tables).
- Show 1 trace in the MLflow UI + the matching row in usage tracking

### Act 1: MCP server types
Create a separate sub-demo per MCP server type. Keep custom and external short (show how they work) and give managed the largest share.

- **1a Custom (short)**:
  - Host a small MCP server as a Databricks App
  - Connect the agent at `https://<app-url>/mcp`
  - Show that access is governed by app permissions (Can Use for the agent's SP)
  - Note the documented limits: OAuth only, no personal access tokens, no OBO
- **1b External (short)**:
  - Register an external MCP server as an MCP Service
  - Show the calls passing through Unity Gateway, authorized by an `EXECUTE` grant in UC
  - Note the Beta/preview requirements
- **1c Managed (deep)**:
  - Expose 1 UC function as a managed MCP tool
    > Per-function URL `/api/2.0/mcp/functions/{catalog}/{schema}/{function_name}`; the schema-level URL lists every function in the schema.
  - Other managed servers exist (AI Search, Genie Agents, Databricks SQL). Name them, do not demo them.
- Test case 1 (governance), managed demo only:
  - Call the function as a user with access
  - Call it as a user without access, and show the denial
  > Requires OBO. With the app's SP both users get the same result. Grant EXECUTE and the catalog/schema privileges to the users or a group, not only to the SP. Do not try this on the custom server, which has no OBO.
- Test case 2 (comparison), wrap-up after 1a-1c:
  - Fill 1 table comparing custom/external/managed servers on:
    - Who hosts it
    - Who governs access
    - Effort to set up
    - A fitting use-case
    - Trust and security exposure

Reference answers for the table (checked 14 Oct 2026; confirm live):

| | Custom | External | Managed |
| --- | --- | --- | --- |
| Who hosts it | You, as a Databricks App | A third party; Databricks proxies it through a UC HTTP connection | Databricks, on serverless compute |
| Who governs access | Databricks Apps permissions | UC (`EXECUTE` on the MCP Service) plus Unity Gateway; per-user OAuth possible | UC permissions plus Unity Gateway; OBO supported |
| Effort to set up | Highest: build and deploy an app | Medium: install from Marketplace or register a connection | Lowest: ready to use |
| Fitting use-case | Organisation-specific tools | Third-party SaaS tools | Your UC data and functions |
| Trust and security | You own the code and tool descriptions | Highest exposure: third-party tool descriptions and responses can carry prompt injection; limit tools with tool selection and policies | Tools bounded by UC grants |

### Act 2: Evaluation-driven loop
- Evaluation setup using judges/scorers, mapped to 3 phases:
  1. Pre-deployment validation: <br> `mlflow.genai.evaluate` over a fixed dataset
  2. Production monitoring: <br> Register scorers (from a notebook) to run on sampled live traces
     > Allow 15-20 minutes for the first results.
  3. Iterative development of judges: <br> Change a judge, re-run, compare
- Test case 3 (the loop):
  - Evaluation exposes 1 failing case
  - Change the agent (a prompt or a tool) and deploy it as a new version
  - Re-run the same evaluation and compare the two runs
  - Promote the better version
- Test case 4 (backfill):
  - Create a new scorer later and show historical backfill
  - Register and start the scorer first, then backfill
  - Give an explicit start time for the backfill window
    > ***NOTE**: The default covers only the last 7 days.

> **Fallback**: If Beta features are unavailable:
> 
> - Keep traces in the experiment
> - Run `mlflow.genai.evaluate` over exported traces
>
> The experiment backend holds at most 100,000 traces per experiment.

> **Suggestion**: You can add more tools to the above app.

### Act 3: Lifecycle view
- Test case 5 (lifecycle view):
  - Show the MLflow record of the deployed agent in one view
    > Version, traces, evaluation results (now available from Act 2).
  - Flip the alias back to the previous version to roll back
  - Pick 1 failing trace and tie it to the version that produced it

### Legacy contrast (optional)
- Deploy the same agent as a Model Serving endpoint
- Add the managed MCP tool
- Mention additional components needed for production use
- Show where the migration to Apps is documented
> Writing traces to UC from a Model Serving endpoint needs a personal access token (per the Azure docs; check your cloud).

# Agentic app dev/deployment principles
## Evaluation-driven development
Clarify:

- The iterative nature of agent deployment + evaluation
- Agent evaluation as key to agent development/deployment
- [Additional] Store MLflow traces in Delta tables
  > Two routes. The route Databricks recommends is a UC trace location (traces land directly in UC Delta tables). The other is production monitoring syncing experiment traces to Delta tables about every 15 minutes (Beta).
- [Additional] Backfilling historical traces with new scorers
  > [Beta]

**Demonstrated in**: the capstone, Act 2 (loop and backfill) and Act 3 (lifecycle view). It is not a separate app any more.

## Context hygiene
Clarify:

- The potential for context rot and bloat
- How sub-agents rectify this
  > Treat this as a hypothesis to test, not a promised result. A supervisor plus sub-agents can use more total tokens through orchestration overhead, while lowering the peak input per call.
- How sub-agents fit within the workflow

Suggested demo:

- Same app as in the capstone
- Note that this demo has:
  - Policy agent
  - Flight agent
- Test case (before/after): Ask the same questions to
  - A single agent given both policy and flight context
  - The policy + flight sub-agents

  Setup:
  - At least 20 questions, each run 3 times
  - Policy and flight context padded to a realistic size
  - A multi-turn variant: at least 10 turns per session, with session IDs on the traces
  - A tool-schema variant: give both variants the same long tool list, then show the sub-agents scoping it

  Compare, from traces:
  - Peak input tokens on any single call
  - Total tokens, including orchestration overhead
  - 1 correctness scorer result
  - For the multi-turn variant: 1 multi-turn judge (experimental)

  Report whichever way the result falls.

> **Prerequisite**: The single-agent baseline does not exist in the skyjet app. Build it beforehand: one agent that receives both the policy and flight context in a single prompt/toolset. Keep model, temperature and questions identical across both variants so the comparison is fair, and trace both so input token counts can be read.

# Interpretability
Demonstrated above; clarify how. Each artifact answers one question:

| Artifact | Question it answers | Shown in |
| --- | --- | --- |
| Span tree of a trace | What did the agent do, in what order? | MLflow observability; capstone Acts 0-2 |
| Tool-call span | Which tool was called, with what input and output? | MLflow observability (demo 4); capstone Act 1 |
| Judge rationale | Why did the judge give this score? | MLflow evaluation; capstone Act 2 |
| Inference table (payload log) | What went through the endpoint, and who used it? | Databricks - 1; capstone Act 0 |
| Version record | Which deployment produced this behaviour? | MLflow lifecycle; capstone Act 3 |

# Flexibility and scalability
Each item is marked demo or discussion:

- Agent -> sub-agent architecture (demo)
  > Add 1 new sub-agent/tool to the app without changing others.
- Managed MCP server + tooling scaling (demo)
  > Add 1 more UC function as a managed tool.
  >
  > **NOTE**: Test whether the agent finds it without redeploying. It depends on whether the agent re-lists tools per request or caches them at startup. The 2026-07-28 MCP spec makes lists cacheable with an expiry, so the new tool may appear only after a refresh.
- Gateway controls (demo)
  > Rate limits and (if the endpoint supports it) traffic splitting.
- Swap the LLM behind the gateway (demo)
  > Change the model behind the gateway endpoint with no agent code change.
- UC trace storage and historical scorer backfill (demo)
- Dev-to-prod promotion (demo, optional)
  > Use DAB targets.
- Trace ingestion limits (discussion)
  > Traces in UC: Initially 200 traces/second per workspace and 100 MB/second per table. Both can be raised through your Databricks account team.
  >
  > **NOTE**: The experiment backend is the fallback, but it holds at most 100,000 traces per experiment. It is a demo fallback, not a scale path.
- Agent runtime scaling and load behaviour (discussion)
  > Agent Runtime on Databricks Apps handles hosting, identity and scaling. Measure before quoting numbers.
- Cost (discussion)
  > Gateway features are free during Beta. Custom MCP servers bill at Databricks Apps pricing and UC-function MCP at serverless general compute pricing.

---

# Change log (V2 to V3)
**Cross-cutting**:

- Verified the release-sensitive claims (see Verification log)
- Merged "Databricks - 2" and "Evaluation-driven development"
  > Into one capstone app (skyjet) with Acts 0-3.
- Test cases in the capstone numbered in presentation order
  > Governance, comparison, loop, backfill, lifecycle view.
- Added "Tiers and time"
- Layering map:
  - Added an Apps column
  - Split UC into tool access and trace tables
  - Added rows for the merged capstone and the legacy contrast
- Marked the Model Serving agent pattern as legacy (contrast only)
- Demoted the above's 3 per-MCP-type demos to 1 optional demo
- Named the product consistently as Unity Gateway
- Fallbacks: V2 lines kept, nothing new added

**Per section**:

- MLflow lifecycle:
  - Added "what is versioned"
  - Added a promote/roll back test case
- MLflow observability:
  - Added a typed-span demo with an error span
- MLflow evaluation:
  - Added a capture step with session IDs
  - Added judge-calibration part
  - Added notes on judge availability + the Gemini judge model
- MCP architecture:
  - Added a resource and a prompt
  - Moved the keyword search to a tool
  - Rewrote the data-layer caveat
  - Listed what not to show
- Databricks - 1:
  - Agent Bricks CLI added as the recommended deploy route
  - Model-serving pattern labelled legacy
  - Usage test case now contrasts Run B with Run A
  - Added a payload-log test case
  - Added a feature-support table and prerequisites
  - Explained why its app differs from the capstone's
- Capstone (new):
  - Prerequisites
  - A local-to-Databricks mapping
  - An acceptance checklist in place of commit pinning
  - A trust and security row
  - Reference answers for the comparison table
- Context hygiene:
  - 3 questions and 1 scorer replaced by:
    - 20+ questions
    - Repeats
    - Padded context
    - A multi-turn variant
    - A tool-schema variant
    - Peak vs total tokens
    - An honest-outcome note
- Interpretability:
  - Tool-call span moved off the MCP demo
  - Sources updated to the new structure
- Flexibility and scalability:
  - Added LLM swap
  - Added dev-to-prod
  - Added runtime scaling and cost
  - The "agent finds it without redeploying" claim is now a test
  - Trace limits corrected

**Unchanged**:

- About
- The format conventions
- The skyjet app reference

# Verification log
Checked on 14 Oct 2026 against Databricks and MCP documentation. "Re-check" means the item is still moving.

| Claim | Status | Note |
| --- | --- | --- |
| MLflow 3.14+ for traces in UC | Confirmed | Docs install `mlflow[databricks]>=3.14.0` |
| 200 traces/s per workspace | Confirmed, with nuance | "Initially" limited; also 100 MB/s per table; raisable. Re-check |
| Experiment-backend trace cap | Added | 100,000 traces per experiment |
| 20-scorer cap on production monitoring | Confirmed | Per experiment |
| 7-day default backfill window | Confirmed | Beta; scorers must be registered and started first |
| Agent Bricks over MLflow `AgentServer` | Confirmed, stronger | `AgentServer` is legacy; "Custom Agent on Model Serving" is also legacy |
| Gateway features per endpoint type | Partly confirmed | Guardrails and traffic splitting verified per type; fallbacks row inferred. Two doc generations exist. Re-check |
| Gateway name | Clarified | "Unity Gateway" (Beta); some pages say "Unity Gateway" |
| `use_ai_gateway=True` | Confirmed | Set on the Databricks LLM client; gateway endpoint passed as the model |
| MCP stateless data layer, `server/discover` | Confirmed | Spec 2026-07-28; servers must implement discover, clients may call it |
| SDK support for the stateless spec | Partly confirmed | TypeScript v2 stable; Python v2 status conflicts across sources. Re-check |
| Multi-turn judges need session IDs | Confirmed | `mlflow.trace.session`; experimental; evaluation takes pre-collected traces only |
| DAB name | Confirmed | Renamed Declarative Automation Bundles in March 2026 |
| External MCP does not touch UC (V2 note) | **Wrong** | External servers use UC connections and MCP Services (UC securables) |
| Custom MCP on Apps and OBO | New | Documented as not supporting OBO or personal access tokens |
| OBO on Databricks Apps | Conflicting | A recent Databricks post announces GA; an older page says Public Preview. Re-check |
| skyjet repo contents | Not verified | The site blocks automated access; use the acceptance checklist |
| Prompt-registry and alias API names | Not verified | Build-time check |
| Human-feedback API names | Not verified | Build-time check |
| Payload-log table name | Not verified | Build-time check |
| Tool-list refresh without redeploy | Not verified | Now a test in Flexibility |

# Sources
- [Store OpenTelemetry traces in Unity Catalog](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/trace-unity-catalog)
- [Tracing overview](https://docs.databricks.com/aws/en/mlflow3/genai/tracing/)
- [Set up production monitoring](https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/production-monitoring)
- [Monitor GenAI in production](https://docs.databricks.com/aws/en/generative-ai/agent-evaluation/monitoring-features)
- [Manage production scorers (backfill)](https://docs.databricks.com/gcp/en/mlflow3/genai/eval-monitor/manage-production-scorers)
- [Evaluate conversations](https://docs.databricks.com/aws/en/mlflow3/genai/eval-monitor/evaluate-conversations)
- [Unity Gateway](https://docs.databricks.com/en/ai-gateway/)
- [Unity Gateway for serving endpoints (feature matrix)](https://learn.microsoft.com/en-us/azure/databricks/ai-gateway/overview-serving-endpoints)
- [Author an agent on Databricks Apps (gateway step)](https://docs.databricks.com/aws/en/agents/agent-framework/author-agent)
- [Deploy agents on Databricks](https://docs.databricks.com/aws/en/agents/deploy/)
- [Legacy agent offerings](https://learn.microsoft.com/en-us/azure/databricks/agents/legacy/)
- [MCP on Databricks](https://docs.databricks.com/aws/generative-ai/mcp)
- [Managed MCP servers](https://learn.microsoft.com/azure/databricks/agents/mcp/managed-mcp)
- [MCP Services in Unity Catalog](https://docs.databricks.com/aws/en/agents/agent-framework/mcp-services)
- [Authentication for agents on Databricks Apps](https://docs.databricks.com/en/generative-ai/agent-framework/agent-authentication.html)
- [Connect non-Databricks clients to Databricks MCP servers](https://docs.databricks.com/gcp/en/generative-ai/mcp/connect-external-services)
- [Declarative Automation Bundles release notes](https://docs.databricks.com/gcp/pt/release-notes/dev-tools/bundles)
- [MCP SEP-2575: Make MCP stateless](https://modelcontextprotocol.io/seps/2575-stateless-mcp)
- [MCP 2026-07-28 release candidate post](https://blog.modelcontextprotocol.io/posts/2026-07-28-release-candidate/)
- [MLflow multi-turn evaluation](https://www.mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/multi-turn/)
- [MLflow predefined LLM judges](https://mlflow.org/docs/latest/genai/eval-monitor/scorers/llm-judge/predefined/)