# Monorepo Template

A production-ready monorepo template for **FastAPI + Flutter** projects, powered by [Copier](https://copier.readthedocs.io/).

## What You Get

- **Backend**: FastAPI, SQLAlchemy 2.0, Dual PostgreSQL, Redis, fastapi-users (Cookie + Bearer + OAuth)
- **Frontend**: Flutter 3.x, Riverpod, OpenAPI auto-generated client, go_router
- **Infrastructure**: Docker Compose, Alembic dual-DB migrations, background workers
- **DevEx**: Makefile commands, pre-commit hooks, CI/CD (GitHub Actions), 80% coverage enforcement

## Usage

### Generate a New Project

```bash
# Install Copier
pip install copier

# Generate from this template
copier copy gh:nebeel0/monorepo-template my-project

# Or from a local clone
copier copy ./monorepo-template my-project
```

You'll be prompted for:

| Question | Example | Used For |
|----------|---------|----------|
| `project_name` | My Awesome App | README title, Flutter app title |
| `project_slug` | my_awesome_app | Python package, Dart package, DB names, Docker containers |
| `project_description` | A marketplace platform | README, pubspec.yaml, pyproject.toml |
| `author_name` | Ben | pyproject.toml |

### Start Developing

```bash
cd my-project
make build      # Install deps, start Docker, run migrations
make backend    # Terminal 1: API at localhost:8000
make frontend   # Terminal 2: App at localhost:3000
```

### Update an Existing Project

When the template improves, pull changes into your project:

```bash
cd my-project
copier update
```

Copier diffs the template changes against your customizations and merges cleanly.

## Template Architecture

```
copier.yml              # Template configuration and questions
README.md               # This file (excluded from generated projects)
README.md.jinja         # Generated project's README
*.jinja                 # Files processed by Copier (suffix removed)
apps/
  backend/              # FastAPI + SQLAlchemy + Dual PostgreSQL
  frontend/             # Flutter + Riverpod + OpenAPI client
packages/shared/        # Shared libraries
scripts/                # OpenAPI code generation
e2e/                    # Playwright E2E tests
```

Files ending in `.jinja` are processed by Copier during generation — `{{ project_slug }}` and other variables are replaced with your answers. All other files are copied as-is.

## Key Patterns

- **Dual PostgreSQL**: Separate `app_db` (domain data) and `users_db` (auth) with independent engines and migrations
- **Dynamic Router Discovery**: Drop a file in `app/api/v1/things/things.py` with a `router` — it's auto-registered
- **BaseWorker**: Subclass for periodic background tasks with graceful shutdown
- **OpenAPI Auto-Gen**: `make openapi` extracts schema from FastAPI and generates a Dart client
- **Platform Auth**: Web uses cookies, mobile uses Bearer tokens — same backend

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for template development guidelines.
