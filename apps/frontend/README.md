# Frontend

Flutter cross-platform application (iOS, Android, Web).

## Quick Start

```bash
# From repo root
make frontend    # Run Flutter web (port 3000)
```

## Stack

- **Flutter 3.x** - Cross-platform UI framework
- **Riverpod** - State management
- **Freezed** - Immutable data models
- **go_router** - Declarative routing
- **Dio** - HTTP client

## Commands

```bash
make install-frontend     # Install deps
make test-frontend        # Run tests
make lint-frontend        # Run linters
make watch                # Code generation watch mode
```

## Code Generation

After modifying Freezed models, run:

```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

Or use watch mode: `make watch`
