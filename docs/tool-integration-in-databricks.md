<h1>Tool Integration in Databricks</h1>

---

**Contents**:

- [Abbreviations](#abbreviations)
- [Tools for agents on Databricks](#tools-for-agents-on-databricks)
- [UC functions as tools](#uc-functions-as-tools)
  - [SQL functions](#sql-functions)
  - [Python functions](#python-functions)
- [Which tool route for which job](#which-tool-route-for-which-job)
- [MCP on Databricks](#mcp-on-databricks)
  - [MCP concepts, mapped to Databricks](#mcp-concepts-mapped-to-databricks)
  - [Databricks-provided MCPs](#databricks-provided-mcps)
  - [External MCP servers](#external-mcp-servers)
  - [Custom MCP servers](#custom-mcp-servers)
  - [Legacy workspace MCP endpoints](#legacy-workspace-mcp-endpoints)
  - [URLs, authentication and networking](#urls-authentication-and-networking)
- [Using MCP tools from an agent](#using-mcp-tools-from-an-agent)
- [Governing tools](#governing-tools)
- [Choosing a route](#choosing-a-route)
- [Not verified yet](#not-verified-yet)

---

# Abbreviations

| Abbreviation | Full form |
| --- | --- |
| UC | Unity Catalog |
| MCP | Model Context Protocol |
| SDK | Software Development Kit |
| REST | Representational State Transfer |
| OAuth | Open Authorization |
| M2M | Machine-to-Machine |
| PAT | Personal Access Token |
| QPM | Queries Per Minute |
| NCC | Network Connectivity Configuration |
| FQDN | Fully Qualified Domain Name |
| GA | General Availability |
 
> **NOTE**: Release stages, as used in this document:
>
> - **GA**: Fully released and supported for production use
> - **Beta**: Still changing, and may need an admin to enable it first
> - **FQDN**: A complete hostname with every part spelled out
>   > E.g.: `mcp.example.com`

# Tools for agents on Databricks
A tool is something an agent's model can ask the agent to run: a name, a description the model reads to decide when to use it, and an input schema (see ["MCP lifecycle", `mcp.md`](./mcp.md#mcp-lifecycle)). Databricks gives an agent several ways to get tools. They differ in *where the tool lives* and *what governs it*:

| Route | Where the tool lives | How the agent reaches it | Governed by |
| --- | --- | --- | --- |
| Code tool | In the agent's own code (e.g. a Python function wrapped with `@function_tool`) | Called in-process | Nothing on the Databricks side; it is just code |
| UC function | UC (a SQL or Python function, `catalog.schema.function`) | Called directly from Python, e.g. with `UCFunctionToolkit` | UC privileges on the function (`EXECUTE`) |
| MCP service (Unity Gateway) | Behind an MCP server: Databricks-provided, external (registered) or custom | MCP over Streamable HTTP, `https://<workspace>/ai-gateway/mcp-services/...` | UC privileges on the MCP service, plus Unity Gateway controls |
| Custom MCP server on Databricks Apps | Behind a server you host as a Databricks App | MCP over Streamable HTTP, `https://<app-url>/mcp` | `CAN USE` on the app, OAuth |
| Legacy workspace MCP endpoint | UC functions, Genie Agent, SQL, AI Search | MCP, `https://<workspace>/api/2.0/mcp/...` | Permissions on the underlying resource; bypasses Unity Gateway |
| REST API through a UC connection | An external REST API | The connection proxy, with the API's own client SDK | `USE CONNECTION` on the UC HTTP connection |

> **NOTE**: The rest of this document goes through the middle four rows. The first row needs no explanation, and the last one is not MCP (it is mentioned at the end of ["Choosing a route" in this document](#choosing-a-route)).

> **NOTE**: The same tool can sometimes be reached by more than one route. A UC function can be called directly (the "UC function" row), or through the legacy MCP endpoint (the "Legacy workspace MCP endpoint" row). The docs list no Unity Gateway MCP for UC functions.

> **References**:
>
> - [MCP on Databricks, **docs.databricks.com/aws/en/agents/mcp-tools**](https://docs.databricks.com/aws/en/agents/mcp-tools/)
> - [Authentication and networking for MCP, **docs.databricks.com/aws/en/agents/mcp-tools/authentication-networking**](https://docs.databricks.com/aws/en/agents/mcp-tools/authentication-networking)
> - [Call REST APIs from agent code, **docs.databricks.com/aws/en/agents/mcp-tools/rest-api-proxy**](https://docs.databricks.com/aws/en/agents/mcp-tools/rest-api-proxy)

# UC functions as tools
A UC function is a securable (`catalog.schema.function`) that an agent can call as a tool. Use it when the agent "needs to run predefined logic": the logic is fixed and written in advance, and the model only supplies the arguments.

## SQL functions
Use these when the query is known in advance. The descriptions that the model reads are the `COMMENT`s. The function-level `COMMENT` says what the function does and returns, so the agent knows *when* to use it. Each parameter's `COMMENT` says what value to supply.

```sql
CREATE FUNCTION my_catalog.my_schema.lookup_customer_info(
  customer_name_input STRING COMMENT 'Name of the customer whose info to look up'
)
RETURNS STRING
-- + a function-level COMMENT, and the body (a query)
```

> **Source of the example**: "Connect agents to structured data". Test a function with a plain `SELECT` before handing it to an agent.

## Python functions
Created with the `unitycatalog.ai` client, from a Python function with type hints and a docstring:

```python
from unitycatalog.ai.core.databricks import DatabricksFunctionClient
client = DatabricksFunctionClient()
client.create_python_function(func=add_numbers, catalog=CATALOG, schema=SCHEMA)
```

**Giving the agent the functions**: Pass full function names to a toolkit:

> One per framework.

```python
from databricks_langchain import UCFunctionToolkit
toolkit = UCFunctionToolkit(function_names=[f"{CATALOG}.{SCHEMA}.add_numbers"], client=client)
tools = toolkit.tools
```

OpenAI: `unitycatalog.ai.openai.toolkit`; Anthropic: `unitycatalog.ai.anthropic.toolkit`; LlamaIndex: `unitycatalog.ai.llama_index.toolkit`. The tools are the ones in the `function_names` list. **There is no discovery at runtime on this route**; adding a function to the schema does not add it to a running agent.

**What it takes**:

| Need | Detail |
| --- | --- |
| Create | `CREATE FUNCTION` on the schema, plus `USE CATALOG` and `USE SCHEMA` |
| Call | `EXECUTE` on the function, plus `USE CATALOG` and `USE SCHEMA` |
| Compute | Serverless general compute. "A SQL warehouse alone is not sufficient" for the Function Client. Priced as serverless general compute. |
| Python | 3.10 or later (on classic compute, Databricks Runtime 15.0 or later) |

> **NOTE: Local mode**: `DatabricksFunctionClient(execution_mode="local")` fetches a Python function from UC and runs it in a local subprocess. It is for trusted code in development, and does not support SQL functions. Use the default serverless mode in production.

> **References**:
>
> - [Create agent tools using Unity Catalog functions, **docs.databricks.com/aws/en/agents/custom-agents/create-custom-tool**](https://docs.databricks.com/aws/en/agents/custom-agents/create-custom-tool)
> - [Connect agents to structured data, **docs.databricks.com/aws/en/agents/custom-agents/structured-retrieval-tools**](https://docs.databricks.com/aws/en/agents/custom-agents/structured-retrieval-tools)

# Which tool route for which job
UC function tools suit "a predefined query where the agent supplies parameters". For natural-language questions over data, or for arbitrary SQL, the docs point to Genie and the Databricks SQL MCP (see ["Choosing a route" in this document](#choosing-a-route)).


# MCP on Databricks
## MCP concepts, mapped to Databricks
> **NOTE**: The protocol itself is covered in [`mcp.md`](./mcp.md).

This is where each of its parts lands on Databricks:

| MCP | On Databricks |
| --- | --- |
| Host | The agent application: a notebook, a served agent, a Databricks App, or a coding agent (Claude Code, Codex, Cursor) |
| Client | `DatabricksMCPClient`, or the MCP clients of the agent framework you use (see ["Using MCP tools from an agent" in this document](#using-mcp-tools-from-an-agent)). One per server. |
| Server | An MCP service in Unity Gateway (provided or registered), a custom server on Databricks Apps, or a legacy workspace endpoint |
| Transport | Streamable HTTP. Registered external servers must support it, and Apps servers must use it. |
| Discover, then invoke | `list_tools()` (`tools/list`), then `call_tool()` (`tools/call`) |
| Authentication | OAuth (with PATs allowed in some cases; see ["URLs, authentication and networking" in this document](#urls-authentication-and-networking)) |

> **NOTE**: The Databricks pages describe MCP *tools*. They do not say whether Databricks MCP servers expose resources or prompts. See ["Not verified yet" in this document](#not-verified-yet).

There are 3 kinds of MCP server on Databricks.

In the workspace, open **Unity Gateway > MCPs** to see them and register your own:

| Kind | What it is | Hosted by | Covered in |
| --- | --- | --- | --- |
| Databricks-provided | Ready-to-use servers: Genie One, Databricks SQL, GitHub, Slack, and others | Databricks | ["Databricks-provided MCPs" in this document](#databricks-provided-mcps) |
| External | Self-hosted or third-party servers that you register and share with your team | You, or a third party | ["External MCP servers" in this document](#external-mcp-servers) |
| Custom | Servers you build, or HTTP REST APIs you turn into MCP tools with Databricks Apps templates | You, on Databricks Apps | ["Custom MCP servers" in this document](#custom-mcp-servers) |

> **NOTE**: Databricks-provided and registered MCPs use UC permissions. Unity Gateway "control[s] access, manage[s] credentials, and monitor[s] usage". Separate from these 3 kinds are the [legacy workspace endpoints](#legacy-workspace-mcp-endpoints), which are not part of Unity Gateway.

> **References**:
>
> - [MCP on Databricks, **docs.databricks.com/aws/en/agents/mcp-tools**](https://docs.databricks.com/aws/en/agents/mcp-tools/)
> - [`mcp.md`](./mcp.md)

## Databricks-provided MCPs
Provided MCPs:

- Live in the `system.ai` schema
- Are named `system.ai.<name>`

***Nothing needs to be hosted.***

---

**Data and compute**:

| MCP | What it does | Status |
| --- | --- | --- |
| `system.ai.genie_one_mcp` | Natural-language analytics across the workspace, grounded in Genie Ontology | GA |
| `system.ai.dbsql` | Runs specific SQL queries on a SQL warehouse, with the caller's UC and warehouse permissions | Beta (an account admin enables the Unity Gateway beta) |
| `system.ai.web_search` | Searches the public web, returns a synthesised answer with citations. Not available in HIPAA/BAA workspaces. | Beta |
| `system.ai.sandbox` | Runs Python, SQL or shell code in an isolated environment, with no network egress | Beta |

**External services**:

> - Users sign in to their provider account via the login link the MCP returns
> - Some organisations require administrator approval

| MCP | Connects to |
| --- | --- |
| `system.ai.slack` | Slack MCP server |
| `system.ai.github` | GitHub MCP server |
| `system.ai.atlassian` | Jira and Confluence, via the Atlassian Rovo MCP server |
| `system.ai.google_drive` | Google Drive, Docs, Sheets and Slides APIs |
| `system.ai.google_calendar` | Google Calendar API |
| `system.ai.gmail` | Gmail API |
| `system.ai.microsoft_365` | SharePoint, Outlook and Teams, via Microsoft Graph |

> **NOTE: `system.ai.github`**: This MCP server reads public repositories by default. Private repositories and write actions need the Databricks GitHub connector app to be installed by the repository owner or a GitHub organisation administrator.

> **NOTE: Genie One's 5 exposed tools**: Genie One exposes 5 tools: `genie_ask`, `genie_poll_response`, `genie_get_query_result`, `genie_cancel_response`, and `view_ask` (offered to MCP Apps clients instead of `genie_ask`). UC permissions are always enforced, so callers see only data they may access. On-behalf-of-user OAuth with the `ai-gateway` scope is recommended; service principals are supported for automated work.

> **NOTE: To list the MCPs in a schema (Databricks CLI)**: `databricks ai-gateway list-mcp-services --parent schemas/system.ai`. For provided MCPs, a metastore admin first has to grant themselves `MANAGE` on the `system.ai` schema before managing them.

> **NOTE: Entitlements and regional availability**: A workspace may not be able to use everything on this list, because of region, entitlements and previews. The Unity Gateway page in the workspace shows what is available.

> **References**:
>
> - [Databricks-provided MCPs, **docs.databricks.com/aws/en/agents/mcp-tools/built-in-mcp-services**](https://docs.databricks.com/aws/en/agents/mcp-tools/built-in-mcp-services)
> - [Genie One MCP server, **docs.databricks.com/aws/en/agents/mcp-tools/genie-mcp**](https://docs.databricks.com/aws/en/agents/mcp-tools/genie-mcp)

## External MCP servers
An external MCP server is one that is not hosted by Databricks and not built as a Databricks App (self-hosted or third-party). You register it, and from then on it is a UC object: an *MCP service* named `<catalog>.<schema>.<service>`, with UC privileges, a tool selection, and the gateway controls.

---

**Requirements**:

- The server supports Streamable HTTP
  > And you have its URL and authentication details.
- The workspace can reach the server over the network
  > See ["URLs, authentication and networking" in this document](#urls-authentication-and-networking).
- `USE CATALOG`, `USE SCHEMA` and `CREATE SERVICE` on the parent schema
- Either one or both of the following:
  - `CREATE CONNECTION` on the schema (to create a connection)
  - `USE CONNECTION` on an existing one
- The "Workspace access" entitlement
  > A user with only "Consumer access" cannot register an MCP.

**Registration** (UI):

1. **Unity Gateway > MCPs > + MCP > Connect an existing MCP server**
2. Choose the catalog and schema; enter the MCP name
3. Select or create a UC *HTTP connection*
    > Server URL + an authentication method
4. Then **Create & load tools**
5. Sign in to the provider if prompted; choose the tools to expose
6. **Create MCP Service**

> **NOTE: What registration does**: the MCP service *wraps* a UC HTTP connection. The connection holds the server's address and credentials, and the service adds the tool selection and the governance on top. This is why `USE CONNECTION` is held back from end users (see ["Governing tools" in this document](#governing-tools)).

> **NOTE**: Limits:
>
> - The MCP name cannot be changed after creation
> - Genie, Databricks Apps, UC entity sources: cannot be registered as your own MCP
> - Registering by SQL (`CREATE MCP SERVICE`) is not supported
> - UC Global Search does not surface MCPs
> - New MCPs should use a schema-level connection
>   > Old MCPs may have used metastore-level connection; supported for legacy.

> **Reference**: [Register an external MCP server, **docs.databricks.com/aws/en/ai-gateway/register-mcp-service**](https://docs.databricks.com/aws/en/ai-gateway/register-mcp-service)

## Custom MCP servers
A custom MCP server is one you write, and host as a Databricks App. Use it when no provided MCP offers the tools you need, and you want the server (and its network position) inside Databricks.

**Requirements**:

| Item | Requirement |
| --- | --- |
| App name | Starts with `mcp-` (e.g. `mcp-my-server`). The prefix lets AI Playground recognise the server. |
| Transport | Streamable HTTP |
| Host and port | Bind to `0.0.0.0`; read the port from `DATABRICKS_APP_PORT` (default `8000` when unset) |
| Path | An MCP path such as `/mcp` (the Starter and OpenAPI templates use `/mcp`) |
| Files | `requirements.txt` (Python) or `package.json` (Node.js), and an `app.yaml` with the start command, e.g. `command: ['python', 'server.py']` |
| Callers | `CAN USE` on the app |

Start from the Starter template, or turn an existing HTTP REST API into MCP tools with the OpenAPI or REST API template. (For the REST API template, each caller also needs `USE CONNECTION` on the HTTP connection.) To add one: **Unity Gateway > MCPs > + MCP > Build a new MCP server**. The server's URL is the app URL (on the app's **Overview** page) + the MCP path, e.g. `https://<app-url>/mcp`. Coding agents connect with `ug mcp add --names "app:mcp-my-server"`; Python agents with the app URL (see ["Using MCP tools from an agent" in this document](#using-mcp-tools-from-an-agent))

> **NOTE: OAuth for Apps-hosted MCP servers**: Apps-hosted MCP servers require OAuth. "Servers hosted on Databricks Apps ... do not accept personal access tokens."

> **NOTE: Gateway-level controls**: Whether the gateway-level controls (service policies, rate limits, the gateway usage table) apply to an Apps-hosted server is not stated in the pages used here. The access control they show is `CAN USE` on the app. See ["Not verified yet" in this document](#not-verified-yet).

> **References**:
>
> - [Custom MCP servers, **docs.databricks.com/aws/en/agents/mcp-tools/custom-mcp**](https://docs.databricks.com/aws/en/agents/mcp-tools/custom-mcp)
> - [Authentication and networking for MCP, **docs.databricks.com/aws/en/agents/mcp-tools/authentication-networking**](https://docs.databricks.com/aws/en/agents/mcp-tools/authentication-networking)

## Legacy workspace MCP endpoints
Before MCPs were services in Unity Gateway, Databricks offered *managed MCP servers* at workspace endpoints. These still exist.

| Server | URL | OAuth scope |
| --- | --- | --- |
| UC functions | `https://<workspace>/api/2.0/mcp/functions/{catalog}/{schema}/{function_name}` | `unity-catalog` |
| Databricks SQL | `https://<workspace>/api/2.0/mcp/sql` | `sql` |
| AI Search (Vector Search) | `https://<workspace>/api/2.0/mcp/ai-search/{catalog}/{schema}/{index_name}` | `ai-search` |
| Genie Agent (one curated Genie Agent) | `https://<workspace>/api/2.0/mcp/genie/{genie_space_id}` | `genie` |

A workspace administrator must enable **Managed MCP Servers** on the workspace Previews page. These endpoints **bypass Unity Gateway**: their calls do not appear in Unity Gateway tracing tables, and MCP-level grants, policies and guardrails do not apply. Access is controlled by the permissions on the underlying resource (the function, the warehouse, the Genie Agent and its data). The docs recommend `system.ai` MCPs for new connections. Where there is a replacement:

  | Legacy | Recommended instead |
  | --- | --- |
  | UC functions MCP | `UCFunctionToolkit` (calls the functions directly from Python); `system.ai.sandbox` for the code interpreter |
  | Databricks SQL (`/api/2.0/mcp/sql`) | `system.ai.dbsql` (needs the Unity Gateway beta) |
  | AI Search MCP | AI Bridge retriever tools |
  | Genie (workspace-wide questions) | `system.ai.genie_one_mcp` |

> **NOTE**: Genie Agent MCP: read-only, does not pass conversation history to the Genie API, billed at Databricks SQL pricing. Each Genie Agent covers up to 50 UC tables, views or metric views. From Python, the docs also show Genie as an AI Bridge tool (`GenieAgent`, `Genie`).

> **NOTE**: The Genie One page says the older Beta endpoint `/api/2.0/mcp/genie` is deprecated and will be sunset on October 31, 2026. The Genie Agent page still shows `/api/2.0/mcp/genie/{genie_space_id}`. The pages do not say whether the sunset affects it, so check before relying on it.

> **References**:
>
> - [Databricks-provided MCPs, **docs.databricks.com/aws/en/agents/mcp-tools/built-in-mcp-services**](https://docs.databricks.com/aws/en/agents/mcp-tools/built-in-mcp-services)
> - [Managed MCP servers, **docs.databricks.com/aws/en/agents/mcp-tools/managed-mcp**](https://docs.databricks.com/aws/en/agents/mcp-tools/managed-mcp)
> - [Genie Agent MCP server, **docs.databricks.com/aws/en/agents/mcp-tools/genie-agent**](https://docs.databricks.com/aws/en/agents/mcp-tools/genie-agent)

## URLs, authentication and networking

**URLs**:

| Target | URL |
| --- | --- |
| Provided or registered MCP | `https://<workspace>/ai-gateway/mcp-services/<catalog>.<schema>.<service>` (e.g. `.../system.ai.genie_one_mcp`) |
| Custom server on Databricks Apps | `https://<app-url>/mcp` |
| Legacy workspace endpoint | See [Legacy workspace MCP endpoints](#legacy-workspace-mcp-endpoints) |

**Authentication**:

| Question | Answer |
| --- | --- |
| Who is the caller? | A user (interactive work), or a service principal with OAuth M2M (unattended agents) |
| Scopes | `ai-gateway` for provided and registered MCPs; the app's user authorisation scopes for Apps servers; the server's own scope for legacy endpoints |
| PATs | Allowed for local testing, for provided and registered MCPs, and for legacy endpoints. Not for Apps servers. |
| Refresh tokens | Request the server's scope and `offline_access` |
| Client registration | "Databricks MCP endpoints don't support dynamic client registration": a client has to use a preconfigured client ID. Changes can take up to 30 minutes to take effect. |
| On deployment | An agent can call as its own service principal (shared access) or as the calling user (per-user access) |

**Networking**:

| Connection | Description |
| --- | --- |
| Client to workspace | If IP access lists are on, allow the client's public outbound IP. Browser sign-in and MCP calls can come from different networks, so allow both. |
| Workspace to an external server | Calls through Unity Gateway use the serverless compute plane. With a Restricted network policy, add the server's FQDN to **Allowed domains**: a UC connection does not allow its destination automatically. |
| Servers inside your cloud network | Use a private endpoint rule in an NCC. For public servers, allow Databricks serverless outbound IPs on the server's firewall, and keep authentication on. |

> **References**:
>
> - [Authentication and networking for MCP, **docs.databricks.com/aws/en/agents/mcp-tools/authentication-networking**](https://docs.databricks.com/aws/en/agents/mcp-tools/authentication-networking)

# Using MCP tools from an agent
The Python client is `DatabricksMCPClient`, from the `databricks-mcp` package. It is the MCP client of the architecture above, one per server.

```python
# pip install --upgrade databricks-mcp databricks-sdk "mcp>=1.24,<2"   (Python 3.12)
from databricks.sdk import WorkspaceClient
from databricks_mcp import DatabricksMCPClient

w = WorkspaceClient()
mcp_client = DatabricksMCPClient(server_url=SERVER_URL, workspace_client=w)

tools = mcp_client.list_tools()            # discovery  (tools/list): name, description, inputSchema
result = mcp_client.call_tool(name, args)  # invocation (tools/call): args is a dict
```

**Handling a result**:

- If `structuredContent` is present, use it directly
- Otherwise, read the `content` blocks.
  > Parse text as JSON only if the tool returns JSON.
- Check `isError` before relying on the output

**With an agent framework** (each wraps the same discover and invoke steps):

| Framework | Packages | MCP pieces |
| --- | --- | --- |
| LangGraph | `databricks-langchain`, `langgraph` | `DatabricksMultiServerMCPClient`, `DatabricksMCPServer`, `create_react_agent` |
| OpenAI Agents SDK | `databricks-openai`, `openai-agents` | `McpServer` with `AsyncDatabricksOpenAI` |
| OpenAI client | `databricks-openai` | `McpServerToolkit` with `DatabricksOpenAI`; you run the tool-calling loop yourself |

> **NOTE: Tool-calling model**: The tool-calling model can be any tool-calling endpoint. The docs' examples use a legacy `databricks-*` serving endpoint name; with Unity Gateway, use a model service (see `ai-models-on-databricks.md`).

> **NOTE: Tool discovery**: Because discovery happens at runtime, the model sees the *current* `tools/list`. For a registered MCP that includes the effect of tool selection: unselected tools are not listed (see ["Governing tools" in this document](#governing-tools)).

> **Reference**: [Use MCP tools in a Python agent, **docs.databricks.com/aws/en/agents/custom-agents/use-mcp-tools**](https://docs.databricks.com/aws/en/agents/custom-agents/use-mcp-tools)

# Governing tools
Governance depends on the route. For MCP services in Unity Gateway:

**Privileges**:

| Action | Needs |
| --- | --- |
| Call an MCP | `EXECUTE` on the MCP, `USE CATALOG` and `USE SCHEMA` on its parents, and workspace assignment. The tool may also need access to its own data or resources. |
| Create (register) an MCP | `CREATE SERVICE` on the schema, and a connection privilege (see [External MCP servers](#external-mcp-servers)) |
| Update, delete, attach a policy | Ownership or `MANAGE` on the MCP, plus `USE CATALOG` and `USE SCHEMA` |
| `USE CONNECTION` | MCP authors and administrators only. It permits using the connection directly, outside the MCP's tool selection and policies, so end users should not hold it. |

**Controls** (all in Unity Gateway; none live in the agent's code):

| Control | What it does |
| --- | --- |
| Tool selection | A registered MCP exposes all the server's tools by default. Select tools by exact name or prefix (`get_*`). Exclusion patterns (`!delete_*`) are not supported. Unselected tools are absent from `tools/list`, and calls to them are refused ("Tool not allowed by MCP service configuration"). Stored in `config.include_tool_selectors`; an empty list exposes all tools. |
| Service policies (Beta) | Run `ON CALL` and `ON RESULT`; allow, block or require approval. Built-in *Sensitive Data Detection* blocks classification tags (e.g. `class.us_ssn`, `class.credit_card`) on input and output. A custom SQL function can deny a tool for a given agent's OAuth client ID (the tool still shows in `tools/list`). Partner guardrails fail closed. Needs the **Unity Ai Gateway Service Policies** preview. |
| Rate limits | In QPM, applied to `tools/call`. Over the limit returns HTTP 429. |
| Usage | Query `system.ai_gateway.usage` where `service_type = 'MCP_SERVICE'` (columns include `service_name`, `mcp_metadata.tool_name`). A built-in dashboard shows call volume, errors and latency. Trace tables (tool requests, responses, policy decisions) can be enabled by an admin. |
| Audit | MCP changes and invocations (`mcpCall`) appear in `system.access.audit` |

**What each route gives you**:

| Route | Access control | Policies / rate limits | Usage in gateway tables |
| --- | --- | --- | --- |
| UC function (direct) | `EXECUTE` on the function | Not an MCP service, so these do not apply | Not an MCP service |
| Provided or registered MCP | `EXECUTE` on the MCP + tool selection | Yes | Yes |
| Custom server on Apps | `CAN USE` on the app, OAuth | Not stated | Not stated |
| Legacy workspace endpoint | Permissions on the underlying resource | No (bypasses the gateway) | No (stated by the docs) |

> **NOTE**: Governing an agent, in practice, is governing the calls it makes (see "Governance for AI on Databricks" in `ai-models-on-databricks.md`). The agent's tool calls are the MCP services above; its LLM calls go through a model service. Service policies do not apply to agent services themselves.

> **References**:
>
> - [Govern an MCP, **docs.databricks.com/aws/en/ai-gateway/govern-mcp-service**](https://docs.databricks.com/aws/en/ai-gateway/govern-mcp-service)
> - [Service policies for AI securables, **docs.databricks.com/aws/en/data-governance/unity-catalog/service-policies**](https://docs.databricks.com/aws/en/data-governance/unity-catalog/service-policies/)
> - [Databricks-provided MCPs, **docs.databricks.com/aws/en/agents/mcp-tools/built-in-mcp-services**](https://docs.databricks.com/aws/en/agents/mcp-tools/built-in-mcp-services)

# Choosing a route
From the docs' own recommendations:

| The agent needs to... | Use |
| --- | --- |
| Answer natural-language business questions over the workspace's data | `system.ai.genie_one_mcp` |
| Run specific SQL, for development or data engineering | `system.ai.dbsql` (Beta) |
| Run a predefined query or piece of logic, where the model only supplies parameters | A UC function (SQL or Python), via `UCFunctionToolkit` |
| Query one curated Genie Agent | Genie as an AI Bridge tool from Python, or the Genie Agent MCP (legacy endpoint) |
| Run code in isolation | `system.ai.sandbox` (Beta) |
| Search the web | `system.ai.web_search` (Beta) |
| Use Slack, GitHub, Jira/Confluence, Google, or Microsoft 365 | The matching `system.ai.*` MCP |
| Use a third-party or self-hosted MCP server | Register it as an external MCP |
| Expose your own tools, or wrap your own REST API, as MCP | A custom MCP server on Databricks Apps |
| Call a REST API with its own client SDK, without handling its credentials | The UC connections proxy (not MCP; needs `USE CONNECTION`) |

> **NOTE**: UC function tools vs. MCP: a UC function is called directly, and it is a fixed list the agent was built with. An MCP is discovered at runtime, and is governed at the gateway. Neither replaces the other.

> **References**:
>
> - [MCP on Databricks, **docs.databricks.com/aws/en/agents/mcp-tools**](https://docs.databricks.com/aws/en/agents/mcp-tools/)
> - [Connect agents to structured data, **docs.databricks.com/aws/en/agents/custom-agents/structured-retrieval-tools**](https://docs.databricks.com/aws/en/agents/custom-agents/structured-retrieval-tools)
> - [Call REST APIs from agent code, **docs.databricks.com/aws/en/agents/mcp-tools/rest-api-proxy**](https://docs.databricks.com/aws/en/agents/mcp-tools/rest-api-proxy)

# Not verified yet
Things the pages used for this document do not settle. Each should be checked in a workspace, or in other docs, before it is stated in a demo:

| Question | Why it matters |
| --- | --- |
| Which MCP spec revision do Databricks servers implement? | `mcp.md` covers 2026-07-28 (no `initialize`, no sessions, `server/discover`). The Databricks pages do not say which revision is implemented. |
| Does MLflow trace each MCP tool call as a span? | `mcp.md` says so. The Databricks pages used here do not mention it. |
| Do Databricks MCP servers expose resources and prompts, or only tools? | The Databricks pages describe tools only. |
| Do gateway policies, rate limits and usage tracking cover an Apps-hosted MCP server? | The custom-server page shows `CAN USE` on the app, and the registration page says Apps cannot be registered as your own MCP. |
| Does the legacy UC functions endpoint expose a whole schema, or one function per URL? | The URL pattern has a function name. `mcp.md` says new UC functions are discovered without redeployment. |
| Does the Genie Agent MCP endpoint survive the October 31, 2026 sunset of the older Genie endpoint? | See [Legacy workspace MCP endpoints](#legacy-workspace-mcp-endpoints). |
| Which previews does the workspace have: Managed MCP Servers, Unity Gateway beta, Service Policies? | They decide which routes can be demonstrated live. |