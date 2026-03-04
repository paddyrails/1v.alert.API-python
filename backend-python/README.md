# 1v-alerts-api (Backend)

Production-ready FastAPI backend with PostgreSQL, JWT auth, and alertdefs CRUD.

## Tech stack

- Python 3.12, FastAPI, Uvicorn
- SQLAlchemy 2.0 (async) + asyncpg, Alembic
- JWT (python-jose), passlib[bcrypt], pydantic-settings
- Docker + docker-compose, GitHub Actions CI

## Quick start

1. Copy `.env.example` to `.env` and set `JWT_SECRET` and `DATABASE_URL` if needed.
2. Start with Docker:

   ```bash
   docker-compose up --build
   ```

3. Run migrations (from host, with DB reachable):

   ```bash
   # If using docker-compose, run inside api container or set DATABASE_URL to localhost:5432
   alembic upgrade head
   ```

   To run migrations from the host when DB is in Docker, use:

   ```bash
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/app alembic upgrade head
   ```

4. Open `http://localhost:8000/docs` for Swagger, `http://localhost:8000/health` for health check.

## Local development (no Docker)

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -e ".[dev]"
cp .env.example .env
# Start Postgres (e.g. local or docker run postgres:16)
alembic upgrade head
uvicorn app.main:app --reload
```

## API

- **Health:** `GET /health` → `{ "status": "ok" }`
- **Auth:** `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/refresh`, `POST /api/auth/logout`
- **AlertDefs (protected):** `POST/GET/PATCH/DELETE /api/alertdefs` (Bearer token required)

## Lint and tests

```bash
ruff check . && ruff format .
pytest
```

## CI

GitHub Actions workflow (`.github/workflows/ci.yml`) runs on push/PR: ruff, pytest, optional docker build.
