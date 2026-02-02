# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this codebase.

## Project Overview

This is a monorepo combining a Python FastAPI backend with a Flutter cross-platform frontend.

## Architecture

### Monorepo Structure

```
apps/backend/    # FastAPI Python application
apps/frontend/   # Flutter mobile/web application
packages/shared/ # Shared libraries (future)
scripts/         # Code generation scripts (OpenAPI)
e2e/             # End-to-end tests (Playwright)
```

### Backend Stack

- **FastAPI** with async SQLAlchemy 2.0
- **Dual PostgreSQL 16** databases (app_db + users_db)
- **Redis 7** for caching and auth sessions
- **UV** for package management
- **Alembic** for dual-database migrations
- **fastapi-users** with Cookie + Bearer + OAuth (Google)
- **BaseWorker** pattern for background tasks

### Frontend Stack

- **Flutter 3.x** with Riverpod state management
- **OpenAPI auto-generated client** (dart-dio) from backend schema
- **Freezed** for immutable data models
- **go_router** for navigation
- **Platform-specific auth**: cookies (web) / Bearer tokens (mobile)

## Development Commands

```bash
# Setup
make build              # Full setup (deps + docker + migrations)
make install            # Install all dependencies

# Development
make backend            # Run FastAPI server (port 8000)
make frontend           # Run Flutter web (port 3000)
make workers            # Run background workers (standalone)

# Testing & Quality
make test               # Run all tests
make lint               # Run all linters
make format             # Auto-format code
make ci                 # Run all CI checks (required before PR)
make coverage           # Tests with coverage

# Database
make migrate            # Run migrations (both databases)
make migrate-create MSG="description"  # Create new migration

# Code Generation
make openapi            # Regenerate OpenAPI client from backend
make watch              # Watch mode for Freezed/json_serializable
```

## Key Architecture Patterns

### Dual Database

Two separate PostgreSQL databases with independent engines, sessions, and DI:

```python
from core.database import AppDbSessionDep, UsersDbSessionDep

@router.get("/items")
async def list_items(session: AppDbSessionDep) -> list[ItemRead]:
    result = await session.execute(select(Item))
    return [ItemRead.model_validate(i) for i in result.scalars().all()]
```

- `AppDbSessionDep` — app/domain data (items, etc.)
- `UsersDbSessionDep` — user auth data (fastapi-users)
- Models: `AppDBModel` (app_db), `UserManagementDBModel` (users_db)

### Dynamic Router Discovery

Routers in `app/api/` are auto-discovered. No manual registration needed.

To add a new endpoint:
1. Create `app/api/v1/things/things.py`
2. Export `router = APIRouter()`
3. It's automatically registered with prefix `/v1/things` and tag `things`

Convention: if filename matches directory name, filename is omitted from prefix.

### Auth System

Three auth flows via fastapi-users:
- **Cookie** (web): `/users/cookie/login`
- **Bearer** (mobile): `/users/token/login`
- **Google OAuth**: `/auth/google-bearer` or `/auth/google-cookie`

Use dependency shortcuts in endpoints:
```python
from app.dependencies.auth import current_user, current_active_verified_user
```

### Background Workers

Subclass `BaseWorker` for periodic background tasks:

```python
from app.workers.base import BaseWorker

class MyWorker(BaseWorker):
    def __init__(self):
        super().__init__(name="my_worker", interval_seconds=60)

    async def process(self, session: AsyncSession) -> None:
        # Your logic here
        pass
```

Register in `app/workers/run.py` and `app/main.py` lifespan.

### OpenAPI Client Generation

The Flutter frontend uses an auto-generated API client:
1. Backend schema is extracted from FastAPI (no running server needed)
2. `make openapi` regenerates the Dart client
3. Platform-specific setup: cookies (web) vs Bearer (mobile)

## Development Practices

### Test-Driven Development

1. Write tests first
2. Run tests to see them fail
3. Implement minimum code to make tests pass
4. Refactor while keeping tests green

### Code Coverage

- **Backend**: 80% minimum enforced
- **Frontend**: Run `flutter test --coverage`

### Git Workflow

Branch naming: `username/type/description`

Types: `feature/`, `bugfix/`, `chore/`, `hotfix/`

## Important Notes

- Always use async/await for database operations
- Never commit `.env` files
- Run `make ci` before submitting PRs
- Run `make openapi` after changing backend API schemas
- Type hints are mandatory for Python (mypy strict mode)
- Two databases: use `AppDbSessionDep` for domain data, `UsersDbSessionDep` for auth
