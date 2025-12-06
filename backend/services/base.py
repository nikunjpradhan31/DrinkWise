"""
Base service class for DrinkWise backend services.
Provides common functionality and database session management.
"""

from abc import ABC, abstractmethod
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from typing import Any, Dict, Optional, List
import logging

logger = logging.getLogger(__name__)

class BaseService(ABC):
    """
    Abstract base class for all services in the DrinkWise backend.
    Provides common functionality for database operations, logging, and error handling.
    """
    
    def __init__(self, db: AsyncSession):
        """
        Initialize the service with a database session.
        
        Args:
            db: AsyncSession instance for database operations
        """
        self.db = db
    
    async def execute_with_rollback(self, operation) -> Any:
        """
        Execute a database operation with automatic rollback on error.
        
        Args:
            operation: Async function to execute
            
        Returns:
            Result of the operation
            
        Raises:
            Exception: If the operation fails
        """
        try:
            result = await operation()
            await self.db.commit()
            return result
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Database operation failed: {str(e)}")
            raise
    
    async def execute_without_commit(self, operation) -> Any:
        """
        Execute a database operation without automatic commit.
        Used for read-only operations or when manual commit control is needed.
        
        Args:
            operation: Async function to execute
            
        Returns:
            Result of the operation
        """
        try:
            result = await operation()
            return result
        except Exception as e:
            logger.error(f"Database read operation failed: {str(e)}")
            raise
    
    def handle_not_found(self, resource: str, resource_id: Any) -> None:
        """
        Handle not found errors consistently.
        
        Args:
            resource: Type of resource (e.g., "User", "Drink")
            resource_id: ID of the resource that was not found
            
        Raises:
            HTTPException: 404 Not Found
        """
        from fastapi import HTTPException
        raise HTTPException(
            status_code=404,
            detail=f"{resource} with id {resource_id} not found"
        )
    
    def handle_validation_error(self, field: str, value: Any) -> None:
        """
        Handle validation errors consistently.
        
        Args:
            field: Field name that failed validation
            value: Invalid value
            
        Raises:
            HTTPException: 400 Bad Request
        """
        from fastapi import HTTPException
        raise HTTPException(
            status_code=400,
            detail=f"Invalid value '{value}' for field '{field}'"
        )
    
    def handle_conflict_error(self, resource: str, conflict_field: str, value: Any) -> None:
        """
        Handle conflict errors (duplicate resources) consistently.
        
        Args:
            resource: Type of resource (e.g., "User", "Drink")
            conflict_field: Field that caused the conflict
            value: Conflicting value
            
        Raises:
            HTTPException: 409 Conflict
        """
        from fastapi import HTTPException
        raise HTTPException(
            status_code=409,
            detail=f"{resource} with {conflict_field} '{value}' already exists"
        )
    
    def log_operation(self, operation: str, details: Dict[str, Any]) -> None:
        """
        Log service operations for debugging and monitoring.
        
        Args:
            operation: Name of the operation
            details: Additional details to log
        """
        logger.info(f"Service operation '{operation}' executed with details: {details}")
    
    def log_error(self, operation: str, error: Exception, details: Dict[str, Any] = None) -> None:
        """
        Log service errors for debugging and monitoring.
        
        Args:
            operation: Name of the operation that failed
            error: The exception that occurred
            details: Additional details about the error
        """
        logger.error(f"Service operation '{operation}' failed: {str(error)}", extra={"details": details})
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Basic health check for the service.
        
        Returns:
            Dict containing service health status
        """
        try:
            # Simple database connectivity check
            await self.db.execute("SELECT 1")
            return {
                "status": "healthy",
                "service": self.__class__.__name__,
                "database": "connected"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "service": self.__class__.__name__,
                "database": "disconnected",
                "error": str(e)
            }