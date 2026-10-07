# Database

PostgreSQL, accessed through SQLAlchemy (async) with Alembic migrations. This document explains every table and why it exists. For the overall design see `architecture.md`.

## 1. Diagram

<img width="1906" height="2349" alt="database_diagram" src="https://github.com/user-attachments/assets/2de33eaf-8d50-4618-9eb1-b5e083802544" />

## 2. Overview

| Group | Tables |
|---|---|
| Users | `users` |
| Catalog | `categories`, `category_criteria`, `products`, `favorites` |
| Chat | `chat_sessions`, `chat_messages` |
| Agent | `search_jobs`, `crawled_pages`, `agent_steps`, `search_queries`, `recommendations` |
| Admin | `admin_audit_log` |

### Where each table is defined

Each table lives in the `models.py` of the feature that owns it. Foreign keys to other features use strings (`ForeignKey("users.id")`).


| File | Tables | Enums |
|---|---|---|
| `features/auth/models.py` | `users` | none |
| `features/catalog/models.py` | `categories`, `category_criteria`, `products`, `favorites` | `stock_status` |
| `features/chat/models.py` | `chat_sessions`, `chat_messages` | `message_role`, `session_status` |
| `features/agent/models.py` | `search_jobs`, `agent_steps`, `recommendations` | `job_status` |
| `features/search/models.py` | `search_queries`, `crawled_pages` | none |
| `features/admin/models.py` | `admin_audit_log` | none |

`crawled_pages` and `search_queries` may move to `agent/models.py`; this is still to be confirmed.

### Common columns

`id` is the unique identity of a row (UUID). `created_at` and `updated_at` record when a row was created and last changed. They are not repeated in every table below.

## 3. Users

### `users`
The application's copy of a Zitadel user. Login happens in Zitadel, but other tables (chats, favorites) need a local row to point to. Passwords are never stored here. Roles are read from the token, not from this table.

| Column | Purpose |
|---|---|
| `external_auth_id` | The Zitadel `sub` value. The user is found by this when a token arrives (unique) |
| `email` | Display and contact (unique) |
| `last_login_at` | Last login time, for statistics |

## 4. Catalog

### `categories`
Single source for product categories (laptop, phone...). Free text would produce "Laptop", "laptob" and "notebook" as different categories.

| Column | Purpose |
|---|---|
| `slug` | Short name used in code, e.g. `laptop` (unique) |
| `name` | Name shown in the UI |
| `is_active` | If false, no new searches run in this category |

### `category_criteria`
What to look at for a category. For laptops it is RAM and GPU, for phones camera and battery.

| Column | Purpose |
|---|---|
| `category_id` | Which category |
| `version` | A new version is created when the schema or prompt changes, so old searches stay explainable. `(category_id, version)` is unique |
| `criteria_schema` | List of properties to extract (JSON) |
| `prompt_template` | Category-specific part of the LLM prompt. General prompts stay in `prompts.py` |
| `is_active` | Which version is currently used |

### `products`
Products found by the crawler. Stored so the same product is not processed again and recommendations can point to it.

| Column | Purpose |
|---|---|
| `source` + `external_id` | Which site and the product's id on that site. Together unique, so a product is never inserted twice |
| `category_id` | Category link |
| `title` | Product name |
| `price` / `currency` | Price and currency (default `TRY`) |
| `url` | Product page, to link the user to it |
| `image_url` | Product picture |
| `specs` | Cleaned specifications, e.g. `{"ram_gb": 16}`. Rule filtering uses this |
| `raw_data` | Raw crawler output, so data can be re-parsed if the parser was wrong |
| `stock_status` | `in_stock`, `out_of_stock`, `unknown` |
| `content_hash` | Fingerprint of the content; if unchanged, no update is needed |
| `scraped_at` | When the product was last fetched |

### `favorites`
Products a user liked (many-to-many between users and products). `(user_id, product_id)` is unique, so a product cannot be added twice.

| Column | Purpose |
|---|---|
| `user_id` | Who added it |
| `product_id` | Which product |

## 5. Chat

### `chat_sessions`
One conversation. Messages belong to it.

| Column | Purpose |
|---|---|
| `user_id` | Owner |
| `category_id` | Topic of the chat, if known |
| `title` | Chat title |
| `summary` | Short summary of older messages. The LLM gets this instead of the full history |
| `summary_up_to_sequence` | Last message number covered by the summary. Later messages are added as they are |
| `status` | `active` or `archived` |

### `chat_messages`
Individual messages in a chat.

| Column | Purpose |
|---|---|
| `session_id` | Which chat |
| `role` | Who wrote it: `user`, `assistant`, `system`, `tool` |
| `content` | Message content (JSON: plain text or product cards) |
| `sequence` | Order inside the chat. `(session_id, sequence)` is unique |
| `token_count` | Size of the message, used to fit the context budget |
| `is_deleted` | Soft delete: hide instead of really deleting |
| `metadata` | Extra info, e.g. which job produced the message |

## 6. Agent

### `search_jobs`
The **checkpoint** of one search. If a worker crashes, another worker reads this row and continues from the saved step.

| Column | Purpose |
|---|---|
| `session_id` | Which chat the request came from |
| `trigger_message_id` | Which message started the job |
| `current_step` | Where the job is: `plan`, `collect`, `validate`, `research`, `rank`, `done`, `failed` |
| `status` | Overall state: `queued`, `running`, `waiting_user`, `completed`, `failed`, `cancelled` |
| `context_snapshot` | Small summary of the job: filters, id lists, counters. Never raw HTML |
| `replan_count` | How many times the job was re-planned (max 2) |
| `tool_call_count` | How many tools were called (max 8) |
| `cost_usd` | LLM cost spent on this job |
| `last_error` | Last error message |
| `started_at` / `finished_at` | When the job started and ended |

`current_step` is *where* the job is; `status` is *how* it is doing. For example, a job asking the user a question is in `plan` with status `waiting_user`.

### `crawled_pages`
Raw HTML pages fetched by the crawler. They are large, so they live in their own table; `search_jobs` only points to them by id. This also prevents raw HTML from being sent to the LLM by accident.

| Column | Purpose |
|---|---|
| `job_id` | Which job fetched it. `(job_id, url)` is unique |
| `source` | Which site |
| `url` | Page address |
| `http_status` | Whether the page loaded (200) or failed (404, 403) |
| `html` | Raw page content |
| `fetched_at` | When it was fetched |

Old jobs' pages will need a cleanup job later (for example after 7 days).

### `agent_steps`
A trace of every step. It answers "why did the agent recommend this?" and "why was this job so expensive?". Very useful for debugging.

| Column | Purpose |
|---|---|
| `job_id` / `step_number` | Which job, which step in order (unique together) |
| `step` | Which step: `plan`, `collect`, `validate`, `research`, `rank` |
| `input_context` | What the LLM was shown in this step |
| `output` | What the LLM answered |
| `model` | Which model was used (cheap or strong) |
| `prompt_tokens` / `completion_tokens` | Tokens sent and received (cost calculation) |
| `latency_ms` | How long the step took |
| `error` | Error, if the step failed |

### `search_queries`
The user's request turned into a search. Keeps what filters "affordable laptop for rendering" became.

| Column | Purpose |
|---|---|
| `session_id` / `job_id` / `message_id` | Which chat, job and message |
| `raw_query` | The text that was searched |
| `extracted_filters` | Extracted filters, e.g. `{"max_price": 40000, "min_ram": 16}` |
| `search_round` | 1 for the first search, 2 or 3 when the job was re-planned |
| `status` | `pending`, `done`, `failed` |

### `recommendations`
The 3-5 products shown to the user. Without this table the information "which product was recommended and why" is lost.

| Column | Purpose |
|---|---|
| `job_id` | Which job recommended it. `(job_id, product_id)` is unique |
| `product_id` | Which product |
| `rank` | Position (1 is best) |
| `score` | Suitability score |
| `reason` | The LLM's explanation, shown to the user as "why this one" |

## 7. Admin

### `admin_audit_log`
A record of every change made in the Refine admin panel: who did what and when. For security and debugging.

| Column | Purpose |
|---|---|
| `admin_user_id` | The admin who did it |
| `action` | `create`, `update`, `delete` |
| `target_type` | What was changed: `product`, `category_criteria`... |
| `target_id` | Id of the changed item |
| `details` | Before and after values |

## 8. Enums

An enum limits a column to a fixed list of values, which prevents typos.

| Enum | Values | Used in |
|---|---|---|
| `message_role` | `user`, `assistant`, `system`, `tool` | `chat_messages.role` |
| `session_status` | `active`, `archived` | `chat_sessions.status` |
| `job_status` | `queued`, `running`, `waiting_user`, `completed`, `failed`, `cancelled` | `search_jobs.status` |
| `stock_status` | `in_stock`, `out_of_stock`, `unknown` | `products.stock_status` |

`search_jobs.current_step` and `agent_steps.step` are plain `varchar` on purpose: the steps are defined as an enum in code (`machine.py`), so adding a step does not need a migration.
