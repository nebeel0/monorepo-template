#!/usr/bin/env python3
"""Post-generation patches for the OpenAPI Dart client.

Fixes known issues with the dart-dio openapi-generator output:
1. Builder factories for nested generic types (BuiltList<T>)
2. Enum default value mismatches (snake_case → proper constants)

Customize this script as needed for your specific API patterns.
"""

import re
from pathlib import Path

FRONTEND_DIR = Path(__file__).parent.parent / "apps" / "frontend"
CLIENT_DIR = FRONTEND_DIR / "app_client" / "lib"


def patch_serializers() -> None:
    """Fix builder factories for nested generics in serializers.dart."""
    serializers_path = CLIENT_DIR / "src" / "serializers.dart"
    if not serializers_path.exists():
        return

    content = serializers_path.read_text()
    # Add any specific serializer patches here based on your API models
    serializers_path.write_text(content)


def patch_enum_defaults() -> None:
    """Fix enum valueOf calls that use snake_case instead of proper constants."""
    for dart_file in CLIENT_DIR.rglob("*.dart"):
        content = dart_file.read_text()
        # Fix common pattern: valueOf('snake_case') → proper enum value
        # Customize regex patterns here for your specific enum naming
        if "valueOf(" in content:
            # This is a placeholder — customize for your specific enums
            dart_file.write_text(content)


def main() -> None:
    if not CLIENT_DIR.exists():
        print(f"Client directory not found: {CLIENT_DIR}")
        print("Run 'make openapi' first to generate the client.")
        return

    print("Patching serializers...")
    patch_serializers()

    print("Patching enum defaults...")
    patch_enum_defaults()

    print("Patches applied.")


if __name__ == "__main__":
    main()
