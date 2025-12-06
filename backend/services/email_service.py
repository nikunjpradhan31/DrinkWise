"""
Email service for DrinkWise backend.
Handles email verification, password reset, and notification emails using FastMail.
"""

import secrets
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from pydantic import EmailStr
import logging
import os
from dotenv import load_dotenv

from models import Verification, Users
from .base import BaseService

# Load environment variables
load_dotenv()

# Email configuration
MAIL_USERNAME = os.getenv("MAIL_USERNAME", "")
MAIL_EMAIL = os.getenv("MAIL_EMAIL", "")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "")
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "DrinkWise")

# Configure FastMail
email_config = ConnectionConfig(
    MAIL_USERNAME=MAIL_EMAIL,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_EMAIL,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_FROM_NAME=MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

logger = logging.getLogger(__name__)

class EmailService(BaseService):
    """
    Service for handling all email-related operations in DrinkWise.
    """
    
    def __init__(self, db: AsyncSession):
        """Initialize email service with database session."""
        super().__init__(db)
        self.fastmail = FastMail(email_config)
        
        # Verification code settings
        self.CODE_LENGTH = 6
        self.CODE_EXPIRY_MINUTES = 10
        self.MAX_VERIFICATION_ATTEMPTS = 3
    
    def generate_verification_code(self) -> str:
        """
        Generate a secure 6-digit verification code.
        
        Returns:
            6-digit verification code as string
        """
        return str(secrets.randbelow(900000) + 100000)
    
    async def send_verification_email(self, email: EmailStr, user_id: int, verification_type: str = "email_verification") -> Optional[int]:
        """
        Send email verification code to user.
        
        Args:
            email: User's email address
            user_id: User ID
            verification_type: Type of verification (email_verification, password_reset, etc.)
            
        Returns:
            Verification ID if successful, None otherwise
        """
        try:
            # Generate verification code
            code = self.generate_verification_code()
            
            # Calculate expiry time
            expires_at = datetime.now() + timedelta(minutes=self.CODE_EXPIRY_MINUTES)
            
            # Create email content based on type
            if verification_type == "email_verification":
                subject = "DrinkWise - Verify Your Email"
                html_content = self._create_verification_email_html(email, code)
            elif verification_type == "password_reset":
                subject = "DrinkWise - Password Reset"
                html_content = self._create_password_reset_email_html(email, code)
            elif verification_type == "login_verification":
                subject = "DrinkWise - Login Verification"
                html_content = self._create_login_verification_email_html(email, code)
            else:
                subject = "DrinkWise - Verification Code"
                html_content = self._create_generic_verification_email_html(email, code)
            
            # Send email
            message = MessageSchema(
                subject=subject,
                recipients=[email],
                body=html_content,
                subtype=MessageType.html
            )
            
            await self.fastmail.send_message(message)
            
            # Store verification code in database
            verification = Verification(
                user_id=user_id,
                email=email,
                code=code,
                verification_type=verification_type,
                expires_at=expires_at
            )
            
            self.db.add(verification)
            await self.db.commit()
            await self.db.refresh(verification)
            
            logger.info(f"Verification email sent to {email} for user {user_id}")
            return verification.id
            
        except Exception as e:
            logger.error(f"Failed to send verification email: {str(e)}")
            return None
    
    def _create_verification_email_html(self, email: str, code: str) -> str:
        """Create HTML content for email verification."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>DrinkWise - Email Verification</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f8f9fa; padding: 30px; }}
                .code {{ font-size: 32px; font-weight: bold; text-align: center; 
                        background-color: #fff; border: 2px solid #007bff; 
                        padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .footer {{ text-align: center; font-size: 12px; color: #666; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🍺 DrinkWise</h1>
                </div>
                <div class="content">
                    <h2>Welcome to DrinkWise!</h2>
                    <p>Hi there!</p>
                    <p>Thank you for signing up for DrinkWise. To complete your registration, 
                       please verify your email address using the verification code below:</p>
                    <div class="code">{code}</div>
                    <p><strong>This code will expire in {self.CODE_EXPIRY_MINUTES} minutes.</strong></p>
                    <p>If you didn't create a DrinkWise account, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2025 DrinkWise - Personalized Drink Recommendations</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_password_reset_email_html(self, email: str, code: str) -> str:
        """Create HTML content for password reset."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>DrinkWise - Password Reset</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #e74c3c; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f8f9fa; padding: 30px; }}
                .code {{ font-size: 32px; font-weight: bold; text-align: center; 
                        background-color: #fff; border: 2px solid #e74c3c; 
                        padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .footer {{ text-align: center; font-size: 12px; color: #666; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🍺 DrinkWise</h1>
                </div>
                <div class="content">
                    <h2>Password Reset Request</h2>
                    <p>We received a request to reset your DrinkWise password.</p>
                    <p>Please use the verification code below to reset your password:</p>
                    <div class="code">{code}</div>
                    <p><strong>This code will expire in {self.CODE_EXPIRY_MINUTES} minutes.</strong></p>
                    <p>If you didn't request a password reset, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>© 2025 DrinkWise - Personalized Drink Recommendations</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_login_verification_email_html(self, email: str, code: str) -> str:
        """Create HTML content for login verification."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>DrinkWise - Login Verification</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #27ae60; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f8f9fa; padding: 30px; }}
                .code {{ font-size: 32px; font-weight: bold; text-align: center; 
                        background-color: #fff; border: 2px solid #27ae60; 
                        padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .footer {{ text-align: center; font-size: 12px; color: #666; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🍺 DrinkWise</h1>
                </div>
                <div class="content">
                    <h2>Login Verification</h2>
                    <p>We detected a login attempt from a new device or location.</p>
                    <p>Please verify this login by entering the code below:</p>
                    <div class="code">{code}</div>
                    <p><strong>This code will expire in {self.CODE_EXPIRY_MINUTES} minutes.</strong></p>
                    <p>If this was you, you can safely ignore this message.</p>
                </div>
                <div class="footer">
                    <p>© 2025 DrinkWise - Personalized Drink Recommendations</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    def _create_generic_verification_email_html(self, email: str, code: str) -> str:
        """Create generic HTML content for verification."""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>DrinkWise - Verification</title>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f8f9fa; padding: 30px; }}
                .code {{ font-size: 32px; font-weight: bold; text-align: center; 
                        background-color: #fff; border: 2px solid #007bff; 
                        padding: 20px; margin: 20px 0; border-radius: 8px; }}
                .footer {{ text-align: center; font-size: 12px; color: #666; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🍺 DrinkWise</h1>
                </div>
                <div class="content">
                    <h2>Verification Code</h2>
                    <p>Your verification code is:</p>
                    <div class="code">{code}</div>
                    <p><strong>This code will expire in {self.CODE_EXPIRY_MINUTES} minutes.</strong></p>
                </div>
                <div class="footer">
                    <p>© 2025 DrinkWise - Personalized Drink Recommendations</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    async def verify_code(self, email: EmailStr, code: str, verification_type: str) -> Optional[int]:
        """
        Verify a verification code.
        
        Args:
            email: Email address
            code: Verification code
            verification_type: Type of verification
            
        Returns:
            User ID if verification successful, None otherwise
        """
        try:
            # Get the latest valid verification record
            result = await self.db.execute(
                select(Verification)
                .where(
                    Verification.email == email,
                    Verification.code == code,
                    Verification.verification_type == verification_type,
                    Verification.is_used == False,
                    Verification.expires_at > datetime.now()
                )
                .order_by(Verification.created_at.desc())
                .limit(1)
            )
            
            verification = result.scalar_one_or_none()
            
            if not verification:
                return None
            
            # Mark verification as used
            verification.is_used = True
            
            # If this is email verification, update user verification status
            if verification_type == "email_verification":
                await self.db.execute(
                    update(Users)
                    .where(Users.user_id == verification.user_id)
                    .values(is_verified=True)
                )
            
            await self.db.commit()
            
            logger.info(f"Verification successful for {email}")
            return verification.user_id
            
        except Exception as e:
            logger.error(f"Failed to verify code: {str(e)}")
            return None
    
    async def resend_verification(self, email: EmailStr, verification_type: str) -> bool:
        """
        Resend verification email.
        
        Args:
            email: Email address
            verification_type: Type of verification
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get user ID from email
            result = await self.db.execute(
                select(Users).where(Users.email == email)
            )
            user = result.scalar_one_or_none()
            
            if not user:
                return False
            
            # Remove existing pending verifications
            await self.db.execute(
                delete(Verification).where(
                    Verification.email == email,
                    Verification.verification_type == verification_type,
                    Verification.is_used == False
                )
            )
            
            # Send new verification email
            verification_id = await self.send_verification_email(email, user.user_id, verification_type)
            
            return verification_id is not None
            
        except Exception as e:
            logger.error(f"Failed to resend verification: {str(e)}")
            return False
    
    async def cleanup_expired_verifications(self):
        """Clean up expired verification codes."""
        try:
            await self.db.execute(
                delete(Verification).where(
                    Verification.expires_at < datetime.now()
                )
            )
            await self.db.commit()
            logger.info("Cleaned up expired verification codes")
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired verifications: {str(e)}")
    
    async def is_verification_pending(self, email: EmailStr, verification_type: str) -> bool:
        """
        Check if there's a pending verification for the email.
        
        Args:
            email: Email address
            verification_type: Type of verification
            
        Returns:
            True if verification is pending
        """
        try:
            result = await self.db.execute(
                select(Verification).where(
                    Verification.email == email,
                    Verification.verification_type == verification_type,
                    Verification.is_used == False,
                    Verification.expires_at > datetime.now()
                )
            )
            
            return result.scalar_one_or_none() is not None
            
        except Exception as e:
            logger.error(f"Failed to check verification status: {str(e)}")
            return False
    
    async def get_verification_attempts(self, email: EmailStr, verification_type: str) -> int:
        """
        Get number of verification attempts for an email.
        
        Args:
            email: Email address
            verification_type: Type of verification
            
        Returns:
            Number of attempts in the last hour
        """
        try:
            one_hour_ago = datetime.now() - timedelta(hours=1)
            
            result = await self.db.execute(
                select(Verification).where(
                    Verification.email == email,
                    Verification.verification_type == verification_type,
                    Verification.created_at > one_hour_ago
                )
            )
            
            verifications = result.scalars().all()
            return len(verifications)
            
        except Exception as e:
            logger.error(f"Failed to get verification attempts: {str(e)}")
            return 0

# Email template constants
EMAIL_TEMPLATES = {
    "welcome": "Welcome to DrinkWise! Your personalized drink journey starts now.",
    "password_reset": "Reset your DrinkWise password with this verification code.",
    "login_verification": "Verify your login to keep your DrinkWise account secure.",
    "email_verification": "Verify your email to complete your DrinkWise registration."
}

# Email subjects
EMAIL_SUBJECTS = {
    "email_verification": "DrinkWise - Verify Your Email",
    "password_reset": "DrinkWise - Password Reset",
    "login_verification": "DrinkWise - Login Verification",
    "welcome": "Welcome to DrinkWise!"
}