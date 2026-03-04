# Cursor Build Instructions — Python FastAPI + PostgreSQL + JWT + .env (pydantic-settings) + Logging/Error Handling + Docker + CI/CD

## Goal
Generate a production-ready backend API using **FastAPI** with:
- PostgreSQL database (SQLAlchemy 2.0)
- Alembic migrations
- JWT authentication (access + refresh tokens)
- Config via `.env` using `pydantic-settings`
- Structured logging + request correlation ID
- Consistent error responses
- Dockerfile + docker-compose (API + Postgres)
- CI/CD pipeline (GitHub Actions) for lint + tests + build

---

## Tech Stack (Required)
- Python: 3.12
- FastAPI + Uvicorn
- SQLAlchemy 2.0 (async) + asyncpg
- Alembic
- Auth: JWT using `python-jose` (or PyJWT; prefer `python-jose`)
- Password hashing: `passlib[bcrypt]`
- Validation: Pydantic v2
- Config: `pydantic-settings` + `.env`
- Logging: Python `logging` + JSON-ish structured logs (simple, no external libs required)
- Tests: Pytest + httpx + pytest-asyncio + Testcontainers (preferred) OR docker service in CI
- Lint/format: ruff (format + lint)
- Type checking (optional): mypy

---

## Required Project Structure
Create this structure exactly:


backend/
app/
init.py
main.py

core/
  __init__.py
  config.py
  logging.py
  errors.py
  security.py
  deps.py

db/
  __init__.py
  session.py
  base.py

models/
  __init__.py
  user.py
  alertdef.py
  refresh_token.py

schemas/
  __init__.py
  auth.py
  user.py
  alertdef.py
  common.py

repositories/
  __init__.py
  user_repo.py
  alertdef_repo.py
  refresh_token_repo.py

services/
  __init__.py
  auth_service.py
  alertdef_service.py

api/
  __init__.py
  router.py
  health.py
  auth.py
  alertdefs.py

middleware/
  __init__.py
  correlation_id.py
  exception_handler.py

alembic/
env.py
script.py.mako
versions/
(generated)

tests/
init.py
conftest.py
test_auth.py
test_alertdefs.py

.env.example
Dockerfile
docker-compose.yml
pyproject.toml
README.md
.github/
workflows/
ci.yml


---

## API Requirements

### Health
- `GET /health`
Response:
```json
{ "status": "ok" }
Auth (JWT)

POST /api/auth/register
Body:

{ "email": "string", "password": "string", "name": "string (optional)" }

POST /api/auth/login
Body:

{ "email": "string", "password": "string" }

Response:

{
  "accessToken": "string",
  "refreshToken": "string",
  "tokenType": "bearer",
  "user": { "id": "uuid", "email": "string", "name": "string|null" }
}

POST /api/auth/refresh
Body:

{ "refreshToken": "string" }

Response same as login (new access/refresh).

POST /api/auth/logout
Header: Authorization: Bearer <accessToken>
Body:

{ "refreshToken": "string" }

Behavior: revoke the refresh token (store in DB, mark revoked).

Rules:

Password min length: 8

Hash passwords using bcrypt

Email unique

alertdefs (Protected)

All require: Authorization: Bearer <accessToken>

POST /api/alertdefs
Body:

{ "name": "string", "description": "string" }

GET /api/alertdefs?page=&limit=
Response:

{ "items": [AlertDef], "page": 1, "limit": 20, "total": 0 }

GET /api/alertdefs/{id}

PATCH /api/alertdefs/{id}
Body:

{ "name": "string (optional)", "description": "string (optional)" }

DELETE /api/alertdefs/{id} → 204

alertdef shape:

{
  "id": "uuid",
  "name": "string",
  "description": "string|null",  
  "createdAt": "ISO-8601",
  "updatedAt": "ISO-8601"
}
Database Requirements (PostgreSQL)

Use SQLAlchemy async models and mappings.

Tables

users

id (uuid pk)

email (unique, indexed)

password_hash

name (nullable)

created_at, updated_at

alertdefs

id (uuid pk)

user_id (fk users.id, indexed)

title

description (nullable)

completed (bool default false)

created_at, updated_at

refresh_tokens

id (uuid pk)

user_id (fk users.id, indexed)

token_hash (store hashed refresh token, not raw)

revoked (bool)

expires_at (timestamp)

created_at

Migrations

Use Alembic. Provide at least:

Initial migration creating tables + indexes + constraints.

Config Requirements (.env + pydantic-settings)

Create app/core/config.py using pydantic-settings.

.env.example
APP_NAME=fastapi-backend
ENV=development
DEBUG=true

API_HOST=0.0.0.0
API_PORT=8000

DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/app

JWT_ISSUER=fastapi-backend
JWT_AUDIENCE=fastapi-backend
JWT_SECRET=change_me_to_a_long_random_value
JWT_ACCESS_EXPIRES_MINUTES=15
JWT_REFRESH_EXPIRES_DAYS=7

LOG_LEVEL=INFO
CORS_ORIGINS=* // http://localhost:5173,http://localhost:3000

Requirements:

Load env from .env

Validate required fields (fail fast)

Provide Settings singleton dependency

Security Requirements (JWT)

Create app/core/security.py:

Hash password with passlib bcrypt

Create/verify JWT access tokens

Refresh tokens:

generate random refresh token string (secure)

store only hashed refresh token in DB with expiry and revoke flag

on refresh: validate, rotate refresh token (invalidate old one)

Access token includes claims:

sub = user_id

email

iss, aud, exp, iat

Auth dependency:

get_current_user() reads Authorization header

validates JWT

loads user from DB

returns user entity

Logging + Correlation ID

Implement:

app/core/logging.py configure Python logging once at startup

middleware correlation_id.py:

accept X-Correlation-Id if present, else generate UUID

add to response header

include correlation id in logs (via contextvars or request.state)

Log format:

timestamp, level, message, correlationId, path, method, statusCode, durationMs

Error Handling (Consistent Error Shape)

Implement middleware exception_handler.py or FastAPI exception handlers.

All errors must return:

{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}

Handle:

validation errors (400)

auth errors (401/403)

not found (404)

conflict (409) e.g., duplicate email

unhandled exceptions (500)

Do not leak stack traces in production.

FastAPI App Setup

app/main.py must:

initialize settings + logging

include routers from app/api/router.py

attach middleware: correlation id + exception handling

configure CORS using settings

expose /health and /api/*

Dependency Injection + DB Session

Create app/db/session.py:

Async engine from DATABASE_URL

async_sessionmaker

Dependency get_db() yields AsyncSession with proper cleanup

Use repositories/services:

Controllers (routers) call services

Services call repositories

Repositories do all DB operations

Packaging & Tooling (pyproject.toml)

Use Poetry-style or standard PEP 621. Prefer uv/pip compatible.
Required dependencies:

fastapi

uvicorn[standard]

sqlalchemy>=2

asyncpg

alembic

pydantic-settings

python-jose[cryptography]

passlib[bcrypt]

python-multipart (if needed)

ruff

pytest

pytest-asyncio

httpx

testcontainers[postgresql] (preferred for integration tests)

Ruff:

enable formatting and linting

run via ruff check . and ruff format .

Docker Requirements
Dockerfile (multi-stage recommended)

Use python:3.12-slim

Install deps

Copy app code

Run uvicorn: uvicorn app.main:app --host 0.0.0.0 --port 8000

docker-compose.yml

Services:

db: postgres:16 with volume

api: build Dockerfile, depends_on db, env_file .env (or env vars)

Expose:

API: 8000:8000

Postgres: 5432:5432 (optional)

Add Postgres healthcheck and make API wait/retry connection on startup (simple retry loop).

CI/CD (GitHub Actions)

Create .github/workflows/ci.yml:

Trigger on push + PR

Steps:

checkout

setup python 3.12

install dependencies

ruff format check + lint

run pytest

docker build (optional but recommended)

For tests:

Use Testcontainers (preferred) OR run a Postgres service in Actions.
If using service:

configure DATABASE_URL to point to service host

run alembic migrations before tests

Tests (Minimum)

Write integration tests:

Register + login returns tokens

Create alertdef without token → 401

Create alertdef with token → success



Refresh token rotates and old refresh is invalidated

Use httpx AsyncClient + FastAPI test app.

Cursor Execution Steps (Do in this order)

Create project structure and pyproject.toml

Implement config + logging

Implement DB session + models

Implement Alembic config and initial migration

Implement auth (register/login/refresh/logout)

Implement alertdefs CRUD

Implement middleware (correlation + exception handler)

Implement Docker + docker-compose

Implement tests

Implement CI workflow + ensure it passes

Acceptance Checklist

 docker-compose up --build starts API + Postgres

 GET /health returns { "status": "ok" }

 Swagger available at /docs

 Register/login returns access + refresh tokens

 Protected endpoints require JWT

 alertdefs CRUD works

 Refresh rotates refresh token; logout revokes refresh token

 Errors follow standard error shape

 Alembic migration runs cleanly

 ruff check . and ruff format . succeed

 pytest passes locally and in CI

 docker build succeeds in CI

Notes / Constraints

Do NOT store raw refresh tokens in DB; store hashed tokens only.

Avoid print; use structured logging.

Keep controllers thin, business logic in services.

Use async DB access throughout.