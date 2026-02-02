# Contributing

## Branch Naming

```
username/type/description
```

Types: `feature/`, `bugfix/`, `chore/`, `hotfix/`

Example: `ben/feature/add-search-endpoint`

## Commit Conventions

Write clear, imperative commit messages:

```
Add user profile endpoint
Fix CORS issue on production
Update Redis connection pooling
```

## Pull Requests

- Fill out the PR template completely
- Include a test plan
- Note any migration or deployment steps
- Request at least one reviewer

## Code Style

### Backend (Python)

- Line length: 100
- Formatter: Black
- Linter: Ruff (E, F, I, UP, B, SIM rules)
- Type checker: MyPy (strict mode)
- All functions must have type hints

### Frontend (Dart/Flutter)

- Line length: 100
- Formatter: `dart format`
- Analyzer: `flutter analyze`
- Use Riverpod for state management
- Use Freezed for data models

## Testing

- Backend: 80% coverage minimum
- Run `make ci` before submitting a PR
- Write tests for all new endpoints
- Use fixtures from `tests/conftest.py`

## Development Setup

```bash
cp .env.example .env
make build
make backend  # Terminal 1
make frontend # Terminal 2
```
