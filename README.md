# Project Name

<!-- TODO: Replace with your project description -->

Monorepo combining a Python FastAPI backend with a Flutter cross-platform frontend.

## Architecture

```
apps/
  backend/       # FastAPI + SQLAlchemy + PostgreSQL
  frontend/      # Flutter + Riverpod + Freezed
packages/
  shared/        # Shared libraries
e2e/             # Playwright E2E tests
```

## Tech Stack

| Layer    | Technology                     |
|----------|--------------------------------|
| Backend  | FastAPI, SQLAlchemy 2.0, PostgreSQL 16, Redis 7 |
| Frontend | Flutter 3.x, Riverpod, Freezed, go_router |
| Tooling  | UV, Makefile, Docker Compose, pre-commit |
| CI/CD    | GitHub Actions                 |

## Prerequisites

- Python 3.12+ and [UV](https://docs.astral.sh/uv/)
- [Flutter 3.x](https://docs.flutter.dev/get-started/install)
- [Docker](https://docs.docker.com/get-docker/) and Docker Compose
- [pre-commit](https://pre-commit.com/) (recommended)

## Quick Start

```bash
# 1. Clone and configure
cp .env.example .env        # Edit with your values

# 2. Setup infrastructure
make build                   # Install deps, start Docker, run migrations

# 3. Install git hooks
make hooks                   # Install pre-commit hooks

# 4. Start development (two terminals)
make backend                 # Terminal 1: API at localhost:8000
make frontend                # Terminal 2: App at localhost:3000
```

## Development

### Common Commands

```bash
make help        # Show all available commands
make build       # Setup infrastructure (deps + docker + migrations)
make backend     # Run backend API (port 8000)
make frontend    # Run Flutter web (port 3000)
make test        # Run all tests
make lint        # Run all linters
make format      # Auto-format code
make ci          # Run all CI checks (required before PR)
make coverage    # Tests with coverage
```

### Database

```bash
make migrate                           # Run pending migrations
make migrate-create MSG="add users"    # Create new migration
make migrate-history                   # Show migration history
```

### Code Generation (Frontend)

```bash
make watch       # Watch mode for Freezed/json_serializable
```

### Infrastructure

```bash
make down        # Stop Docker services
make clean       # Stop and remove all data
make kill        # Kill all dev processes
make ports       # Check port status
make smoke-test  # Quick health check
```

## Pre-commit Hooks

Hooks run automatically on `git commit` to enforce code quality:

- **Python**: Ruff linting/formatting, Black, MyPy type checking
- **Flutter**: dart format, flutter analyze
- **General**: Trailing whitespace, merge conflicts, secret detection, branch protection

```bash
make hooks           # Install hooks
make hooks-run       # Run on all files
make hooks-update    # Update hook versions
```

## CI/CD

GitHub Actions runs on push/PR to `main`:

1. **Backend Lint** - Ruff, Black, MyPy
2. **Backend Tests** - pytest with PostgreSQL + Redis services, 80% coverage
3. **Frontend Tests** - flutter analyze + flutter test
4. **Frontend Build** - flutter build web

## Git Workflow

```bash
# Branch naming: username/type/description
git checkout -b ben/feature/add-auth
git checkout -b ben/bugfix/fix-login
git checkout -b ben/chore/update-deps
```

Run `make ci` before submitting pull requests.

## Customizing This Template

1. Find and replace `myapp` with your project name across all files
2. Update `APP_NAME` in `.env.example`
3. Update `name` in `apps/backend/pyproject.toml` and `apps/frontend/pubspec.yaml`
4. Update container names in `docker-compose.yml`
5. Update `CLAUDE.md` and this `README.md` with project-specific details
6. Add your domain models and API endpoints
