<h1>Agent Deployment on Databricks</h1>

---

**Contents**:

- [Key abbreviations](#key-abbreviations)
- [Conceptual foundations](#conceptual-foundations)
- [The agent lifecycle](#the-agent-lifecycle)
  - [Stages (prototype -\> production)](#stages-prototype---production)
  - [Deployment](#deployment)
    - [What is this about?](#what-is-this-about)
    - [Model-serving pattern](#model-serving-pattern)
    - [App-based pattern](#app-based-pattern)
    - [Comparing both patterns](#comparing-both-patterns)
    - [Unity AI Gateway as centralised governance](#unity-ai-gateway-as-centralised-governance)
  - [Observability](#observability)
  - [Evaluation](#evaluation)
  - [Monitoring](#monitoring)

---

# Key abbreviations

| Abbreviation | Full form |
| --- | --- |
| UC | Unity Catalog |

# Conceptual foundations
**See**: [`agentic-ai-basic-concepts.md`](./agentic-ai-basic-concepts.md)

# The agent lifecycle
## Stages (prototype -> production)
1. Deployment
2. Observability
3. Evaluation
4. Monitoring

Each stage has its own:

- Tools/platforms
- Methods/approaches

Stages may share the above (e.g. MLflow for stages 2 and 3).

> **KEY POINT**: Lifecycle stages are meant to be incremental, not linearly sequential. You can add tracing before deployment, attach scorers to an agent that is already live, or backfill evaluation data onto traces logged weeks ago. ***The lifecycle is designed to be incremental.***

## Deployment
> "Pattern" here => Replicable approach to addressing a need.

### What is this about?
The deployment stage is about packaging the agent and deploying it, either as a Databricks App (using Declarative Automation Bundles (DABs) or directly by linking/uploading a codebase) or as a Model Serving endpoint. Both deployment patterns are discussed below.

### Model-serving pattern
**First, a note about Model Serving**:

Model Serving is the Databricks solution for deploying AI and ML models for real-time serving and batch inference. More precisely, it is a platform centered around a unified interface to deploy, govern, and query AI models. Each model you serve (i.e. expose via the unified interface) is available as a REST API server, which is how you can integrate the model into your web or client application.

> **KEY POINTS**:
>
> - Model Serving is a Databricks-native platform
> - It offers a unified interface to interact with models
> - Can involve both Databricks-hosted and external models

> **Reference**: [Deploy models using Model Serving \| Databricks on AWS, **docs.databricks.com/aws/en/machine-learning/model-serving**](https://docs.databricks.com/aws/en/machine-learning/model-serving/)

---

**About the model-serving pattern**:

- Register a model in UC or MLflow
- Deploy it directly as a Model Serving endpoint

### App-based pattern
**First, a note about Databricks Apps**:

Databricks Apps (as a platform) is a Databricks-managed website-hosting platform that enables developers to build and deploy secure data and AI applications directly on the Databricks platform, which eliminates the need for separate infrastructure. Apps run on serverless compute provided by Databricks and integrate with key Databricks services, including UC for data governance, Databricks SQL for querying data, and OAuth for authentication. Common use cases include:

- Interactive dashboards
- AI chat apps
- Data entry forms
- Custom operational interfaces

When you deploy an agent as a Databricks App (note: "Databricks Apps" is the platform, "Databricks App" is an artifact (a particular app) you deploy on the platform), the platform handles the infrastructure concerns so you can focus on the application logic.

> **TECHNICAL NOTE**: Databricks apps (the artifacts) locally use Python or Node.js, which are then deployed to a Databricks workspace and can be moved between workspaces. Popular Python frameworks include Streamlit, Dash, and Gradio. Node.js frameworks such as React, Angular, Svelte, and Express are also supported.
>
> **BILLING NOTE**: Apps are billed per hour of compute time while running, based on provisioned capacity. You can create a limited number of apps per workspace. Details vary for free vs. paid editions.

---

**Second, a note about Databricks App**:

> - "Databricks Apps" => The managed web hosting platform
> - "Databricks App" => The web application deployed above

A Databricks app is a web application that runs as a containerized service on the Databricks serverless platform. Developers use supported frameworks such as Streamlit, Dash, or Gradio to build apps that deliver interactive data or AI experiences within a Databricks workspace.

> **Reference**: ["App", Key concepts in Databricks Apps
, **docs.databricks.com/aws/en/dev-tools/databricks-apps/key-concepts**](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/key-concepts#app)

Key characteristics of a Databricks App:

- Managed compute
  - The platform provisions and manages compute resources
  - You do not configure clusters, VMs, or containers
- Service principal
  - Each app runs under its own service principal identity
  - This determines what Databricks resources the app can access
    > E.g.: Serving endpoints, UC objects, MLflow experiments.
- Unique URL
  - Every deployed app gets a workspace-scoped URL
  - Users or downstream services can call this directly.
- Workspace integration
  - Apps are first-class workspace objects
  - They are visible on the Apps page in the workspace sidebar
  - On this page, you can:
    - Monitor status
    - View logs
    - Trigger redeployments

> **CONCEPTUAL NOTE**: A service principal is the identity an application or automated workload uses to sign in and receive access. In other words, a service principal is a non-human identity that lets an app or automation authenticate and access resources. The cloud equivalent of a service account - an app's own login, which must be protected like any credential.
>
> **NOTE**: The name means different components by platform, e.g.:
>
> - An app instance running in a tenant (Microsoft)
> - A service in a trust or resource policy (AWS)
> - etc.
>
> **Reference**: [Service principal, **cybersecurity101.net/glossary/service-principal**](https://cybersecurity101.net/glossary/service-principal/)

> **Reference**: [Databricks Apps, **docs.databricks.com/aws/en/dev-tools/databricks-apps**](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/)

---

**About the app-based pattern**:

In the app-based pattern, the serving endpoint is still present. It hosts the foundation model that the agent calls for inference. ***But the [agent orchestration](./agentic-ai-basic-concepts.md#multi-agent-systems-ai-orchestration), tool integrations (e.g. via [MCP](./mcp.md)), and observability wiring (e.g. via [MLflow](./mlflow.md)) all live in the app code.*** This separation gives you full control over the application layer while Databricks manages model hosting.

### Comparing both patterns
Both patterns use the Model Serving platform in Databricks as the platform to deploy and expose the actual models being used by the agent deployment. The differences between the model-serving and app-based patterns lie in how agent orchestration, tool integration, and observability wiring is done. Here is table to compare the differences (taken directly from the course "Agent Deployment on Databricks" on the Databricks Partner Academy website):

| Concern | Model Serving Endpoint | Databricks App |
|---|---|---|
| What is deployed | A registered model (MLflow/UC) | Application code (DAB) |
| Inference | The endpoint runs the model directly | The app calls a serving endpoint for inference |
| Scaling | Managed by the serving infrastructure | Managed by the Apps platform |
| Customization | Limited to model configuration | Full control: custom UI, middleware, routing logic |
| Governance | UC model permissions | App-level ACLs + UC permissions on accessed resources |
| Tool integration | Defined in the registered model | MCP servers, direct API calls, any Python library |

For a more practically-grounded comparison:

| Feature | Model Serving | Databricks Apps |
|---|---|---|
| MLflow Tracing | Automatic | Manual setup required |
| Auto-scaling | Yes (scale-to-zero) | Single instance |
| Custom UI | AI Playground only | React, Streamlit, Gradio... |
| Deploy Time | ~15 minutes | ~5 minutes |
| Iteration Speed | Slow (redeploy model) | Fast (hot reload) |
| A/B Testing | Native traffic splitting | Custom implementation |
| Cost Model | Pay-per-token + compute | Fixed compute cost |

> **Reference** (edited from original): [Deploying AI Agents on Databricks, **natefleming.github.io/agents-on-apps-vs-model-serving/presentation/model-serving-vs-apps.html**](https://natefleming.github.io/agents-on-apps-vs-model-serving/presentation/model-serving-vs-apps.html)

---

> **CONCEPTUAL NOTE**: A/B Testing also called split testing is a method of comparing two versions of a webpage, app, or feature to find which one performs better based on user response. It helps in making data-driven decisions by testing real user behavior.
>
> **Reference**: [Introduction to A/B Testing, **www.geeksforgeeks.org/blogs/what-is-a-b-testing**](https://www.geeksforgeeks.org/blogs/what-is-a-b-testing/)

### Unity AI Gateway as centralised governance
When a deployed agent calls a model serving endpoint for inference, that request passes through the Unity AI Gateway, which is the centralised AI governance layer on Databricks. The gateway sits between your application and the serving endpoints, providing guardrails, rate limiting, usage tracking, and traffic management without requiring changes to your agent code. As per Databricks' own documentation:

> "Unity Gateway is the Databricks governance solution for enterprise AI. Built on Unity Catalog, it extends governance beyond your data and AI assets to the runtime interactions between models, agents, MCP servers, and tools. Control which AI services teams can use, route and manage AI traffic, set guardrails with service policies, and monitor usage from one control plane."
> 
> **Reference**: [AI governance with Unity Gateway, **docs.databricks.com/aws/en/ai-gateway**](https://docs.databricks.com/aws/en/ai-gateway/)

Considering an app-based deployment pattern:

```
Databricks App <--> Unity AI Gateway <--> Model Serving endpoint
(agent code)        - Guardrails          (foundational model)
                    - Rate limits
                    - Usage tracking
                    - Traffic splitting
                    - etc.
```

> **KEY POINT 1**: The gateway governs more than just agent traffic. It provides a unified governance layer across LLM endpoints, MCP servers, and coding agents (such as Cursor, Claude Code, and Codex CLI), ***giving platform teams a single place to manage AI access across the organisation.***

> **KEY POINT 2**: The Unity AI Gateway is transparent to your agent code. Your app calls the serving endpoint as usual; the gateway intercepts and governs the request automatically. No code changes are needed to benefit from rate limiting, guardrails, or usage tracking. Rather, these are configured at the platform level (i.e. via the Unity AI Gateway platform configurations).

---

Key capabilities of Unity AI Gateway:

- **Guardrails**: <br> Enforce safety and content policies
  > Do so on requests and responses at the gateway level.
- **Rate limiting**: <br> Configure consumption limits per endpoint
  > This is to manage capacity and control costs.
- **Usage tracking**: <br> Analyze costs by endpoint, model, principal, and tags
  > This is done via billable usage system tables.
- **Traffic splitting**: <br> Distribute requests across multiple model backends
  > This is for A/B testing or gradual rollouts.
- **Inference tables**: Log requests and responses to UC Delta tables
  > This is for auditing and analysis.

## Observability
Integrate MLflow Tracing (the tracing component of [MLflow](./mlflow.md)) so every request produces a structured trace capturing inputs, outputs, latency, and execution flow. MLflow Tracing is a fully OpenTelemetry-compatible LLM observability solution for your agents and LLM applications. It captures the inputs, outputs, and metadata associated with each intermediate step of a request, enabling you to easily pinpoint the source of bugs and unexpected behaviors.

> **KEY POINT**:  MLflow Tracing gives you complete visibility into your agents and LLM applications.

> **References**:
>
> - [MLflow Tracing for LLM and Agent Observability, **mlflow.org/docs/latest/genai/tracing**](https://mlflow.org/docs/latest/genai/tracing/)
> - Learn more about tracing: ["Trace", Common Terms, **Getting into Observability**, **pranigopu.github.io/getting-into-observability/common-terms.html**](https://pranigopu.github.io/getting-into-observability/common-terms.html#trace)
> - Learn more about OpenTelemetry (OTel): [OTel, **Getting into Observability**, **pranigopu.github.io/getting-into-observability/otel.html**](https://pranigopu.github.io/getting-into-observability/otel.html)

---

How it helps at every step of agent development:

- Building and debugging
- Human feedback management, which means... <br> - collecting <br> - managing <br> - utilising <br> ... feedback from end-users and domain experts
  > Feedback are:
  > 
  > - Attached to traces
  > - Recorded with metadata, including user, timestamp, revisions, etc.
- Evaluation with the help of MLflow Evaluation
  > **Reference**: [Evaluating LLMs and Agents with MLflow, **mlflow.org/docs/latest/genai/eval-monitor**](https://mlflow.org/docs/latest/genai/eval-monitor/)
  > 
  > MLflow Tracing provides the material for MLflow Evaluation.
- Monitoring
  > "MLflow Tracing captures key metrics like latency and token usage at each step, as well as various quality metrics, helping you identify bottlenecks, monitor efficiency, and find optimization opportunities."
  > 
  > **Reference**: [MLflow Tracing for LLM and Agent Observability, **mlflow.org/docs/latest/genai/tracing**](https://mlflow.org/docs/latest/genai/tracing/)
- Dataset collection (for future evaluation)
  > "Traces from production systems capture perfect data for building high-quality datasets with precise details for internal components like retrievers and tools."
  > 
  > **Reference**: [MLflow Tracing for LLM and Agent Observability, **mlflow.org/docs/latest/genai/tracing**](https://mlflow.org/docs/latest/genai/tracing/)

In essence: MLflow Tracing is key to what makes evaluation and monitoring possible.

> **Reference**: [MLflow Tracing for LLM and Agent Observability, **mlflow.org/docs/latest/genai/tracing**](https://mlflow.org/docs/latest/genai/tracing/)

## Evaluation
Attach scorers to the MLflow experiment that automatically assess trace quality using LLM judges, guidelines, or custom Python functions. MLflow's evaluation and monitoring capabilities help you systematically measure, improve, and maintain the quality of your LLM applications and AI agents throughout their lifecycle from development through production.

> **Reference**: [Evaluating LLMs and Agents with MLflow, **mlflow.org/docs/latest/genai/eval-monitor**](https://mlflow.org/docs/latest/genai/eval-monitor/)

A core tenet of MLflow's evaluation capabilities is Evaluation-Driven Development, i.e. development that progresses iteratively based on feedback from evaluation at various steps of the development process (more on this discussed in [`agent-evaluation.md`](./agent-evaluation.md)), as illustrated in the following:

![](/_common-resources/evaluation-driven-development.png)

> **Source**: [Evaluating LLMs and Agents with MLflow, **mlflow.org/docs/latest/genai/eval-monitor**](https://mlflow.org/docs/latest/genai/eval-monitor/)

> **KEY POINT**: "MLflow is an open source AI engineering platform that is designed to support this practice and help you quickly build production-quality AI agents and LLM applications."
>
> **Reference**: [Evaluating LLMs and Agents with MLflow, **mlflow.org/docs/latest/genai/eval-monitor**](https://mlflow.org/docs/latest/genai/eval-monitor/)

Key capabilities:

- Dataset management (management of "Evaluation Datasets") 
  > Evaluation Datasets => Centralised repository for managing:
  > 
  > - Test cases
  > - Ground truth expectations
  > - Evaluation data at scale
  >
  > "Think of Evaluation Datasets as your "test database" - a single source of truth for all the data needed to evaluate your AI systems."
  > 
  > **Reference**: [Evaluating LLMs and Agents with MLflow, **mlflow.org/docs/latest/genai/eval-monitor**](https://mlflow.org/docs/latest/genai/eval-monitor/)
- Human feedback management (discussed in the previous section)
- LLM-as-a-judge
  > MLflow offers various built-in LLM-as-a-Judge scorers to help automate the process of assessing the quality of your AI deployments (models or agents), as well as a flexible toolset to build your own LLM judges with ease.
  > 
  > **Reference**: [Evaluating LLMs and Agents with MLflow, **mlflow.org/docs/latest/genai/eval-monitor**](https://mlflow.org/docs/latest/genai/eval-monitor/)
- Systematic evaluation
  > This means:
  > 
  > - Tracking your evaluation results
  > - Effectively collaborating with your team
- Monitoring (discussed in the previous section)

## Monitoring
Monitoring is the process of ensuring data from observability and evaluation are maintained and kept up to date across time. It is meant to enable long-term analysis and long-term maintenance + improvement of quality assessment standards and deployment performance. This involves managing scorer lifecycles, ings historical traces with new scorers, and archiving traces to Delta tables for long-term analysis.

