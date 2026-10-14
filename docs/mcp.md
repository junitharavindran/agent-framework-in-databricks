<h1>MCP</h1>

> Model Context Protocol.

---

**Contents**:

- [Key abbreviations](#key-abbreviations)
- [About](#about)
- [Architecture](#architecture)
  - [Core architecture](#core-architecture)
  - [MCP's scope](#mcps-scope)
  - [MCP's protocol layers](#mcps-protocol-layers)
  - [MCP's statelessness](#mcps-statelessness)
  - [MCP's primitives](#mcps-primitives)
- [MCP lifecycle](#mcp-lifecycle)

---

# Key abbreviations

| Abbreviation | Full form |
| --- | --- |
| UC | Unity Catalog |
| MCP | Model Context Protocol |
| SDK | Software Development Kit |
| IDE | Integrated Development Environment |

# About
MCP =>

- Model => <br> An application/engine, typically an AI application/reasoning engine
- Context => <br> Data and information that the model can benefit from using
- Protocol => <br> Standard procedure for regulating context requests and transmission

Now, from [Specification, **modelcontextprotocol.io/specification/2026-07-28**](https://modelcontextprotocol.io/specification/2026-07-28):

> "Model Context Protocol (MCP) is an open protocol that enables seamless integration between LLM applications and external data sources and tools. Whether you're building an AI-powered IDE, enhancing a chat interface, or creating custom AI workflows, MCP provides a standardized way to connect LLMs with the context they need."

In other words, MCP is a protocol defined for the use of AI models (originally intended to be LLMs) and the server(s) supporting them, in order for them to request and receive the required context from the server(s) as well as make required tool calls to the server(s) that host these tools (via a JSON-RPC-based protocol; see: ["MCP's protocol layers" in this document](#mcps-protocol-layers)) and receive the tool call responses from the server(s). It standardises the procedure of requesting for context from a remote source and reading the context received from that remote source (here, "context" also refers to the results of tool calls); hence, the MCP protocol handles discovery, invocation, and response formatting. A Databricks-native use-case is shown below in abstract (the terms shall become clearer later):

```
     |-(user query)--->| Databricks:
User |                 |    - Agent (MCP client)
     |<-----(response)-|    - MCP servers
```

> **NOTE**: Tools are discovered at runtime, not hardcoded. If a new UC function is registered on the MCP server, connected agents can discover and use it without redeployment. In a Databricks context, when MLflow Tracing is active, every MCP tool call is captured as a span within the trace.

The relationship between the MCP client and servers shall become clearer. For now, know that the agent, as an MCP client, discovers and calls tools over MCP, making tool discovery/call requests to the MCP servers (which can be applications such as Genie or AI search), which respond back to the agent (i.e. the MCP client) with the requested context (if available).

# Architecture
## Core architecture
MCP follows a client-server architecture where an MCP host (an AI application) establishes connections to 1+ MCP servers. The MCP host accomplishes this by creating 1 MCP client for each MCP server. Each MCP client maintains a dedicated connection with its corresponding MCP server. E.g.:

![](/_common-resources/mcp-architecture-abstract-example.png)

> **Source**: [Architecture, **modelcontextprotocol.io/docs/2026-07-28/learn/architecture**](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)

> **NOTE**: A single host can connect to multiple servers simultaneously, each through its own client instance. This lets an agent access tools from UC functions, external APIs, and custom services all through the same protocol.

The key participants in the MCP architecture are:

- **MCP host**: <br> The AI application that coordinates and manages one or multiple MCP clients
- **MCP client**: <br> A component that:
  - Maintains a connection to an MCP server
  - Obtains context from an MCP server for the MCP host to use
- **MCP server**: <br> A program that responds to MCP clients' requests

> **Reference**: [Architecture, **modelcontextprotocol.io/docs/2026-07-28/learn/architecture**](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)

## MCP's scope
MCP has the following projects built for it/from it:

- **MCP specification**:
    > See: [Specification, **modelcontextprotocol.io/specification/2026-07-28**](https://modelcontextprotocol.io/specification/2026-07-28)
  - The specification of MCP
  - Outlines the implementation requirements for clients and servers
- **MCP SDKs**: <br> SDKs for different programming languages that implement MCP
    > See: [SDK, **modelcontextprotocol.io/docs/2026-07-28/sdk**](https://modelcontextprotocol.io/docs/2026-07-28/sdk)
- **MCP development tools**: <br> Tools for developing MCP servers and clients
- **MCP reference server implementations**

> **Reference**: [Architecture, **modelcontextprotocol.io/docs/2026-07-28/learn/architecture**](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)

## MCP's protocol layers
MCP is actually 2 related protocols merged into a single standard:

1. **Data layer**
    > To specify the format and options for the data exchange.
  - Based on JSON-RPC (see: https://www.jsonrpc.org/)
2. **Transport layer**
    > To specify the procedures to establish and maintain client-server connection.
  - 2 mechanisms:
    - STDIO transport
      > Data exchange through standard I/O streams.
    - Streamable HTTP transport

> **KEY POINT**: The transport layer abstracts communication details from the data layer. This enables the same JSON-RPC 2.0 message format across all transport mechanisms.

> **Reference**: [Architecture, **modelcontextprotocol.io/docs/2026-07-28/learn/architecture**](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)

> **[UPDATE]**: In the 2026-07-28 revision of the specification:
>
> - The HTTP+SSE transport is reclassified as Deprecated; the migration path is Streamable HTTP
> - SSE stream resumability and message redelivery (i.e. the `Last-Event-ID` header and SSE event IDs) are removed from the Streamable HTTP transport; a broken response stream loses the in-flight request, which the client must re-issue as a new request with a new request ID
> - The standard request headers `Mcp-Method` and `Mcp-Name` are required on Streamable HTTP POST requests
>
> **Reference**: [Key Changes, **modelcontextprotocol.io/specification/2026-07-28/changelog**](https://modelcontextprotocol.io/specification/2026-07-28/changelog)

## MCP's statelessness
> "MCP is a stateless protocol. Every request carries the protocol version and the capabilities relevant to that request in its `_meta` field, so the server can process each request on its own. Clients should also identify themselves in the same field unless configured not to. Servers advertise their supported versions and capabilities through the mandatory server/discover request, which clients may send before any other request."
> 
> **Reference**: ["Statelessness and discovery", Architecture, **modelcontextprotocol.io/docs/2026-07-28/learn/architecture**](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture#statelessness-and-discovery)

> **[UPDATE]**: To clarify the above, as per the 2026-07-28 revision of the specification:
>
> - Servers MUST implement `server/discover`, whereas clients MAY call it before any other request (e.g. for up-front version selection, or as a backward-compatibility probe over STDIO)
> - Calling `server/discover` is therefore optional for a client: since every request carries the same `_meta` fields, a client can send any request directly and handle a version error if one comes back
> - The `initialize`/`notifications/initialized` handshake and the `Mcp-Session-Id` header (i.e. protocol-level sessions) are removed in this revision
> - A version mismatch returns an `UnsupportedProtocolVersionError`
> - Servers that need state across calls use explicit, server-minted handles passed as ordinary tool arguments
>
> **References**:
> 
> - [Key Changes, **modelcontextprotocol.io/specification/2026-07-28/changelog**](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
> - ["Statelessness and discovery", Architecture overview, **modelcontextprotocol.io/docs/2026-07-28/learn/architecture**](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture#statelessness-and-discovery)

## MCP's primitives
> **NOTE**: Primitive => Pre-defined types (i.e. data interfaces) that are available directly (as opposed to composite types built from objects of other types).

MCP primitives are the most important concept within MCP. They define what clients and servers can offer each other. ***These primitives specify the types of contextual information that can be shared with AI applications and the range of actions that can be performed***. MCP defines 3 core primitives that servers can expose:

1. **Tools**: <br> Executable functions that AI applications can invoke to perform actions
    > E.g.: File operations, API calls, database queries.
2. **Resources**: <br> Data sources that provide contextual information to AI applications
    > E.g.: File contents, database records, API responses.
3. **Prompts**: <br> Reusable templates that help structure interactions with language models
    > E.g.: System prompts, few-shot examples.

Each primitive type has associated methods for:

- Discovery (`*/list`)
- Retrieval (`*/get`)
- Execution (in some cases) (`tools/call`)

MCP clients will use the `*/list` methods to discover available primitives. For example, a client can first list all available tools (`tools/list`) and then execute them. ***This design allows listings to be dynamic.*** As a concrete example, consider an MCP server that provides context about a database. It can expose tools for querying the database, a resource that contains the schema of the database, and a prompt that includes few-shot examples for interacting with the tools.

---

MCP also defines primitives that clients can expose.

> These primitives allow MCP server authors to build richer interactions.

**Elicitation**: Allows servers to request additional information from users. This is useful when server authors want to get more information from the user, or ask for confirmation of an action. Servers request user input with the elicitation/create method.

> **NOTE**: I guess this is the only client-exposed primitive that is not deprecated; sampling and logging are deprecated client-exposed primitives.

> **Reference**: ["Primitives", Architecture, **modelcontextprotocol.io/docs/2026-07-28/learn/architecture**](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture#primitives)

> **[UPDATE]**: As per the 2026-07-28 revision of the specification:
>
> - The architecture overview lists elicitation as the client feature, with Sampling and Logging marked as deprecated client primitives (consistent with the note above); the changelog additionally deprecates Roots
> - Deprecated features remain functional during the deprecation window, but new implementations should not adopt them; the suggested migrations are: pass directories/files via tool parameters, resource URIs or server configuration (instead of Roots), integrate directly with LLM provider APIs (instead of Sampling), and log to `stderr` (stdio) or use OpenTelemetry (instead of Logging)
> - Server-initiated requests such as `roots/list`, `sampling/createMessage` and `elicitation/create` are replaced by the Multi Round-Trip Requests (MRTR) pattern: the server returns an `InputRequiredResult` (`resultType: "input_required"`) whose `inputRequests` field carries what it needs, and the client retries the original request with `inputResponses`
> - Elicitation requests are delivered through the MRTR pattern
>
> **References**:
> 
> - [Key Changes, **modelcontextprotocol.io/specification/2026-07-28/changelog**](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
> - ["Primitives", Architecture overview, **modelcontextprotocol.io/docs/2026-07-28/learn/architecture**](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture#primitives)

---

Hence, note...

> **KEY POINT**: MCP provides a standardised way for AI applications to DISCOVER AND INVOKE tools, resources, and prompts defined externally from the parametric memory of the AI models.

# MCP lifecycle
> Focusing on tool-based usage; usage for resources and prompts is similar.

```
Initialise | capability handshake
|
v
Discover   | via tools/list  | This is where:
|                            | - Tools are discovered
v                            | - Tools are called
Invoke     | via tools/call  | - Result/context is acquired
|
v
Shutdown   | close connection
```

**Initialisation**:

The client sends an initialize request declaring its protocol version and capabilities. The server responds with its own capabilities. The client then sends an initialized notification to confirm readiness before normal message exchange begins.

> **[UPDATE]**: The handshake described above belongs to the previous revision of the specification (2025-11-25). In the 2026-07-28 revision, the `initialize`/`notifications/initialized` exchange is removed. Instead, every request carries its protocol version and client capabilities in `_meta` (`io.modelcontextprotocol/protocolVersion` and `io.modelcontextprotocol/clientCapabilities`), and clients should also identify themselves via `io.modelcontextprotocol/clientInfo`. A client that wants to learn a server's capabilities up front can call `server/discover`, which is optional for the client (see: ["MCP's statelessness" in this document](#mcps-statelessness)).
>
> **References**:
> 
> - [Key Changes, **modelcontextprotocol.io/specification/2026-07-28/changelog**](https://modelcontextprotocol.io/specification/2026-07-28/changelog)
> - ["Statelessness and discovery", Architecture overview, **modelcontextprotocol.io/docs/2026-07-28/learn/architecture**](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture#statelessness-and-discovery)

**Tool discovery**:

The client sends a `tools/list` request. The server returns all available tools with their names, descriptions, and input schemas. The agent uses these descriptions to decide when to call each tool in the tool invocation step described below.

> **[UPDATE]**: In the 2026-07-28 revision of the specification:
>
> - `tools/list` results must carry the `ttlMs` field (a freshness hint in milliseconds) and the `cacheScope` field (`"public"` or `"private"`), so that clients can cache responses
> - All results carry a required `resultType` field (`"complete"` for ordinary results)
> - Servers should return tools from `tools/list` in a deterministic order, to enable client-side caching and improve LLM prompt cache hit rates
>
> **Reference**: [Key Changes, **modelcontextprotocol.io/specification/2026-07-28/changelog**](https://modelcontextprotocol.io/specification/2026-07-28/changelog)

**Tool invocation**:

When the agent decides to use a tool, the client sends a `tools/call` request with the tool name and arguments. The server executes the function and returns the result. The client does not need to know anything about the function except what it does and how to identify it (both of which are information obtained during tool discovery).

**Shutdown**:

Either side can close the connection gracefully.