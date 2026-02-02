# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with this codebase.

## Project Overview

<!-- TODO: Replace with your project description -->

This is a monorepo combining a Python FastAPI backend with a Flutter cross-platform frontend.

## Architecture

### Monorepo Structure

```
apps/backend/    # FastAPI Python application
apps/frontend/   # Flutter mobile/web application
packages/shared/ # Shared libraries (future)
e2e/             # End-to-end tests (Playwright)
```

### Backend Stack

- **FastAPI** with async SQLAlchemy 2.0
- **PostgreSQL 16** database
- **Redis 7** for caching
- **UV** for package management
- **Alembic** for migrations

### Frontend Stack

- **Flutter 3.x** with Riverpod state management
- **Freezed** for immutable data models
- **go_router** for navigation
- **Dio** for HTTP client

## Development Commands

```bash
# Setup
make build              # Full setup (deps + docker + migrations)
make install            # Install all dependencies

# Development
make backend            # Run FastAPI server (port 8000)
make frontend           # Run Flutter web (port 3000)

# Testing & Quality
make test               # Run all tests
make lint               # Run all linters
make format             # Auto-format code
make ci                 # Run all CI checks (required before PR)
make coverage           # Tests with coverage

# Database
make migrate            # Run migrations
make migrate-create MSG="description"  # Create new migration

# Code Generation
make watch              # Watch mode for Freezed/json_serializable
```

## Code Patterns

### Backend Dependency Injection

```python
from core.database import DbSessionDep

@router.get("/items")
async def list_items(session: DbSessionDep) -> list[ItemRead]:
    result = await session.execute(select(Item))
    return [ItemRead.model_validate(i) for i in result.scalars().all()]
```

### Frontend State Management

```dart
// Using Riverpod
final itemsProvider = StateNotifierProvider<ItemsNotifier, ItemsState>((ref) {
  return ItemsNotifier(ref);
});

// In widget
final state = ref.watch(itemsProvider);
```

### Frontend Data Models

```dart
@freezed
class Item with _$Item {
  const factory Item({
    required String id,
    required String title,
    String? description,
  }) = _Item;

  factory Item.fromJson(Map<String, dynamic> json) => _$ItemFromJson(json);
}
```

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
- Run `flutter pub run build_runner build` after modifying Freezed models
- Type hints are mandatory for Python (mypy strict mode)
