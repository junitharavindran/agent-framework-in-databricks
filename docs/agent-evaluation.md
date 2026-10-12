<h1>Agent Evaluation</h1>

> Specifically, AI agent evaluation.

---

**Contents**:

- [Reason for a separate paradigm](#reason-for-a-separate-paradigm)
  - [Agent evaluation vs. traditional software testing](#agent-evaluation-vs-traditional-software-testing)
  - [Agent evaluation vs. AI model evaluation](#agent-evaluation-vs-ai-model-evaluation)
- [Challenges in agent evaluation](#challenges-in-agent-evaluation)
  - [Multi-dimensional and multi-process complexity](#multi-dimensional-and-multi-process-complexity)
  - [Safety and alignment](#safety-and-alignment)
  - [Real-world variability](#real-world-variability)
  - [Unstable/evolving quality signals](#unstableevolving-quality-signals)
- [Evaluation-driven development](#evaluation-driven-development)
  - [What is it?](#what-is-it)
  - [Continuous evaluation cycle](#continuous-evaluation-cycle)
  - [Preparing for evaluation](#preparing-for-evaluation)
    - [What is effective evaluation?](#what-is-effective-evaluation)
    - [Designing evaluation dataset](#designing-evaluation-dataset)
- [Evaluation-driven development with MLflow](#evaluation-driven-development-with-mlflow)
  - [Overview of MLflow's gen-AI evaluation framework](#overview-of-mlflows-gen-ai-evaluation-framework)
  - [Core components of MLflow's evaluation architecture](#core-components-of-mlflows-evaluation-architecture)
  - [MLflow evaluation workflow](#mlflow-evaluation-workflow)
  - [Observability via MLflow Tracing for evaluation](#observability-via-mlflow-tracing-for-evaluation)

---

# Reason for a separate paradigm
## Agent evaluation vs. traditional software testing
Traditional software testing approaches are fundamentally insufficient for AI agents due to AI agents' non-deterministic nature, emergent behaviors, and context-dependent responses. It is also important to consider that the problems AI agents are made to solve (i.e. adaptive, multi-dimensional, highly variable in details/specifics, requirements that are hard/impossible to satisfy programmatically, etc.) pose distinct challenges that make traditional software testing approaches inapplicable (see: ["Challenges in agent evaluation" in this document](#challenges-in-agent-evaluation)). These challenges demand a more sophisticated evaluation framework specifically designed for the probabilistic, contextual nature of AI agents.

---

Traditional software testing approaches have the following pattern:

- **Assumption**: Same input -> same output
- **Verification**: Exact value match
- **Behavior**: Explicitly programmed
- **Edge Cases**: Anticipated and well-defined

AI agents fundamentally break the deterministic testing paradigm:

- **Non-determinism**
  > Same input -> Different outputs due to temperature and sampling.
- **Emergent Behavior**
  > Autonomous tool and reasoning decisions not explicitly programmed.
- **Context Dependency**
  > Responses depend on retrieval, history and external data.
- **Qualitative Assessment**
  > Success requires qualitative judgment, not exact value-matching.

## Agent evaluation vs. AI model evaluation
Evaluating standalone models focuses on output quality metrics like coherence, factual accuracy, and response relevance. These metrics assume the model's job ends when it generates its output. Agent evaluation requires a different approach because agents do not just generate output, but rather, they take actions, invoke tools with specific parameters, make sequential decisions that build on previous steps, and must recover when external APIs fail or return unexpected data.

Agent evaluation frameworks measure 4 interconnected dimensions.

> Each addresses a different failure mode in agent reliability.

1. Task success
  > Has the agent accomplised its assigned objective?
  > 
  > **NOTE**: This requires precise definition, and may be:
  > 
  > - Outcome-based (as per output)
  > - Process-based (as per steps taken)
  > - Quality-based (as per feedback/external qualitative evaluation)
2. Tool use quality
  > Has the agent invoked:
  > 
  > - The right tools?
  > - With the correct arguments/parameters?
  > - At the appropriate time(s)?
3. Reasoning coherence
  > Was the agent's decision logical and justified given available info?
  > 
  > **NOTE**: This touches on the agent's reasoning's interpretability.
  > 
  > Read more: [Interpretability, **pranigopu.github.io/foundations-of-agentic-ai/interpretability.html**](https://pranigopu.github.io/foundations-of-agentic-ai/interpretability.html)
3. Cost-performance trade-off
  > What does each successful task cost relative to value delivered?
  > 
  > **NOTE**: Cost may be measured in tokens, API calls, latency, etc.

This presents a significant shift from model evaluation.

> **Reference**: [Agent Evaluation: How to Test and Measure Agentic AI Performance, **machinelearningmastery.com/agent-evaluation-how-to-test-and-measure-agentic-ai-performance**](https://machinelearningmastery.com/agent-evaluation-how-to-test-and-measure-agentic-ai-performance/)

# Challenges in agent evaluation
- Multi-dimensional and multi-process complexity
- Safety and alignment
- Real-world variability
  > Diverse inputs and environmental factors.
- Unstable/evolving quality signals

## Multi-dimensional and multi-process complexity
- Multi-step reasoning
  > Cannot just evaluate output, must evaluate intermediate steps.
  > 
  > **NOTE**: In deterministic programs, the intermediate steps are known, but this is not the case with AI agents, due to the non-determinism discussed in ["Reason for a separate paradigm" in this document](#reason-for-a-separate-paradigm).
- Tool calling accuracy
  > - Did the agent select the right tools?
  > - Did it pass appropriate parameters?
  > - Did it correctly interpret tool results?
- Retrieval quality (especially for RAG-based agents)
  > - Verify that retrieved documents contain relevant info
  > - Verify gent correctly synthesises info from multiple sources

## Safety and alignment
Agents must:

- Avoid harmful outputs (safety)
- Respect user boundaries (alignment)
- Decline inappropriate requests (safety + alignment)

## Real-world variability
Production agents encounter:

- Diverse user queries
- Unexpected phrasings
- Edge cases difficult to anticipate during development

## Unstable/evolving quality signals
In traditional software, test suites provide stable quality signals. On the other hand, AI agent evaluation is an ongoing process, and necessarily so, due to non-determinism, context-dependency, and real-world variability, because these aspects ensure there is no guarantee that the quality that was observed initially will remain as the context evolves and as new real-world scenarios emerge, and non-determinism means the intermediate steps taken by the AI agent to achieve its ends cannot be known beforehand. Furthermore, AI agents typically use LLMs or other neural network models, which are black-boxes when it comes to their functioning, which makes continuous evaluation a necessity, not a "good-to-have".

> **KEY POINT**: This continuous evaluation cycle means your evaluation infrastructure must be scalable, automated, and integrated into your development workflow. The evaluation framework must support: (1) rapid feedback loops during development, (2) comprehensive validation before deployment, (3) ongoing monitoring in production, and (4) dataset evolution as usage patterns change.
> 
> More on this discussed in ["Evaluation-driven development" in this document](#evaluation-driven-development).

# Evaluation-driven development
## What is it?
Evaluation-driven development is development that progresses iteratively based on feedback from evaluation at various steps of the development process, including pre-deployment and post-deployment. This kind of development does not cleanly separate development and production, since production monitoring feeds into development and pre-deployment validation. This development approach is illustrated in the following.

![](/_common-resources/evaluation-driven-development.png)

> **Source**: [Evaluating LLMs and Agents with MLflow, **mlflow.org/docs/latest/genai/eval-monitor**](https://mlflow.org/docs/latest/genai/eval-monitor/)

## Continuous evaluation cycle

| Phase | Description |
| --- | --- |
| Development | Rapid iteration requires frequent evaluation to validate that changes improve quality without introducing regressions\*. |
| Pre-deployment validation | Comprehensive evaluation across diverse test cases ensures agents meet quality bars before production release. |
| Production monitoring | Continuous evaluation of live interactions identifies quality degradation, emerging failure patterns, and opportunities for improvement. |

> \* **CONCEPTUAL NOTE**: "Regression" in this context refers to "software regression", which is a type of software bug where a feature that has worked before stops working correctly. This may happen after changes are applied to the software, e.g. new features or, ironically, bug fixes.

This is an iterative process, as production monitoring leads to:

- Enhancement of pre-deployment validation dataset(s)
- New requirements for development

---

This continuous evaluation cycle => evaluation infrastructure must be:

- Scalable
- Automated
- Itegrated into your development workflow

Specifically, the evaluation framework must support:

- Rapid feedback loops during development
- Comprehensive validation before deployment
- Ongoing monitoring in production
- Dataset evolution as usage patterns change

## Preparing for evaluation
### What is effective evaluation?
Effective evaluation requires:

- Defining quality dimensions
- Assembling representative datasets
- Enabling tracing
  > So judges can assess not just answers but how answers were produced.

The aim of preparing for evaluation is to create a feedback loop where:

- Metrics reflect real user needs
- Failures are diagnosable through traces and rationales

### Designing evaluation dataset

| Principle | Practical guidance |
| --- | --- |
| Representativeness | Include common, high-impact user queries so offline results generalise to production |
| Edge cases | Add ambiguous, out-of-scope, and adversarial prompts to surface failure modes early |
| Diversity | Vary length, complexity, domain, and user expertise to expose blind spots in reasoning and retrieval |
| Ground truth and/or guidelines | Use expected answers or fact sets for objective questions; use natural-language guidelines where style, policy, or completeness matter |
| Storage and versioning | Maintain versioning, lineage, sharing, and governance of evaluation datasets to ensure development, improvement, security, and collaboration |

# Evaluation-driven development with MLflow
> **Context**: [MLflow](./mlflow.md)

## Overview of MLflow's gen-AI evaluation framework
A core tenet of MLflow's evaluation capabilities is evaluation-driven development, which is discussed in ["Evaluation-driven development" in this document](#evaluation-driven-development). MLflow provides a comprehensive evaluation framework specifically designed for gen-AI applications, offering automated judges, tracing capabilities, and the means to add custom judges and tracing.

> **Reference**: [Evaluating LLMs and Agents with MLflow, **mlflow.org/docs/latest/genai/eval-monitor**](https://mlflow.org/docs/latest/genai/eval-monitor/)

> **NOTE**: MLflow provides an evaluation framework for gen-AI applications, but it is not limited to these applications. It also provides an evaluation framework for traditional ML and deep learning, including model training and testing (see the general ML documentation [MLflow: AI Engineering Platform for LLMs, Agents, & Models, **mlflow.org/docs/latest/ml**](https://mlflow.org/docs/latest/ml/), as opposed to the gen-AI-specific documentation [MLflow: AI Engineering Platform for LLMs and Agents, **mlflow.org/docs/latest/genai**](https://mlflow.org/docs/latest/genai/)). However, we shall be focusing on MLflow's gen-AI-related offerings.

MLflow's `mlflow.genai.evaluate()` function provides the interface to MLflow's gen-AI evaluation harness: a structured way to feed in test data, run your app, and automatically score the results - it helps you quickly execute your application for every record in your evaluation set and then run each output through your LLM judges and metric computations.

> **CONCEPTUAL NOTE**: An evaluation harness is the infrastructure that runs your LLM/agent evaluations end-to-end. More precisely, an evaluation harness is the controlled combination of scripts, test data, permissions, execution boundaries, and network conditions used to assess a model, agent, or adjacent system before release.
> 
> **References**:
> 
> - [Eval harness: What it is, how to use it, and why you should care, **deepeval.com/blog/what-is-an-eval-harness**](https://deepeval.com/blog/what-is-an-eval-harness)
> - [Evaluation Harness, **nhimg.org/glossary/evaluation-harness**](https://nhimg.org/glossary/evaluation-harness/)

## Core components of MLflow's evaluation architecture
1. Evaluation Dataset
  > Inputs, expectations, outputs.
2. Scorers (Judges)
  > Built-in, custom, code-based.
3. Predict Function
  > Omitted if evaluating pre-generated outputs ("answer sheet" mode).

```
(1)--+
     |
(2)--+-->(evaluation harness)-->(evaluation result)
     |
(3)--+
```

More precisely, in MLflow's specific interface:

```
data (EvaluationDataset, DataFrame, list) ---+
                                             |
scorers (built-in, custom, code-based) ------+
                                             +--> mlflow.genai.evaluate() --> EvaluationResult
predict_fn (agent/app function (optional)) --+     |- orchestrates             |- metrics (aggregate)
                                             |     |- logs                     |- tables (per example)
model_id (LoggedModel linkage (optional))- --+                                 |- run_id
```

> **TECHNICAL NOTE**: When implemented and provided, `predict_fn` must accept keys from the inputs dictionary as keyword arguments, return a JSON-serialisable dictionary, be instrumented with MLflow Tracing, and emit exactly one trace per call.

## MLflow evaluation workflow
1. Data loading
  > Validate structure
2. Output generation
  > Call `predict_fn` or use pre-generated/obtained outputs.
3. Trace creation
  > Auto-instrumented; see ["Observability via MLflow Tracing for evaluation" in this document](#observability-via-mlflow-tracing-for-evaluation).
4. Scorer execution
  > Apply judges
5. Aggregate and log metrics to MLflow

## Observability via MLflow Tracing for evaluation
> **Context**: ["Observability via MLflow Tracing", `agent-deployment-on-databricks.md`](./agent-deployment-on-databricks.md#observability-via-mlflow-tracing)

MLflow Tracing provides comprehensive observability into agent execution, capturing every step of your agent's reasoning process. ***Tracing is enabled when using `mlflow.genai.evaluate()` with properly instrumented predict functions.***