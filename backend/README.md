# AI Personal Knowledge Manager — Backend

## Step 4 status: `documents` model, file upload/list/get/delete (PDF & Markdown only).
## Step 2 status: `users` model, JWT auth (register/login/me).
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

The `users` table migration is already generated and included in
`alembic/versions/`. To apply it to your database:

```bash
alembic upgrade head
```

If you ever change a model later, generate a new migration like this:

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

## Auth endpoints (Step 2)

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"yourpassword123"}'

# Login (returns a JWT)
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"you@example.com","password":"yourpassword123"}'

# Use the token from login to call a protected route
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer <paste-token-here>"
```

You can also test this interactively at `/docs` — click "Authorize",
paste your token, and try `/auth/me` directly in the Swagger UI.

**Password rule:** minimum 8 characters (enforced by the `UserCreate` schema).
**Note on bcrypt version:** `requirements.txt` pins `bcrypt==4.0.1` deliberately.
Newer bcrypt (4.1+) breaks `passlib==1.7.4` due to a removed version
attribute passlib depends on — don't upgrade bcrypt alone without also
upgrading passlib, or password hashing will fail with a cryptic
`AttributeError: module 'bcrypt' has no attribute '__about__'`.

## Document endpoints (Step 4)

Only `.pdf` and `.md`/`.markdown` files are accepted, up to 20MB. All
routes require the `Authorization: Bearer <token>` header from login.

```bash
TOKEN="<paste-your-token-here>"

# Upload
curl -X POST http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/Notes.pdf"

# List your documents
curl http://localhost:8000/api/v1/documents \
  -H "Authorization: Bearer $TOKEN"

# Get one document's metadata
curl http://localhost:8000/api/v1/documents/<document_id> \
  -H "Authorization: Bearer $TOKEN"

# Delete a document (removes both the file and the DB row)
curl -X DELETE http://localhost:8000/api/v1/documents/<document_id> \
  -H "Authorization: Bearer $TOKEN"
```

**Ownership:** every document belongs to the user who uploaded it. Trying
to read or delete someone else's document returns `404` (not `403`) —
this is deliberate, so a user can't even confirm a given document id
exists if it isn't theirs.

**Where files land:** `storage/{user_id}/{document_id}.{ext}` — the
filename on disk is never the original filename, to avoid any path or
collision issues. The original filename is preserved in the database
and returned in API responses.

**Status field:** every document starts as `"uploaded"`. It'll transition
to `"processing"` → `"ready"`/`"failed"` once Step 5 (text extraction)
and Step 6 (embeddings) are wired in — no schema change needed for that.

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
