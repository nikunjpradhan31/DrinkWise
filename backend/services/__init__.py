"""
Services package for DrinkWise backend.
Provides access to all service classes.
"""

from .auth_service import AuthService
from .catalog_service import CatalogService
from .email_service import EmailService
from .preference_service import PreferenceService
from .quiz_service import TasteQuizService
from .user_drinks_service import UserDrinksService
from .base import BaseService

__all__ = [
    "AuthService",
    "CatalogService",
    "EmailService",
    "PreferenceService",
    "TasteQuizService",
    "UserDrinksService",
    "BaseService"
]