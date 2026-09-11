# CarbonIQ API

## Local development with Docker

From the repository root, copy `.env.example` to `.env`, generate a unique local
password, and set both `POSTGRES_PASSWORD` and `DATABASE_URL` in `.env`. Generate
a separate JWT signing secret of at least 32 characters and set
`JWT_SECRET_KEY` in the same ignored file. Never commit that file. Then start
PostgreSQL and FastAPI:

```bash
cp .env.example .env
docker compose up --build
```

The backend waits for PostgreSQL to become healthy, applies every Alembic
migration with `alembic upgrade head`, and then starts on port `8000`.

Access tokens expire after 15 minutes by default. Refresh tokens rotate on use,
are stored only as SHA-256 digests, and are revoked by
`POST /api/v1/auth/logout`.

The public project catalogue supports search, filters, sorting, pagination,
details, inventory, document metadata, and two-to-four-project comparisons.
Writes under `/api/v1/admin/projects` require an administrator token.
Buyer-preference endpoints require authentication and
enforce ownership, so users cannot read or change another user's profiles.
Interactive API documentation is available at `http://127.0.0.1:8000/docs`.

Verify the services:

```bash
curl http://127.0.0.1:8000/api/v1/health
```

Stop the services with `docker compose down`. Add `--volumes` only when you
intentionally want to remove the local PostgreSQL data volume.

## Local development without Docker

With PostgreSQL already running, create `services/api/.env` from its example,
set `DATABASE_URL` to the local connection URL, activate the virtual
environment, and run:

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
