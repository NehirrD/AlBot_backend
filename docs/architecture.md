# Architecture

This document describes how the AlBot backend is organized and why.
For setup instructions see the [README](../README.md).

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
| LLM | NVIDIA-hosted models (final model not decided yet) |
| Admin panel | Refine (separate frontend, talks to `/admin` endpoints) |
| Dependencies and tasks | Poetry, Poe the Poet |

## 2. Folder structure

```
src/albot/
├── __init__.py
├── main.py                  # Creates the FastAPI app, registers routers and exception handlers
│
├── core/                    # Infrastructure only, no business logic
│   ├── config.py            # Loads and validates settings from .env
│   ├── database.py          # Async engine and get_db dependency (may be merged into config.py)
│   ├── rabbitmq.py          # Connection, publish and consume helpers
│   ├── events.py            # DomainEvent base class and event dispatcher
│   └── exceptions.py        # NotFoundError, ForbiddenError, ValidationError
│
├── features/
│   ├── auth/                # Zitadel token verification and role checks
│   │   ├── zitadel.py       # Verifies JWTs against Zitadel's public keys
│   │   └── dependencies.py  # get_current_user, require_role
│   │
│   ├── search/              # Core flow: a single search request and its result
│   │   ├── router.py        # HTTP endpoints, builds the service with its dependencies
│   │   ├── schemas.py       # API request and response models
│   │   ├── websocket.py     # Streams search progress to the client
│   │   ├── models.py        # Database tables
│   │   ├── domain.py        # Pure business rules and status transitions
│   │   ├── events.py        # SearchRequested, CrawlCompleted, SearchCompleted...
│   │   ├── service.py       # Use cases (start search, crawl, rank)
│   │   ├── repository.py    # Database access
│   │   ├── event_handlers.py# Publishes the next queue task when an event occurs
│   │   └── clients/
│   │       ├── searxng.py   # SearXNG client
│   │       └── crawl4ai.py  # Crawl4AI client
│   │
│   ├── chat/                # Chat sessions and message history
│   ├── catalog/             # Products and categories
│   ├── agent/               # LLM side: client, prompts, output schemas, pipeline
│   └── admin/               # API for the Refine admin panel
│
└── workers/                 # Separate processes that consume queue messages
    ├── crawl_worker.py      # Runs the crawling step
    └── llm_worker.py        # Runs the ranking step
```

Outside `src/`:

```
docker/searxng/settings.yml  # SearXNG settings (enables JSON output)
migrations/                  # Alembic migrations
tests/                       # Mirrors the feature layout (search, chat, auth, admin)
docs/                        # Project documentation
```

### Feature summary

| Feature | Responsibility |
|---|---|
| `auth` | Verifies Zitadel tokens, exposes the current user and role checks. Also stores the local `users` table. |
| `search` | Owns the lifecycle of one search: request, status, queue tasks, result. |
| `chat` | Owns chat sessions and messages, including history used for follow-up questions. |
| `catalog` | Stores scraped products, categories and user favorites. |
| `agent` | Talks to the LLM: prompts, structured output, and the ranking pipeline. |
| `admin` | Admin-only read and management endpoints for the Refine panel. |

## 3. Layering rules

Inside a feature, files depend on each other in one direction only:

```
router.py  ->  service.py  ->  domain.py
                   |
                   +-> repository.py   (database)
                   +-> clients/*.py    (external services)
```

- **`domain.py` imports no framework.** No FastAPI, SQLAlchemy or httpx. It contains plain Python rules, such as which status changes are allowed.
- **`service.py` does not know HTTP.** It raises exceptions from `core/exceptions.py`; `main.py` turns them into 404, 403 or 422 responses.
- **`router.py` stays thin.** It checks permissions, calls the service and returns the result.
- **External tools live behind small client files.** Replacing Crawl4AI or the LLM provider should change one file, not the whole feature.

### Features do not import each other's internals

Features communicate in two ways only:

1. **Domain events** through `core/events.py`. Example: when `search` publishes `SearchCompleted`, an event handler in `chat` adds the assistant message to the session.
2. **Injected dependencies.** Example: `search/service.py` receives the agent's ranking function from the router instead of importing the agent's internals.

This keeps each feature replaceable and testable on its own.

## 4. Request flow

Planned flow for one user message:

```
1. Client sends a message          -> chat router (JWT checked by auth)
2. Search request is created       -> search service saves it, emits SearchRequested
3. Event handler                   -> publishes a crawl task to RabbitMQ
4. crawl_worker                    -> SearXNG finds URLs, Crawl4AI scrapes ~100 products
5. CrawlCompleted event            -> publishes an LLM task to RabbitMQ
6. llm_worker                      -> agent pipeline selects the best 3-5 products
7. SearchCompleted event           -> chat adds the assistant message to the session
8. Progress at every step          -> Redis pub/sub -> WebSocket to the client
```

A search moves through these statuses:
`pending -> crawling -> filtering -> completed | failed`

Each step is its own queue task, so a slow LLM call never blocks scraping.

## 5. Authentication and authorization

- **Zitadel** handles registration, login and role assignment. The backend never sees passwords.
- The client sends `Authorization: Bearer <JWT>`; `auth/zitadel.py` verifies the token and `auth/dependencies.py` extracts the user and roles.
- Roles come from the token, not from a local table, so there is no second copy to keep in sync.
- Two roles: `user` (search and chat) and `admin` (everything, including `/admin`).
- Authorization is always enforced in the backend with `require_role(...)`, regardless of what the admin panel hides.

## 6. Errors

Services raise framework-independent errors from `core/exceptions.py`.
`main.py` maps them to HTTP responses in one place. Workers catch the same errors
and decide what to do (for example, mark the search as `failed`).

## 7. Conventions

- Import from the package root: `from albot.core.config import settings`, `from albot.features.search.service import SearchService`.
- Every directory under `src/albot` and `tests` contains an `__init__.py`.
- Tests mirror the feature layout; file names start with `test_`.
- Configuration comes only from `core/config.py`; never call `os.getenv` elsewhere.
- Secrets live in `.env` (never committed); `.env.example` lists every variable.
