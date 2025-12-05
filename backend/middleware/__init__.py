"""
DrinkWise Middleware Package

This package contains middleware components for the DrinkWise application.
"""

from .auth import (
    AuthMiddleware,
    get_current_user,
    get_current_verified_user,
    get_age_verified_user,
    get_optional_user
)

__all__ = [
    "AuthMiddleware",
    "get_current_user",
    "get_current_verified_user", 
    "get_age_verified_user",
    "get_optional_user"
]