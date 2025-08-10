import json
from datetime import date
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from db.models.meal_plan import MealPlan, Meal
from db.models.user import User, UserProfile, FitnessGoal
from db.models.tracker import DailyActivityTracker
from services.llm_service import LLMService
from services.tracker_service import TrackerService
from utils import app_logger


class MealPlanningService:
    """Service for generating and managing meal plans using LLM"""
    
    def __init__(self):
        self.llm_service = LLMService()
    
    async def generate_meal_plan(self, user_id: int, target_date: date, 
                               custom_config: Optional[Dict[str, Any]] = None,
                               regenerate_if_exists: bool = False,
                               db: Session = None) -> Dict[str, Any]:
        """Generate a complete meal plan for a user on a specific date"""
        try:
            # Check if meal plan already exists
            existing_plan = db.query(MealPlan).filter(
                MealPlan.user_id == user_id,
                MealPlan.date == target_date
            ).first()
            
            if existing_plan and not regenerate_if_exists:
                return {
                    "status": "info",
                    "message": f"Meal plan already exists for {target_date}",
                    "meal_plan_id": existing_plan.id,
                    "existing_plan": True
                }
            
            # Gather user data
            user_data = await self._gather_user_data(user_id, db)
            if not user_data["success"]:
                return user_data
            
            # Calculate nutrition targets
            nutrition_targets = await self._calculate_nutrition_targets(user_id, target_date, custom_config, db)
            if not nutrition_targets["success"]:
                return nutrition_targets
            
            # Get activity data for the day
            activity_data = await self._get_activity_data(user_id, target_date, db)
            
            # Create LLM prompt
            prompt = self.llm_service.create_meal_plan_prompt(
                user_data["data"],
                nutrition_targets["data"],
                activity_data
            )
            
            # Configure LLM
            llm_config = self._get_llm_config(custom_config)
            
            # Generate meal plan using LLM
            llm_result = await self.llm_service.generate_meal_plan(prompt, llm_config)
            
            if not llm_result["success"]:
                return {
                    "status": "error",
                    "message": f"Failed to generate meal plan: {llm_result['error']}",
                    "provider": llm_result["provider"]
                }
            
            # Save meal plan to database
            meal_plan_result = await self._save_meal_plan_to_db(
                user_id, target_date, llm_result, nutrition_targets["data"], 
                prompt, existing_plan, db
            )
            
            return meal_plan_result
            
        except Exception as e:
            app_logger.exceptionlogs(f"Error in generate_meal_plan: {e}")
            return {
                "status": "error",
                "message": "Failed to generate meal plan",
                "error": str(e)
            }
    
    async def _gather_user_data(self, user_id: int, db: Session) -> Dict[str, Any]:
        """Gather all relevant user data for meal planning"""
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "message": "User not found"}
            
            user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            
            user_data = {
                "user_id": user_id,
                "name": user.name,
                "gender": user_profile.gender.value if user_profile and user_profile.gender else "not_specified",
                "food_preference_type": user_profile.food_preference_type.value if user_profile and user_profile.food_preference_type else "omnivore",
                "cooking_skill_level": user_profile.cooking_skill_level if user_profile else 3,
                "max_prep_time_minutes": user_profile.max_prep_time_minutes if user_profile else 45,
                "preferred_meal_frequency": user_profile.preferred_meal_frequency if user_profile else 3,
                "snack_preference": user_profile.snack_preference if user_profile else True,
                "allergies": json.loads(user_profile.allergies) if user_profile and user_profile.allergies else [],
                "dietary_restrictions": json.loads(user_profile.dietary_restrictions) if user_profile and user_profile.dietary_restrictions else [],
                "disliked_foods": json.loads(user_profile.disliked_foods) if user_profile and user_profile.disliked_foods else [],
                "preferred_cuisines": json.loads(user_profile.preferred_cuisines) if user_profile and user_profile.preferred_cuisines else []
            }
            
            return {"success": True, "data": user_data}
            
        except Exception as e:
            app_logger.exceptionlogs(f"Error gathering user data: {e}")
            return {"success": False, "message": "Failed to gather user data"}
    
    async def _calculate_nutrition_targets(self, user_id: int, target_date: date, 
                                         custom_config: Optional[Dict[str, Any]], 
                                         db: Session) -> Dict[str, Any]:
        """Calculate nutrition targets based on user's fitness goals and activity"""
        try:
            # Get user's active fitness goal
            fitness_goal = db.query(FitnessGoal).filter(
                FitnessGoal.user_id == user_id,
                FitnessGoal.is_active == True
            ).first()
            
            # Default calorie target
            base_calories = 2000
            
            if fitness_goal and fitness_goal.calculated_daily_calories:
                base_calories = fitness_goal.calculated_daily_calories
            elif custom_config and custom_config.get("custom_calorie_target"):
                base_calories = custom_config["custom_calorie_target"]
            
            # Get activity data to adjust calories
            activity_tracker = db.query(DailyActivityTracker).filter(
                DailyActivityTracker.user_id == user_id,
                DailyActivityTracker.date == target_date
            ).first()
            
            # Adjust calories based on activity
            if activity_tracker and activity_tracker.calories_burned_from_activity:
                # Add back some of the burned calories (typically 50-70%)
                additional_calories = activity_tracker.calories_burned_from_activity * 0.6
                base_calories += additional_calories
            
            # Calculate macronutrient targets (standard ratios)
            protein_percentage = 25  # 25% protein
            carbs_percentage = 45   # 45% carbs
            fat_percentage = 30     # 30% fat
            
            protein_calories = base_calories * (protein_percentage / 100)
            carbs_calories = base_calories * (carbs_percentage / 100)
            fat_calories = base_calories * (fat_percentage / 100)
            
            # Convert to grams (protein: 4 cal/g, carbs: 4 cal/g, fat: 9 cal/g)
            protein_g = protein_calories / 4
            carbs_g = carbs_calories / 4
            fat_g = fat_calories / 9
            
            # Fiber target (14g per 1000 calories)
            fiber_g = (base_calories / 1000) * 14
            
            nutrition_targets = {
                "calories": round(base_calories),
                "protein_g": round(protein_g, 1),
                "carbs_g": round(carbs_g, 1),
                "fat_g": round(fat_g, 1),
                "fiber_g": round(fiber_g, 1),
                "protein_percentage": protein_percentage,
                "carbs_percentage": carbs_percentage,
                "fat_percentage": fat_percentage
            }
            
            return {"success": True, "data": nutrition_targets}
            
        except Exception as e:
            app_logger.exceptionlogs(f"Error calculating nutrition targets: {e}")
            return {"success": False, "message": "Failed to calculate nutrition targets"}
    
    async def _get_activity_data(self, user_id: int, target_date: date, db: Session) -> Optional[Dict[str, Any]]:
        """Get activity data for the target date"""
        try:
            activity_tracker = db.query(DailyActivityTracker).filter(
                DailyActivityTracker.user_id == user_id,
                DailyActivityTracker.date == target_date
            ).first()
            
            if not activity_tracker:
                return None
            
            # Parse workout types
            workout_types = []
            if activity_tracker.workout_types_done:
                try:
                    workout_types = json.loads(activity_tracker.workout_types_done)
                except:
                    workout_types = []
            
            return {
                "calories_burned": activity_tracker.calories_burned_from_activity,
                "total_exercises": activity_tracker.total_exercises_done,
                "total_sets": activity_tracker.total_sets_completed,
                "workout_time": activity_tracker.total_workout_time,
                "workout_types": workout_types,
                "activity_summary": f"Completed {activity_tracker.total_exercises_done} exercises, {activity_tracker.total_sets_completed} sets"
            }
            
        except Exception as e:
            app_logger.exceptionlogs(f"Error getting activity data: {e}")
            return None
    
    def _get_llm_config(self, custom_config: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Get LLM configuration with defaults"""
        default_config = {
            "llm_provider": "openai",
            "model_name": "gpt-4",
            "temperature": 0.7,
            "max_tokens": 4000
        }
        
        if custom_config:
            default_config.update(custom_config)
        
        return default_config
    
    async def _save_meal_plan_to_db(self, user_id: int, target_date: date, 
                                  llm_result: Dict[str, Any], nutrition_targets: Dict[str, Any],
                                  prompt: str, existing_plan: Optional[MealPlan],
                                  db: Session) -> Dict[str, Any]:
        """Save the generated meal plan to database"""
        try:
            meal_data = llm_result["data"]
            daily_summary = meal_data.get("daily_summary", {})
            
            # Create or update meal plan
            if existing_plan:
                meal_plan = existing_plan
                # Delete existing meals
                db.query(Meal).filter(Meal.meal_plan_id == meal_plan.id).delete()
            else:
                meal_plan = MealPlan(
                    user_id=user_id,
                    date=target_date
                )
                db.add(meal_plan)
            
            # Update meal plan data
            meal_plan.target_calories = nutrition_targets["calories"]
            meal_plan.target_protein_g = nutrition_targets["protein_g"]
            meal_plan.target_carbs_g = nutrition_targets["carbs_g"]
            meal_plan.target_fat_g = nutrition_targets["fat_g"]
            meal_plan.target_fiber_g = nutrition_targets["fiber_g"]
            meal_plan.total_calories = daily_summary.get("total_calories", 0)
            meal_plan.total_protein_g = daily_summary.get("total_protein_g", 0)
            meal_plan.total_carbs_g = daily_summary.get("total_carbs_g", 0)
            meal_plan.total_fat_g = daily_summary.get("total_fat_g", 0)
            meal_plan.total_fiber_g = daily_summary.get("total_fiber_g", 0)
            meal_plan.generation_prompt = prompt
            meal_plan.llm_model_used = f"{llm_result['provider']}-{llm_result['model']}"
            meal_plan.generation_time_seconds = llm_result["generation_time"]
            
            db.flush()  # Get the meal plan ID
            
            # Create meals
            meal_types = ["breakfast", "lunch", "dinner", "snack_1", "snack_2"]
            created_meals = []
            
            for meal_type in meal_types:
                if meal_type in meal_data:
                    meal_info = meal_data[meal_type]
                    
                    meal = Meal(
                        meal_plan_id=meal_plan.id,
                        meal_type=meal_type,
                        meal_name=meal_info.get("meal_name", ""),
                        description=meal_info.get("description", ""),
                        calories=meal_info.get("calories", 0),
                        protein_g=meal_info.get("protein_g", 0),
                        carbs_g=meal_info.get("carbs_g", 0),
                        fat_g=meal_info.get("fat_g", 0),
                        fiber_g=meal_info.get("fiber_g", 0),
                        sodium_mg=meal_info.get("sodium_mg", 0),
                        sugar_g=meal_info.get("sugar_g", 0),
                        prep_time_minutes=meal_info.get("prep_time_minutes", 0),
                        cooking_time_minutes=meal_info.get("cooking_time_minutes", 0),
                        difficulty_level=meal_info.get("difficulty_level", 1),
                        cuisine_type=meal_info.get("cuisine_type", ""),
                        ingredients=json.dumps(meal_info.get("ingredients", [])),
                        instructions=json.dumps(meal_info.get("instructions", [])),
                        is_vegetarian=meal_info.get("is_vegetarian", False),
                        is_vegan=meal_info.get("is_vegan", False),
                        is_gluten_free=meal_info.get("is_gluten_free", False),
                        is_dairy_free=meal_info.get("is_dairy_free", False)
                    )
                    
                    db.add(meal)
                    created_meals.append(meal_type)
            
            db.commit()
            
            return {
                "status": "success",
                "message": "Meal plan generated successfully",
                "meal_plan_id": meal_plan.id,
                "date": target_date.isoformat(),
                "target_calories": meal_plan.target_calories,
                "total_calories": meal_plan.total_calories,
                "meals_created": len(created_meals),
                "generation_time": llm_result["generation_time"],
                "llm_provider": llm_result["provider"],
                "llm_model": llm_result["model"]
            }
            
        except Exception as e:
            app_logger.exceptionlogs(f"Error saving meal plan to database: {e}")
            db.rollback()
            return {
                "status": "error",
                "message": "Failed to save meal plan to database",
                "error": str(e)
            }
    
    async def get_meal_plan(self, user_id: int, target_date: date, db: Session) -> Optional[MealPlan]:
        """Get meal plan for a specific date"""
        try:
            meal_plan = db.query(MealPlan).filter(
                MealPlan.user_id == user_id,
                MealPlan.date == target_date
            ).first()
            
            return meal_plan
            
        except Exception as e:
            app_logger.exceptionlogs(f"Error getting meal plan: {e}")
            return None
    
    async def get_meal_plan_summary(self, user_id: int, target_date: date, db: Session) -> Dict[str, Any]:
        """Get a summary of the meal plan"""
        try:
            meal_plan = await self.get_meal_plan(user_id, target_date, db)
            
            if not meal_plan:
                return {
                    "status": "not_found",
                    "message": "No meal plan found for this date"
                }
            
            calorie_difference = meal_plan.total_calories - meal_plan.target_calories
            
            # Calculate macronutrient percentages
            total_calories = meal_plan.total_calories or 1  # Avoid division by zero
            protein_percentage = (meal_plan.total_protein_g * 4 / total_calories) * 100
            carbs_percentage = (meal_plan.total_carbs_g * 4 / total_calories) * 100
            fat_percentage = (meal_plan.total_fat_g * 9 / total_calories) * 100
            
            return {
                "status": "success",
                "meal_plan_id": meal_plan.id,
                "date": meal_plan.date.isoformat(),
                "target_calories": meal_plan.target_calories,
                "total_calories": meal_plan.total_calories,
                "calorie_difference": round(calorie_difference, 1),
                "protein_percentage": round(protein_percentage, 1),
                "carbs_percentage": round(carbs_percentage, 1),
                "fat_percentage": round(fat_percentage, 1),
                "meals_count": len(meal_plan.meals),
                "generation_time": meal_plan.generation_time_seconds,
                "llm_model": meal_plan.llm_model_used
            }
            
        except Exception as e:
            app_logger.exceptionlogs(f"Error getting meal plan summary: {e}")
            return {
                "status": "error",
                "message": "Failed to get meal plan summary"
            }
