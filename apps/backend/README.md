# Backend

FastAPI application with async SQLAlchemy and PostgreSQL.

## Quick Start

```bash
# From repo root
make build      # Setup infrastructure
make backend    # Start dev server (port 8000)
```

## Stack

- **FastAPI** - Async web framework
- **SQLAlchemy 2.0** - Async ORM
- **PostgreSQL 16** - Database
- **Redis 7** - Caching
- **UV** - Package management
- **Alembic** - Database migrations

## Commands

```bash
make install-backend      # Install deps
make test-backend         # Run tests
make lint-backend         # Run linters
make format-backend       # Auto-format code
make coverage-backend     # Tests with coverage
make migrate              # Run migrations
make migrate-create MSG="description"  # New migration
```
