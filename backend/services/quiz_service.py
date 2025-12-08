# """
# Taste quiz service for DrinkWise backend.
# Handles taste preference questions and answer processing.
# """

# from typing import Optional, Dict, Any, List, Tuple
# from datetime import datetime
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy import select, update, delete, func
# from sqlalchemy.orm import selectinload
# import logging

# from models import TasteQuizQuestion, TasteQuizOption, TasteQuizResult, Users
# from .base import BaseService
# from pydantic_models import (
#     QuizQuestion, QuizOption, QuizQuestionsResponse,
#     QuizAnswer, QuizSubmission, QuizSubmissionResponse
# )

# logger = logging.getLogger(__name__)

# class TasteQuizService(BaseService):
#     """
#     Service for handling taste quiz operations in DrinkWise.
#     """
    
#     def __init__(self, db: AsyncSession):
#         """Initialize taste quiz service with database session."""
#         super().__init__(db)
        
#         # Default quiz questions for initialization
#         self.DEFAULT_QUESTIONS = [
#             {
#                 "question_text": "How sweet do you like your drinks?",
#                 "options": [
#                     "Not sweet at all - I prefer bitter or savory",
#                     "Slightly sweet - just a hint of sweetness", 
#                     "Moderately sweet - balanced sweetness",
#                     "Quite sweet - I enjoy sweet flavors",
#                     "Very sweet - I love intensely sweet drinks"
#                 ]
#             },
#             {
#                 "question_text": "How do you feel about caffeine?",
#                 "options": [
#                     "I avoid caffeine completely",
#                     "Very little caffeine - occasional tea or coffee",
#                     "Moderate caffeine - 1-2 cups of coffee per day",
#                     "Quite a bit of caffeine - several caffeinated drinks",
#                     "I love high caffeine content drinks"
#                 ]
#             },
#             {
#                 "question_text": "What's your preferred drink temperature?",
#                 "options": [
#                     "Iced or cold drinks only",
#                     "Mostly cold drinks with some room temperature",
#                     "Room temperature - neither hot nor cold",
#                     "Warm drinks - tea, coffee, hot chocolate",
#                     "I love hot beverages"
#                 ]
#             },
#             {
#                 "question_text": "How complex should drink flavors be?",
#                 "options": [
#                     "Simple and straightforward flavors",
#                     "Slightly complex with 2-3 flavor notes",
#                     "Moderately complex with multiple layers",
#                     "Quite complex with many flavor components",
#                     "Very complex with intricate flavor profiles"
#                 ]
#             },
#             {
#                 "question_text": "What's your preference for alcohol content?",
#                 "options": [
#                     "Non-alcoholic drinks only",
#                     "Light alcoholic drinks (beer, wine coolers)",
#                     "Moderate alcohol content (wine, light spirits)",
#                     "Strong alcoholic drinks (cocktails, liquors)",
#                     "I enjoy high-proof alcoholic beverages"
#                 ]
#             },
#             {
#                 "question_text": "How important is nutritional content to you?",
#                 "options": [
#                     "Very important - I count calories and nutrients",
#                     "Somewhat important - I check basic nutrition facts",
#                     "Neutral - I don't pay much attention to nutrition",
#                     "Not very important - taste matters more than nutrition",
#                     "Not important at all - I focus purely on taste"
#                 ]
#             },
#             {
#                 "question_text": "What type of flavors do you enjoy most?",
#                 "options": [
#                     "Fruity flavors - berries, citrus, tropical fruits",
#                     "Floral flavors - jasmine, rose, lavender",
#                     "Spicy flavors - ginger, cinnamon, chili",
#                     "Herbal flavors - mint, basil, sage",
#                     "Rich flavors - chocolate, vanilla, caramel"
#                 ]
#             },
#             {
#                 "question_text": "How do you feel about carbonation?",
#                 "options": [
#                     "I prefer still (non-carbonated) drinks",
#                     "Slightly carbonated is okay",
#                     "I enjoy moderately carbonated drinks",
#                     "I like quite a bit of fizz",
#                     "I love highly carbonated, fizzy drinks"
#                 ]
#             }
#         ]
    
#     async def get_quiz_questions(self, count: Optional[int] = None) -> QuizQuestionsResponse:
#         """
#         Get taste quiz questions.
        
#         Args:
#             count: Number of questions to return (optional)
            
#         Returns:
#             Quiz questions response with options
#         """
#         try:
#             query = select(TasteQuizQuestion).where(
#                 TasteQuizQuestion.is_active == True
#             ).order_by(TasteQuizQuestion.question_id)
            
#             if count:
#                 query = query.limit(count)
            
#             result = await self.db.execute(query)
#             questions = result.scalars().all()
            
#             if not questions and count is None:
#                 # Initialize default questions if none exist
#                 await self._initialize_default_questions()
#                 return await self.get_quiz_questions(count)
            
#             quiz_questions = []
            
#             for question in questions:
#                 # Get options for this question
#                 options_result = await self.db.execute(
#                     select(TasteQuizOption).where(
#                         TasteQuizOption.question_id == question.question_id
#                     ).order_by(TasteQuizOption.option_id)
#                 )
#                 options = options_result.scalars().all()
                
#                 quiz_question = QuizQuestion(
#                     question_id=question.question_id,
#                     question_text=question.question_text,
#                     is_active=question.is_active,
#                     created_at=question.created_at,
#                     options=[
#                         QuizOption(
#                             option_id=option.option_id,
#                             option_text=option.option_text
#                         ) for option in options
#                     ]
#                 )
                
#                 quiz_questions.append(quiz_question)
            
#             return QuizQuestionsResponse(
#                 questions=quiz_questions,
#                 total_questions=len(quiz_questions)
#             )
            
#         except Exception as e:
#             self.log_error("get_quiz_questions", e)
#             return QuizQuestionsResponse(questions=[], total_questions=0)
    
#     async def submit_quiz_answers(self, user_id: int, submission: QuizSubmission) -> QuizSubmissionResponse:
#         """
#         Submit quiz answers for a user.
        
#         Args:
#             user_id: ID of user
#             submission: Quiz submission with answers
            
#         Returns:
#             Quiz submission response
#         """
#         try:
#             # Validate that all question-option pairs exist
#             valid_answers = []
#             for answer in submission.answers:
#                 # Check if question exists
#                 question_result = await self.db.execute(
#                     select(TasteQuizQuestion).where(
#                         TasteQuizQuestion.question_id == answer.question_id,
#                         TasteQuizQuestion.is_active == True
#                     )
#                 )
#                 question = question_result.scalar_one_or_none()
                
#                 if not question:
#                     continue  # Skip invalid questions
                
#                 # Check if option exists for this question
#                 option_result = await self.db.execute(
#                     select(TasteQuizOption).where(
#                         TasteQuizOption.option_id == answer.option_id,
#                         TasteQuizOption.question_id == answer.question_id
#                     )
#                 )
#                 option = option_result.scalar_one_or_none()
                
#                 if not option:
#                     continue  # Skip invalid options
                
#                 valid_answers.append(answer)
            
#             if not valid_answers:
#                 raise ValueError("No valid answers provided")
            
#             # Delete existing answers for these questions to avoid duplicates
#             question_ids = [answer.question_id for answer in valid_answers]
#             await self.db.execute(
#                 delete(TasteQuizResult).where(
#                     TasteQuizResult.user_id == user_id,
#                     TasteQuizResult.question_id.in_(question_ids)
#                 )
#             )
            
#             # Insert new answers
#             quiz_results = []
#             for answer in valid_answers:
#                 quiz_result = TasteQuizResult(
#                     user_id=user_id,
#                     question_id=answer.question_id,
#                     option_id=answer.option_id
#                 )
#                 quiz_results.append(quiz_result)
#                 self.db.add(quiz_result)
            
#             await self.db.commit()
            
#             # Update user's questionnaire_finished status
#             await self.db.execute(
#                 update(Users).where(Users.user_id == user_id).values(
#                     questionnaire_finished=True
#                 )
#             )
#             await self.db.commit()
            
#             self.log_operation("submit_quiz_answers", {
#                 "user_id": user_id,
#                 "answers_submitted": len(valid_answers)
#             })
            
#             return QuizSubmissionResponse(
#                 message="Quiz answers submitted successfully",
#                 answers_submitted=len(valid_answers),
#                 quiz_completed=True
#             )
            
#         except Exception as e:
#             await self.db.rollback()
#             self.log_error("submit_quiz_answers", e, {"user_id": user_id})
#             return QuizSubmissionResponse(
#                 message="Failed to submit quiz answers",
#                 answers_submitted=0,
#                 quiz_completed=False
#             )
    
#     async def get_user_quiz_answers(self, user_id: int) -> Optional[List[Dict[str, Any]]]:
#         """
#         Get user's quiz answers.
        
#         Args:
#             user_id: ID of user
            
#         Returns:
#             List of user's quiz answers with question and option details
#         """
#         try:
#             result = await self.db.execute(
#                 select(TasteQuizResult)
#                 .options(
#                     selectinload(TasteQuizResult.question),
#                     selectinload(TasteQuizResult.option)
#                 )
#                 .where(TasteQuizResult.user_id == user_id)
#                 .order_by(TasteQuizResult.question_id)
#             )
            
#             quiz_results = result.scalars().all()
            
#             if not quiz_results:
#                 return None
            
#             user_answers = []
#             for result in quiz_results:
#                 user_answers.append({
#                     "question_id": result.question_id,
#                     "question_text": result.question.question_text,
#                     "option_id": result.option_id,
#                     "option_text": result.option.option_text,
#                     "answered_at": result.answered_at
#                 })
            
#             return user_answers
            
#         except Exception as e:
#             self.log_error("get_user_quiz_answers", e, {"user_id": user_id})
#             return None
    
#     async def get_quiz_statistics(self) -> Dict[str, Any]:
#         """
#         Get overall quiz statistics.
        
#         Returns:
#             Dictionary with quiz statistics
#         """
#         try:
#             # Count total questions
#             total_questions_result = await self.db.execute(
#                 select(func.count(TasteQuizQuestion.question_id)).where(
#                     TasteQuizQuestion.is_active == True
#                 )
#             )
#             total_questions = total_questions_result.scalar()
            
#             # Count total options
#             total_options_result = await self.db.execute(
#                 select(func.count(TasteQuizOption.option_id))
#             )
#             total_options = total_options_result.scalar()
            
#             # Count users who completed quiz
#             completed_quiz_result = await self.db.execute(
#                 select(func.count(Users.user_id)).where(
#                     Users.questionnaire_finished == True
#                 )
#             )
#             completed_quiz = completed_quiz_result.scalar()
            
#             # Count total users
#             total_users_result = await self.db.execute(
#                 select(func.count(Users.user_id))
#             )
#             total_users = total_users_result.scalar()
            
#             # Calculate completion rate
#             completion_rate = (completed_quiz / total_users * 100) if total_users > 0 else 0
            
#             return {
#                 "total_questions": total_questions,
#                 "total_options": total_options,
#                 "total_users": total_users,
#                 "completed_quiz": completed_quiz,
#                 "completion_rate": round(completion_rate, 2),
#                 "quiz_available": total_questions > 0
#             }
            
#         except Exception as e:
#             self.log_error("get_quiz_statistics", e)
#             return {"error": "Failed to get quiz statistics"}
    
#     async def get_quiz_progress(self, user_id: int) -> Dict[str, Any]:
#         """
#         Get user's quiz progress.
        
#         Args:
#             user_id: ID of user
            
#         Returns:
#             Dictionary with user's quiz progress
#         """
#         try:
#             # Get total active questions
#             total_questions_result = await self.db.execute(
#                 select(func.count(TasteQuizQuestion.question_id)).where(
#                     TasteQuizQuestion.is_active == True
#                 )
#             )
#             total_questions = total_questions_result.scalar()
            
#             # Get user's answered questions
#             user_answers_result = await self.db.execute(
#                 select(func.count(TasteQuizResult.question_id)).where(
#                     TasteQuizResult.user_id == user_id
#                 )
#             )
#             answered_questions = user_answers_result.scalar()
            
#             # Check if user completed questionnaire
#             user_result = await self.db.execute(
#                 select(Users.questionnaire_finished).where(Users.user_id == user_id)
#             )
#             questionnaire_finished = user_result.scalar() or False
            
#             # Calculate progress percentage
#             progress_percentage = (answered_questions / total_questions * 100) if total_questions > 0 else 0
            
#             return {
#                 "user_id": user_id,
#                 "total_questions": total_questions,
#                 "answered_questions": answered_questions,
#                 "remaining_questions": max(0, total_questions - answered_questions),
#                 "progress_percentage": round(progress_percentage, 2),
#                 "questionnaire_finished": questionnaire_finished,
#                 "can_submit": answered_questions == total_questions and total_questions > 0
#             }
            
#         except Exception as e:
#             self.log_error("get_quiz_progress", e, {"user_id": user_id})
#             return {"error": "Failed to get quiz progress"}
    
#     async def create_quiz_question(self, question_text: str, options: List[str]) -> Optional[int]:
#         """
#         Create a new quiz question.
        
#         Args:
#             question_text: Text of the question
#             options: List of option texts
            
#         Returns:
#             Question ID if successful, None otherwise
#         """
#         try:
#             if len(options) < 2:
#                 raise ValueError("Question must have at least 2 options")
            
#             # Create question
#             question = TasteQuizQuestion(
#                 question_text=question_text,
#                 is_active=True
#             )
            
#             self.db.add(question)
#             await self.db.flush()  # Get question_id without committing
            
#             # Create options
#             for option_text in options:
#                 option = TasteQuizOption(
#                     question_id=question.question_id,
#                     option_text=option_text
#                 )
#                 self.db.add(option)
            
#             await self.db.commit()
#             await self.db.refresh(question)
            
#             self.log_operation("create_quiz_question", {
#                 "question_id": question.question_id,
#                 "options_count": len(options)
#             })
            
#             return question.question_id
            
#         except Exception as e:
#             await self.db.rollback()
#             self.log_error("create_quiz_question", e)
#             return None
    
#     async def update_quiz_question(self, question_id: int, question_text: str, options: List[str]) -> bool:
#         """
#         Update an existing quiz question.
        
#         Args:
#             question_id: ID of question to update
#             question_text: New question text
#             options: New list of option texts
            
#         Returns:
#             True if successful, False otherwise
#         """
#         try:
#             # Check if question exists
#             question_result = await self.db.execute(
#                 select(TasteQuizQuestion).where(TasteQuizQuestion.question_id == question_id)
#             )
#             question = question_result.scalar_one_or_none()
            
#             if not question:
#                 return False
            
#             # Update question text
#             question.question_text = question_text
            
#             # Delete existing options
#             await self.db.execute(
#                 delete(TasteQuizOption).where(TasteQuizOption.question_id == question_id)
#             )
            
#             # Create new options
#             for option_text in options:
#                 option = TasteQuizOption(
#                     question_id=question_id,
#                     option_text=option_text
#                 )
#                 self.db.add(option)
            
#             await self.db.commit()
            
#             self.log_operation("update_quiz_question", {"question_id": question_id})
#             return True
            
#         except Exception as e:
#             await self.db.rollback()
#             self.log_error("update_quiz_question", e, {"question_id": question_id})
#             return False
    
#     async def delete_quiz_question(self, question_id: int) -> bool:
#         """
#         Delete a quiz question (soft delete by setting is_active to False).
        
#         Args:
#             question_id: ID of question to delete
            
#         Returns:
#             True if successful, False otherwise
#         """
#         try:
#             result = await self.db.execute(
#                 update(TasteQuizQuestion)
#                 .where(TasteQuizQuestion.question_id == question_id)
#                 .values(is_active=False)
#             )
            
#             await self.db.commit()
            
#             success = result.rowcount > 0
            
#             if success:
#                 self.log_operation("delete_quiz_question", {"question_id": question_id})
            
#             return success
            
#         except Exception as e:
#             await self.db.rollback()
#             self.log_error("delete_quiz_question", e, {"question_id": question_id})
#             return False
    
#     async def reset_user_quiz_progress(self, user_id: int) -> bool:
#         """
#         Reset user's quiz progress (for testing or user request).
        
#         Args:
#             user_id: ID of user
            
#         Returns:
#             True if successful, False otherwise
#         """
#         try:
#             # Delete user's quiz answers
#             await self.db.execute(
#                 delete(TasteQuizResult).where(TasteQuizResult.user_id == user_id)
#             )
            
#             # Update user's questionnaire_finished status
#             await self.db.execute(
#                 update(Users).where(Users.user_id == user_id).values(
#                     questionnaire_finished=False
#                 )
#             )
            
#             await self.db.commit()
            
#             self.log_operation("reset_user_quiz_progress", {"user_id": user_id})
#             return True
            
#         except Exception as e:
#             await self.db.rollback()
#             self.log_error("reset_user_quiz_progress", e, {"user_id": user_id})
#             return False
    
#     async def _initialize_default_questions(self):
#         """Initialize default quiz questions if none exist."""
#         try:
#             # Check if any questions already exist
#             existing_questions = await self.db.execute(
#                 select(func.count(TasteQuizQuestion.question_id))
#             )
            
#             if existing_questions.scalar() > 0:
#                 return  # Questions already exist
            
#             # Create default questions
#             for question_data in self.DEFAULT_QUESTIONS:
#                 await self.create_quiz_question(
#                     question_data["question_text"],
#                     question_data["options"]
#                 )
            
#             logger.info("Initialized default quiz questions")
            
#         except Exception as e:
#             logger.error(f"Failed to initialize default questions: {str(e)}")
    
#     async def analyze_user_taste_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
#         """
#         Analyze user's taste profile based on quiz answers.
        
#         Args:
#             user_id: ID of user
            
#         Returns:
#             Dictionary with taste profile analysis
#         """
#         try:
#             user_answers = await self.get_user_quiz_answers(user_id)
#             if not user_answers:
#                 return None
            
#             # Analyze answers to create taste profile
#             profile = {
#                 "user_id": user_id,
#                 "sweetness_preference": None,
#                 "caffeine_preference": None,
#                 "temperature_preference": None,
#                 "complexity_preference": None,
#                 "alcohol_preference": None,
#                 "nutrition_importance": None,
#                 "flavor_profile": None,
#                 "carbonation_preference": None,
#                 "analyzed_at": datetime.now()
#             }
            
#             # Map answer patterns to preferences
#             for answer in user_answers:
#                 question_text = answer["question_text"].lower()
#                 option_text = answer["option_text"].lower()
#                 option_id = answer["option_id"]
                
#                 if "sweet" in question_text:
#                     # Map sweetness preference (1-5 scale)
#                     if "not sweet" in option_text or "bitter" in option_text:
#                         profile["sweetness_preference"] = 2
#                     elif "slightly sweet" in option_text or "hint" in option_text:
#                         profile["sweetness_preference"] = 3
#                     elif "moderately sweet" in option_text or "balanced" in option_text:
#                         profile["sweetness_preference"] = 5
#                     elif "quite sweet" in option_text or "enjoy sweet" in option_text:
#                         profile["sweetness_preference"] = 7
#                     elif "very sweet" in option_text or "intensely" in option_text:
#                         profile["sweetness_preference"] = 9
                
#                 elif "caffeine" in question_text:
#                     # Map caffeine preference (1-5 scale, inverse of avoidance)
#                     if "avoid" in option_text or "completely" in option_text:
#                         profile["caffeine_preference"] = 1
#                     elif "very little" in option_text or "occasional" in option_text:
#                         profile["caffeine_preference"] = 2
#                     elif "moderate" in option_text or "1-2 cups" in option_text:
#                         profile["caffeine_preference"] = 3
#                     elif "quite a bit" in option_text or "several" in option_text:
#                         profile["caffeine_preference"] = 4
#                     elif "love" in option_text or "high caffeine" in option_text:
#                         profile["caffeine_preference"] = 5
                
#                 elif "temperature" in question_text:
#                     # Map temperature preference
#                     if "iced" in option_text or "cold" in option_text:
#                         profile["temperature_preference"] = "cold"
#                     elif "mostly cold" in option_text:
#                         profile["temperature_preference"] = "mostly_cold"
#                     elif "room temperature" in option_text:
#                         profile["temperature_preference"] = "room_temp"
#                     elif "warm" in option_text:
#                         profile["temperature_preference"] = "warm"
#                     elif "hot" in option_text:
#                         profile["temperature_preference"] = "hot"
                
#                 elif "complex" in question_text:
#                     # Map complexity preference (1-5 scale)
#                     if "simple" in option_text or "straightforward" in option_text:
#                         profile["complexity_preference"] = 1
#                     elif "slightly complex" in option_text or "2-3 flavor" in option_text:
#                         profile["complexity_preference"] = 2
#                     elif "moderately complex" in option_text or "multiple layers" in option_text:
#                         profile["complexity_preference"] = 3
#                     elif "quite complex" in option_text or "many components" in option_text:
#                         profile["complexity_preference"] = 4
#                     elif "very complex" in option_text or "intricate" in option_text:
#                         profile["complexity_preference"] = 5
            
#             return profile
            
#         except Exception as e:
#             self.log_error("analyze_user_taste_profile", e, {"user_id": user_id})
#             return None