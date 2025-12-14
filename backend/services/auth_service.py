"""
Authentication service for DrinkWise backend.
Handles user authentication, JWT token management, and security operations.
"""

import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import secrets
import logging

from models import Users, Verification
from .base import BaseService
from middleware.auth_middleware import create_access_token, create_refresh_token, create_user_session, invalidate_user_session
from pydantic_models import UserRegistration, UserLogin, UserResponse, UserUpdate
from .email_service import EmailService

logger = logging.getLogger(__name__)

class AuthService(BaseService):
    """
    Service for handling authentication operations in DrinkWise.
    """
    
    def __init__(self, db: AsyncSession, email_service: EmailService):
        """
        Initialize authentication service.
        
        Args:
            db: Database session
            email_service: Email service for verification
        """
        super().__init__(db)
        self.email_service = email_service
        self.PASSWORD_HASH_ROUNDS = 12
        self.MAX_LOGIN_ATTEMPTS = 5
        self.LOCKOUT_DURATION_MINUTES = 15
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt(rounds=self.PASSWORD_HASH_ROUNDS)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plain text password
            hashed_password: Hashed password
            
        Returns:
            True if password is correct, False otherwise
        """
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {str(e)}")
            return False
    
    def validate_username(self, username: str) -> bool:
        """
        Validate username format and constraints.
        
        Args:
            username: Username to validate
            
        Returns:
            True if username is valid
        """
        if not username or len(username) < 3 or len(username) > 50:
            return False
        
        # Check for valid characters (alphanumeric, underscore, hyphen)
        valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-')
        return all(c in valid_chars for c in username)
    
    def validate_password_strength(self, password: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid, validation_details)
        """
        if len(password) < 8:
            return False, {"error": "Password must be at least 8 characters long"}
        
        if len(password) > 128:
            return False, {"error": "Password must not exceed 128 characters"}
        
        has_uppercase = any(c.isupper() for c in password)
        has_lowercase = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        
        if not all([has_uppercase, has_lowercase, has_digit]):
            return False, {"error": "Password must contain at least one uppercase letter, one lowercase letter, and one digit"}
        
        return True, {
            "strength": "strong" if all([has_uppercase, has_lowercase, has_digit, has_special]) else "medium",
            "checks": {
                "has_uppercase": has_uppercase,
                "has_lowercase": has_lowercase,
                "has_digit": has_digit,
                "has_special": has_special
            }
        }
    
    def generate_secure_token(self, length: int = 32) -> str:
        """
        Generate a secure random token.
        
        Args:
            length: Token length
            
        Returns:
            Secure token string
        """
        return secrets.token_urlsafe(length)
    
    async def register_user(self, registration_data: UserRegistration) -> Tuple[bool, Optional[str], Optional[UserResponse]]:
        """
        Register a new user.
        
        Args:
            registration_data: User registration data
            
        Returns:
            Tuple of (success, error_message, user_response)
        """
        try:
            # Validate inputs
            if not self.validate_username(registration_data.username):
                return False, "Invalid username format", None
            
            is_valid_password, password_details = self.validate_password_strength(registration_data.password)
            if not is_valid_password:
                return False, password_details["error"], None
            
            # Check if username already exists
            existing_user = await self._get_user_by_username(registration_data.username)
            if existing_user:
                return False, "Username already exists", None
            
            # Check if email already exists
            existing_email = await self._get_user_by_email(registration_data.email)
            if existing_email:
                return False, "Email already exists", None
            
            # Create new user
            hashed_password = self.hash_password(registration_data.password)

            # Log the date_of_birth for debugging
            logger.info(f"Registration date_of_birth: {registration_data.date_of_birth}, type: {type(registration_data.date_of_birth)}, tzinfo: {getattr(registration_data.date_of_birth, 'tzinfo', None)}")

            # Convert aware datetime to naive for database storage
            date_of_birth_naive = registration_data.date_of_birth.replace(tzinfo=None) if registration_data.date_of_birth else None

            new_user = Users(
                username=registration_data.username,
                email=registration_data.email,
                password=hashed_password,
                date_of_birth=date_of_birth_naive,
                is_verified=False,
                preference_finished=False
            )
            
            self.db.add(new_user)
            await self.db.commit()
            await self.db.refresh(new_user)
            
            # # Send verification email
            # await self.email_service.send_verification_email(
            #     email=registration_data.email,
            #     user_id=new_user.user_id,
            #     verification_type="email_verification"
            # )
            
            # Create JWT tokens
            access_token = create_access_token({
                "sub": str(new_user.user_id),
                "username": new_user.username,
                "email": new_user.email,
                "is_verified": new_user.is_verified
            })
            
            # Create user session
            session_key = create_user_session(new_user, self.db)
            await self.db.commit()
            
            user_response = UserResponse(
                user_id=new_user.user_id,
                username=new_user.username,
                email=new_user.email,
                joindate=new_user.joindate,
                is_verified=new_user.is_verified,
                date_of_birth=new_user.date_of_birth,
                preference_finished=new_user.preference_finished,
                verification_completed=False,
                access_token=access_token,
                token_type="bearer"
            )
            
            self.log_operation("user_registration", {
                "user_id": new_user.user_id,
                "username": new_user.username,
                "email": new_user.email
            })
            
            return True, None, user_response
            
        except Exception as e:
            await self.db.rollback()
            self.log_error("user_registration", e, {"username": registration_data.username})
            return False, "Registration failed", None
    
    async def login_user(self, login_data: UserLogin) -> Tuple[bool, Optional[str], Optional[UserResponse]]:
        """
        Authenticate user and generate tokens.
        
        Args:
            login_data: User login data
            
        Returns:
            Tuple of (success, error_message, user_response)
        """
        try:
            # Get user by username
            user = await self._get_user_by_username(login_data.username)
            if not user:
                return False, "Invalid username or password", None
            
            # Check if account is locked (implement lockout logic if needed)
            # For now, we'll just check if user exists and password is correct
            
            # Verify password
            if not self.verify_password(login_data.password, user.password):
                return False, "Invalid username or password", None
            
            # Create JWT tokens
            access_token = create_access_token({
                "sub": str(user.user_id),
                "username": user.username,
                "email": user.email,
                "is_verified": user.is_verified
            })
            
            refresh_token = create_refresh_token({
                "sub": str(user.user_id),
                "username": user.username,
                "email": user.email
            })
            
            # Create user session
            session_key = create_user_session(user, self.db)
            await self.db.commit()
            
            user_response = UserResponse(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                joindate=user.joindate,
                is_verified=user.is_verified,
                date_of_birth=user.date_of_birth,
                preference_finished=user.preference_finished,
                verification_completed=user.is_verified,
                access_token=access_token,
                token_type="bearer"
            )
            
            self.log_operation("user_login", {
                "user_id": user.user_id,
                "username": user.username
            })
            
            return True, None, user_response
            
        except Exception as e:
            self.log_error("user_login", e, {"username": login_data.username})
            return False, "Login failed", None
    
    async def logout_user(self, user_id: int) -> bool:
        """
        Logout user by invalidating their session.
        
        Args:
            user_id: ID of user to logout
            
        Returns:
            True if logout successful
        """
        try:
            user = await self._get_user_by_id(user_id)
            if not user:
                return False
            
            invalidate_user_session(user, self.db)
            await self.db.commit()
            
            self.log_operation("user_logout", {"user_id": user_id})
            return True
            
        except Exception as e:
            self.log_error("user_logout", e, {"user_id": user_id})
            return False
    
    async def get_user_profile(self, user_id: int) -> Optional[UserResponse]:
        """
        Get user profile information.
        
        Args:
            user_id: ID of user
            
        Returns:
            User response object or None
        """
        try:
            user = await self._get_user_by_id(user_id)
            if not user:
                return None
            
            return UserResponse(
                user_id=user.user_id,
                username=user.username,
                email=user.email,
                joindate=user.joindate,
                is_verified=user.is_verified,
                date_of_birth=user.date_of_birth,
                preference_finished=user.preference_finished,
                verification_completed=user.is_verified,
                access_token=None,  # Don't return token in profile
                token_type=None
            )
            
        except Exception as e:
            self.log_error("get_user_profile", e, {"user_id": user_id})
            return None
    
    async def update_user_profile(self, user_id: int, update_data: UserUpdate) -> Tuple[bool, Optional[str], Optional[UserResponse]]:
        """
        Update user profile information.
        
        Args:
            user_id: ID of user to update
            update_data: Updated profile data
            
        Returns:
            Tuple of (success, error_message, user_response)
        """
        try:
            user = await self._get_user_by_id(user_id)
            if not user:
                return False, "User not found", None
            
            # Update fields if provided
            if update_data.username is not None:
                if not self.validate_username(update_data.username):
                    return False, "Invalid username format", None
                
                # Check if username is already taken
                existing_user = await self._get_user_by_username(update_data.username)
                if existing_user and existing_user.user_id != user_id:
                    return False, "Username already exists", None
                
                user.username = update_data.username
            
            if update_data.date_of_birth is not None:
                logger.info(f"Update date_of_birth: {update_data.date_of_birth}, type: {type(update_data.date_of_birth)}, tzinfo: {getattr(update_data.date_of_birth, 'tzinfo', None)}")
                # Convert aware datetime to naive for database storage
                user.date_of_birth = update_data.date_of_birth.replace(tzinfo=None)
            
            await self.db.commit()
            await self.db.refresh(user)
            
            user_response = await self.get_user_profile(user_id)
            
            self.log_operation("update_user_profile", {
                "user_id": user_id,
                "updated_fields": update_data.dict(exclude_unset=True)
            })
            
            return True, None, user_response
            
        except Exception as e:
            await self.db.rollback()
            self.log_error("update_user_profile", e, {"user_id": user_id})
            return False, "Profile update failed", None
    
    async def verify_user_email(self, email: str, verification_code: str) -> Tuple[bool, Optional[str]]:
        """
        Verify user's email address using verification code.
        
        Args:
            email: User's email address
            verification_code: Verification code from email
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            user_id = await self.email_service.verify_code(
                email=email,
                code=verification_code,
                verification_type="email_verification"
            )
            
            if not user_id:
                return False, "Invalid or expired verification code"
            
            # Check if user exists and update verification status
            user = await self._get_user_by_id(user_id)
            if user:
                user.is_verified = True
                await self.db.commit()
            
            self.log_operation("email_verification", {"user_id": user_id, "email": email})
            return True, None
            
        except Exception as e:
            self.log_error("email_verification", e, {"email": email})
            return False, "Email verification failed"
    
    async def request_password_reset(self, email: str) -> Tuple[bool, Optional[str]]:
        """
        Request password reset for user.
        
        Args:
            email: User's email address
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            user = await self._get_user_by_email(email)
            if not user:
                # Don't reveal if email exists or not
                return True, None
            
            # Send password reset email
            verification_id = await self.email_service.send_verification_email(
                email=email,
                user_id=user.user_id,
                verification_type="password_reset"
            )
            
            if not verification_id:
                return False, "Failed to send reset email"
            
            self.log_operation("password_reset_request", {"user_id": user.user_id, "email": email})
            return True, None
            
        except Exception as e:
            self.log_error("password_reset_request", e, {"email": email})
            return False, "Password reset request failed"
    
    async def reset_password(self, email: str, verification_code: str, new_password: str) -> Tuple[bool, Optional[str]]:
        """
        Reset user password using verification code.
        
        Args:
            email: User's email address
            verification_code: Verification code from email
            new_password: New password
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            # Validate new password
            is_valid_password, password_details = self.validate_password_strength(new_password)
            if not is_valid_password:
                return False, password_details["error"]
            
            # Verify the code
            user_id = await self.email_service.verify_code(
                email=email,
                code=verification_code,
                verification_type="password_reset"
            )
            
            if not user_id:
                return False, "Invalid or expired verification code"
            
            # Update password
            user = await self._get_user_by_id(user_id)
            if not user:
                return False, "User not found"
            
            hashed_password = self.hash_password(new_password)
            user.password = hashed_password
            
            # Invalidate any existing sessions
            invalidate_user_session(user, self.db)
            
            await self.db.commit()
            
            self.log_operation("password_reset", {"user_id": user_id, "email": email})
            return True, None
            
        except Exception as e:
            await self.db.rollback()
            self.log_error("password_reset", e, {"email": email})
            return False, "Password reset failed"
    
    # Helper methods
    
    async def _get_user_by_username(self, username: str) -> Optional[Users]:
        """Get user by username."""
        result = await self.db.execute(
            select(Users).where(Users.username == username)
        )
        return result.scalar_one_or_none()
    
    async def _get_user_by_email(self, email: str) -> Optional[Users]:
        """Get user by email."""
        result = await self.db.execute(
            select(Users).where(Users.email == email)
        )
        return result.scalar_one_or_none()
    
    async def _get_user_by_id(self, user_id: int) -> Optional[Users]:
        """Get user by ID."""
        result = await self.db.execute(
            select(Users).where(Users.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def check_username_availability(self, username: str) -> bool:
        """Check if username is available."""
        user = await self._get_user_by_username(username)
        return user is None
    
    async def check_email_availability(self, email: str) -> bool:
        """Check if email is available."""
        user = await self._get_user_by_email(email)
        return user is None
    
    async def get_user_statistics(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics."""
        try:
            user = await self._get_user_by_id(user_id)
            if not user:
                return {}
            
            return {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "joindate": user.joindate,
                "is_verified": user.is_verified,
                "date_of_birth": user.date_of_birth,
                "preference_finished": user.preference_finished,
                "last_session": user.session_at,
                "account_age_days": (datetime.now() - user.joindate).days
            }
            
        except Exception as e:
            self.log_error("get_user_statistics", e, {"user_id": user_id})
            return {}