from fastapi import FastAPI

from app import api
from app.routers.dynamic_endpoints import add_endpoints


def add_service_endpoints(app: FastAPI) -> None:
    """Discover and register all API endpoints from the app.api package."""
    add_endpoints(app, api)
