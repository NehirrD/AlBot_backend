# AlBot Backend

AlBot helps people find the right product. The user writes a request, for example *"I want an affordable laptop for rendering"*. The system finds the minimum requirements for that job, searches the web, collects many products, and recommends the best 3-5.

> **Status:** early development. At the moment, login with Zitadel and role checks (`user` and `admin`) are working. The search agent is not built yet.

## Tech stack

- **API:** FastAPI
- **Database:** PostgreSQL (SQLAlchemy, Alembic)
- **Login and roles:** Zitadel (JWT)
- **Later:** RabbitMQ, Redis, SearXNG, Crawl4AI, LLM

More details are in [`docs/architecture.md`](docs/architecture.md) and [`docs/database.md`](docs/database.md).

## Requirements

- Python 3.12
- [Poetry](https://python-poetry.org/)
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (it must be running)

## Setup

### 1. Install the packages

```bash
poetry install
```

### 2. Create your `.env` file

Copy the example file and fill in the values:

```bash
cp .env.example .env
```

The Zitadel values (`ZITADEL_CLIENT_ID` and `ZITADEL_PROJECT_ID`) come from step 4 below.

> Never commit `.env`. It contains passwords.

### 3. Start Zitadel

Start only the services we need. Do not run `docker compose up` without names, because it will try to download every image.

```bash
docker compose up -d db zitadel zitadel_login
docker compose ps
```

Wait until `zitadel` is `healthy` (1-2 minutes on the first start).

### 4. Set up Zitadel (one time)

Open the console: <http://localhost:8080/ui/console>

Login: `zitadel-admin@zitadel.localhost` with the password `ZITADEL_ADMIN_PASSWORD` from your `.env` (the default is `Password1!`).

Then:

1. **Create a project** named `albot`. Turn on **Return user roles during authentication**.
2. **Add two roles** to the project: `admin` and `user`.
3. **Create an application** named `albot-web`: type **Web**, authentication method **PKCE**.
   - Turn on **Development Mode**.
   - Redirect URIs:
     - `http://localhost:8000/docs/oauth2-redirect`
     - `http://127.0.0.1:8000/docs/oauth2-redirect`
   - In the token settings, set **Auth Token Type** to **JWT** and add the user roles to the access token.
4. **Create a test user** (turn on "email verified") and give roles in **Role Assignments**: `admin` for the admin user, `user` for the test user.
5. Copy the **Client ID** (from the application) and the **Project ID** (from the project) into your `.env`.

### 5. Run the API

```bash
poetry run uvicorn main:app --reload --app-dir src
```

Open <http://localhost:8000/docs>, click **Authorize**, and log in.

To check your login, call `GET /me`. It returns your user id and roles. `GET /admin-only` works only for admins (others get `403`).

> To test two users at the same time, use a normal browser window for one user and a private window for the other.


## Common problems

| Problem | Solution |
|---|---|
| `docker` cannot connect to the engine | Start Docker Desktop and wait until it is running |
| `redirect_uri is missing` | Add the exact redirect URI in the Zitadel application |
| Roles are empty or the token is not a JWT | Check the application's token settings (JWT, add roles) |
| `Invalid audience` or `Invalid issuer` | Check `ZITADEL_PROJECT_ID` and `ZITADEL_ISSUER` in `.env`, then restart the API |
| Settings change has no effect | Restart `uvicorn` (the `.env` file is read only at startup) |
