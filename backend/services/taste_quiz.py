from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from datetime import datetime
import logging
import random
from typing import Optional, Dict, Any, List

from .base import BaseService, ValidationError
from models import TasteQuizQuestion, TasteQuizResult
from pydantic_models import (
    TasteQuizQuestionCreate, TasteQuizQuestionResponse, 
    TasteQuizSubmission, QuizAnswer
)

class TasteQuizService(BaseService[TasteQuizQuestion, TasteQuizQuestionCreate, Dict]):
    """
    Service for managing taste quiz questions and processing user responses
    """
    
    def __init__(self, db: AsyncSession):
        super().__init__(TasteQuizQuestion, db)
        self.logger = logging.getLogger("taste_quiz_service")
    
    # Pre-defined quiz questions for different categories
    SAMPLE_QUESTIONS = [
        {
            "question_text": "How do you prefer your coffee?",
            "question_type": "multiple_choice",
            "options": ["Very sweet", "Slightly sweet", "Black", "With cream only"],
            "category": "sweetness"
        },
        {
            "question_text": "What bitterness level do you prefer?",
            "question_type": "scale",
            "options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            "category": "bitterness"
        },
        {
            "question_text": "Do you prefer caffeinated or decaffeinated beverages?",
            "question_type": "boolean",
            "options": ["Caffeinated", "Decaffeinated"],
            "category": "caffeine"
        },
        {
            "question_text": "What time of day do you usually have your first beverage?",
            "question_type": "multiple_choice",
            "options": ["Morning", "Afternoon", "Evening", "Night"],
            "category": "timing"
        },
        {
            "question_text": "How important is sugar content to you?",
            "question_type": "scale",
            "options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            "category": "sugar"
        },
        {
            "question_text": "What budget range do you prefer for drinks?",
            "question_type": "multiple_choice",
            "options": ["$ (Under $5)", "$$ ($5-$10)", "$$$ (Over $10)"],
            "category": "budget"
        },
        {
            "question_text": "Do you have any food allergies or ingredient dislikes?",
            "question_type": "multiple_choice",
            "options": ["None", "Dairy", "Nuts", "Gluten", "Sugar", "Other"],
            "category": "allergies"
        },
        {
            "question_text": "How adventurous are you with new flavors?",
            "question_type": "scale",
            "options": ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"],
            "category": "adventure"
        },
        {
            "question_text": "What beverage temperature do you prefer?",
            "question_type": "multiple_choice",
            "options": ["Very hot", "Warm", "Room temperature", "Cold", "Very cold"],
            "category": "temperature"
        },
        {
            "question_text": "Do you prefer traditional or innovative drink combinations?",
            "question_type": "multiple_choice",
            "options": ["Traditional only", "Mostly traditional", "Mix of both", "Mostly innovative", "Very innovative"],
            "category": "innovation"
        }
    ]
    
    async def initialize_sample_questions(self) -> bool:
        """
        Initialize the database with sample quiz questions
        
        Returns:
            True if successful
        """
        try:
            # Check if questions already exist
            existing_count = await self.count()
            if existing_count > 0:
                self.logger.info("Sample questions already exist")
                return True
            
            # Create sample questions
            questions_to_create = []
            for question_data in self.SAMPLE_QUESTIONS:
                question = TasteQuizQuestionCreate(**question_data)
                questions_to_create.append(question)
            
            # Bulk create questions
            created_questions = await self.bulk_create(questions_to_create)
            
            if len(created_questions) == len(self.SAMPLE_QUESTIONS):
                self.logger.info(f"Successfully created {len(created_questions)} sample questions")
                return True
            else:
                self.logger.error("Failed to create all sample questions")
                return False
                
        except Exception as e:
            self.logger.error(f"Error initializing sample questions: {str(e)}")
            return False
    
    async def get_random_questions(self, count: int = 8) -> List[TasteQuizQuestionResponse]:
        """
        Get random quiz questions for onboarding
        
        Args:
            count: Number of questions to return
            
        Returns:
            List of TasteQuizQuestionResponse
        """
        try:
            # Get all active questions
            result = await self.db.execute(
                select(TasteQuizQuestion).where(TasteQuizQuestion.is_active == True)
            )
            all_questions = result.scalars().all()
            
            if len(all_questions) <= count:
                # Return all questions if we have fewer than requested
                return [TasteQuizQuestionResponse.from_orm(q) for q in all_questions]
            
            # Randomly select questions
            selected_questions = random.sample(all_questions, count)
            return [TasteQuizQuestionResponse.from_orm(q) for q in selected_questions]
            
        except Exception as e:
            self.logger.error(f"Error getting random questions: {str(e)}")
            return []
    
    async def submit_quiz_answers(self, user_id: int, submission: TasteQuizSubmission) -> bool:
        """
        Process quiz submission and store user answers
        
        Args:
            user_id: User ID
            submission: Quiz answers
            
        Returns:
            True if successful
        """
        try:
            # Validate that all questions exist
            question_ids = [answer.question_id for answer in submission.answers]
            existing_questions = await self.db.execute(
                select(TasteQuizQuestion.question_id).where(
                    TasteQuizQuestion.question_id.in_(question_ids),
                    TasteQuizQuestion.is_active == True
                )
            )
            existing_ids = [q[0] for q in existing_questions.scalars().all()]
            
            # Check if all submitted question IDs exist
            if set(question_ids) != set(existing_ids):
                raise ValidationError("One or more questions are invalid or inactive")
            
            # Delete existing answers for this user (to avoid duplicates)
            await self.db.execute(
                delete(TasteQuizResult).where(TasteQuizResult.user_id == user_id)
            )
            
            # Store new answers
            for answer in submission.answers:
                quiz_result = TasteQuizResult(
                    user_id=user_id,
                    question_id=answer.question_id,
                    answer=answer.answer,
                    answered_at=datetime.now()
                )
                self.db.add(quiz_result)
            
            await self.db.commit()
            
            self.logger.info(f"Quiz submitted successfully for user {user_id}")
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error submitting quiz answers: {str(e)}")
            await self.db.rollback()
            return False
    
    async def get_user_quiz_results(self, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Get user's quiz results and convert to preference profile
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary with preference profile or None
        """
        try:
            # Get user's answers
            result = await self.db.execute(
                select(TasteQuizResult).where(TasteQuizResult.user_id == user_id)
            )
            answers = result.scalars().all()
            
            if not answers:
                return None
            
            # Convert answers to preference profile
            preference_profile = self._convert_answers_to_preferences(answers)
            
            return {
                "user_id": user_id,
                "answers": [{"question_id": a.question_id, "answer": a.answer} for a in answers],
                "preference_profile": preference_profile,
                "quiz_completed_at": max(a.answered_at for a in answers)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user quiz results: {str(e)}")
            return None
    
    async def has_user_completed_quiz(self, user_id: int) -> bool:
        """
        Check if user has completed the taste quiz
        
        Args:
            user_id: User ID
            
        Returns:
            True if quiz completed
        """
        try:
            result = await self.db.execute(
                select(TasteQuizResult).where(TasteQuizResult.user_id == user_id).limit(1)
            )
            return result.scalar_one_or_none() is not None
        except Exception as e:
            self.logger.error(f"Error checking quiz completion: {str(e)}")
            return False
    
    async def get_quiz_analytics(self) -> Dict[str, Any]:
        """
        Get analytics about quiz participation
        
        Returns:
            Dictionary with quiz analytics
        """
        try:
            # Get total questions
            total_questions = await self.db.execute(
                select(TasteQuizQuestion).where(TasteQuizQuestion.is_active == True)
            )
            total_active_questions = len(total_questions.scalars().all())
            
            # Get total participants
            participants_result = await self.db.execute(
                select(TasteQuizResult.user_id).distinct()
            )
            total_participants = len(participants_result.scalars().all())
            
            # Get average completion rate
            completion_stats = await self.db.execute(
                select(TasteQuizResult.user_id, func.count(TasteQuizResult.question_id))
                .group_by(TasteQuizResult.user_id)
            )
            completions = completion_stats.scalars().all()
            
            avg_questions_per_user = sum(c[1] for c in completions) / len(completions) if completions else 0
            
            return {
                "total_active_questions": total_active_questions,
                "total_participants": total_participants,
                "average_questions_per_user": round(avg_questions_per_user, 2),
                "completion_rate": round((avg_questions_per_user / total_active_questions) * 100, 2) if total_active_questions > 0 else 0
            }
            
        except Exception as e:
            self.logger.error(f"Error getting quiz analytics: {str(e)}")
            return {
                "total_active_questions": 0,
                "total_participants": 0,
                "average_questions_per_user": 0,
                "completion_rate": 0
            }
    
    def _convert_answers_to_preferences(self, answers: List[TasteQuizResult]) -> Dict[str, Any]:
        """
        Convert quiz answers to preference profile
        
        Args:
            answers: List of user answers
            
        Returns:
            Dictionary with preference profile
        """
        try:
            preferences = {
                "sweetness_preference": 5,  # Default
                "bitterness_preference": 5,  # Default
                "preferred_categories": [],
                "caffeine_limit": 400,  # Default daily limit
                "sugar_limit": 50.0,  # Default daily limit
                "preferred_price_tier": "$$",  # Default
                "time_sensitivity": {},
                "mode_preferences": {},
                "allergies": [],
                "adventure_level": 5
            }
            
            for answer in answers:
                answer_value = answer.answer
                
                # Map answers to preferences
                if answer.question.category == "sweetness":
                    if answer_value == "Very sweet":
                        preferences["sweetness_preference"] = 8
                    elif answer_value == "Slightly sweet":
                        preferences["sweetness_preference"] = 6
                    elif answer_value == "Black":
                        preferences["sweetness_preference"] = 2
                    elif answer_value == "With cream only":
                        preferences["sweetness_preference"] = 4
                
                elif answer.question.category == "bitterness":
                    preferences["bitterness_preference"] = int(answer_value)
                
                elif answer.question.category == "caffeine":
                    if answer_value == "Decaffeinated":
                        preferences["mode_preferences"]["decaf_preference"] = True
                        preferences["caffeine_limit"] = 50
                
                elif answer.question.category == "budget":
                    if answer_value == "$ (Under $5)":
                        preferences["preferred_price_tier"] = "$"
                    elif answer_value == "$$ ($5-$10)":
                        preferences["preferred_price_tier"] = "$$"
                    elif answer_value == "$$$ (Over $10)":
                        preferences["preferred_price_tier"] = "$$$"
                
                elif answer.question.category == "sugar":
                    preferences["sugar_limit"] = (int(answer_value) - 5) * 10 + 50  # Scale 1-10 to 0-100
                
                elif answer.question.category == "adventure":
                    preferences["adventure_level"] = int(answer_value)
                    if int(answer_value) >= 7:
                        preferences["preferred_categories"].extend(["innovative", "experimental"])
                
                elif answer.question.category == "temperature":
                    preferences["time_sensitivity"]["preferred_temperature"] = answer_value
                
                elif answer.question.category == "innovation":
                    if answer_value in ["Very innovative", "Mostly innovative"]:
                        preferences["preferred_categories"].append("innovative")
                    elif answer_value in ["Traditional only", "Mostly traditional"]:
                        preferences["preferred_categories"].append("traditional")
                
                elif answer.question.category == "allergies":
                    if answer_value != "None":
                        preferences["allergies"].append(answer_value.lower())
            
            return preferences
            
        except Exception as e:
            self.logger.error(f"Error converting answers to preferences: {str(e)}")
            # Return default preferences
            return {
                "sweetness_preference": 5,
                "bitterness_preference": 5,
                "preferred_categories": [],
                "caffeine_limit": 400,
                "sugar_limit": 50.0,
                "preferred_price_tier": "$$",
                "time_sensitivity": {},
                "mode_preferences": {},
                "allergies": [],
                "adventure_level": 5
            }
    
    async def create_custom_question(self, question_data: TasteQuizQuestionCreate) -> Optional[TasteQuizQuestionResponse]:
        """
        Create a custom quiz question (admin function)
        
        Args:
            question_data: Question data
            
        Returns:
            Created TasteQuizQuestionResponse or None
        """
        try:
            question_dict = question_data.dict()
            question_dict['created_at'] = datetime.now()
            question_dict['is_active'] = True
            
            question = await self.create(TasteQuizQuestionCreate(**question_dict))
            if not question:
                return None
            
            return TasteQuizQuestionResponse.from_orm(question)
            
        except Exception as e:
            self.logger.error(f"Error creating custom question: {str(e)}")
            return None
    
    async def deactivate_question(self, question_id: int) -> bool:
        """
        Deactivate a quiz question (admin function)
        
        Args:
            question_id: Question ID
            
        Returns:
            True if successful
        """
        try:
            await self.db.execute(
                update(TasteQuizQuestion)
                .where(TasteQuizQuestion.question_id == question_id)
                .values(is_active=False)
            )
            await self.db.commit()
            return True
            
        except Exception as e:
            self.logger.error(f"Error deactivating question {question_id}: {str(e)}")
            return False