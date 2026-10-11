<h1>MLflow</h1>

---

**Contents**:

- [Key abbreviations](#key-abbreviations)
- [About](#about)
- [Architecture](#architecture)
  - [Scale](#scale)
  - [Core components](#core-components)
- [Common setups](#common-setups)

---

# Key abbreviations

| Abbreviation | Full form |
| --- | --- |
| UC | Unity Catalog |
| SDK | Software Development Kit |

# About
MLflow is an open-source platform ("platform" being an infrastructure to host various related applications/functionalities) for managing lifecycle of ML/AI applications/deployments. This management includes: tracking specific applications/deployments (via ID'd "experiments" and training runs), deployment of ML/AI models, tracing ML/AI workflows, and evaluating outputs. Hence, it addresses:

- Tracking (ML experiment tracking)
- Model versioning
- Model deployment
- Tracing (a form of observability)
  > Learn more about tracing: ["Trace", Common Terms, **Getting into Observability**, **pranigopu.github.io/getting-into-observability/common-terms.html**](https://pranigopu.github.io/getting-into-observability/common-terms.html#trace)
- Evaluation
- Monitoring (via continuous tracking, tracing, evaluation)

> **Reference**: [MLflow: AI Engineering Platform for LLMs, Agents, & Models, **mlflow.org/docs/latest/ml**](https://mlflow.org/docs/latest/ml/)

# Architecture
> **Key reference**: [Architecture Overview, **www.mlflow.org/docs/latest/self-hosting/architecture/overview**](https://www.mlflow.org/docs/latest/self-hosting/architecture/overview/)

## Scale
It is a scalable architecture that covers:

- Solo local deployment
- Production-scale deployment

## Core components
- **MLflow SDK**
  - Provides client SDKs in multiple languages
    > Python, TypeScript, Java, R.
  - Users use these SDKs to interact with the backend
- **Backend store**
  - A database that stores the metadata of:
    - Experiments
    - Runs
    - Traces
    - Metrics
    - etc.
    > This database can also be a file system that emulates a database.
    - MLflow supports different databases via SQLAlchemy [1]:
      - postgresql
      - mysql
      - sqlite
      - mssql
  > Read more: [Backend Stores, **www.mlflow.org/docs/latest/self-hosting/architecture/backend-store**](https://www.mlflow.org/docs/latest/self-hosting/architecture/backend-store/)
- **Artifact store**
  - Persists artifacts for each run, such as:
    - Model weights (e.g. a pickled scikit-learn model)
    - Images (e.g. PNGs)
    - Model and data files (e.g. Parquet file).
  - These files are... <br> - too large to be stored within the tracking backend <br> - often less-frequently accessed than metadata <br> ... rendering them more suited for cheap object storage such as Amazon S3
  > Read more: [Artifact Stores, **www.mlflow.org/docs/latest/self-hosting/architecture/backend-store**](https://www.mlflow.org/docs/latest/self-hosting/architecture/artifact-store/)
- **Tracking server**
  - FastAPI [2] server that:
    - Serves REST APIs for accessing the backend and the artifact store
    - Hosts the MLflow UI
  - This is optional for local development
    > Since MLflow SDK can directly interact with a local database and file system.
  - However, it is essential for team development
  - Importantly, it provides features such as access control
  > Read more: [Tracking Server, **www.mlflow.org/docs/latest/self-hosting/architecture/backend-store**](https://www.mlflow.org/docs/latest/self-hosting/architecture/tracking-server/)

> [1] **TECHNICAL NOTE: SQLAlchemy**: SQLAlchemy is the Python S*QL toolkit and Object Relational Mapper that gives application developers the full power and flexibility of SQL. SQLAlchemy provides a full suite of well known enterprise-level persistence patterns, designed for efficient and high-performing database access, adapted into a simple and Pythonic domain language.
>
> **Reference**: [SQLAlchemy 2.1.4, **pypi.org/project/SQLAlchemy** (last accessed: 2026-10-11)](https://pypi.org/project/SQLAlchemy/)

> [2] **TECHNICAL NOTE: FastAPI**: FastAPI is a modern, fast (high-performance), web framework for building APIs with Python based on standard Python type hints.
>
> **Reference**: [FastAPI, **fastapi.tiangolo.com**](https://fastapi.tiangolo.com/)

# Common setups
> I shall not go in detail here; refer to this for details:
>
> ["Common Setups", Architecture Overview, **www.mlflow.org/docs/latest/self-hosting/architecture/overview**](https://www.mlflow.org/docs/latest/self-hosting/architecture/overview/#common-setups)

- Localhost (default)
- Localhost with various data stores
- Remote tracking with tracking server