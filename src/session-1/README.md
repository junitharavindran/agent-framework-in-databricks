<h1>Demos for Session 1</h1>

---

**Contents**:

- [Demo plan](#demo-plan)
- [Demos](#demos)
  - [How the LLM is called](#how-the-llm-is-called)
  - [Notes](#notes)

---

# Demo plan
**See**: ["Session 1", `docs/demo-plan/demo-plan-v5.md`](/docs/demo-plan/demo-plan-v5.md#session-1)

# Demos
Required installations:

- `pip install google-genai`
- `pip install mcp`
- `pip install mlflow`

5 demos, 1 folder each:

- Every folder is self-contained
- Run code from inside the folder
  > Nothing is shared between folders.

| Folder | Block | Run (from inside the folder) | Shows |
| --- | --- | --- | --- |
| [`1-agent-loop`](./1-agent-loop/) | 1.3 | `python agent_loop.py` | The agent loop: the model decides, a tool runs, the result goes back |
| [`2-tracing`](./2-tracing/) | 1.4 | `python tracing.py` (change the `STEP` variable to 1, 2 and 3); lab L1: `lab.py` | One span, a span tree, an error span |
| [`3-mcp`](./3-mcp/) | 1.5 | `python client.py` | 2 MCP servers (STDIO and HTTP): tools, a resource, a prompt; one client per server |
| [`4-evaluation`](./4-evaluation/) | 2.2 | `python evaluation.py`; lab L2: `lab.py` | 3 scorer kinds on a small dataset |
| [`5-versions-loop`](./5-versions-loop/) | 2.3, 2.4 | `python setup_prompts.py`, then `python versions_loop.py`; lab L3: `lab.py` | Evaluate, fix, new version, compare, promote, roll back, find a trace by version |

> **Status**:
> 
> - Run end to end in offline mode only
> - The live Gemini call and the default model name not tested yet

## How the LLM is called
Each folder has its own `helpers.py` with the same small `call_llm` function. It uses, in order: the offline stand-in (if `DEMO_OFFLINE=1`), a saved reply in that folder's `cache/`, then a live Gemini call (which saves its reply). Offline replies are rule-based, not model output: use them to rehearse, never to show. To build the cached fallback, run each demo once with `GEMINI_API_KEY` set and keep the `cache/` folders. Demo 3 needs no LLM.

## Notes
- View traces from inside a folder: <br> E.g.: `mlflow ui --backend-store-uri sqlite:///mlflow.db --port 5001`
- Each folder keeps its own `mlflow.db` <br> => To reset a demo, delete it
- Traces export in the background, so scripts call `mlflow.flush_trace_async_logging()` before reading them.
- Spell-checking uses a small fixed list in `helpers.py`
  > This is so the demo is predictable. It is not a real spell checker.
- Demo 3 uses `127.0.0.1:8765` <br> => Change the port in `servers.py` and `client.py` if it is taken.