<h1>AI Assets in Databricks</h1>

---

**Contents**:

- [Abbreviations](#abbreviations)
- [The foundations - UC OSS and UC](#the-foundations---uc-oss-and-uc)
- [Governance for AI on Databricks - Unity Gateway](#governance-for-ai-on-databricks---unity-gateway)
- [AI models hosted on Databricks](#ai-models-hosted-on-databricks)
  - [Foundation model, Foundation Model API](#foundation-model-foundation-model-api)
  - [Model service](#model-service)
  - [Model Serving](#model-serving)
- [Other key points](#other-key-points)
  - [Registered models as functions in UC](#registered-models-as-functions-in-uc)

---

# Abbreviations

| Abbreviation | Full form |
| --- | --- |
| UC | Unity Catalog |
| OSS | Open-Source Software |

# The foundations - UC OSS and UC
UC OSS is an open-source catalog-as-a-service for data and AI assets, i.e. a service to organise and manage data and AI assets (kind of like an OS's file system). For complex data and AI applications, the assets worth governing are no longer just tables, but also raw files, functions, and machine-learning models. UC provides the catalog as a shared, open service that does these jobs for all of them.

---

At its core, it addresses 3 concerns of any catalog system:

1. Which files hold the data a given asset/object (e.g. table, model)?
2. Which user(s) is/are allowed to read them?
3. What is the asset's schema/structure/metadata?

---

***UC is a metadata and access service.***

It works alongside the systems that run queries and store data:

- Engines run the queries
  > E.g.: Spark, DuckDB, your own apps; connect through:
  > 
  > - UC REST API
  > - Delta API for catalog-managed Delta tables
  > - Iceberg REST API for Iceberg/Delta tables with Iceberg metadata
- Storage holds the data.
  > Table and volume files live in object storage or a file system. The catalog records where. When an engine needs the files, the catalog can issue short-lived credentials scoped to that one table or volume, a mechanism called credential vending.

> **NOTE**: This split is the point of an open catalog:
> 
> - Any engine that speaks the APIs sees the same names/schemas/permissions
> - No engine has to own the data

---

**UC OSS and UC on Databricks**: UC OSS is the open-source project described above. Databricks has its own Unity Catalog, which is the one the rest of this document builds on. The ideas carry over: assets are *securables* (objects you grant permissions on, to users, groups or service principals), they have three-level names (`catalog.schema.name`), and access is controlled through privileges such as `USE CATALOG`, `USE SCHEMA` and `EXECUTE`. On Databricks, the securables include AI assets as well as data: models, model services, model providers, MCP servers and skills.

> **NOTE**: A model registered in UC is an *asset at rest* (versions, metadata, artifacts). Registering it does not make it callable. To call a model, it has to be served (see ["Model Serving" in this document](#model-serving)) or reached through a model service (see ["Model service" in this document](#model-service)).

---

> **References**:
>
> - [What is Unity Catalog OSS?, **docs.unitycatalog.io/explanation/what-is-unity-catalog**](https://docs.unitycatalog.io/explanation/what-is-unity-catalog)
> - [Unity Gateway concepts, **docs.databricks.com/aws/en/unity-gateway/concepts**](https://docs.databricks.com/aws/en/unity-gateway/concepts)

# Governance for AI on Databricks - Unity Gateway
Unity Gateway extends governance to the runtime interactions between:

- Models
- Agents
- MCP servers
- Tools

Key features:

- Control which AI services teams can use, route and manage AI traffic
- Set guardrails with service policies
- Monitor usage from one control plane

> **NOTE**: Unity Gateway does not host models. It routes and governs requests to models that are:
> 
> - Served by Databricks
> - Provided by third-party providers
>
> It does this through *model services* (see [Model service](#model-service)) and *model provider services*.

> **NOTE**: Governing agents, in practice:
>
> - An agent is governed mainly through the calls it makes: its LLM calls (through a model service) and its tool calls (through MCP services)
> - Service policies (guardrails) currently apply to MCP services, model services and model provider services. Agent services are not supported.
> - Service policies are in Beta

> **References**:
>
> - [AI governance with Unity Gateway, **learn.microsoft.com/en-us/azure/databricks/ai-gateway**](https://learn.microsoft.com/en-us/azure/databricks/ai-gateway/)
> - [AI governance with Unity Gateway, **docs.databricks.com/aws/en/ai-gateway**](https://docs.databricks.com/aws/en/ai-gateway/)
> - [Unity Gateway concepts, **docs.databricks.com/aws/en/unity-gateway/concepts**](https://docs.databricks.com/aws/en/unity-gateway/concepts)
> - [Service policies for AI securables, **docs.databricks.com/aws/en/data-governance/unity-catalog/service-policies**](https://docs.databricks.com/aws/en/data-governance/unity-catalog/service-policies/)
> - [Detailed list of models supported by Databricks Foundation Model APIs, **docs.databricks.com/gcp/en/machine-learning/foundation-model-apis/supported-models**](https://docs.databricks.com/gcp/en/machine-learning/foundation-model-apis/supported-models)

# AI models hosted on Databricks
## Foundation model, Foundation Model API
A foundation model in Databricks is a state-of-the-art model hosted natively on Databricks (i.e. pre-deployed on Databricks), so you do not have to serve it yourself. These include open models, and proprietary models that Databricks makes available. Foundation Model APIs let you access and query these models. You can send query requests to them through Unity Gateway using their model service names (`system.ai.<model>`).

> **NOTE: Legacy access route**: Foundation models used to be queried through *pay-per-token serving endpoints* (`databricks-*` names, under `/serving-endpoints`). Databricks is replacing these with Unity Gateway model services. A workspace setting, *Enforce Unity Gateway*, disables the legacy endpoints. Use `system.ai.<model>` for anything new.

> **NOTE: Availability**: Availability of these models may vary by workspace region and entitlements. A name existing in `system.ai` is not a guarantee that you can query it; the AI Gateway page in the workspace UI shows what you can actually use.

> **References**:
>
> - [Detailed list of models supported by Databricks Foundation Model APIs, **docs.databricks.com/gcp/en/machine-learning/foundation-model-apis/supported-models**](https://docs.databricks.com/gcp/en/machine-learning/foundation-model-apis/supported-models)
> - [Databricks Foundation Model APIs, **docs.databricks.com/gcp/en/machine-learning/foundation-model-apis**](https://docs.databricks.com/gcp/en/machine-learning/foundation-model-apis/)
> - [Migration guide: Moving to Unity Gateway, **kb.databricks.com**](https://kb.databricks.com/unity-catalog/migration-guide-moving-to-unity-ai-gateway)

## Model service
A model service is a UC object, named `catalog.schema.name`, that routes inference requests to one or more models. It is queried by its fully qualified name (e.g. through the OpenAI-compatible endpoint under `/ai-gateway/mlflow/v1`), not as a serving endpoint.

> **NOTE: Ready-made model services**: Databricks provides ready-made model services in `system.ai` (see ["Foundation model, Foundation Model API" in this document](#foundation-model-foundation-model-api)). By default, all account users can call them, which is why you can query a foundation model without serving anything yourself.

> **NOTE: Custom model services**: You can also create your own, in a catalog and schema you choose. Its destinations can be Databricks-served models (pay-per-token or provisioned throughput) or an external model provider, and you can mix them. This supports traffic splitting and fallbacks.

Rate limits, service policies (guardrails), usage tracking and inference logging are configured on the model service, not in application code. Access is controlled with UC privileges: `EXECUTE` to call it, `CREATE SERVICE` to create one, `MANAGE` to change it. Callers also need `USE CATALOG` and `USE SCHEMA`.

> **KEY POINT**:
> 
> - ***A model service provides no compute of its own***
> - The model behind it is served by Databricks or by the external provider

---

> **NOTE**: Model service vs. serving endpoint:
>
> A serving endpoint belongs to Model Serving: it is a deployment that hosts a model and has compute behind it. A model service belongs to Unity Gateway: it is a governed, routable name that points at models hosted elsewhere. They connect where a provisioned-throughput endpoint stays in Model Serving and a model service references it.

---

> **References**:
>
> - [Custom model services, **docs.databricks.com/aws/en/ai-gateway/model-services**](https://docs.databricks.com/aws/en/ai-gateway/model-services)
> - [Query foundation and embedding models, **docs.databricks.com/aws/en/ai-gateway/query-model-services**](https://docs.databricks.com/aws/en/ai-gateway/query-model-services)
> - [Unity Gateway concepts, **docs.databricks.com/aws/en/unity-gateway/concepts**](https://docs.databricks.com/aws/en/unity-gateway/concepts)
> - [Migration guide: Moving to Unity Gateway, **kb.databricks.com**](https://kb.databricks.com/unity-catalog/migration-guide-moving-to-unity-ai-gateway)

## Model Serving
Model Serving is an AI deployment platform hosted on Databricks. Essentially, it is two things in one: an interface and a service. Its interface is a unified interface to deploy, govern, and query AI models. Its service is a highly available and low-latency service for deploying models; the service automatically scales up or down to meet demand changes, saving infrastructure costs while optimizing latency performance (this functionality uses serverless compute). To deploy a model here, you register it in UC and create a *serving endpoint* (a URL that acts as an entrypoint for the model) that points at a model name and version. Agents are served the same way, as custom models.

> **NOTE: Model Serving vs. Unity Gateway**:
>
> - Unity Gateway governs runtime interactions between an AI app's services
> - Model Serving handles the deployment, governance, querying of AI models
>   > Here, "governance" focuses on:
>   > 
>   > - Who can access the model
>   > - What can a given user do with the model
>
> These are complementary offerings, rather than competing ones:
>
> - Model Serving is the hosting layer with attached governance for AI models
>   > Governance features that were configured per endpoint ("AI Gateway (legacy)": rate limits, guardrails, usage tracking, inference tables) are superseded by Unity Gateway, which Databricks recommends.
> - Unity Gateway is a separate governance layer that:
>   - Governs the runtime interactions
>   - Governs not just AI models but MCP servers and tools, and agents
>     > Governance of agents is done through the calls they make.

> **NOTE: Model Serving vs. Foundation Model API**:
>
> - Foundation models are pre-defined and pre-existing
> - Foundation Model API enables access to the above
> - Model Serving is more general; you can serve custom or available models
>   > Model Serving supports Foundation Model APIs, external models and custom models

> **References**:
>
> - [Deploy models using Model Serving, **docs.databricks.com/aws/en/machine-learning/model-serving**](https://docs.databricks.com/aws/en/machine-learning/model-serving/)
> - [Governance for model serving endpoints (legacy), **learn.microsoft.com**](https://learn.microsoft.com/en-us/azure/databricks/ai-gateway/overview-serving-endpoints)

# Other key points
## Registered models as functions in UC
In UC, registered models are a subtype of the FUNCTION securable object. To grant access to a model registered in Unity Catalog, you use GRANT ON FUNCTION. You can also use Catalog Explorer to set model ownership and permissions.

> **Reference**: [Manage model lifecycle in Unity Catalog, **docs.databricks.com/aws/en/machine-learning/manage-model-lifecycle**](https://docs.databricks.com/aws/en/machine-learning/manage-model-lifecycle)