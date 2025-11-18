from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from passlib.context import CryptContext
from datetime import datetime, timedelta
import secrets
import string
import logging
from typing import Optional, Dict, Any

from .base import BaseService, AuthenticationError, ValidationError
from models import Users, Verification, EmailVerification
from pydantic_models import (
    UserCreate, UserLogin, UserUpdate, 
    LoginResponse, UserResponse, EmailVerificationRequest
)

# Password hashing context
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

class AuthService(BaseService[Users, UserCreate, UserUpdate]):
    """
    Authentication service handling user registration, login, and verification
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(Users, db)
        self.logger = logging.getLogger("auth_service")
    
    def hash_password(self, password: str) -> str:
        """Hash a password using argon2"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def generate_access_token(self) -> str:
        """Generate a secure random access token"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(64))
    
    def generate_verification_code(self) -> str:
        """Generate a 6-digit verification code"""
        return ''.join(secrets.choice('0123456789') for _ in range(6))
    
    async def create_user(self, user_data: UserCreate) -> Optional[UserResponse]:
        """
        Create a new user account
        
        Args:
            user_data: User registration data
            
        Returns:
            UserResponse if successful, None if failed
        """
        try:
            # Validate data
            if not validate_email(user_data.email):
                raise ValidationError("Invalid email format")
            
            if user_data.password != user_data.confirmpassword:
                raise ValidationError("Passwords do not match")
            
            # Check if user already exists
            existing_user = await self.get_user_by_email(user_data.email)
            if existing_user:
                raise ValidationError("User with this email already exists")
            
            existing_username = await self.get_user_by_username(user_data.username)
            if existing_username:
                raise ValidationError("Username already exists")
            
            # Create user
            user_dict = user_data.dict(exclude={'confirmpassword'})
            user_dict['password'] = self.hash_password(user_data.password)
            user_dict['joindate'] = datetime.now()
            user_dict['is_verified'] = False
            user_dict['verification_completed'] = False
            user_dict['profile_picture'] = ""
            user_dict['description'] = ""
            
            user = await self.create(UserCreate(**user_dict))
            if not user:
                return None
            
            return UserResponse.from_orm(user)
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error creating user: {str(e)}")
            return None
    
    async def authenticate_user(self, login_data: UserLogin) -> Optional[LoginResponse]:
        """
        Authenticate user with username and password
        
        Args:
            login_data: User login credentials
            
        Returns:
            LoginResponse with access token if successful, None if failed
        """
        try:
            # Get user by username
            user = await self.get_user_by_username(login_data.username)
            if not user:
                return None
            
            # Verify password
            if not self.verify_password(login_data.password, user.password):
                return None
            
            # Generate access token
            access_token = self.generate_access_token()
            session_at = datetime.now()
            
            # Update user session
            await self.db.execute(
                update(Users)
                .where(Users.user_id == user.user_id)
                .values(access_key=access_token, session_at=session_at)
            )
            await self.db.commit()
            
            # Create response
            response_data = {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "joindate": user.joindate,
                "access_token": access_token,
                "token_type": "bearer",
                "profile_picture": user.profile_picture,
                "description": user.description,
                "is_verified": user.is_verified,
                "verification_completed": user.verification_completed
            }
            
            return LoginResponse(**response_data)
            
        except Exception as e:
            self.logger.error(f"Error authenticating user: {str(e)}")
            return None
    
    async def get_user_by_email(self, email: str) -> Optional[Users]:
        """Get user by email address"""
        try:
            result = await self.db.execute(
                select(Users).where(Users.email == email)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting user by email: {str(e)}")
            return None
    
    async def get_user_by_username(self, username: str) -> Optional[Users]:
        """Get user by username"""
        try:
            result = await self.db.execute(
                select(Users).where(Users.username == username)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting user by username: {str(e)}")
            return None
    
    async def get_user_by_token(self, token: str) -> Optional[Users]:
        """Get user by access token"""
        try:
            result = await self.db.execute(
                select(Users).where(Users.access_key == token)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.logger.error(f"Error getting user by token: {str(e)}")
            return None
    
    async def update_user_profile(self, user_id: int, profile_data: UserUpdate) -> Optional[UserResponse]:
        """
        Update user profile information
        
        Args:
            user_id: User ID to update
            profile_data: Profile update data
            
        Returns:
            Updated UserResponse or None if failed
        """
        try:
            # Validate data
            if profile_data.username:
                existing_user = await self.get_user_by_username(profile_data.username)
                if existing_user and existing_user.user_id != user_id:
                    raise ValidationError("Username already exists")
            
            if profile_data.age and not validate_age(profile_data.age):
                raise ValidationError("Invalid age")
            
            # Update user
            updated_user = await self.update(user_id, profile_data)
            if not updated_user:
                return None
            
            return UserResponse.from_orm(updated_user)
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error updating user profile: {str(e)}")
            return None
    
    async def logout_user(self, user_id: int) -> bool:
        """
        Logout user by clearing access token
        
        Args:
            user_id: User ID to logout
            
        Returns:
            True if successful
        """
        try:
            await self.db.execute(
                update(Users)
                .where(Users.user_id == user_id)
                .values(access_key=None, session_at=None)
            )
            await self.db.commit()
            self.logger.info(f"User {user_id} logged out successfully")
            return True
        except Exception as e:
            self.logger.error(f"Error logging out user {user_id}: {str(e)}")
            return False
    
    async def verify_age(self, user_id: int, age: int) -> bool:
        """
        Verify and update user age
        
        Args:
            user_id: User ID
            age: User age
            
        Returns:
            True if successful
        """
        try:
            if not validate_age(age):
                return False
            
            await self.db.execute(
                update(Users)
                .where(Users.user_id == user_id)
                .values(age=age, date_of_birth=datetime.now().replace(year=datetime.now().year - age))
            )
            await self.db.commit()
            return True
        except Exception as e:
            self.logger.error(f"Error verifying age for user {user_id}: {str(e)}")
            return False
    
    async def mark_verification_completed(self, user_id: int) -> bool:
        """
        Mark user as having completed verification process
        
        Args:
            user_id: User ID
            
        Returns:
            True if successful
        """
        try:
            await self.db.execute(
                update(Users)
                .where(Users.user_id == user_id)
                .values(verification_completed=True, is_verified=True)
            )
            await self.db.commit()
            return True
        except Exception as e:
            self.logger.error(f"Error marking verification completed for user {user_id}: {str(e)}")
            return False

# Import validation functions
from .base import validate_age, validate_email