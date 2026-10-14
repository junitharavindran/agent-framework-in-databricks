<h1>Demo Plan V2</h1>

> AI-enhanced.

---

**Contents**:

- [Key abbreviations](#key-abbreviations)
- [About](#about)
- [How to read this plan](#how-to-read-this-plan)
  - [Coverage map](#coverage-map)
  - [Layering map](#layering-map)
  - [Demo hygiene](#demo-hygiene)
- [Core concepts](#core-concepts)
  - [MLflow as a deployment lifecycle management](#mlflow-as-a-deployment-lifecycle-management)
  - [MLflow as an observability framework](#mlflow-as-an-observability-framework)
  - [MLflow as an evaluation framework](#mlflow-as-an-evaluation-framework)
  - [MCP architecture and tooling](#mcp-architecture-and-tooling)
  - [Agentic app deployment in Databricks - 1](#agentic-app-deployment-in-databricks---1)
  - [Agentic app deployment in Databricks - 2](#agentic-app-deployment-in-databricks---2)
- [Agentic app dev/deployment principles](#agentic-app-devdeployment-principles)
  - [Evaluation-driven development](#evaluation-driven-development)
  - [Context hygiene](#context-hygiene)
- [Interpretability](#interpretability)
- [Flexibility and scalability](#flexibility-and-scalability)
- [Change log (V1 to V2)](#change-log-v1-to-v2)

---

# Key abbreviations

| Abbreviation | Full form |
| --- | --- |
| UC | Unity Catalog |

# About
The demo plan is meant to organise the practical demonstration of the deployment of agentic applications in Databricks such that the core concepts are clarified (in terms of what they mean in practice), the principles behind agentic application development and deployment are clarified (e.g. evaluation-driven development, context hygiene (i.e. keeping agent context well-scoped and preventing context rot), interpretability (of the agentic application's processes and outcomes), etc.), flexibility and scalability are addressed, and practical components are clarified (e.g. tooling, governance, etc.).

> In essence: the demo plan is to clarify theory via realistic practice.

# How to read this plan
## Coverage map
Each intent in "About" is closed by at least one demo:

| Intent | Where it is demonstrated |
| --- | --- |
| Core concepts | The 6 demos under "Core concepts" |
| Evaluation-driven development | "Evaluation-driven development" |
| Context hygiene | "Context hygiene" |
| Interpretability | "Interpretability" (artifact map over earlier demos) |
| Flexibility and scalability | "Flexibility and scalability" (each item labelled demo or discussion) |
| Tooling | MLflow, MCP, Databricks demos |
| Governance | Unity Gateway (Databricks - 1 and 2), UC (Databricks - 2) |

## Layering map
Which layer each demo exercises.

> X = used; blank = deliberately absent.

| Demo | Model Serving | MLflow | Unity Gateway | MCP | UC |
| --- | --- | --- | --- | --- | --- |
| MLflow lifecycle | | X | | | |
| MLflow observability | | X | | | |
| MLflow evaluation | | X | | | |
| MCP architecture | | | | X | |
| Databricks - 1 (app-based) | | | optional | | |
| Databricks - 1 (model-serving) | X | X | optional | | |
| Databricks - 2 | X | X | X | X | X |
| Evaluation-driven development | X | X | X | X | X |

## Demo hygiene
- Use synthetic data only
- Gemini's free tier is rate-limited
  > Keep cached outputs of each LLM-backed demo as a fallback.
- Some Databricks features used here are Beta:
  - Trace archival
  - Production monitoring
  - Scorer backfill
  > Each is marked where used, with a fallback.

# Core concepts
Keep each demo:

- As concise and bare-bones as possible
- As direct about the concept as possible

## MLflow as a deployment lifecycle management
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

> **Suggested deployment mode**:
> 
> - Locally-hosted
> - Externally-connected LLM
>   > Preferably Gemini, as it is free.

## MLflow as an observability framework
Clarify:

- How MLflow Tracing is actually used by code components
- The different kinds of spans and traces we can create
- Automatically-created vs. custom spans/traces

Suggested demos (in order):

1. Perform tracing for a recursive function
    > E.g.: Factorial calculation.
2. Perform tracing for 2 sorting functions
    > E.g.: Selection sort vs. bubble sort.
3. Perform tracing for 1 LLM call
    > Automatically-created (autologged) span, shown next to the custom spans above.

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
  > Via a trace-based scorer (e.g. a scorer that checks which tools were called).

> **NOTE**: The older `mlflow.metrics` API is legacy. Use scorers instead.

Suggested demo:

Part 1: Scorer taxonomy

- 1 chatbot + 1 conversation
- Apply a suite of judges and custom scorers on it:
  - Individually first
  - Together next

Part 2: Tracing + evaluation

- Trace the same chatbot
- Apply 1 trace-based scorer to the traces

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
- MCP protocol layers in action:
  - Data layer
    > Stateless in the current spec:
    > 
    > - No initialization handshake
    > - Protocol version/client capabilities travel per request
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
- Use-case: Paragraph analysis; e.g.:
  - Check word and character count
  - Check spelling (without AI)
  - Evaluate sentiment (with AI, but not host)
  - Identify keywords for tags (with AI, but not host)
  - Externally-stored documents with same keywords
- Test case 1 (architecture):
  - Log each client's connection to its server
  - Thereby show the dedicated client-server pairing
- Test case 2 (transport):
  - Run 1 server over STDIO
  - Run 1 server over Streamable HTTP
- Test case 3 (data layer):
  - Call `server/discover` on 1 server
  - Show a tool call with no prior handshake

> **Suggested deployment mode**:
> 
> - Locally-hosted
> - Self-managed (locally-hosted) MCP servers
> - Externally-connected LLM
>   > Preferably Gemini, as it is free.

## Agentic app deployment in Databricks - 1
Clarify:

- App-based pattern of deployment
  - Using DAB (Declarative Automation Bundles)
  - Using externally-hosted source code (e.g. Git repo)
  - Using direct code upload
- Model-serving pattern of deployment (without app)
- Unity Gateway as governance (optional in both patterns):
  - Guardrails
  - Rate limiting
  - Usage tracking
  - Traffic management
  - Inference tables

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
>   > The earlier AI Gateway is legacy and is not used.

Suggested demo:

- For app-based pattern:
  - Same use-case as ["MCP architecture and tooling" above](#mcp-architecture-and-tooling)
    > But deployed in Databricks, and without MCP tooling.
  - Avoid Model Serving and MLflow
  - Run twice to show Unity Gateway is optional:
    - Run A: direct LLM call, no gateway
    - Run B: the same call routed through Unity Gateway
      > The code change is only the routing step, e.g.: <br> `use_ai_gateway=True` in the Databricks client
  - Test case 1 (rate limit):
    - Set a very low limit
    - Send requests until 1 is rejected
  - Test case 2 (usage):
    - Show the 2 calls in usage tracking
- For model-serving pattern:
  - Create backend for the same demo as above
  - Show the necessity of MLflow for this case

> **NOTE 1**: Not every gateway feature applies to every endpoint type (e.g. traffic splitting and guardrails are not supported on Databricks agent endpoints). State the endpoint type before showing each feature.

> **NOTE 2**: For new agents, Databricks currently recommends its Agent Bricks CLI and runtime over the older MLflow `AgentServer`. Mention this, and use whichever the demo's source code already uses.

> **Required deployment mode**: In Databricks.

## Agentic app deployment in Databricks - 2
Clarify:

- Everything from ["Agentic app deployment in Databricks - 1"](#agentic-app-deployment-in-databricks---1)
- MCP servers in Databricks:
  > Also talk about the use-cases/merits/demerits of each.
  - Custom
    > Hosted by you as an app.
  - External
  - Managed
    > E.g.: A UC function exposed as an MCP tool.
- UC for data governance
  > Especially: what IS UC and how does it govern?
- How MLflow actually manages agent lifecycle in specifics

Suggested demos #1 (app-based pattern):

- Same demo as ["MCP architecture and tooling" above](#mcp-architecture-and-tooling)
  > But deployed in Databricks.
- Use Model Serving and MLflow
  > App-based pattern can use Model Serving for AI model backend.
- Use Unity Gateway
- Use MCP; demonstrate for all kinds of MCP servers
  > Simple demos for custom and external, deeper for managed.
  > 
  > **NOTE**: The idea is to show how the other 2 work, but focus on the managed.
- Test case 1 (governance):
  - Expose 1 UC function as a managed MCP tool
  - Call it:
    - As a user with access
    - As a user without access, and show the denial
- Test case 2 (comparison):
  - Fill 1 table comparing custom/external/managed servers on:
    - Who hosts it
    - Who governs access
    - Effort to set up
    - A fitting use-case.
- Test case 3 (lifecycle):
  - Show the MLflow record of the deployed agent in one view
    > Show version, traces, evaluation results.

> Create separate demo per MCP server type.

Suggested demos #2 (model-serving pattern):

- Replicate the above as much as possible
- Add MCP tooling
- Mention additional components needed for production use

> Create separate demo per MCP server type.

# Agentic app dev/deployment principles
## Evaluation-driven development
Clarify:

- The iterative nature of agent deployment + evaluation
- Agent evaluation as key to agent development/deployment
- [Additional] Store MLflow traces in Delta tables
  > [Beta]
  > 
  > Trace archival streams traces to Delta tables.
- [Additional] Backfilling historical traces with new scorers
  > [Beta]

Suggested demo:

- Shri Veena's [`Module 5B/skyjet-app`, `Platformatory`, **github.com**](https://github.com/Platformatory/generative-ai/tree/main/Module%205B/skyjet-app)
  > Use this as the agentic app.
- Use Model Serving and MLflow
- Use tooling (including MCP server-based tools)
- Set up observability via MLflow Tracing + Unity Gateway
  > In Unity Gateway, focus on inference tables.
- Evaluation setup using judges/scorers, mapped to 3 phases:
  1. Pre-deployment validation: <br> `mlflow.genai.evaluate` over a fixed dataset
  2. Production monitoring: <br> Register scorers to run on sampled live traces
  3. Iterative development of judges: <br> Change a judge, re-run, compare
- Create a new scorer later and show historical backfill
  > Give an explicit start time for the backfill window.
  > 
  > ***NOTE**: The default covers only the last 7 days.

> **Prerequisites**:
> 
> - A SQL warehouse
> - A recent MLflow version (3.14 or later for traces in UC)
> - Explicit table grants
> 
> **NOTE**: Production monitoring allows at most 20 scorers.
>
> **Fallback**: If Beta features are unavailable:
> 
> - Keep traces in the experiment
> - Run `mlflow.genai.evaluate` over exported traces

> **Suggestion**: You can add more tools to the above app.

## Context hygiene
Clarify:

- The potential for context rot and bloat
- How sub-agents rectify this
- How sub-agents fit within the workflow

Suggested demo:

- Same demo as in ["Evaluation-driven development"](#evaluation-driven-development)
- Note that this demo has:
  - Policy agent
  - Flight agent
- Test case (before/after): Ask the same 3 questions to
  - A single agent given both policy and flight context
  - The policy + flight sub-agents
  
  Compare input token counts (from traces) and 1 scorer result (e.g. correctness) for each.

# Interpretability
Demonstrated above; clarify how. Each artifact answers one question:

| Artifact | Question it answers | Shown in |
| --- | --- | --- |
| Span tree of a trace | What did the agent do, in what order? | MLflow observability; Evaluation-driven development |
| Tool-call span | Which tool was called, with what input and output? | MCP architecture; Databricks - 2 |
| Judge rationale | Why did the judge give this score? | MLflow evaluation |
| Inference table | What went through the endpoint, and who used it? | Databricks - 1; Evaluation-driven development |
| Version record | Which deployment produced this behaviour? | MLflow lifecycle |

# Flexibility and scalability
Each item is marked demo or discussion:

- Agent -> sub-agent architecture (demo)
  > Add 1 new sub-agent/tool to the app without changing others.
- Managed MCP server + tooling scaling (demo)
  > Add 1 more UC function as a managed tool.
  > 
  > **NOTE**: The agent finds it without redeploying.
- Gateway controls (demo)
  > Rate limits and (if the endpoint supports it) traffic splitting.
- Trace archival and historical scorer backfill (demo)
- Trace ingestion limits (discussion)
  > Traces in UC are capped per workspace (200 traces/second).
  > 
  > **NOTE**: The experiment backend is the fallback.

---

# Change log (V1 to V2)
**Cross-cutting**:

- Added "How to read this plan":
  - Coverage map
  - Layering map
  - Demo hygiene
- Marked Beta features and added a fallback

**Per section**:

- MLflow lifecycle: added:
  - A reuse test case
  - A debug test case
- MLflow observability: added a 3rd demo (autologged LLM call)
- MLflow evaluation: split the demo into 2 parts:
  - Trace-based scorers now covered via "Tracing + evaluation"
  - `mlflow.metrics` replaced by a one-line legacy note
- MCP architecture:
  - Added 3 test cases:
    - Client pairing
    - Transports
    - Stateless data layer
  - Data layer and transport notes added
- Databricks - 1
  - Unity Gateway marked optional with a with/without run
  - 2 test cases
  - Endpoint-type caveat
  - Agent Bricks note
  - "AI Gateway is legacy" note reworded so only Unity Gateway is used
- Databricks - 2: added:
  - A governance test case
  - A comparison table
  - A lifecycle view
- Evaluation-driven development:
  - Demo mapped to 3 phases
  - Backfill window made explicit
  - Prerequisites and fallback added
- Context hygiene: added a before/after test case
- Interpretability: replaced the one-liner with an artifact map
- Flexibility and scalability: replaced "?" with concrete items
  > Each marked demo or discussion.

**Unchanged**:

- About
- The format conventions
- The skyjet app reference