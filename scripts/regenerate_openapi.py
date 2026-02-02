#!/usr/bin/env python3
"""Regenerate OpenAPI schema from FastAPI and trigger Dart client generation.

Usage:
    cd apps/backend && uv run python ../../scripts/regenerate_openapi.py

This script:
1. Extracts the OpenAPI schema directly from the FastAPI app (no running server needed)
2. Converts OpenAPI 3.1 → 3.0.2 for dart-dio generator compatibility
3. Saves the schema to apps/frontend/schema/openapi.json
4. Runs flutter build_runner to regenerate the Dart client
"""

import json
import subprocess
import sys
from pathlib import Path


def get_openapi_schema() -> dict:
    """Extract OpenAPI schema from FastAPI app without starting server."""
    from app.main import app

    return app.openapi()


def convert_openapi_31_to_30(schema: dict) -> dict:
    """Downgrade OpenAPI 3.1 features to 3.0.2 for compatibility with dart-dio generator."""
    schema["openapi"] = "3.0.2"

    def fix_schema_node(node: dict) -> dict:
        """Recursively fix schema nodes for 3.0 compatibility."""
        if not isinstance(node, dict):
            return node

        # Convert anyOf with null type to nullable
        if "anyOf" in node:
            types = node["anyOf"]
            non_null = [t for t in types if t != {"type": "null"}]
            if len(non_null) == 1 and len(types) > len(non_null):
                result = {**non_null[0], "nullable": True}
                for k, v in node.items():
                    if k != "anyOf":
                        result[k] = v
                return fix_schema_node(result)

        # Recursively process nested schemas
        for key in ["properties", "items", "additionalProperties"]:
            if key in node:
                if isinstance(node[key], dict):
                    if key == "properties":
                        node[key] = {k: fix_schema_node(v) for k, v in node[key].items()}
                    else:
                        node[key] = fix_schema_node(node[key])

        return node

    # Fix all component schemas
    if "components" in schema and "schemas" in schema["components"]:
        schema["components"]["schemas"] = {
            k: fix_schema_node(v) for k, v in schema["components"]["schemas"].items()
        }

    return schema


def main() -> None:
    # Resolve paths
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent
    frontend_dir = repo_root / "apps" / "frontend"
    schema_dir = frontend_dir / "schema"
    schema_file = schema_dir / "openapi.json"

    # Ensure output directory exists
    schema_dir.mkdir(parents=True, exist_ok=True)

    # Extract schema
    print("Extracting OpenAPI schema from FastAPI app...")
    schema = get_openapi_schema()
    schema = convert_openapi_31_to_30(schema)

    # Write schema
    schema_file.write_text(json.dumps(schema, indent=2))
    print(f"Schema written to: {schema_file}")

    # Run Dart code generation
    print("\nRunning Flutter build_runner...")
    result = subprocess.run(
        ["flutter", "pub", "run", "build_runner", "build", "--delete-conflicting-outputs"],
        cwd=frontend_dir,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"build_runner failed:\n{result.stderr}")
        sys.exit(1)

    print(result.stdout)

    # Apply patches
    print("Applying post-generation patches...")
    patch_script = script_dir / "patch_openapi_client.py"
    if patch_script.exists():
        subprocess.run([sys.executable, str(patch_script)], cwd=repo_root, check=True)

    print("\nOpenAPI client regeneration complete!")


if __name__ == "__main__":
    main()
