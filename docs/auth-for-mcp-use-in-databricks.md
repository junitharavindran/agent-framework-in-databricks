<h1>Auth for MCP Use in Databricks</h1>

---

**Contents**:

- [What is authentication and authorisation (auth)?](#what-is-authentication-and-authorisation-auth)
- [OAuth 2.0](#oauth-20)
  - [Motivating problem and key ideas](#motivating-problem-and-key-ideas)
  - [Components](#components)
  - [Tokens and values](#tokens-and-values)
  - [The flow in five steps](#the-flow-in-five-steps)
- [MCP servers in Databricks and auth](#mcp-servers-in-databricks-and-auth)
  - [How MCP uses OAuth](#how-mcp-uses-oauth)
  - [Databricks MCP endpoints](#databricks-mcp-endpoints)
  - [Auth methods in Databricks](#auth-methods-in-databricks)
  - [Setting up OAuth for an MCP client](#setting-up-oauth-for-an-mcp-client)
  - [User vs machine access](#user-vs-machine-access)
- [References](#references)

---

# What is authentication and authorisation (auth)?
Authentication is the process of confirming the identity of a user, device, or system by validating provided credentials before granting access to a network or its resources. Authorisation is the process of confirming the resource-related permissions of an authenticated user, device, or system.

OAuth handles **authorisation**. Identity ("who is this?") comes from a layer on top, OpenID Connect. [1][2]

# OAuth 2.0
OAuth 2.0 is the industry-standard protocol for authorisation. [1] Current security guidance is in RFC 9700. [3] OAuth 2.1, which consolidates that guidance, is still an Internet-Draft. [4]

## Motivating problem and key ideas
You want to let an app use your data on another service without giving the app your password. Instead of your password, the app gets a limited-use key, called a token. The token says what the app can do, for how long, and on whose behalf. You can revoke it without changing your password. Here are the players:

1. The owner of the data
2. The app (wants access)
3. The login service
   1. Checks who the owner is
   2. Asks owner's permission
   3. Hands out tokens to app(s)
4. The data service (holds owner's data and accepts tokens)

> **NOTE**: Often, login service and data service are the same company but separate roles.

## Components

| Plain term | Technical name | What it is in practice |
|---|---|---|
| The owner | **Resource owner** | The user, in a browser |
| The app | **Client** | A web app, mobile app, or backend service |
| The login service | **Authorization server (AS)** | A server that authenticates users, collects consent, and issues tokens |
| The data service | **Resource server (RS)** | Owner's API, which accepts tokens |

## Tokens and values

| Plain term | Technical name |
|---|---|
| One-time code | **Authorization code** |
| Limited-use key | **Access token** (usually a signed JWT (JSON Web Token) [5]) |
| Quiet renewal ticket | **Refresh token** |
| One-time proof the same app finished the login | **PKCE** (Proof Key for Code Exchange) (`code_verifier` / `code_challenge`) [6] |
| Permissions | **Scopes** |
| Return address | **Redirect URI** |

## The flow in five steps

1. The app sends you to the login service: "this app wants permission X" (plus the PKCE challenge).
2. You log in and approve.
3. The login service sends you back to the app's redirect URI with a short-lived one-time code.
4. The app swaps the code (plus the PKCE verifier) for tokens, directly with the login service.
5. The app calls the data service with the access token. When it expires, the app uses the refresh token to get a new one.

The code step exists so the access token never passes through the browser, where it could leak. [3]

# MCP servers in Databricks and auth

## How MCP uses OAuth

MCP (Model Context Protocol) is how AI apps call tools on remote servers. Its authorisation spec reuses OAuth rather than inventing something new. [7]

| OAuth role | MCP role |
|---|---|
| Client | The MCP client (e.g. Claude, Claude Code, Cursor, ChatGPT) [7] |
| Resource server | The MCP server (it accepts access tokens) [7] |
| Authorization server | Whoever issues tokens. It may be hosted with the MCP server or be a separate entity. [7] |

Key rules from the spec:

- Authorisation is optional, and applies to HTTP-based transports. Local (STDIO) servers should instead take credentials from the environment. [7]
- An MCP server must publish **Protected Resource Metadata** (RFC 9728), which tells clients which authorisation server to use. [7][8] A server also returns this location when it answers a request with `401 Unauthorized`. [8]
- Clients find the authorisation server's endpoints through its metadata (RFC 8414). [7]
- Clients must send a `resource` parameter (RFC 8707) naming the MCP server the token is for, and servers must check that tokens were issued for them. [7][9]
- Tokens are sent as `Authorization: Bearer <access-token>`. [7]
- Before starting the flow, a client needs a client ID. Options are pre-registration, Client ID Metadata Documents, or Dynamic Client Registration (now deprecated, kept for backwards compatibility). [7]

## Databricks MCP endpoints

A client is given a Databricks MCP server URL, authenticates, and calls tools over Streamable HTTP. There are three endpoint types: [10]

1. **Managed MCP servers**: Databricks data and code (e.g. Genie, Unity Catalog).
2. **MCP Services**: third-party tools such as GitHub and Slack.
3. **Databricks-hosted MCP servers**: your own MCP server running on Databricks Apps.

## Auth methods in Databricks

| Method | Managed MCP and MCP Services | Databricks-hosted | When to use |
|---|---|---|---|
| **OAuth** (recommended) | Supported | Supported | Production, teams, long-term access. Scoped permissions and automatic token refresh. |
| **Personal access token** | Supported | Not supported | Individual development, testing, short-term access |

Source: [10]. There is also a no-OAuth-app route for developers: the Databricks CLI login can be reused through a small proxy (`uc-mcp-proxy`) or `ucode` (for OpenAI Codex), so you don't create an OAuth app, client ID, or secret. [10][11]

## Setting up OAuth for an MCP client

1. **An account admin creates a Databricks OAuth application**, either in the Account Console or with the CLI (`databricks account custom-app-integration create`). Retrieve its client ID, and the client secret if your client needs one. [11]
2. **Choose client type.** Databricks supports both public clients (no secret) and confidential clients (with secret), as in the MCP spec. [10]
3. **Set the redirect URL** to your MCP client's callback. For example, Claude uses `https://claude.ai/api/mcp/auth_callback` and `https://claude.com/api/mcp/auth_callback`, Claude Code uses a local `http://localhost:<port>/callback`, and ChatGPT uses `https://chatgpt.com/connector_platform_oauth_redirect`. [10][11]
4. **Configure the client** with the server URL and the OAuth client ID (and secret if confidential). [10]
5. **Allow the client's network access** if your workspace has IP access lists, otherwise authentication requests are blocked. [11]

A third-party gateway vendor notes that Databricks doesn't support Dynamic Client Registration, which is why an admin must pre-register the OAuth app. [12] I haven't confirmed this in Databricks' own docs, so check before relying on it.

## User vs machine access

Databricks has two OAuth modes in general: [13][14]

| Mode | Use | Who is authenticated |
|---|---|---|
| **U2M** (user-to-machine) | A person signs in through a browser. It works only with locally run apps, not server or cloud apps. [13] | A Databricks user |
| **M2M** (machine-to-machine) | Unattended jobs and services, using client credentials | A **service principal** (a non-human identity) with an OAuth secret [13][14] |

OAuth tokens have a default lifetime of 1 hour, and U2M refreshes them automatically. [14]

The MCP client docs above describe the user-facing flow. For unattended agents, the service principal route is the general Databricks pattern, but check the MCP docs for the current supported setup. [10][13]

---

# References

1. OAuth 2.0 Authorization Framework, RFC 6749: https://www.rfc-editor.org/rfc/rfc6749
2. OpenID Connect Core: https://openid.net/specs/openid-connect-core-1_0.html
3. Best Current Practice for OAuth 2.0 Security, RFC 9700: https://www.rfc-editor.org/rfc/rfc9700
4. The OAuth 2.1 Authorization Framework (draft): https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/
5. JSON Web Token (JWT), RFC 7519: https://www.rfc-editor.org/rfc/rfc7519
6. Proof Key for Code Exchange (PKCE), RFC 7636: https://www.rfc-editor.org/rfc/rfc7636
7. MCP Authorization specification (2025-06-18 and later revisions): https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization and https://modelcontextprotocol.io/specification/draft/basic/authorization
8. OAuth 2.0 Protected Resource Metadata, RFC 9728: https://www.rfc-editor.org/rfc/rfc9728
9. Resource Indicators for OAuth 2.0, RFC 8707: https://www.rfc-editor.org/rfc/rfc8707
10. Databricks: Connect MCPs to AI assistants and coding agents: https://docs.databricks.com/generative-ai/mcp/connect-external-services/
11. Databricks: Connect clients to Databricks MCPs: https://docs.databricks.com/aws/en/generative-ai/mcp/connect-clients
12. Aembit: Databricks MCP server (third-party, on pre-registration): https://docs.aembit.io/ai-guide/mcp/identity-gateway/supported-servers/databricks/
13. Databricks: JDBC driver authentication (U2M and M2M explained): https://docs.databricks.com/en/integrations/jdbc/authentication.html
14. Databricks: ODBC driver authentication (token lifetime, service principals): https://docs.databricks.com/aws/en/integrations/odbc/authentication