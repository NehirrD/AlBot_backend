# Architecture

This document describes how the AlBot backend is organized and why. For setup instructions see the README. Table details live in `database.md`.

## 1. Tech stack

| Concern | Tool |
|---|---|
| API | FastAPI, Uvicorn |
| Database | PostgreSQL (SQLAlchemy, Alembic) |
| Task queue | RabbitMQ |
| Cache and live progress | Redis |
| Authentication and roles | Zitadel (JWT, role-based authorization) |
| Web search | SearXNG |
| Scraping | Crawl4AI |
| LLM | NVIDIA-hosted models (final model not decided yet; cheap and strong model are chosen per step) |
| Admin panel | Refine (separate frontend, talks to `/admin` endpoints) |
| Dependencies and tasks | Poetry, Poe the Poet |

## 2. Folder structure

```
src/
├── __init__.py
├── main.py                  # Creates the FastAPI app, registers routers and exception handlers
│
├── core/                    # Infrastructure only, no business logic
│   ├── config.py            # Loads and validates settings from .env
│   ├── database.py          # Async engine and get_db dependency
│   ├── dtos.py              # Shared DTO types (e.g. JsonDecimal)
│   ├── rabbitmq.py          # Connection, publish and consume helpers
│   ├── events.py            # DomainEvent base class and event dispatcher
│   ├── exceptions.py        # NotFoundError, ForbiddenError, ValidationError
│   └── logging.py           # Logging setup (log lines carry the job id)
│
├── features/
│   ├── auth/                # Zitadel token verification and role checks
│   │   ├── zitadel.py       # Verifies JWTs against Zitadel's public keys
│   │   ├── dependencies.py  # get_current_user, require_role
│   │   └── dtos.py, models.py
│   │
│   ├── agent/               # The brain: runs one search job as a state machine
│   │   ├── fsm.py           # Step enum, allowed-transitions table, default order
│   │   ├── dossier.py       # In-memory journal of one job (mirrors context_log rows)
│   │   ├── gateways.py      # Context (ctx) with the gateways + fake LLM / dataset
│   │   ├── orchestrator.py  # The loop that runs steps (the only place with a loop)
│   │   ├── steps/           # One step = one file
│   │   │   ├── base.py      # BaseStep (abstract) and StepResult
│   │   │   ├── plan.py      # Understand the query, extract filters
│   │   │   ├── collect.py   # Gather candidate products
│   │   │   ├── validate.py  # Rule filter (plain code)
│   │   │   └── rank.py      # Pick the best 3 and explain
│   │   ├── policy.py        # Budget and retry rules (planned)
│   │   ├── llm.py           # Real LLM client: cheap / strong model, retry, token log (planned)
│   │   ├── prompts.py       # Prompt templates (planned)
│   │   ├── repository.py    # Database access (planned)
│   │   ├── models.py        # search_jobs, context_log, agent_steps, recommendations
│   │   ├── dtos.py          # API schemas and SearchFilters
│   │   └── router.py        # HTTP endpoints (currently the demo endpoint only)
│   │
│   ├── search/              # Search infrastructure and stored results
│   │   ├── clients/
│   │   │   ├── searxng.py   # SearXNG client
│   │   │   └── crawl4ai.py  # Crawl4AI client
│   │   └── router.py, dtos.py, models.py, domain.py,
│   │       events.py, event_handlers.py, repository.py
│   │
│   ├── chat/                # Chat sessions, messages, progress channel
│   │   ├── sse.py           # Streams progress to the client (Server-Sent Events)
│   │   └── router.py, dtos.py, models.py, domain.py,
│   │       event_handlers.py, repository.py
│   │
│   ├── catalog/             # Products, categories, favorites
│   └── admin/               # API for the Refine admin panel
│
└── workers/                 # Separate processes that consume queue messages
    ├── crawl_worker.py
    └── llm_worker.py
```

Outside `src/`:

```
docker/searxng/settings.yml  # SearXNG settings (enables JSON output)
migrations/                  # Alembic migrations
scripts/                     # Runs the agent in the terminal with fake data - temporary
tests/                       # Mirrors the feature layout (tests/agent/mocks.py, 
docs/                        # Project documentation
```

### Feature summary

| Feature | Responsibility |
|---|---|
| `auth` | Verifies Zitadel tokens, exposes the current user and role checks. Also stores the local `users` table. |
| `agent` | Owns the lifecycle of one search job: state machine, steps, LLM calls, budget, journal. |
| `search` | SearXNG and Crawl4AI clients, search queries and crawled pages. |
| `chat` | Chat sessions and messages (including the summary used for follow-ups) and the progress channel to the client. |
| `catalog` | Stores scraped products, categories and user favorites. |
| `admin` | Admin-only read and management endpoints for the Refine panel. |

## 3. Layering rules

Inside a feature, files depend on each other in one direction only:
 
```
router.py  ->  service.py  ->  domain.py
                   |
                   +-> repository.py   (database)
                   +-> clients/*.py    (external services)
```
 
- `domain.py` imports no framework (no FastAPI, SQLAlchemy or httpx). It contains plain Python rules.
- `service.py` does not know HTTP. It raises exceptions from `core/exceptions.py`; `main.py` turns them into 404, 403 or 422 responses.
- `router.py` stays thin. It checks permissions, calls the service and returns the result.
- External tools live behind small client files. Replacing Crawl4AI or the LLM provider should change one file, not the whole feature.
- `service.py` is created only when a feature needs it. Today `agent` has none: its demo router calls the orchestrator directly. The job-creating service arrives with the queue (see section 4).

### Features do not import each other's internals

Features communicate in two ways only:
 
1. **Domain events** through `core/events.py`. Example: when a job finishes, an event handler in `chat` adds the assistant message to the session.
2. **Injected dependencies.** `agent` may use other features' services (search clients, catalog, chat), but they are passed in through the context gateways (section 5). Other features never import `agent`; this prevents circular dependencies.

## 4. Request flow

<img width="1600" height="626" alt="agent-components" src="https://github.com/user-attachments/assets/b42785b3-9128-492a-8f6b-22c5397e59ba" />

Planned flow for one user message:

```
1. Client sends a message        -> chat router (JWT checked by auth)
2. agent service creates a job   -> saves search_jobs row, publishes {search_id} to RabbitMQ
3. Worker takes the message      -> loads the job from PostgreSQL
4. Orchestrator runs the steps   -> PLAN -> COLLECT -> VALIDATE -> RANK
5. After every step              -> journal rows written to context_log, progress event to Redis
6. Redis pub/sub                 -> progress streamed to the client (SSE)
7. Job completed                 -> event handler in chat adds the assistant message
```

The message on the queue only carries the job id. The job's real state always lives in PostgreSQL, so queue messages can be repeated or lost without corrupting anything.

## 5. Agent design

The agent is a **finite state machine (FSM)** run by an **orchestrator**. Four ideas fit together:
 
- **FSM (`fsm.py`)**: which steps exist and which transitions are allowed.
- **Orchestrator (`orchestrator.py`)**: the loop that runs the current step and moves to the next one.
- **Dossier (`dossier.py`)**: the journal of one job. Steps read earlier results from it; the orchestrator writes to it.
- **Context management**: what each step (and each LLM call) is allowed to see.

### Steps and transitions

```
PLAN     -> COLLECT
COLLECT  -> VALIDATE | FAILED
VALIDATE -> RANK | PLAN | RESEARCH
RESEARCH -> VALIDATE
RANK     -> DONE
any step -> FAILED   (on permanent error)
```

- `VALIDATE -> PLAN`: wrong search or too few good products, re-plan (at most 2 rounds).
- `VALIDATE -> RESEARCH`: evidence is missing, a small agent loop reads forums, reviews or video transcripts (later phase, at most 8 tool calls).
- When the budget runs out, the orchestrator jumps to `RANK` and finishes with what it has.

The transition table lives in code (`fsm.py`). A step may return `next=Step.X` to choose the next step; if it returns nothing, `DEFAULT_NEXT` is used. A transition that is not in the table raises an error.

### The orchestrator loop

For every step the orchestrator, in this order:
 
1. writes a `step_started` event,
2. runs the step,
3. writes a `step_finished` event with the step's summary, public message and data,
4. picks the next step (`result.next` or `DEFAULT_NEXT`) and checks that the transition is allowed.

If a worker crashes, another worker takes the job from the queue, reads `current_step` and continues from there. Steps must therefore be safe to run twice.

### Steps and gateways

- Steps never call each other; only the orchestrator calls them.
- A step reaches the outside world only through **context gateways** (`ctx.llm`, `ctx.search`, `ctx.crawler`, `ctx.store`, `ctx.cache`, `ctx.events`). In tests a fake gateway is plugged in, so no real LLM or internet is needed.
  

### Context management (what the LLM sees)

The LLM has no memory; it only sees what we send. Answer quality depends mostly on that input, and too much input also lowers quality.

1. **Never send raw HTML to the LLM.** Raw pages are stored in `crawled_pages`; the snapshot only holds their ids. A parser reduces each product to a short form (`id, title, price, ram, gpu, ...`).
2. **Code first, LLM second.** Price, stock, category and spec thresholds are filtered with plain code. The LLM only sees the remaining candidates.
3. **Each step has its own small context.** `PLAN` sees only the user request; `RANK` sees only the filtered candidates and the criteria, not the whole chat.
4. **The right model for the right job.** Cheap model for understanding, extraction and validation; strong model for ranking and reasoning (one call).
5. **Long chats are summarized.** `chat_sessions.summary` plus the latest messages are sent instead of the whole history.
6. **Cross-check the output.** Prices and specs written by the LLM are compared with the stored data before the user sees them.
7. **The snapshot stays small.** Only references, filters and counters are kept in `context_snapshot`.

### Where the LLM decides
 
An agent is a system where the model decides what happens next. In this design the decision points are the `StepResult.next` value and the step logic itself (for example: "10 products wanted, 2 found, go back to PLAN"). For now those decisions are plain `if/else` code. When the LLM is connected, the same points call `ctx.llm` instead, and only the gateway implementation and the step bodies change.

## 6. Authentication and authorization

- Zitadel handles registration, login and role assignment. The backend never sees passwords.
- The client sends `Authorization: Bearer <JWT>`; `auth/zitadel.py` verifies the token and `auth/dependencies.py` extracts the user and roles.
- Roles come from the token, not from a local table, so there is no second copy to keep in sync.
- Two roles: `user` (search and chat) and `admin` (everything, including `/admin`).
- Authorization is always enforced in the backend with `require_role(...)`, regardless of what the admin panel hides.
- The `admin` endpoints support pagination, sorting and filtering (what Refine's data provider expects) and return the total count in the `X-Total-Count` header. Admin actions are written to `admin_audit_log`.

## 7. Errors

Services raise framework-independent errors from `core/exceptions.py`. `main.py` maps them to HTTP responses in one place. The orchestrator catches the same errors and decides what to do (retry, re-plan or mark the job as `failed`).

## 8. Conventions

- Import from the package root: `from core.config import settings`, `from features.agent.service import AgentService`.
- Every directory under `src/` and `tests` contains an `__init__.py`.
- Tests mirror the feature layout; file names start with `test_`.
- Configuration comes only from `core/config.py`; never call `os.getenv` elsewhere.
- Secrets live in `.env` (never committed); `.env.example` lists every variable.
- Create a new file only when you can describe its job in one sentence; split a file when it passes roughly 150 lines.
- Logs include the job id (`job=<id> step=<step> ...`) so one user's journey can be filtered.


## 9. Implementation order

1. `fsm.py`: `Step` enum and the transition table.
2. `orchestrator.py`: the loop, with fake steps and no LLM.
4. Steps one by one: `plan`, `collect`, `validate`, `rank`.
5. Context management details: product compression, chat summary, budget limits.
6. `RESEARCH` step, `tools/` and an evaluation set of example queries.
