from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, Dict, Any
import logging

from database import get_db_async
from models import Users

# Security scheme for Bearer token
security = HTTPBearer()

class AuthMiddleware:
    """Authentication middleware for verifying user requests"""
    
    def __init__(self, db_session: AsyncSession, credentials: HTTPAuthorizationCredentials):
        self.db = db_session
        self.credentials = credentials
    
    async def verify_token(self) -> Dict[str, Any]:
        """
        Verify the access token and return user information
        
        Returns:
            Dict containing user_id and user data
            
        Raises:
            HTTPException: If token is invalid or expired
        """
        token = self.credentials.credentials
        
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access token is required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Query user by access_key (token)
        result = await self.db.execute(
            select(Users).where(Users.access_key == token)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if session is still valid (within 12 hours)
        if user.session_at:
            from datetime import datetime, timedelta
            session_expiry = user.session_at + timedelta(hours=12)
            if datetime.now() > session_expiry:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Session has expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        
        return {
            "user_id": user.user_id,
            "username": user.username,
            "email": user.email,
            "is_verified": user.is_verified,
            "verification_completed": user.verification_completed,
            "age": user.age
        }
    
    async def verify_age_restriction(self, user_info: Dict[str, Any]) -> bool:
        """
        Verify if user meets age requirements for alcohol content
        
        Args:
            user_info: User information from token verification
            
        Returns:
            bool: True if user meets age requirements (21+ for alcohol)
        """
        if not user_info.get("age"):
            return False
        
        return user_info["age"] >= 21
    
    async def verify_verification_requirement(self, user_info: Dict[str, Any]) -> bool:
        """
        Verify if user has completed verification requirements
        
        Args:
            user_info: User information from token verification
            
        Returns:
            bool: True if user has completed verification
        """
        return user_info.get("verification_completed", False)

# FastAPI dependency functions

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_async)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current authenticated user
    
    Usage:
        @app.get("/protected")
        async def protected_endpoint(current_user: dict = Depends(get_current_user)):
            return {"user_id": current_user["user_id"]}
    """
    auth_middleware = AuthMiddleware(db, credentials)
    return await auth_middleware.verify_token()

async def get_current_verified_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current user who has completed verification
    
    Usage:
        @app.get("/verified-only")
        async def verified_endpoint(user: dict = Depends(get_current_verified_user)):
            return {"message": "User is verified"}
    """
    if not current_user.get("verification_completed"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User verification required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user

async def get_age_verified_user(
    current_user: Dict[str, Any] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    FastAPI dependency to get current user who meets age requirements
    
    Usage:
        @app.get("/alcohol-content")
        async def alcohol_endpoint(user: dict = Depends(get_age_verified_user)):
            return {"message": "Age verified user"}
    """
    auth_middleware = AuthMiddleware(None, None)  # Initialize with dummy values
    
    if not await auth_middleware.verify_age_restriction(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Age verification required for alcohol content",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return current_user

# Optional authentication (for endpoints that work with or without auth)
async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db_async)
) -> Optional[Dict[str, Any]]:
    """
    FastAPI dependency for optional authentication
    
    Usage:
        @app.get("/optional-auth")
        async def optional_endpoint(user: Optional[dict] = Depends(get_optional_user)):
            if user:
                return {"user_id": user["user_id"]}
            else:
                return {"message": "Anonymous user"}
    """
    if not credentials:
        return None
    
    try:
        auth_middleware = AuthMiddleware(db, credentials)
        return await auth_middleware.verify_token()
    except HTTPException:
        return None

# Exception handlers for authentication errors

def create_auth_exception_handler():
    """Create custom exception handlers for authentication errors"""
    
    async def unauthorized_handler(request, exc):
        return {
            "error": "Unauthorized",
            "message": str(exc.detail),
            "status_code": exc.status_code
        }
    
    async def forbidden_handler(request, exc):
        return {
            "error": "Forbidden",
            "message": str(exc.detail),
            "status_code": exc.status_code
        }
    
    return unauthorized_handler, forbidden_handler

# Logging configuration
logging.basicConfig(level=logging.INFO)
auth_logger = logging.getLogger("auth")