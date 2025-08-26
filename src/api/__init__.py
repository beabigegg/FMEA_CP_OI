# Expose routers so they can be imported directly from src.api
"""
This module exposes the available API routers.  Only routers present in the
``src/api`` package should be imported here.  Additional routers can be added
in future as needed (e.g. associations or AI suggestions), but those
implementations are not included in this code base.
"""

from . import documents_router, items_router, ap_router, fe_router  # noqa: F401
