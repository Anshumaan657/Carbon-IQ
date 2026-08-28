# CarbonIQ API

## Local development with Docker

From the repository root, copy `.env.example` to `.env`, then start PostgreSQL
and FastAPI:

```bash
cp .env.example .env
docker compose up --build
```

The backend waits for PostgreSQL to become healthy, applies every Alembic
migration with `alembic upgrade head`, and then starts on port `8000`.

Verify the services:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Stop the services with `docker compose down`. Add `--volumes` only when you
intentionally want to remove the local PostgreSQL data volume.

## Local development without Docker

With PostgreSQL already running, create `services/api/.env` from its example,
activate the virtual environment, and run:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

The credentials in `.env.example` are development-only and must never be
reused in production.

## Tests

The migration test creates a uniquely named, empty PostgreSQL schema, upgrades
that isolated namespace to the current Alembic revision, verifies the revision,
and drops the temporary schema afterward. This exercises clean-state migrations
without granting the application role permission to create arbitrary databases.

```bash
python -m pytest -v
```
