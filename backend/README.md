# AI Personal Knowledge Manager — Backend

## Step 1 status: App skeleton, config, DB session, Alembic wiring, health check.

## Prerequisites
- Python 3.11+
- PostgreSQL running locally (or accessible remotely)

## Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# edit .env: set DATABASE_URL to your local Postgres connection string
```

Create the database (if it doesn't exist yet):

```bash
# using psql
createdb ai_pkm
```

## Run

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`.
Interactive docs: `http://localhost:8000/docs`

## Test it

1. Basic liveness check (no DB required):
   ```bash
   curl http://localhost:8000/api/v1/health
   # -> {"status": "ok"}
   ```

2. Database connectivity check:
   ```bash
   curl http://localhost:8000/api/v1/health/db
   # -> {"status": "ok", "database": "connected"}
   ```
   If this fails, double-check `DATABASE_URL` in `.env` and that Postgres is running.

## Alembic (migrations)

No models exist yet in Step 1, so there's nothing to migrate. Once we add
the `users` model in Step 2, migrations will be run like this:

```bash
alembic revision --autogenerate -m "create users table"
alembic upgrade head
```

This is verified to work correctly at the end of Step 1 by generating an
empty migration (see below) — just to confirm Alembic can talk to the DB
before we start adding real models.

```bash
alembic revision -m "step1: verify alembic setup"
alembic upgrade head
```

You should see a new file in `alembic/versions/` and Alembic should report
it applied the migration without errors.

## Project layout

```
app/
  main.py            # FastAPI app factory
  core/               # config, exceptions
  database/           # engine, session, declarative base
  api/v1/              # routers (health.py for now)
  models/              # SQLAlchemy models (empty until Step 2)
  schemas/             # Pydantic schemas (empty until Step 2)
  repositories/        # DB access layer (empty until Step 2)
  services/            # business logic (empty until Step 2)
  rag/                 # RAG pipeline (empty until Step 5+)
  utils/
alembic/               # migrations
storage/                # uploaded files land here (Step 4+)
```
