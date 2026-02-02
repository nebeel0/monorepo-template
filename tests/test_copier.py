"""Tests for the Copier monorepo template.

Verifies that `copier copy` generates a correct project with all template
variables substituted, proper directory structure, and no leftover artifacts.

Best practices applied:
- Session-scoped fixture: template generated once, shared across read-only tests
- Function-scoped fixtures only for tests needing different template data
- YAML/TOML parse validity tests
- .copier-answers.yml verification
- Generated CI content validation
"""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path

import pytest
import yaml
from copier import run_copy

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent

DEFAULT_DATA = {
    "project_name": "Test Project",
    "project_slug": "test_project",
    "project_description": "A test project for CI",
    "author_name": "CI Bot",
}

# ── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture(scope="session")
def generated_project(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Generate a project once, shared across all read-only tests."""
    dst = tmp_path_factory.mktemp("output")
    run_copy(
        str(TEMPLATE_ROOT),
        str(dst),
        data=DEFAULT_DATA,
        vcs_ref="HEAD",
        defaults=True,
        unsafe=True,
    )
    return dst


# ── Generation ──────────────────────────────────────────────────────────────


class TestGeneration:
    """Copier generates a project without errors."""

    def test_generation_succeeds(self, generated_project: Path) -> None:
        assert generated_project.is_dir()

    def test_git_initialized(self, generated_project: Path) -> None:
        assert (generated_project / ".git").is_dir()

    def test_env_created_from_example(self, generated_project: Path) -> None:
        env = generated_project / ".env"
        example = generated_project / ".env.example"
        assert env.is_file()
        assert env.read_text() == example.read_text()


# ── Directory Structure ─────────────────────────────────────────────────────


EXPECTED_DIRS = [
    "apps/backend",
    "apps/backend/app/api/v1/items",
    "apps/backend/app/auth",
    "apps/backend/app/dependencies",
    "apps/backend/app/models",
    "apps/backend/app/routers",
    "apps/backend/app/workers",
    "apps/backend/core/schemas",
    "apps/backend/tests",
    "apps/backend/alembic/versions",
    "apps/frontend",
    "apps/frontend/lib/core/client",
    "apps/frontend/lib/core/services",
    "apps/frontend/lib/core/widgets",
    "apps/frontend/lib/core/theme",
    "apps/frontend/lib/features",
    "apps/frontend/lib/router",
    "apps/frontend/schema",
    "scripts",
    "packages/shared",
    "e2e",
    "docs",
    ".github/workflows",
]


class TestDirectoryStructure:
    @pytest.mark.parametrize("rel_dir", EXPECTED_DIRS)
    def test_directory_exists(self, generated_project: Path, rel_dir: str) -> None:
        assert (generated_project / rel_dir).is_dir(), f"Missing directory: {rel_dir}"


# ── Key Files ───────────────────────────────────────────────────────────────

EXPECTED_FILES = [
    # Root
    "Makefile",
    ".gitignore",
    ".gitattributes",
    "CONTRIBUTING.md",
    "CLAUDE.md",
    "README.md",
    "docker-compose.yml",
    "docker-compose.prod.yml",
    ".env.example",
    # Backend core
    "apps/backend/pyproject.toml",
    "apps/backend/Dockerfile",
    "apps/backend/entrypoint.sh",
    "apps/backend/.dockerignore",
    "apps/backend/alembic.ini",
    "apps/backend/alembic/env.py",
    "apps/backend/core/config.py",
    "apps/backend/core/database.py",
    "apps/backend/core/exceptions.py",
    "apps/backend/core/logging.py",
    "apps/backend/core/schemas/base.py",
    "apps/backend/core/schemas/item.py",
    "apps/backend/core/schemas/users.py",
    # Backend app
    "apps/backend/app/main.py",
    "apps/backend/app/api/v1/items/items.py",
    "apps/backend/app/routers/dynamic_endpoints.py",
    "apps/backend/app/routers/service_endpoints.py",
    "apps/backend/app/routers/fastapi_users_endpoints.py",
    "apps/backend/app/dependencies/auth.py",
    "apps/backend/app/auth/user_manager.py",
    "apps/backend/app/models/item.py",
    "apps/backend/app/models/user.py",
    "apps/backend/app/workers/base.py",
    "apps/backend/app/workers/example.py",
    "apps/backend/app/workers/run.py",
    # Backend tests
    "apps/backend/tests/conftest.py",
    "apps/backend/tests/test_health.py",
    # Frontend
    "apps/frontend/pubspec.yaml",
    "apps/frontend/build.yaml",
    "apps/frontend/analysis_options.yaml",
    "apps/frontend/openapi_generator_config.json",
    "apps/frontend/lib/main.dart",
    "apps/frontend/lib/router/app_router.dart",
    "apps/frontend/lib/core/client/app_client.dart",
    "apps/frontend/lib/core/client/mobile.dart",
    "apps/frontend/lib/core/client/web.dart",
    "apps/frontend/lib/core/services/storage_service.dart",
    "apps/frontend/lib/core/widgets/error_view.dart",
    # Scripts
    "scripts/regenerate_openapi.py",
    "scripts/patch_openapi_client.py",
    # GitHub
    ".github/pull_request_template.md",
    ".github/workflows/ci.yml",
]


class TestKeyFiles:
    @pytest.mark.parametrize("rel_path", EXPECTED_FILES)
    def test_file_exists(self, generated_project: Path, rel_path: str) -> None:
        assert (generated_project / rel_path).is_file(), f"Missing file: {rel_path}"


# ── Excluded Artifacts ──────────────────────────────────────────────────────


class TestExcludedArtifacts:
    def test_no_copier_yml(self, generated_project: Path) -> None:
        assert not (generated_project / "copier.yml").exists()

    def test_no_jinja_files(self, generated_project: Path) -> None:
        jinja_files = list(generated_project.rglob("*.jinja"))
        assert jinja_files == [], f"Found .jinja files: {jinja_files}"

    def test_no_template_test_files(self, generated_project: Path) -> None:
        """Template test files should not appear in generated project."""
        assert not (generated_project / "tests/test_copier.py").exists()
        # apps/backend/tests/ must still exist
        assert (generated_project / "apps/backend/tests/conftest.py").is_file()

    def test_no_root_pyproject(self, generated_project: Path) -> None:
        """Root pyproject.toml (template config) should be excluded."""
        assert not (generated_project / "pyproject.toml").exists()
        # apps/backend/pyproject.toml must still exist
        assert (generated_project / "apps/backend/pyproject.toml").is_file()

    def test_no_template_ci_workflow(self, generated_project: Path) -> None:
        """Template CI workflow should not appear in generated project."""
        assert not (generated_project / ".github/workflows/template-tests.yml").exists()
        # Generated project CI must exist
        assert (generated_project / ".github/workflows/ci.yml").is_file()


# ── No Myapp Remnants ───────────────────────────────────────────────────────

SEARCHABLE_EXTENSIONS = {
    ".py", ".yaml", ".yml", ".toml", ".dart", ".md", ".sh", ".ini", ".cfg",
    ".json", ".mako",
}


class TestNoMyappRemnants:
    def test_no_myapp_in_any_file(self, generated_project: Path) -> None:
        violations = []
        for path in generated_project.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in SEARCHABLE_EXTENSIONS:
                continue
            # skip .git internals
            if ".git" in path.parts:
                continue
            content = path.read_text(errors="ignore")
            if "myapp" in content:
                violations.append(str(path.relative_to(generated_project)))
        assert violations == [], f"Files still contain 'myapp': {violations}"


# ── No Raw Jinja Syntax ────────────────────────────────────────────────────


class TestNoJinjaSyntax:
    def test_no_raw_jinja_in_output(self, generated_project: Path) -> None:
        """No {{ or {% in output, except GitHub Actions ${{ }} syntax."""
        violations = []
        for path in generated_project.rglob("*"):
            if not path.is_file():
                continue
            if path.suffix not in SEARCHABLE_EXTENSIONS:
                continue
            if ".git" in path.parts:
                continue
            content = path.read_text(errors="ignore")
            for marker in ("{%", "%}"):
                if marker in content:
                    violations.append(f"{path.relative_to(generated_project)}: {marker}")
            # {{ is OK in GitHub Actions (${{ }}), check for bare {{ without $
            for i, ch in enumerate(content):
                if ch == "{" and i + 1 < len(content) and content[i + 1] == "{":
                    # Allow ${{ (GitHub Actions)
                    if i > 0 and content[i - 1] == "$":
                        continue
                    violations.append(
                        f"{path.relative_to(generated_project)}: bare {{"
                    )
                    break
        assert violations == [], f"Raw Jinja syntax found: {violations}"


# ── Variable Substitution ──────────────────────────────────────────────────


class TestVariableSubstitution:
    """Spot-check each templated file for correct variable replacement."""

    def test_readme_title(self, generated_project: Path) -> None:
        content = (generated_project / "README.md").read_text()
        assert content.startswith("# Test Project\n")

    def test_readme_description(self, generated_project: Path) -> None:
        content = (generated_project / "README.md").read_text()
        assert "A test project for CI" in content

    def test_claude_md_description(self, generated_project: Path) -> None:
        content = (generated_project / "CLAUDE.md").read_text()
        assert "A test project for CI" in content

    def test_env_app_name(self, generated_project: Path) -> None:
        content = (generated_project / ".env.example").read_text()
        assert "APP_NAME=test_project" in content

    def test_env_app_db_url(self, generated_project: Path) -> None:
        content = (generated_project / ".env.example").read_text()
        assert "test_project:test_project_dev@localhost:5434/test_project_app_db" in content

    def test_env_users_db_url(self, generated_project: Path) -> None:
        content = (generated_project / ".env.example").read_text()
        assert "test_project:test_project_dev@localhost:5435/test_project_users_db" in content

    def test_config_app_name(self, generated_project: Path) -> None:
        content = (generated_project / "apps/backend/core/config.py").read_text()
        assert 'APP_NAME: str = "test_project"' in content

    def test_config_db_urls(self, generated_project: Path) -> None:
        content = (generated_project / "apps/backend/core/config.py").read_text()
        assert "test_project:test_project_dev@localhost:5434/test_project_app_db" in content
        assert "test_project:test_project_dev@localhost:5435/test_project_users_db" in content

    def test_pyproject_name(self, generated_project: Path) -> None:
        content = (generated_project / "apps/backend/pyproject.toml").read_text()
        assert 'name = "test_project-backend"' in content

    def test_pyproject_description(self, generated_project: Path) -> None:
        content = (generated_project / "apps/backend/pyproject.toml").read_text()
        assert 'description = "A test project for CI"' in content

    def test_pubspec_name(self, generated_project: Path) -> None:
        content = (generated_project / "apps/frontend/pubspec.yaml").read_text()
        assert content.startswith("name: test_project\n")

    def test_pubspec_description(self, generated_project: Path) -> None:
        content = (generated_project / "apps/frontend/pubspec.yaml").read_text()
        assert "description: A test project for CI" in content

    def test_docker_compose_containers(self, generated_project: Path) -> None:
        content = (generated_project / "docker-compose.yml").read_text()
        assert "${APP_NAME:-test_project}_db_app" in content
        assert "${APP_NAME:-test_project}_db_users" in content
        assert "${APP_NAME:-test_project}_redis" in content

    def test_docker_compose_volumes(self, generated_project: Path) -> None:
        content = (generated_project / "docker-compose.yml").read_text()
        assert "${APP_NAME:-test_project}_app_db_data" in content
        assert "${APP_NAME:-test_project}_users_db_data" in content

    def test_dart_imports_use_slug(self, generated_project: Path) -> None:
        for rel_path in [
            "apps/frontend/lib/main.dart",
            "apps/frontend/lib/core/client/app_client.dart",
            "apps/frontend/lib/core/client/mobile.dart",
            "apps/frontend/lib/router/app_router.dart",
        ]:
            content = (generated_project / rel_path).read_text()
            assert "package:test_project/" in content, f"Missing slug import in {rel_path}"

    def test_main_dart_title(self, generated_project: Path) -> None:
        content = (generated_project / "apps/frontend/lib/main.dart").read_text()
        assert "title: 'Test Project'" in content


# ── Non-Templated Files Unchanged ──────────────────────────────────────────

NON_TEMPLATED_FILES = [
    "Makefile",
    ".gitignore",
    "CONTRIBUTING.md",
    "apps/backend/core/database.py",
    "apps/backend/app/main.py",
    "apps/backend/app/workers/base.py",
    "apps/backend/app/routers/dynamic_endpoints.py",
    "apps/frontend/lib/core/client/web.dart",
    "scripts/regenerate_openapi.py",
]


class TestNonTemplatedFiles:
    @pytest.mark.parametrize("rel_path", NON_TEMPLATED_FILES)
    def test_file_matches_source(self, generated_project: Path, rel_path: str) -> None:
        source = TEMPLATE_ROOT / rel_path
        generated = generated_project / rel_path
        assert source.read_text() == generated.read_text(), (
            f"{rel_path} differs from template source"
        )


# ── Config File Validity ──────────────────────────────────────────────────


class TestConfigValidity:
    """Generated config files parse without errors."""

    def test_pyproject_toml_parses(self, generated_project: Path) -> None:
        path = generated_project / "apps/backend/pyproject.toml"
        with open(path, "rb") as f:
            data = tomllib.load(f)
        assert data["project"]["name"] == "test_project-backend"
        assert "fastapi" in str(data["project"]["dependencies"])

    def test_docker_compose_yml_parses(self, generated_project: Path) -> None:
        path = generated_project / "docker-compose.yml"
        data = yaml.safe_load(path.read_text())
        assert "services" in data

    def test_docker_compose_prod_yml_parses(self, generated_project: Path) -> None:
        path = generated_project / "docker-compose.prod.yml"
        data = yaml.safe_load(path.read_text())
        assert "services" in data

    def test_pubspec_yaml_parses(self, generated_project: Path) -> None:
        path = generated_project / "apps/frontend/pubspec.yaml"
        data = yaml.safe_load(path.read_text())
        assert data["name"] == "test_project"

    def test_ci_yml_parses(self, generated_project: Path) -> None:
        path = generated_project / ".github/workflows/ci.yml"
        data = yaml.safe_load(path.read_text())
        assert "jobs" in data

    def test_analysis_options_parses(self, generated_project: Path) -> None:
        path = generated_project / "apps/frontend/analysis_options.yaml"
        data = yaml.safe_load(path.read_text())
        assert data is not None

    def test_pre_commit_config_parses(self, generated_project: Path) -> None:
        path = generated_project / ".pre-commit-config.yaml"
        data = yaml.safe_load(path.read_text())
        assert "repos" in data


# ── Generated CI Workflow ──────────────────────────────────────────────────


class TestGeneratedCI:
    """Generated CI workflow has correct dual-DB and modern tooling config."""

    def test_ci_has_dual_postgres_services(self, generated_project: Path) -> None:
        content = (generated_project / ".github/workflows/ci.yml").read_text()
        assert "postgres-app:" in content
        assert "postgres-users:" in content

    def test_ci_has_dual_db_env_vars(self, generated_project: Path) -> None:
        content = (generated_project / ".github/workflows/ci.yml").read_text()
        assert "APP_DB_URL:" in content
        assert "USERS_DB_URL:" in content

    def test_ci_uses_ruff_not_black(self, generated_project: Path) -> None:
        content = (generated_project / ".github/workflows/ci.yml").read_text()
        assert "ruff check" in content
        assert "ruff format" in content
        assert "black" not in content

    def test_ci_has_all_job_types(self, generated_project: Path) -> None:
        data = yaml.safe_load(
            (generated_project / ".github/workflows/ci.yml").read_text()
        )
        jobs = set(data["jobs"].keys())
        assert jobs == {"backend-lint", "backend-test", "frontend-test", "frontend-build"}


# ── Default Slug Derivation ────────────────────────────────────────────────


class TestSlugDerivation:
    """project_slug auto-derives from project_name when not explicitly set."""

    @pytest.fixture()
    def auto_slug_project(self, tmp_path: Path) -> Path:
        dst = tmp_path / "auto_slug"
        run_copy(
            str(TEMPLATE_ROOT),
            str(dst),
            data={
                "project_name": "My Cool App",
                "project_description": "test",
                "author_name": "",
            },
            vcs_ref="HEAD",
            defaults=True,
            unsafe=True,
        )
        return dst

    def test_slug_derived_from_name(self, auto_slug_project: Path) -> None:
        content = (auto_slug_project / "apps/backend/core/config.py").read_text()
        assert 'APP_NAME: str = "my_cool_app"' in content

    def test_dart_uses_derived_slug(self, auto_slug_project: Path) -> None:
        content = (auto_slug_project / "apps/frontend/lib/main.dart").read_text()
        assert "package:my_cool_app/" in content

    def test_title_uses_original_name(self, auto_slug_project: Path) -> None:
        content = (auto_slug_project / "apps/frontend/lib/main.dart").read_text()
        assert "title: 'My Cool App'" in content


# ── Edge Cases ──────────────────────────────────────────────────────────────


class TestEdgeCases:
    """Hyphens, spaces, and other project name variations."""

    @pytest.fixture()
    def hyphenated_project(self, tmp_path: Path) -> Path:
        dst = tmp_path / "hyphenated"
        run_copy(
            str(TEMPLATE_ROOT),
            str(dst),
            data={
                "project_name": "my-cool-project",
                "project_slug": "my_cool_project",
                "project_description": "Hyphen test",
                "author_name": "",
            },
            vcs_ref="HEAD",
            defaults=True,
            unsafe=True,
        )
        return dst

    def test_hyphenated_name_in_readme(self, hyphenated_project: Path) -> None:
        content = (hyphenated_project / "README.md").read_text()
        assert content.startswith("# my-cool-project\n")

    def test_slug_in_config(self, hyphenated_project: Path) -> None:
        content = (hyphenated_project / "apps/backend/core/config.py").read_text()
        assert 'APP_NAME: str = "my_cool_project"' in content

    def test_slug_in_dart(self, hyphenated_project: Path) -> None:
        content = (hyphenated_project / "apps/frontend/lib/main.dart").read_text()
        assert "package:my_cool_project/" in content

    def test_title_uses_original(self, hyphenated_project: Path) -> None:
        content = (hyphenated_project / "apps/frontend/lib/main.dart").read_text()
        assert "title: 'my-cool-project'" in content


# ── Backend Python Validity ─────────────────────────────────────────────────


class TestPythonValidity:
    """Generated Python files are syntactically valid."""

    PYTHON_FILES = [
        "apps/backend/core/config.py",
        "apps/backend/core/database.py",
        "apps/backend/core/exceptions.py",
        "apps/backend/core/logging.py",
        "apps/backend/core/schemas/base.py",
        "apps/backend/core/schemas/item.py",
        "apps/backend/core/schemas/users.py",
        "apps/backend/app/main.py",
        "apps/backend/app/api/v1/items/items.py",
        "apps/backend/app/routers/dynamic_endpoints.py",
        "apps/backend/app/dependencies/auth.py",
        "apps/backend/app/auth/user_manager.py",
        "apps/backend/app/workers/base.py",
        "apps/backend/app/workers/run.py",
        "apps/backend/tests/conftest.py",
        "scripts/regenerate_openapi.py",
    ]

    @pytest.mark.parametrize("rel_path", PYTHON_FILES)
    def test_python_syntax_valid(self, generated_project: Path, rel_path: str) -> None:
        path = generated_project / rel_path
        result = subprocess.run(
            ["python", "-m", "py_compile", str(path)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"Syntax error in {rel_path}: {result.stderr}"
        )
