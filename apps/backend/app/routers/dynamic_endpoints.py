"""Dynamic router discovery — scans app/api/ and registers all routers automatically."""

import importlib
import logging
import os
import types

from fastapi import APIRouter, FastAPI

logger = logging.getLogger(__name__)


def add_endpoints(app: FastAPI, base_module: types.ModuleType) -> None:
    """Recursively discover and register APIRouter instances from the api directory.

    Convention:
    - Each .py file in app/api/ must export a `router = APIRouter()` to be discovered.
    - URL prefix is derived from the file's path relative to the base module.
    - If the filename matches the last directory name, the filename is omitted from the prefix.
      e.g., api/v1/items/items.py -> /v1/items (not /v1/items/items)
    - Tags are auto-generated from the directory name after the version prefix.
    """
    base_dir = os.path.dirname(base_module.__file__)  # type: ignore[arg-type]
    base_module_name = base_module.__name__

    for root, _, files in os.walk(base_dir):
        for file in files:
            if not file.endswith(".py") or file == "__init__.py":
                continue

            # Build module path
            full_path = os.path.join(root, file)
            relative_path = os.path.relpath(full_path, base_dir)
            module_suffix = os.path.splitext(relative_path)[0]
            module_path = f"{base_module_name}.{module_suffix.replace(os.sep, '.')}"

            # Import the module
            try:
                module = importlib.import_module(module_path)
            except Exception:
                logger.exception("Failed to import module: %s", module_path)
                continue

            # Check for router
            if not hasattr(module, "router") or not isinstance(module.router, APIRouter):
                continue

            # Build prefix
            file_name_without_ext = os.path.splitext(file)[0]
            last_directory_name = os.path.basename(root)

            if file_name_without_ext == last_directory_name:
                dynamic_prefix = f"/{os.path.dirname(module_suffix).replace(os.sep, '/')}"
            else:
                dynamic_prefix = f"/{module_suffix.replace(os.sep, '/')}"

            # Build tags
            module_suffix_parts = module_suffix.split(os.sep)
            if (
                len(module_suffix_parts) > 1
                and module_suffix_parts[0].startswith("v")
                and module_suffix_parts[0][1:].isdigit()
            ):
                tag_base_name = module_suffix_parts[1]
            else:
                tag_base_name = file_name_without_ext

            router_tags = [" ".join(word.lower() for word in tag_base_name.split("_"))]

            # Register
            app.include_router(module.router, prefix=dynamic_prefix, tags=router_tags)
            logger.info(
                "Registered router: %s -> prefix=%s tags=%s",
                module_path,
                dynamic_prefix,
                router_tags,
            )
