"""
API package for DrinkWise backend.
Provides access to all API routers.
"""

from .auth import router as auth_router
from .catalog import router as catalog_router
from .user_drinks import router as user_drinks_router

__all__ = [
    "auth_router",
    "catalog_router",
    "user_drinks_router"
]