.PHONY: help build dev install backend frontend
.PHONY: test test-backend test-frontend lint lint-backend lint-frontend
.PHONY: format coverage ci clean down
.PHONY: migrate migrate-create migrate-history
.PHONY: hooks hooks-install hooks-update hooks-run
.PHONY: watch kill ports smoke-test
.PHONY: e2e-build e2e-test e2e-test-headed e2e-up e2e-down e2e-report
.PHONY: openapi workers

# Use bash for echo -e support
SHELL := /bin/bash

# Colors
CYAN := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

# Directories
BACKEND_DIR := apps/backend
FRONTEND_DIR := apps/frontend
E2E_DIR := e2e

.DEFAULT_GOAL := help

#==============================================================================
# HELP
#==============================================================================

help: ## Show this help message
	@echo ""
	@echo -e "$(CYAN)Monorepo Development Commands$(RESET)"
	@echo ""
	@echo -e "$(GREEN)Quick Start:$(RESET)"
	@echo "  make build              Setup infrastructure (deps + docker + migrations)"
	@echo "  make backend            Run backend API (localhost:8000)"
	@echo "  make frontend           Run Flutter web (localhost:3000)"
	@echo ""
	@echo -e "$(GREEN)Development:$(RESET)"
	@grep -E '^(build|install|dev|backend|frontend|watch|openapi|workers):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-18s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(GREEN)Testing & Quality:$(RESET)"
	@grep -E '^(test|lint|format|analyze|coverage|ci|smoke-test):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-18s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(GREEN)Database:$(RESET)"
	@grep -E '^(migrate|migrate-create|migrate-history):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-18s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(GREEN)Infrastructure:$(RESET)"
	@grep -E '^(down|clean|kill|ports):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-18s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo -e "$(GREEN)Git Hooks:$(RESET)"
	@grep -E '^(hooks|hooks-install|hooks-update|hooks-run):.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(YELLOW)%-18s$(RESET) %s\n", $$1, $$2}'
	@echo ""

#==============================================================================
# SETUP & BUILD
#==============================================================================

build: ## Setup infrastructure (deps + docker + migrations)
	@echo -e "$(CYAN)Setting up infrastructure...$(RESET)"
	@echo ""
	@echo -e "$(CYAN)Step 1/4: Validating environment...$(RESET)"
	@if [ ! -f .env ]; then \
		echo -e "$(RED)Missing .env file!$(RESET)"; \
		echo -e "$(YELLOW)Run: cp .env.example .env$(RESET)"; \
		exit 1; \
	fi
	@echo -e "$(GREEN)Root .env found$(RESET)"
	@ln -sf ../../.env $(BACKEND_DIR)/.env
	@echo -e "$(GREEN)Backend .env symlinked$(RESET)"
	@echo ""
	@echo -e "$(CYAN)Step 2/4: Installing dependencies...$(RESET)"
	@cd $(BACKEND_DIR) && uv sync
	@echo -e "$(GREEN)Backend dependencies installed$(RESET)"
	@cd $(FRONTEND_DIR) && flutter pub get > /dev/null 2>&1
	@echo -e "$(GREEN)Frontend dependencies installed$(RESET)"
	@echo ""
	@echo -e "$(CYAN)Step 3/4: Starting Docker infrastructure...$(RESET)"
	@docker compose up -d
	@echo -e "$(GREEN)Infrastructure started$(RESET)"
	@echo ""
	@echo -e "$(CYAN)Step 4/4: Running database migrations...$(RESET)"
	@sleep 5
	@cd $(BACKEND_DIR) && uv run alembic upgrade head
	@echo -e "$(GREEN)Migrations complete$(RESET)"
	@echo ""
	@echo -e "$(GREEN)Infrastructure ready! Run 'make backend' and 'make frontend' in separate terminals.$(RESET)"

install: ## Install all dependencies (backend + frontend)
	@echo -e "$(CYAN)Installing backend dependencies (UV)...$(RESET)"
	@cd $(BACKEND_DIR) && uv sync
	@echo -e "$(GREEN)Backend dependencies installed$(RESET)"
	@echo -e "$(CYAN)Installing frontend dependencies (Flutter)...$(RESET)"
	@cd $(FRONTEND_DIR) && flutter pub get
	@echo -e "$(GREEN)Frontend dependencies installed$(RESET)"

dev: ## Show development server instructions
	@echo -e "$(CYAN)Start these in separate terminals:$(RESET)"
	@echo ""
	@echo -e "$(YELLOW)Terminal 1 - Backend API:$(RESET)"
	@echo "  make backend"
	@echo ""
	@echo -e "$(YELLOW)Terminal 2 - Frontend App:$(RESET)"
	@echo "  make frontend"
	@echo ""

#==============================================================================
# DEVELOPMENT
#==============================================================================

backend: ## Run backend API server (port 8000)
	@echo -e "$(CYAN)Starting FastAPI development server...$(RESET)"
	cd $(BACKEND_DIR) && uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend: ## Run Flutter web app (port 3000)
	@echo -e "$(CYAN)Running Flutter web...$(RESET)"
	cd $(FRONTEND_DIR) && flutter run -d chrome --web-port=3000 --dart-define=ENVIRONMENT=dev

watch: ## Watch mode for frontend code generation (Freezed, json_serializable)
	@echo -e "$(CYAN)Starting code generation watcher...$(RESET)"
	@cd $(FRONTEND_DIR) && dart run build_runner watch --delete-conflicting-outputs

openapi: ## Regenerate OpenAPI schema and Dart client from backend
	@echo -e "$(CYAN)Regenerating OpenAPI client...$(RESET)"
	@cd $(BACKEND_DIR) && uv run python ../../scripts/regenerate_openapi.py
	@echo -e "$(GREEN)OpenAPI client regenerated$(RESET)"

workers: ## Run background workers (standalone process)
	@echo -e "$(CYAN)Starting background workers...$(RESET)"
	cd $(BACKEND_DIR) && uv run python -m app.workers.run

#==============================================================================
# TESTING & QUALITY
#==============================================================================

test-backend: ## Run backend tests
	@echo -e "$(CYAN)Running backend tests...$(RESET)"
	@cd $(BACKEND_DIR) && uv run pytest -v
	@echo -e "$(GREEN)Backend tests passed$(RESET)"

test-frontend: ## Run frontend tests
	@echo -e "$(CYAN)Running frontend tests...$(RESET)"
	@cd $(FRONTEND_DIR) && flutter test
	@echo -e "$(GREEN)Frontend tests passed$(RESET)"

test: test-backend test-frontend ## Run all tests (backend + frontend)
	@echo -e "$(GREEN)All tests passed!$(RESET)"

lint-backend: ## Lint backend code
	@echo -e "$(CYAN)Linting backend code...$(RESET)"
	@cd $(BACKEND_DIR) && uv run ruff check .
	@cd $(BACKEND_DIR) && uv run ruff format --check .
	@cd $(BACKEND_DIR) && uv run mypy .
	@echo -e "$(GREEN)Backend lint passed$(RESET)"

lint-frontend: ## Lint frontend code
	@echo -e "$(CYAN)Linting frontend code...$(RESET)"
	@cd $(FRONTEND_DIR) && dart format --output=none --set-exit-if-changed .
	@cd $(FRONTEND_DIR) && flutter analyze --no-fatal-infos
	@echo -e "$(GREEN)Frontend lint passed$(RESET)"

lint: lint-backend lint-frontend ## Run all linters (backend + frontend)
	@echo -e "$(GREEN)All lint checks passed!$(RESET)"

format: ## Auto-fix formatting (backend + frontend)
	@echo -e "$(CYAN)Formatting backend code...$(RESET)"
	@cd $(BACKEND_DIR) && uv run ruff format .
	@cd $(BACKEND_DIR) && uv run ruff check . --fix
	@echo -e "$(GREEN)Backend formatted$(RESET)"
	@echo -e "$(CYAN)Formatting frontend code...$(RESET)"
	@cd $(FRONTEND_DIR) && dart format .
	@echo -e "$(GREEN)Frontend formatted$(RESET)"

analyze: ## Analyze code quality (mypy + flutter analyzer)
	@echo -e "$(CYAN)Analyzing backend code (mypy)...$(RESET)"
	@cd $(BACKEND_DIR) && uv run mypy .
	@echo -e "$(GREEN)Backend type check passed$(RESET)"
	@echo -e "$(CYAN)Analyzing frontend code...$(RESET)"
	@cd $(FRONTEND_DIR) && flutter analyze
	@echo -e "$(GREEN)Frontend analysis passed$(RESET)"

coverage: ## Run tests with coverage reports
	@echo -e "$(CYAN)Backend coverage...$(RESET)"
	@cd $(BACKEND_DIR) && uv run pytest --cov=app --cov=core \
		--cov-report=html --cov-report=term --cov-report=xml \
		--cov-fail-under=80 -v
	@echo -e "$(GREEN)Coverage report: $(BACKEND_DIR)/htmlcov/$(RESET)"
	@echo -e "$(CYAN)Frontend coverage...$(RESET)"
	@cd $(FRONTEND_DIR) && flutter test --coverage
	@echo -e "$(GREEN)Frontend coverage generated$(RESET)"

ci: lint-backend lint-frontend test-backend test-frontend ## Run all CI checks - required before PR
	@echo ""
	@echo -e "$(GREEN)All CI checks passed! Ready to submit a pull request.$(RESET)"

smoke-test: ## Quick health check (API + infrastructure)
	@echo -e "$(CYAN)Running smoke tests...$(RESET)"
	@if curl -sf http://localhost:8000/health > /dev/null 2>&1; then \
		echo -e "$(GREEN)Backend healthy$(RESET)"; \
	else \
		echo -e "$(RED)Backend not responding$(RESET)"; \
		exit 1; \
	fi
	@echo -e "$(GREEN)Smoke tests passed!$(RESET)"

#==============================================================================
# DATABASE
#==============================================================================

migrate: ## Run pending database migrations
	@echo -e "$(CYAN)Running database migrations...$(RESET)"
	@cd $(BACKEND_DIR) && uv run alembic upgrade head
	@echo -e "$(GREEN)Migrations complete$(RESET)"

migrate-create: ## Create a new migration (usage: make migrate-create MSG="description")
	@if [ -z "$(MSG)" ]; then \
		echo -e "$(RED)Error: MSG parameter required$(RESET)"; \
		echo -e "$(YELLOW)Usage: make migrate-create MSG=\"your migration description\"$(RESET)"; \
		exit 1; \
	fi
	@echo -e "$(CYAN)Creating new migration: $(MSG)$(RESET)"
	@cd $(BACKEND_DIR) && uv run alembic revision --autogenerate -m "$(MSG)"
	@echo -e "$(GREEN)Migration created. Review it before running 'make migrate'.$(RESET)"

migrate-history: ## Show migration history
	@cd $(BACKEND_DIR) && uv run alembic history

#==============================================================================
# INFRASTRUCTURE
#==============================================================================

down: ## Stop Docker services
	@echo -e "$(CYAN)Stopping Docker services...$(RESET)"
	docker compose down
	@echo -e "$(GREEN)Services stopped.$(RESET)"

clean: ## Stop services and remove all data
	@echo -e "$(YELLOW)WARNING: This will delete all data!$(RESET)"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	docker compose down -v --remove-orphans
	@echo -e "$(GREEN)All data removed.$(RESET)"

kill: ## Kill all dev processes
	@echo -e "$(CYAN)Killing all dev processes...$(RESET)"
	@lsof -ti:8000 | xargs kill -9 2>/dev/null || true
	@pkill -f "flutter.*run.*3000" 2>/dev/null || true
	@lsof -ti:3000 | xargs kill -9 2>/dev/null || true
	@echo -e "$(GREEN)All processes killed$(RESET)"

ports: ## Check development port status
	@echo -e "$(CYAN)Development Port Status:$(RESET)"
	@echo ""
	@echo -e "$(YELLOW)Backend (8000):$(RESET)"
	@lsof -i:8000 2>/dev/null || echo "  Available"
	@echo ""
	@echo -e "$(YELLOW)Frontend (3000):$(RESET)"
	@lsof -i:3000 2>/dev/null || echo "  Available"
	@echo ""
	@echo -e "$(YELLOW)PostgreSQL App DB (5434):$(RESET)"
	@lsof -i:5434 2>/dev/null || echo "  Available"
	@echo ""
	@echo -e "$(YELLOW)PostgreSQL Users DB (5435):$(RESET)"
	@lsof -i:5435 2>/dev/null || echo "  Available"
	@echo ""
	@echo -e "$(YELLOW)Redis (6381):$(RESET)"
	@lsof -i:6381 2>/dev/null || echo "  Available"

#==============================================================================
# E2E TESTING
#==============================================================================

e2e-build: ## Build E2E test containers
	@echo -e "$(CYAN)Building Flutter web for E2E...$(RESET)"
	@cd $(FRONTEND_DIR) && flutter build web --release --dart-define=ENVIRONMENT=dev
	@echo -e "$(GREEN)Flutter web built$(RESET)"
	@echo -e "$(CYAN)Building E2E Docker containers...$(RESET)"
	@cd $(E2E_DIR) && docker compose build
	@echo -e "$(GREEN)E2E containers built$(RESET)"

e2e-test: ## Run E2E tests (headless)
	@echo -e "$(CYAN)Running E2E tests...$(RESET)"
	@cd $(E2E_DIR) && docker compose run --rm playwright npx playwright test
	@echo -e "$(GREEN)E2E tests complete$(RESET)"

e2e-test-headed: ## Run E2E tests with visible browser
	@cd $(E2E_DIR) && docker compose run --rm playwright npx playwright test --headed

e2e-up: ## Start E2E environment
	@cd $(E2E_DIR) && docker compose up -d
	@echo -e "$(GREEN)E2E environment started$(RESET)"

e2e-down: ## Stop E2E environment
	@cd $(E2E_DIR) && docker compose down
	@echo -e "$(GREEN)E2E environment stopped$(RESET)"

e2e-report: ## Open Playwright HTML report
	@cd $(E2E_DIR) && npx playwright show-report playwright-report

#==============================================================================
# GIT HOOKS
#==============================================================================

hooks: hooks-install ## Setup pre-commit hooks

hooks-install: ## Install pre-commit hooks
	@echo -e "$(CYAN)Installing pre-commit hooks...$(RESET)"
	@if command -v pre-commit > /dev/null 2>&1; then \
		pre-commit install; \
		echo -e "$(GREEN)Pre-commit hooks installed$(RESET)"; \
	else \
		echo -e "$(RED)pre-commit not found!$(RESET)"; \
		echo -e "$(YELLOW)Install with: pip install pre-commit$(RESET)"; \
		echo -e "$(YELLOW)Or: uv tool install pre-commit$(RESET)"; \
		exit 1; \
	fi

hooks-update: ## Update pre-commit hook versions
	@pre-commit autoupdate

hooks-run: ## Run pre-commit hooks on all files
	@pre-commit run --all-files
