"""
Authentication API endpoints for DrinkWise backend.
Handles user registration, login, logout, and password reset.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from email_validator import EmailNotValidError, validate_email
from database import get_db_async
from middleware.auth_middleware import get_current_user
from middleware.rate_limit import rate_limit_middleware
from models import Users
from services.auth_service import AuthService
from services.email_service import EmailService
from pydantic_models import (
    UserRegistration, UserLogin, UserResponse, UserUpdate,
    ForgotPassword, ForgotPasswordResponse, LogoutResponse,
    ErrorResponse
)

router = APIRouter(prefix="/auth", tags=["authentication"])

async def get_auth_service(
    db: AsyncSession = Depends(get_db_async)
) -> AuthService:
    """Get AuthService instance."""
    # Create EmailService instance for AuthService
    email_service = EmailService(db)
    return AuthService(db, email_service)

# Registration endpoint
@router.post(
    "/register",
    response_model=UserResponse,
    responses={400: {"model": ErrorResponse}, 409: {"model": ErrorResponse}}
)
async def register_user(
    registration_data: UserRegistration,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user with email verification.
    
    - **username**: Unique username (3-50 characters)
    - **email**: Valid email address
    - **password**: Strong password (8+ chars, uppercase, lowercase, digit)
    - **confirmpassword**: Password confirmation
    - **date_of_birth**: Optional date of birth for age verification
    """
    success, error_message, user_response = await auth_service.register_user(registration_data)
    
    if not success:
        if "already exists" in error_message:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
    
    return user_response

# Login endpoint
@router.post(
    "/login", 
    response_model=UserResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}}
)
async def login_user(
    login_data: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate user and return JWT tokens.
    
    - **username**: User's username
    - **password**: User's password
    """
    success, error_message, user_response = await auth_service.login_user(login_data)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error_message
        )
    
    return user_response

# Logout endpoint
@router.post(
    "/logout",
    response_model=LogoutResponse,
    responses={401: {"model": ErrorResponse}}
)
async def logout_user(
    current_user: Users = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Logout user by invalidating their session.
    
    Requires valid JWT token in Authorization header.
    """
    success = await auth_service.logout_user(current_user.user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Logout failed"
        )
    
    return LogoutResponse()

# Get current user profile
@router.get(
    "/me",
    response_model=UserResponse,
    responses={401: {"model": ErrorResponse}}
)
async def get_current_user_profile(
    current_user: Users = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Get current user's profile information.
    
    Requires valid JWT token in Authorization header.
    """
    user_response = await auth_service.get_user_profile(current_user.user_id)
    
    if not user_response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return user_response

# Update user profile
@router.put(
    "/me",
    response_model=UserResponse,
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}}
)
async def update_user_profile(
    update_data: UserUpdate,
    current_user: Users = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Update current user's profile information.
    
    - **username**: Optional new username
    - **date_of_birth**: Optional new date of birth
    
    Requires valid JWT token in Authorization header.
    """
    success, error_message, user_response = await auth_service.update_user_profile(
        current_user.user_id, update_data
    )
    
    if not success:
        if "not found" in error_message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_message
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
    
    return user_response

# Forgot password endpoint
@router.post(
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    responses={400: {"model": ErrorResponse}}
)
async def forgot_password(
    request_data: ForgotPassword,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Reset user password using verification code.
    
    - **email**: User's email address
    - **verification_code**: Code from email
    - **new_password**: New password
    - **confirm_password**: Password confirmation
    """
    success, error_message = await auth_service.reset_password(
        request_data.email,
        request_data.verification_code,
        request_data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    # Get user ID for response
    from sqlalchemy import select
    from models import Users
    
    # This should ideally be part of the auth_service method
    # For now, we'll return a generic response
    return ForgotPasswordResponse(user_id=0)

# Resend verification email
@router.post(
    "/resend-verification",
    responses={400: {"model": ErrorResponse}}
)
async def resend_verification_email(
    email: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Resend email verification code.
    
    - **email**: User's email address
    """
    
    try:
        email_obj = validate_email(email, check_deliverability=False)
        email_obj = email_obj.email

    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    success = await auth_service.email_service.resend_verification(
        email_obj, "email_verification"
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to resend verification email"
        )
    
    return {"message": "Verification email sent"}

# Verify email endpoint
@router.post(
    "/verify-email",
    responses={400: {"model": ErrorResponse}}
)
async def verify_email(
    email: str,
    verification_code: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Verify email address using verification code.
    
    - **email**: User's email address
    - **verification_code**: Code from email
    """
    
    try:
        email_obj = validate_email(email, check_deliverability=False)
        email_obj = email_obj.email
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    success, error_message = await auth_service.verify_user_email(email_obj, verification_code)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )
    
    return {"message": "Email verified successfully"}

# Check username availability
@router.get(
    "/check-username/{username}",
    responses={400: {"model": ErrorResponse}}
)
async def check_username_availability(
    username: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Check if username is available for registration.
    
    - **username**: Username to check
    """
    if not auth_service.validate_username(username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid username format"
        )
    
    is_available = await auth_service.check_username_availability(username)
    
    return {
        "username": username,
        "available": is_available,
        "message": "Username is available" if is_available else "Username is already taken"
    }

# Check email availability
@router.get(
    "/check-email/{email}",
    responses={400: {"model": ErrorResponse}}
)
async def check_email_availability(
    email: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Check if email is available for registration.
    
    - **email**: Email to check
    """
    
    try:
        email_obj = validate_email(email, check_deliverability=False)
        email_obj = email_obj.email
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    is_available = await auth_service.check_email_availability(email_obj)
    
    return {
        "email": email,
        "available": is_available,
        "message": "Email is available" if is_available else "Email is already registered"
    }

# Request password reset
@router.post(
    "/request-password-reset",
    responses={400: {"model": ErrorResponse}}
)
async def request_password_reset(
    email: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Request password reset email.
    
    - **email**: User's email address
    """
    
    try:
        email_obj = validate_email(email, check_deliverability=False)
        email_obj = email_obj.email
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid email format"
        )
    
    success, error_message = await auth_service.request_password_reset(email_obj)
    
    # Always return success to prevent email enumeration
    if not success:
        logger.warning(f"Password reset request failed for {email_obj}: {error_message}")
    
    return {"message": "If the email exists, a password reset link has been sent"}

# Get user statistics
@router.get(
    "/statistics",
    responses={401: {"model": ErrorResponse}}
)
async def get_user_statistics(
    current_user: Users = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Get current user's statistics and account information.
    
    Requires valid JWT token in Authorization header.
    """
    stats = await auth_service.get_user_statistics(current_user.user_id)
    
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User statistics not found"
        )
    
    return stats

# Delete user account
@router.delete(
    "/delete-account",
    responses={401: {"model": ErrorResponse}, 400: {"model": ErrorResponse}}
)
async def delete_user_account(
    current_user: Users = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Delete user account and all associated data.
    
    Requires valid JWT token in Authorization header.
    
    ⚠️ **Warning**: This action is irreversible and will delete all user data.
    """
    # This would need to be implemented in the auth_service
    # For now, we'll return a placeholder response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Account deletion not yet implemented"
    )

# Token refresh endpoint
@router.post(
    "/refresh-token",
    responses={401: {"model": ErrorResponse}}
)
async def refresh_token(
    current_user: Users = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Refresh JWT token.
    
    Requires valid JWT token in Authorization header.
    """
    from ..middleware.auth_middleware import create_access_token
    
    # Create new access token
    new_access_token = create_access_token({
        "sub": str(current_user.user_id),
        "username": current_user.username,
        "email": current_user.email,
        "is_verified": current_user.is_verified
    })
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": 1800  # 30 minutes
    }

# Export router
__all__ = ["router"]