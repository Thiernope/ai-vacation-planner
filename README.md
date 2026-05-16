# AI Vacation Planner — Backend

FastAPI backend for the Vacation Planner capstone. Users can register, log in, create trips, and store itineraries.

> Detailed setup and architecture documentation will land in a later PR. The instructions below are enough to boot the project locally.

## Stack

- Python 3.12 with [uv](https://docs.astral.sh/uv/)
- FastAPI + Uvicorn
- PostgreSQL 16 (via Docker Compose)
- SQLAlchemy + Alembic (added in PR #2)
- JWT authentication (added in PR #3)

## Quick start

```bash
# 1. Install Python dependencies (creates .venv automatically)
uv sync

# 2. Start the Postgres container in the background
docker compose up -d

# 3. Run the API with hot reload
uv run uvicorn app.main:app --reload
```

Then open:

- Health check: <http://localhost:8000/health>
- Swagger UI: <http://localhost:8000/docs>

## Environment

Copy `.env.example` to `.env` before running anything that touches the database:

```bash
cp .env.example .env
```

## Status

In active development — see open PRs for what is shipping next.
