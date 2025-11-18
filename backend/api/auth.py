from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from middleware import get_current_user
from services import AuthService, EmailService
from pydantic_models import (
    UserCreate, UserLogin, LoginResponse, UserResponse,
    EmailVerificationRequest, EmailVerificationResponse,
    VerifyEmailRequest, VerifyEmailResponse, UserUpdate
)

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

@router.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate,
    auth_service: AuthService = Depends(),
    email_service: EmailService = Depends()
):
    """Register a new user"""
    try:
        # Create user
        user = await auth_service.create_user(user_data)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )
        
        # Send verification email
        verification_result = await email_service.send_verification_email(
            user.user_id, user.email
        )
        
        if not verification_result:
            # Log warning but don't fail registration
            pass
        
        return user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/login", response_model=LoginResponse)
async def login_user(
    login_data: UserLogin,
    auth_service: AuthService = Depends()
):
    """Authenticate user and return access token"""
    try:
        user_session = await auth_service.authenticate_user(login_data)
        if not user_session:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
        
        return user_session
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/logout")
async def logout_user(
    current_user: dict = Depends(get_current_user),
    auth_service: AuthService = Depends()
):
    """Logout user by clearing access token"""
    try:
        success = await auth_service.logout_user(current_user["user_id"])
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to logout user"
            )
        
        return {"message": "Logged out successfully"}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/verify-email", response_model=VerifyEmailResponse)
async def verify_email(
    verify_request: VerifyEmailRequest,
    email_service: EmailService = Depends(),
    auth_service: AuthService = Depends()
):
    """Verify email using verification token"""
    try:
        verification_result = await email_service.verify_email_token(verify_request)
        if not verification_result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification token"
            )
        
        # Mark verification as completed
        await auth_service.mark_verification_completed(verification_result.user_id)
        
        return verification_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/send-verification", response_model=EmailVerificationResponse)
async def send_verification_email(
    email_request: EmailVerificationRequest,
    current_user: dict = Depends(get_current_user),
    email_service: EmailService = Depends()
):
    """Send verification email to current user"""
    try:
        verification_result = await email_service.send_verification_email(
            current_user["user_id"], email_request.email
        )
        
        if not verification_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send verification email"
            )
        
        return verification_result
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/verify-age")
async def verify_age(
    age: int,
    current_user: dict = Depends(get_current_user),
    auth_service: AuthService = Depends()
):
    """Verify user age for alcohol content access"""
    try:
        if age < 0 or age > 150:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid age provided"
            )
        
        success = await auth_service.verify_age(current_user["user_id"], age)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to verify age"
            )
        
        is_age_verified = age >= 21
        
        return {
            "age_verified": is_age_verified,
            "message": "Age verified successfully" if is_age_verified else "Age verification pending for alcohol content"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    auth_service: AuthService = Depends()
):
    """Get current user profile"""
    try:
        # Get full user details from database
        user = await auth_service.get_user_by_id(current_user["user_id"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.from_orm(user)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    profile_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
    auth_service: AuthService = Depends()
):
    """Update current user profile"""
    try:
        updated_user = await auth_service.update_user_profile(
            current_user["user_id"], profile_data
        )
        
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user profile"
            )
        
        return updated_user
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

# Helper methods for AuthService (need to add to the service)
# These would be additional methods in the AuthService class
async def get_user_by_id(self, user_id: int):
    """Get user by ID"""
    try:
        result = await self.db.execute(
            select(Users).where(Users.user_id == user_id)
        )
        return result.scalar_one_or_none()
    except Exception as e:
        self.logger.error(f"Error getting user by ID: {str(e)}")
        return None

# Add this method to AuthService class