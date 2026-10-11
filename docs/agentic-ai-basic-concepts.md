<h1>Agentic AI Basic Concepts</h1>

---

**Contents**:

- [Key abbreviations](#key-abbreviations)
- [Agent](#agent)
- [AI agent](#ai-agent)
- [Multi-agent systems, AI orchestration](#multi-agent-systems-ai-orchestration)

---

# Key abbreviations

| Abbreviation | Full form |
| --- | --- |
| UC | Unity Catalog |

# Agent
An agent is any entity that exerts power autonomously.

> **NOTE**: Power refers to the ability to cause change.

Hence, an agent is an entity that is...

- independent
- self-directed

... in its exertion of power as it acts toward one or more goals.

> **References**:
> 
> - ["Agent", Conceptual Foundation, Foundations of Agentic AI, **pranigopu.github.io/foundations-of-agentic-ai/conceptual-foundation.html**](https://pranigopu.github.io/foundations-of-agentic-ai/conceptual-foundation.html#agent)
> - [agent, merriam-webster.com/dictionary](http://merriam-webster.com/dictionary)

> Examples of non-AI agents:
>
> - Software agents (rule-based, no learning):
>   - Thermostat
>   - Email spam filter (keyword rules)
>   - Web crawlers
>   - Antivirus signature scanners
>   - Decision-tree-based conversational agents
> - Physical or mechanical agents:
>   - Washing machine controller
>   - Cruise control (rule-based)
>   - Multi-elevator controllers
>
> **CONCEPTUAL NOTE**: It is useful to identify "agent" as a genus that extends beyond AI agents, so that we can carry forward key characteristics that define agents as such (e.g. autonomy, self-contained response patterns, continuous interaction with its environment, etc.) and apply that to AI-based decision-making, thereby treating AI agents as a composition of concepts, rather than treating AI agents as a completely novel (and therefore completely uncharted) construct.

# AI agent
An AI agent is an agent whose decision-making apparatus is based on artificial intelligence. Hence, in effect, AI agents are adaptive programs/systems designed to make decisions autonomously. Adaptive => not constrained by training data or a well-defined set of use-case parameters. In this context, autonomous decision-making specifically refers to not being dependent on human input/feedback to facilitate or validate its decision-making, at least within a range of conditions and circumstances.

AI agents can:

- Act to obtain information
- Create and execute workflows
- Perform actions and tasks
- Interact with:
  - External systems
  - Applications/tools
  - Other AI agents

Another way to define AI agents is as "compound software systems, inclusive of one or more AI models, that operate within an environment and take actions within it." (Feng et al, 2025; see below). In other words, combining this definition with the previous one, an AI agent is an AI system (e.g. a decision tree, a neural network, an LLM, etc.) that uses one or more tools to act and modify its environment autonomously.

> **References**:
> 
> - [(Feng et al, 2025): Levels of Autonomy for AI Agents, knightcolumbia.org/content](http://knightcolumbia.org/content)
> - ["AI Agent", Conceptual Foundation, Foundations of Agentic AI, **pranigopu.github.io/foundations-of-agentic-ai/conceptual-foundation.html**](https://pranigopu.github.io/foundations-of-agentic-ai/conceptual-foundation.html#ai-agent)

# Multi-agent systems, AI orchestration
Single-agent is when 1 AI agent performs the entire activity needed for a goal or goals. Multi-agent is when multiple AI agents perform sub-tasks in a coordinated way. Multi-agent activities are coordinated by AI orchestration. E.g.:

```
supervisor agent (routes and synthesises)
                      |
                (delegates to)
                      |
                      v
     +----------------+----------------+
     |                |                |       |
     v                v                v       |
data agent      research agent   general agent | workers
- UC functions  - AI search      - Knowledge   |
- SQL           - Documents      - Reasoning   |
```

**AI orchestration**: Adaptive coordination + management of 2+:

- AI agents
- Systems
- Data sources

> **NOTE**:
> 
> - AI orchestration is adaptive, not rule-based
> - Usually happens on an AI orchestration platform

**AI orchestration platform**: A software framework used to...

- create
- deploy
- manage
- monitor

... the safe operation of AI agents.

**AI orchestration platforms**:

- Automate AI workflows
- Facilitate external data access
- Facilitate human governance
- Enable agent-to-agent (A2A) communication

---

**Further notes**:

- Agent Bricks is a no-code Databricks-native AI orchestration platform
- Databricks has code-based frameworks for AI/agentic  orchestration
- Facilitation of external data access involves:
  - Querying external data sources (external to agent’s parametric context)
  - Receiving and processing data/information from the above

The Databricks platform as a whole (especially Unity Catalog) is relevant for the 1st point. MCP is a key aspect of implementing the 2nd point. Another key aspect is vector search (for RAG). Both shall be discussed next. Next, it is key to know how Databricks (and Agent Bricks in particular) incorporates these elements (i.e. MCP, vector search). It is important to know the AI-specific platform offerings of Databricks via Agent Bricks as well as other offerings, beyond general Databricks offerings and MCP/vector search (e.g. Unity AI Gateway, Model Serving, Agent Evaluation, etc.).