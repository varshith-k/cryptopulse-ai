# CryptoPulse AI — a grounded agent for crypto market monitoring

**Subtitle:** An LLM agent that turns a live crypto data stream into explainable,
source-cited answers — with its analytics toolset exposed over MCP so any client can
reuse it.

**Track:** Agents for Business

---

## The problem

Crypto markets never sleep, and the tooling around them is fragmented. Prices live in one
app, technical indicators in another, alerts in a third, and "what does this mean?" is
answered by generic chatbots that hallucinate numbers and hand out buy/sell advice.
Someone trying to keep an eye on a handful of coins ends up tab-hopping, and the moment
that actually matters — a volatility spike at 2am — is exactly the one they miss.

The business cost is real: fragmented monitoring means slower reactions, missed risk, and
decisions made on vibes instead of data. The failure mode of naive "AI for crypto" tools
is worse than no tool at all — a confident, wrong number is a liability.

## Why an agent?

This is a problem an agent is genuinely suited to, not a chatbot with a crypto skin.

A user's question — *"is anything unusual today, and what should I look at?"* — doesn't map
to a single API call. Answering it well means **deciding which data sources to pull**
(current prices? anomaly scores? recommendations?), pulling them, and then **reasoning over
the combined result** in plain language. That plan-then-act loop is the core of an agent.

Crucially, the agent must stay **grounded**. Our agent never invents market data: it can
only relay what the backend tools return, and every answer cites the exact tools that
produced it. The LLM's job is planning and explanation, not being the source of truth.
That is what makes the tool safe to put in front of someone with money on the line.

## The solution

CryptoPulse AI is a full monitoring product — a React dashboard, a FastAPI backend, a
streaming data pipeline, and an agent service — but the heart of it is the agent.

**How the agent answers a question:**

1. **Plan.** The question goes to the LLM (Groq / Llama 3.3 70B) which returns a JSON plan
   of which tools to call, chosen from the registered toolset.
2. **Enforce.** A deterministic layer adds required tools the model might have missed — e.g.
   comparison questions always include market overview; risk/volatility questions always
   include anomalies and recommendations. This guarantees important data is never dropped
   because of a shaky model plan.
3. **Call.** Each planned tool is executed against the backend analytics endpoints.
4. **Compose.** The combined tool data plus a strict system prompt ("use only the provided
   data, no financial advice, cite your sources") goes back to the LLM to produce a concise,
   grounded answer.
5. **Cite.** The response returns the answer *and* the list of backend tools that grounded
   it.

If no Groq key is configured, the agent falls back to a deterministic intent-routing path so
the product still demos end-to-end offline — a small but important reliability decision.

## The MCP server — one toolset, many consumers

The most interesting technical decision is how the toolset is structured. The agent's four
grounded tools — `market.overview`, `analytics.anomalies`, `analytics.recommendations`,
`analytics.summary` — are defined **once**, in a shared registry (`apps/agent/src/tools.py`).

Two things consume that one registry:

- **Our own agent**, whose planning loop calls the registry directly.
- **A Model Context Protocol server** (`apps/agent/src/mcp_server.py`, built on FastMCP)
  that exposes the same tools to *any* MCP client — Claude Desktop, the MCP Inspector, or a
  different agent entirely.

Because both surfaces are generated from the same source, they can never drift apart. Each
tool's docstring and type hints become its public MCP schema automatically, so an external
client discovers exactly what it can call and why. This turns CryptoPulse's grounded
analytics from a private implementation detail into a reusable, standards-based capability —
a business could drop these tools into their own internal assistant without touching our
code.

## Architecture

```text
Market APIs / backfill
        |
        v
Ingestion service ──► PostgreSQL snapshots
        |
        └─► Kafka market topics
                 ├─► Streaming processor (group A) ──► indicators + insights
                 └─► Real-time detector (group B)  ──► sliding-window z-score spikes
                 |
                 v
        FastAPI backend  ◄──►  Agent service ──► shared tool registry
              |                      │                    │
              v                      │                    ├─► MCP server (external clients)
        React dashboard              │                    └─► Agent CLI (terminal)
                                     └─► Groq (plan + compose)
```

A second data path is worth calling out: a dedicated real-time Kafka consumer runs a
per-symbol sliding-window z-score over the live tick stream, flagging volatility spikes with
bounded O(symbols × window) memory. It runs in its own consumer group alongside the batch
processor, so stream-time detection and daily-indicator analysis coexist. The agent's anomaly
tool can reason over both.

## Course concepts applied

We demonstrate five of the course's key concepts (three required):

| Concept | Where | What |
| --- | --- | --- |
| **Agent system** | `apps/agent/src/logic.py`, `groq_client.py` | Plan → enforce → call → compose → cite loop. |
| **MCP Server** | `apps/agent/src/mcp_server.py`, `tools.py` | FastMCP server exposing the shared toolset to any MCP client. |
| **Security features** | `apps/api` (JWT), `.env` handling | Signed accounts, per-user isolation, no secrets in code. |
| **Deployability** | `docker-compose.yml`, `Makefile` | One-command ten-service stack with health/readiness endpoints. |
| **Agent skills / CLI** | `apps/agent/src/cli.py` | Terminal client that queries the agent and shows its sources. |

## Security

Because this is the Business track, safety matters. Accounts use JWT auth; alerts and
triggered-alert history are scoped per user. Every credential — Groq key, SMTP password,
webhook URL, JWT secret — is loaded from a git-ignored `.env`; only a placeholder
`.env.example` is committed, so no key ever enters the repository. Outbound notification
delivery is sandboxed: a failing or unconfigured channel is logged and skipped, never
allowed to break alert evaluation.

## Deployability

The whole system comes up with `make up` (Docker Compose), spanning the API, frontend, agent,
Postgres, Redis, Kafka, ingestion, streaming, and the real-time detector. Every service
exposes health and readiness endpoints, so orchestration and reproduction are
straightforward. The MCP server and CLI run from `apps/agent` with a single `pip install`.

## The build & journey

CryptoPulse AI was built in ten phases, from an empty monorepo scaffold to a streaming
pipeline with real-time anomaly detection and outbound alert notifications (the full phase
log is in the README). The capstone phase focused the project on its agent story: I
extracted the ad-hoc tool calls into a shared registry, wrapped that registry in an MCP
server so the tools become reusable by any client, and added a CLI so the agent is usable
without the dashboard. The guiding principle throughout was **grounding** — the LLM plans and
explains, but the backend is always the source of truth.

**Stack:** FastAPI, React/TypeScript/Vite/Tailwind, PostgreSQL, Redis, Kafka, Groq
(Llama 3.3 70B), FastMCP, Docker Compose.

## Limits & next steps

The app targets local development and product exploration. Alert evaluation is still triggered
manually (notifications then fire automatically); the next step is a scheduled worker. Auth is
intentionally basic (no reset/verification yet). Cloud deployment and CI are on the roadmap.
On the agent side, the natural next move is agent-suggested alerts ("you should watch SOL
volatility") and historical-comparison tools — both of which slot straight into the existing
shared registry and, for free, into the MCP surface.

## Why it fits Agents for Business

CryptoPulse turns a noisy, fragmented, high-stakes data stream into grounded, explainable,
source-cited answers — the exact shape of problem enterprises face when they need AI to
*inform decisions with money on the line* without hallucinating. And by exposing its analytics
as an MCP server, the agent's value isn't locked inside one app: it's a reusable capability
any business assistant can plug into.
