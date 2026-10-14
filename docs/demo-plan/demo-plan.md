<h1>Demo Plan</h1>

---

**Contents**:

- [About](#about)
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

---

# About
The demo plan is meant to organise the practical demonstration of the deployment of agentic applications in Databricks such that the core concepts are clarified (in terms of what they mean in practice), the principles behind agentic application development and deployment are clarified (e.g. evaluation-driven development, context hygiene (i.e. keeping agent context well-scoped and preventing context rot), interpretability (of the agentic application's processes and outcomes), etc.), flexibility and scalability are addressed, and practical components are clarified (e.g. tooling, governance, etc.).

> In essence: the demo plan is to clarify theory via realistic practice.

# Core concepts
Keep each demo:

- As concise and bare-bones as possible
- As direct about the concept as possible

## MLflow as a deployment lifecycle management
Clarify:

- What lifecycle management concretely consists of
  > Beyond the generic "tracking" via experiments/run IDs.
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
  > - Trace-based scorers/judges
  > - Global vs. row-wise guidelines in guideline judge
- Combination of MLflow Tracing and MLflow Evaluation
- Demonstrate `mlflow.metrics` as a part of evaluation

Suggested demo:

- 1 chatbot + 1 conversation
- Apply a suite of judges and custom scorers on it:
  - Individually first
  - Together next

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
- MPC protocol layers in action:
  - Data layer
  - Transport layer

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

> **Suggested deployment mode**:
> 
> - Locally-hosted
> - Self-managed (locally-hosted) MCP servers
> - Externally-connected LLM
>   > Preferably Gemini, as it is free.

## Agentic app deployment in Databricks - 1
Clarify:

- App-based pattern of deployment
  - Using DAB (Databricks Automation Bundles)
  - Using externally-hosted source code (e.g. Git repo)
  - Using direct code upload
- Model-serving pattern of deployment (without app)
- Unity Gateway as governance:
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

Suggested demo:

- For app-based pattern:
  - Same use-case as ["MCP architecture and tooling" above](#mcp-architecture-and-tooling)
    > But deployed in Databricks, and without MCP tooling.
  - Avoid Model Serving and MLflow
  - Use Unity Gateway
    > Show how it is optional and why it is useful.
- For model-serving pattern:
  - Create backend for the same demo as above
  - Show the necessity of MLflow for this case

> **NOTE**: AI Gateway is legacy; migrate to Unity Gateway.

> **Required deployment mode**: In Databricks.

## Agentic app deployment in Databricks - 2
Clarify:

- Everything from ["Agentic app deployment in Databricks - 1"](#agentic-app-deployment-in-databricks---1)
- MCP servers in Databricks:
  > Also talk about the use-cases/merits/demerits of each.
  - Custom
  - External
  - Managed
- Unity Catalog for data governance
  > Especially: what IS Unity Catalog and how does it govern?
- How MLflow actually manages agent lifecycle in specifics

Suggested demo 1 (app-based pattern):

- Same demo as ["MCP architecture and tooling" above](#mcp-architecture-and-tooling)
  > But deployed in Databricks.
- Use Model Serving and MLflow
  > App-based pattern can use Model Serving for AI model backend.
- Use Unity Gateway
- Use MCP; demonstrate for all kinds of MCP servers
  > Simple demos for custom and external, deeper for managed.
  > 
  > **NOTE**: The idea is to show how the other 2 work, but focus on the managed.

Suggested demo 2 (model-serving pattern):

- Replicate the above as much as possible
- Add MCP tooling
- Mention additional components needed for production use

# Agentic app dev/deployment principles
## Evaluation-driven development
Clarify:

- The iterative nature of agent deployment + evaluation
- Agent evaluation as key to agent development/deployment
- [Additional] Store MLflow traces in Delta tables
  > Trace archival streams traces to Delta tables.
- [Additional] Backfilling historical traces with new scorers

Suggested demo:

- Shri Veena's [`Module 5B/skyjet-app`, `Platformatory`, **github.com**](https://github.com/Platformatory/generative-ai/tree/main/Module%205B/skyjet-app)
  > Use this as the agentic app.
- Use Model Serving and MLflow
- Use tooling (including MCP server-based tools)
- Set up observability via MLflow Tracing + Unity Gateway
  > In Unity Gateway, focus on inference tables.
- Create evaluation setup using judges and scorers
  > Design the setup to:
  > 
  > - Cover different types of judges
  > - Address pre-deployment validation
  > - Address production monitoring
  > - Address iterative development of judges
- Create a new scorer later and show historical backfill

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

# Interpretability
Demonstrated above; clarify how.

# Flexibility and scalability
- Agent -> sub-agent architecture
- Managed MCP server + tooling scaling
- Trace archival and historical scorer backfill
- ?