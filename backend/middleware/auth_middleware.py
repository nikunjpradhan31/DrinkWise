"""
JWT Authentication middleware for DrinkWise backend.
Handles token validation, user extraction, and authentication verification.
"""

from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
import secrets
import logging
from dotenv import load_dotenv
import os
load_dotenv()
from database import get_db_async
from models import Users

logger = logging.getLogger(__name__)

# Security scheme
security = HTTPBearer()

# JWT Configuration
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "")
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS = 7

class TokenData:
    """Data class for JWT token payload"""
    def __init__(self, user_id: int, username: str, email: str, is_verified: bool = False):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.is_verified = is_verified
        self.iat = datetime.now(timezone.utc)
        self.exp = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

def create_access_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Dictionary containing user data
        
    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()
    
    # Set expiration time
    expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    
    # Add issued at time
    to_encode.update({"iat": datetime.now(timezone.utc)})
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    Create a JWT refresh token.
    
    Args:
        data: Dictionary containing user data
        
    Returns:
        Encoded JWT refresh token string
    """
    to_encode = data.copy()
    
    # Set expiration time for refresh token (longer)
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    
    # Add issued at time
    to_encode.update({"iat": datetime.now(timezone.utc)})
    
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id: int = payload.get("sub")
        username: str = payload.get("username")
        email: str = payload.get("email")
        token_type: str = payload.get("type")
        is_verified: bool = payload.get("is_verified", False)
        
        if user_id is None or username is None or email is None:
            raise credentials_exception
            
        # Check token type
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        token_data = {
            "user_id": user_id,
            "username": username, 
            "email": email,
            "is_verified": is_verified,
            "exp": payload.get("exp"),
            "iat": payload.get("iat")
        }
        return token_data
        
    except JWTError:
        raise credentials_exception

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db_async)
) -> Users:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials from request header
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If authentication fails or user not found
    """
    try:
        # Verify token and extract data
        token_data = verify_token(credentials.credentials)
        
        # Query user from database
        from sqlalchemy import select
        result = await db.execute(
            select(Users).where(Users.user_id == int(token_data["user_id"]))
        )
        user = result.scalar_one_or_none()
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Check if user is still active (not disabled)
        if not user.access_key:  # User might be logged out
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User session expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        return user
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_verified_user(
    current_user: Users = Depends(get_current_user)
) -> Users:
    """
    Get current user but require email verification.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User object (verified only)
        
    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user

async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db_async)
) -> Optional[Users]:
    """
    Get current user if authenticated, otherwise return None.
    
    Args:
        credentials: Optional HTTP Bearer credentials
        db: Database session
        
    Returns:
        User object or None if not authenticated
    """
    if not credentials:
        return None
        
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

def generate_session_key() -> str:
    """
    Generate a secure session key for user sessions.
    
    Returns:
        Secure random session key
    """
    return secrets.token_urlsafe(32)

def create_user_session(user: Users, db: AsyncSession) -> str:
    """
    Create a new session for a user and update their access key.
    
    Args:
        user: User object
        db: Database session
        
    Returns:
        Generated access key
    """
    session_key = generate_session_key()
    user.access_key = session_key
    user.session_at = datetime.now()
    return session_key

def invalidate_user_session(user: Users, db: AsyncSession) -> None:
    """
    Invalidate a user's session by clearing their access key.
    
    Args:
        user: User object
        db: Database session
    """
    user.access_key = None
    user.session_at = None