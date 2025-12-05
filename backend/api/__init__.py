"""
DrinkWise API Routes Package

This package contains all API route handlers for the DrinkWise application.
Each router handles specific domain functionality and uses the service layer.
"""

# Import all routers for easy inclusion in main app
from .auth import router as auth_router
from .users import router as users_router
from .catalog import router as catalog_router
from .recommendations import router as recommendations_router
from .preferences import router as preferences_router
from .quiz import router as quiz_router
from .interactions import router as interactions_router

__all__ = [
    "auth_router",
    "users_router", 
    "catalog_router",
    "recommendations_router",
    "preferences_router",
    "quiz_router",
    "interactions_router"
]