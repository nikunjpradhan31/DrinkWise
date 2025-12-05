"""
DrinkWise Services Package

This package contains all business logic services for the DrinkWise application.
Each service handles specific domain logic and provides clean interfaces for the API layer.
"""

from .base import BaseService, ServiceError, ValidationError, NotFoundError, AuthenticationError
from .auth import AuthService
from .preferences import PreferenceService
from .filters import FilterService
from .catalog import CatalogService
from .hybrid_model import HybridModelService
from .taste_quiz import TasteQuizService
from .explainability import ExplainabilityService
from .email import EmailService

__all__ = [
    # Base classes and exceptions
    "BaseService",
    "ServiceError", 
    "ValidationError",
    "NotFoundError",
    "AuthenticationError",
    
    # Service implementations
    "AuthService",
    "PreferenceService", 
    "FilterService",
    "CatalogService",
    "HybridModelService",
    "TasteQuizService",
    "ExplainabilityService",
    "EmailService"
]

# Service factory function for dependency injection
def create_service(service_type: str, db_session):
    """
    Factory function to create service instances
    
    Args:
        service_type: Type of service to create
        db_session: Database session
        
    Returns:
        Service instance
        
    Raises:
        ValueError: If service_type is not supported
    """
    services = {
        "auth": AuthService,
        "preferences": PreferenceService,
        "filters": FilterService,
        "catalog": CatalogService,
        "hybrid_model": HybridModelService,
        "taste_quiz": TasteQuizService,
        "explainability": ExplainabilityService,
        "email": EmailService
    }
    
    if service_type not in services:
        raise ValueError(f"Unsupported service type: {service_type}")
    
    return services[service_type](db_session)