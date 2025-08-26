# Expose routers so they can be imported directly from src.api
"""
This module exposes the available API routers.
"""

from . import (
    documents_router,
    items_router,
    fe_router,
    auth_router,
    ai_suggestions_router,
    export_router
) # noqa: F401
