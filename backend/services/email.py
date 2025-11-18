from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from datetime import datetime, timedelta
import logging
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any

from .base import BaseService, ValidationError
from models import EmailVerification, Verification
from pydantic_models import (
    EmailVerificationRequest, EmailVerificationResponse,
    VerifyEmailRequest, VerifyEmailResponse
)

class EmailService:
    """
    Service for handling email verification and communications
    Integrates with FastAPI-Mail for email sending
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.logger = logging.getLogger("email_service")
    
    async def send_verification_email(self, user_id: int, email: str) -> Optional[EmailVerificationResponse]:
        """
        Send email verification to user
        
        Args:
            user_id: User ID
            email: User email address
            
        Returns:
            EmailVerificationResponse or None
        """
        try:
            # Generate verification token
            verification_token = secrets.token_urlsafe(32)
            
            # Create email verification record
            email_verification = EmailVerification(
                user_id=user_id,
                email=email,
                verification_token=verification_token,
                created_at=datetime.now(),
                expires_at=datetime.now() + timedelta(hours=24),
                is_verified=False
            )
            
            self.db.add(email_verification)
            await self.db.commit()
            await self.db.refresh(email_verification)
            
            # Send email (placeholder - would integrate with actual email service)
            email_sent = await self._send_email(
                to_email=email,
                subject="Verify Your DrinkWise Account",
                html_content=self._get_verification_email_template(verification_token, user_id)
            )
            
            if not email_sent:
                self.logger.error(f"Failed to send verification email to {email}")
                return None
            
            return EmailVerificationResponse(
                verification_id=email_verification.verification_id,
                user_id=user_id,
                email=email,
                message="Verification email sent successfully"
            )
            
        except Exception as e:
            self.logger.error(f"Error sending verification email: {str(e)}")
            await self.db.rollback()
            return None
    
    async def verify_email_token(self, verify_request: VerifyEmailRequest) -> Optional[VerifyEmailResponse]:
        """
        Verify email using verification token
        
        Args:
            verify_request: Token verification request
            
        Returns:
            VerifyEmailResponse or None
        """
        try:
            # Find verification record
            result = await self.db.execute(
                select(EmailVerification).where(
                    EmailVerification.verification_token == verify_request.verification_token,
                    EmailVerification.is_verified == False
                )
            )
            email_verification = result.scalar_one_or_none()
            
            if not email_verification:
                raise ValidationError("Invalid or expired verification token")
            
            # Check if token is expired
            if datetime.now() > email_verification.expires_at:
                raise ValidationError("Verification token has expired")
            
            # Mark as verified
            await self.db.execute(
                update(EmailVerification)
                .where(EmailVerification.verification_id == email_verification.verification_id)
                .values(is_verified=True)
            )
            
            await self.db.commit()
            
            return VerifyEmailResponse(
                user_id=email_verification.user_id,
                email=email_verification.email,
                is_verified=True,
                message="Email verified successfully"
            )
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error verifying email token: {str(e)}")
            await self.db.rollback()
            return None
    
    async def send_password_reset_email(self, user_id: int, email: str, reset_token: str) -> bool:
        """
        Send password reset email
        
        Args:
            user_id: User ID
            email: User email
            reset_token: Password reset token
            
        Returns:
            True if email sent successfully
        """
        try:
            email_content = self._get_password_reset_email_template(reset_token, user_id)
            
            email_sent = await self._send_email(
                to_email=email,
                subject="Reset Your DrinkWise Password",
                html_content=email_content
            )
            
            if email_sent:
                self.logger.info(f"Password reset email sent to {email}")
                return True
            else:
                self.logger.error(f"Failed to send password reset email to {email}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending password reset email: {str(e)}")
            return False
    
    async def send_welcome_email(self, user_id: int, email: str, username: str) -> bool:
        """
        Send welcome email to new user
        
        Args:
            user_id: User ID
            email: User email
            username: Username
            
        Returns:
            True if email sent successfully
        """
        try:
            email_content = self._get_welcome_email_template(username)
            
            email_sent = await self._send_email(
                to_email=email,
                subject="Welcome to DrinkWise!",
                html_content=email_content
            )
            
            if email_sent:
                self.logger.info(f"Welcome email sent to {email}")
                return True
            else:
                self.logger.error(f"Failed to send welcome email to {email}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending welcome email: {str(e)}")
            return False
    
    async def send_recommendation_email(self, user_id: int, email: str, recommendations: list) -> bool:
        """
        Send personalized recommendations email
        
        Args:
            user_id: User ID
            email: User email
            recommendations: List of recommended drinks
            
        Returns:
            True if email sent successfully
        """
        try:
            email_content = self._get_recommendations_email_template(recommendations)
            
            email_sent = await self._send_email(
                to_email=email,
                subject="Your Personalized Drink Recommendations",
                html_content=email_content
            )
            
            if email_sent:
                self.logger.info(f"Recommendations email sent to {email}")
                return True
            else:
                self.logger.error(f"Failed to send recommendations email to {email}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error sending recommendations email: {str(e)}")
            return False
    
    async def cleanup_expired_verifications(self) -> int:
        """
        Clean up expired email verifications
        
        Returns:
            Number of records cleaned up
        """
        try:
            result = await self.db.execute(
                delete(EmailVerification).where(
                    EmailVerification.expires_at < datetime.now(),
                    EmailVerification.is_verified == False
                )
            )
            await self.db.commit()
            
            # Note: result.rowcount might not be available for all DB drivers
            self.logger.info("Cleaned up expired email verifications")
            return 1  # Placeholder return
            
        except Exception as e:
            self.logger.error(f"Error cleaning up expired verifications: {str(e)}")
            return 0
    
    async def _send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """
        Send email using SMTP or FastAPI-Mail (placeholder implementation)
        
        Args:
            to_email: Recipient email
            subject: Email subject
            html_content: HTML content
            
        Returns:
            True if sent successfully
        """
        try:
            # In a real implementation, this would use FastAPI-Mail or similar
            # For now, we'll simulate email sending
            
            self.logger.info(f"EMAIL SENT:")
            self.logger.info(f"To: {to_email}")
            self.logger.info(f"Subject: {subject}")
            self.logger.info(f"Content: {html_content[:100]}...")
            
            # Simulate email sending delay
            import asyncio
            await asyncio.sleep(0.1)
            
            # Simulate success (90% success rate for testing)
            import random
            return random.random() > 0.1
            
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False
    
    def _get_verification_email_template(self, token: str, user_id: int) -> str:
        """Get email verification HTML template"""
        verification_url = f"https://drinkwise.com/verify?token={token}&user_id={user_id}"
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #2c3e50;">Welcome to DrinkWise!</h1>
                
                <p>Thank you for signing up for DrinkWise! To complete your registration and start discovering your perfect drinks, please verify your email address.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background-color: #3498db; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Verify Email Address
                    </a>
                </div>
                
                <p>If the button doesn't work, you can also copy and paste this link into your browser:</p>
                <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 3px;">
                    {verification_url}
                </p>
                
                <p><strong>Note:</strong> This verification link will expire in 24 hours.</p>
                
                <p>If you didn't create an account with DrinkWise, please ignore this email.</p>
                
                <hr style="margin: 30px 0;">
                
                <p style="font-size: 12px; color: #666;">
                    This is an automated message from DrinkWise. Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
    
    def _get_password_reset_email_template(self, reset_token: str, user_id: int) -> str:
        """Get password reset email HTML template"""
        reset_url = f"https://drinkwise.com/reset-password?token={reset_token}&user_id={user_id}"
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #e74c3c;">Password Reset Request</h1>
                
                <p>We received a request to reset your DrinkWise password. If you made this request, click the button below to reset your password.</p>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" style="background-color: #e74c3c; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Reset Password
                    </a>
                </div>
                
                <p>If the button doesn't work, you can also copy and paste this link into your browser:</p>
                <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 3px;">
                    {reset_url}
                </p>
                
                <p><strong>Note:</strong> This reset link will expire in 1 hour.</p>
                
                <p>If you didn't request a password reset, please ignore this email. Your password will remain unchanged.</p>
                
                <hr style="margin: 30px 0;">
                
                <p style="font-size: 12px; color: #666;">
                    This is an automated message from DrinkWise. Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
    
    def _get_welcome_email_template(self, username: str) -> str:
        """Get welcome email HTML template"""
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #27ae60;">Welcome to DrinkWise, {username}!</h1>
                
                <p>We're excited to have you join the DrinkWise community! You're now ready to discover drinks perfectly tailored to your taste preferences.</p>
                
                <h3 style="color: #2c3e50;">Here's what you can do next:</h3>
                
                <ul>
                    <li><strong>Complete your taste profile:</strong> Take our 60-second quiz to get personalized recommendations</li>
                    <li><strong>Set your preferences:</strong> Adjust sweetness, caffeine, and dietary preferences</li>
                    <li><strong>Browse our catalog:</strong> Explore drinks from coffee to smoothies to cocktails</li>
                    <li><strong>Save favorites:</strong> Keep track of drinks you love</li>
                </ul>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://drinkwise.com/quiz" style="background-color: #27ae60; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        Take the Taste Quiz
                    </a>
                </div>
                
                <p>If you have any questions or need help getting started, our support team is here to help!</p>
                
                <p>Cheers to finding your perfect drink!</p>
                
                <p>The DrinkWise Team</p>
                
                <hr style="margin: 30px 0;">
                
                <p style="font-size: 12px; color: #666;">
                    This is an automated message from DrinkWise. Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
    
    def _get_recommendations_email_template(self, recommendations: list) -> str:
        """Get personalized recommendations email HTML template"""
        recommendations_html = ""
        
        for drink in recommendations[:5]:  # Limit to top 5
            recommendations_html += f"""
            <div style="border: 1px solid #ddd; padding: 15px; margin: 10px 0; border-radius: 5px;">
                <h4 style="margin: 0 0 10px 0; color: #2c3e50;">{drink.get('name', 'Unknown Drink')}</h4>
                <p style="margin: 5px 0; color: #666;">{drink.get('description', 'No description available')}</p>
                <p style="margin: 5px 0;"><strong>Category:</strong> {drink.get('category', 'N/A')}</p>
                <p style="margin: 5px 0;"><strong>Sweetness:</strong> {drink.get('sweetness_level', 'N/A')}/10</p>
                <p style="margin: 5px 0;"><strong>Caffeine:</strong> {drink.get('caffeine_content', 0)}mg</p>
            </div>
            """
        
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #f39c12;">Your Personalized Drink Recommendations</h1>
                
                <p>Based on your taste preferences and past interactions, we've handpicked some drinks we think you'll love!</p>
                
                <h3 style="color: #2c3e50;">Top Recommendations:</h3>
                
                {recommendations_html}
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="https://drinkwise.com/recommendations" style="background-color: #f39c12; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                        View All Recommendations
                    </a>
                </div>
                
                <p>Don't forget to let us know what you think! Your feedback helps us improve our recommendations.</p>
                
                <p>Enjoy discovering your next favorite drink!</p>
                
                <p>The DrinkWise Team</p>
                
                <hr style="margin: 30px 0;">
                
                <p style="font-size: 12px; color: #666;">
                    This is an automated message from DrinkWise. Please do not reply to this email.
                </p>
            </div>
        </body>
        </html>
        """
    
    async def get_email_analytics(self) -> Dict[str, Any]:
        """
        Get email service analytics
        
        Returns:
            Dictionary with email analytics
        """
        try:
            # Get email verification stats
            verifications_result = await self.db.execute(
                select(EmailVerification)
            )
            verifications = verifications_result.scalars().all()
            
            total_sent = len(verifications)
            total_verified = sum(1 for v in verifications if v.is_verified)
            verification_rate = (total_verified / total_sent * 100) if total_sent > 0 else 0
            
            return {
                "total_emails_sent": total_sent,
                "total_verifications": total_verified,
                "verification_rate": round(verification_rate, 2),
                "expired_tokens": sum(1 for v in verifications if datetime.now() > v.expires_at and not v.is_verified)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting email analytics: {str(e)}")
            return {
                "total_emails_sent": 0,
                "total_verifications": 0,
                "verification_rate": 0,
                "expired_tokens": 0
            }