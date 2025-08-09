import json
from db.models.user import UserProfile, FitnessGoal
from sqlalchemy.orm import Session

from db.models import User
from utils import app_logger
from utils.enums import ActivityLevel, GoalAchievementTimeFrameType, Gender, FoodPreferenceType


class UserService:

    @staticmethod
    def get_user_profile(user_id):
        user_id = UserProfile()

    @staticmethod
    def today_meals(request):
        user_id = request.user_id
        user_profile = UserProfile()
        meal_frequency = user_profile.preferred_meal_frequency
        snacks = user_profile.snack_preference
        food_preference_type = user_profile.food_preference_type




    @staticmethod
    def calculate_nutrition_targets(fitness_goal):
        """
        # this algo is given by AI.
        # I just instructed what needs to be done,
        # I am aware of how these calculations are done
        """

        # Activity level multipliers for TDEE calculation
        activity_multipliers = {
            "sedentary": 1.2,
            "lightly_active": 1.375,
            "moderately_active": 1.55,
            "very_active": 1.725,
            "extremely_active": 1.9
        }

        # Weight change rates (kg per week)
        weekly_change_map = {
            "slow": 0.25,  # Conservative approach
            "average": 0.5,  # Moderate approach
            "fast": 1.0  # Aggressive approach (max safe rate)
        }

        current_weight = fitness_goal.current_weight
        target_weight = fitness_goal.target_weight
        speed = fitness_goal.goal_achievement_time_frame
        maintenance_calories = fitness_goal.current_daily_calories  # This should be BMR
        daily_activity_level = fitness_goal.daily_activity_level

        # Constants
        kcal_per_kg = 7700  # Calories per kg of body weight
        weekly_change = weekly_change_map.get(speed, 0.5)
        daily_kcal_change = (weekly_change * kcal_per_kg) / 7

        activity_multiplier = activity_multipliers.get(daily_activity_level, 1.55)  # Default to moderately active
        tdee_calories = maintenance_calories * activity_multiplier

        # More active people can handle larger deficits/surpluses
        activity_adjustment = {
            "sedentary": 0.8,
            "lightly_active": 0.9,
            "moderately_active": 1.0,
            "very_active": 1.1,
            "extremely_active": 1.2
        }

        adjusted_daily_change = daily_kcal_change * activity_adjustment.get(daily_activity_level, 1.0)

        if current_weight < target_weight:
            # Gaining weight - need calorie surplus
            total_kg = target_weight - current_weight
            weeks = total_kg / weekly_change
            target_calories = tdee_calories + adjusted_daily_change
            goal_type = "weight_gain"

        elif current_weight > target_weight:
            # Losing weight - need calorie deficit
            total_kg = current_weight - target_weight
            weeks = total_kg / weekly_change
            target_calories = tdee_calories - adjusted_daily_change
            goal_type = "weight_loss"

            # Safety check: Don't go below minimum safe calories
            min_safe_calories = {
                "sedentary": 1200,
                "lightly_active": 1300,
                "moderately_active": 1400,
                "very_active": 1500,
                "extremely_active": 1600
            }
            min_calories = min_safe_calories.get(daily_activity_level, 1200)
            target_calories = max(target_calories, min_calories)

        else:
            # Maintaining weight
            return {
                "weeks": 0,
                "calculated_daily_calories": round(tdee_calories),
                "goal_type": "maintenance",
                "tdee_calories": round(tdee_calories),
                "bmr_calories": round(maintenance_calories),
                "activity_level": daily_activity_level,
                "activity_multiplier": activity_multiplier
            }

        # Calculate macro adjustments based on activity level and goal
        protein_multiplier = {
            "sedentary": 0.8,
            "lightly_active": 1.0,
            "moderately_active": 1.2,
            "very_active": 1.6,
            "extremely_active": 2.0
        }

        recommended_protein_g = current_weight * protein_multiplier.get(daily_activity_level, 1.2)

        return {
            "weeks": round(weeks, 1),
            "calculated_daily_calories": round(target_calories),
            "goal_type": goal_type,
            "tdee_calories": round(tdee_calories),
            "bmr_calories": round(maintenance_calories),
            "activity_level": daily_activity_level,
            "activity_multiplier": activity_multiplier,
            "calorie_adjustment": round(adjusted_daily_change),
            "recommended_protein_g": round(recommended_protein_g),
            "weight_change_per_week_kg": weekly_change,
            "total_weight_change_kg": round(total_kg, 1) if 'total_kg' in locals() else 0
        }


    @staticmethod
    def get_user_by_id(user_id: int, db: Session):
        query = db.query(User)
        return query.filter(User.id == user_id).first()

    @staticmethod
    def get_user_by_phone_number(phone_number: str, db: Session):
        try:
            user = db.query(User).filter(User.phone_number == phone_number).first()
            return user
        except Exception as e:
            app_logger.exceptionlogs(f"Error, {e}")
            return None


    @staticmethod
    def update_user_data(db: Session, user: User, user_profile_data: UserProfile):
        try:
            update_fields = user_profile_data.model_dump(exclude_unset=True)

            # Update fields dynamically
            for key, value in update_fields.items():
                setattr(user, key, value)

            db.commit()
            db.refresh(user)  # Refresh to get updated data
            return user
        except Exception as e:
            app_logger.exceptionlogs(f"Error in update_user_data {e}")
            return None

    @staticmethod
    def create_user_by_phone_number(phone_number: str, db: Session):
        try:
            user = UserService.get_user_by_phone_number(phone_number=phone_number, db=db)
            if not user:
                user = User(phone_number=phone_number, is_phone_verified=True, is_active=True)
                db.add(user)
                db.commit()
                db.refresh(user)
            else:
                user.is_phone_verified = True
                user.is_active = True
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            app_logger.exceptionlogs(f"Error in get_or_create_user_by_phone_number, Error: {e}")
            return None

    @staticmethod
    def create_fitness_goal(user_id: int, fitness_goal_data, db: Session):
        try:
            # Check if user already has an active fitness goal
            existing_goal = db.query(FitnessGoal).filter(
                FitnessGoal.user_id == user_id,
                FitnessGoal.is_active == True
            ).first()
            
            if existing_goal:
                # Deactivate existing goal
                existing_goal.is_active = False
            
            # Create new fitness goal
            fitness_goal = FitnessGoal(
                user_id=user_id,
                daily_activity_level=ActivityLevel(fitness_goal_data.daily_activity_level),
                goal_achievement_time_frame=GoalAchievementTimeFrameType(fitness_goal_data.goal_achievement_time_frame),
                current_weight=fitness_goal_data.current_weight,
                target_weight=fitness_goal_data.target_weight,
                current_daily_calories=fitness_goal_data.current_daily_calories
            )
            
            # Calculate nutrition targets
            nutrition_data = UserService.calculate_nutrition_targets(fitness_goal_data)
            fitness_goal.calculated_daily_calories = nutrition_data.get("calculated_daily_calories")
            
            db.add(fitness_goal)
            db.commit()
            db.refresh(fitness_goal)
            
            return {
                "status": "success",
                "message": "Fitness goal created successfully",
                "fitness_goal_id": fitness_goal.id,
                "nutrition_targets": nutrition_data
            }
        except Exception as e:
            app_logger.exceptionlogs(f"Error in create_fitness_goal: {e}")
            db.rollback()
            return None

    @staticmethod
    def update_fitness_goal(user_id: int, fitness_goal_data, db: Session):
        try:
            # Get user's active fitness goal
            fitness_goal = db.query(FitnessGoal).filter(
                FitnessGoal.user_id == user_id,
                FitnessGoal.is_active == True
            ).first()
            
            if not fitness_goal:
                return None
            
            # Update fields that are provided
            update_data = fitness_goal_data.model_dump(exclude_unset=True)
            
            for field, value in update_data.items():
                if field == "daily_activity_level" and value:
                    fitness_goal.daily_activity_level = ActivityLevel(value)
                elif field == "goal_achievement_time_frame" and value:
                    fitness_goal.goal_achievement_time_frame = GoalAchievementTimeFrameType(value)
                elif hasattr(fitness_goal, field) and value is not None:
                    setattr(fitness_goal, field, value)
            
            # Recalculate nutrition targets with updated data
            class TempGoalData:
                def __init__(self, goal):
                    self.daily_activity_level = goal.daily_activity_level.value
                    self.goal_achievement_time_frame = goal.goal_achievement_time_frame.value
                    self.current_weight = goal.current_weight
                    self.target_weight = goal.target_weight
                    self.current_daily_calories = goal.current_daily_calories
            
            temp_goal = TempGoalData(fitness_goal)
            nutrition_data = UserService.calculate_nutrition_targets(temp_goal)
            fitness_goal.calculated_daily_calories = nutrition_data.get("calculated_daily_calories")
            
            db.commit()
            db.refresh(fitness_goal)
            
            return {
                "status": "success",
                "message": "Fitness goal updated successfully",
                "fitness_goal_id": fitness_goal.id,
                "nutrition_targets": nutrition_data
            }
        except Exception as e:
            app_logger.exceptionlogs(f"Error in update_fitness_goal: {e}")
            db.rollback()
            return None

    @staticmethod
    def create_or_update_user_profile(user_id: int, profile_data, db: Session):
        try:
            # Check if user profile already exists
            user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            
            if user_profile:
                # Update existing profile
                return UserService.update_user_profile(user_id, profile_data, db)
            else:
                # Create new profile
                return UserService.create_user_profile(user_id, profile_data, db)
        except Exception as e:
            app_logger.exceptionlogs(f"Error in create_or_update_user_profile: {e}")
            return None

    @staticmethod
    def create_user_profile(user_id: int, profile_data, db: Session):
        try:
            update_data = profile_data.model_dump(exclude_unset=True)
            
            # Convert list fields to JSON strings
            if "allergies" in update_data and update_data["allergies"]:
                update_data["allergies"] = json.dumps(update_data["allergies"])
            if "dietary_restrictions" in update_data and update_data["dietary_restrictions"]:
                update_data["dietary_restrictions"] = json.dumps(update_data["dietary_restrictions"])
            if "disliked_foods" in update_data and update_data["disliked_foods"]:
                update_data["disliked_foods"] = json.dumps(update_data["disliked_foods"])
            if "preferred_cuisines" in update_data and update_data["preferred_cuisines"]:
                update_data["preferred_cuisines"] = json.dumps(update_data["preferred_cuisines"])
            
            # Convert enum fields
            if "gender" in update_data and update_data["gender"]:
                update_data["gender"] = Gender(update_data["gender"])
            if "food_preference_type" in update_data and update_data["food_preference_type"]:
                update_data["food_preference_type"] = FoodPreferenceType(update_data["food_preference_type"])
            
            user_profile = UserProfile(user_id=user_id, **update_data)
            
            db.add(user_profile)
            db.commit()
            db.refresh(user_profile)
            
            return {
                "status": "success",
                "message": "User profile created successfully",
                "profile_id": user_profile.id
            }
        except Exception as e:
            app_logger.exceptionlogs(f"Error in create_user_profile: {e}")
            db.rollback()
            return None

    @staticmethod
    def update_user_profile(user_id: int, profile_data, db: Session):
        try:
            user_profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
            
            if not user_profile:
                return None
            
            update_data = profile_data.model_dump(exclude_unset=True)
            
            # Convert list fields to JSON strings
            if "allergies" in update_data and update_data["allergies"] is not None:
                update_data["allergies"] = json.dumps(update_data["allergies"])
            if "dietary_restrictions" in update_data and update_data["dietary_restrictions"] is not None:
                update_data["dietary_restrictions"] = json.dumps(update_data["dietary_restrictions"])
            if "disliked_foods" in update_data and update_data["disliked_foods"] is not None:
                update_data["disliked_foods"] = json.dumps(update_data["disliked_foods"])
            if "preferred_cuisines" in update_data and update_data["preferred_cuisines"] is not None:
                update_data["preferred_cuisines"] = json.dumps(update_data["preferred_cuisines"])
            
            # Update fields
            for field, value in update_data.items():
                if field == "gender" and value:
                    user_profile.gender = Gender(value)
                elif field == "food_preference_type" and value:
                    user_profile.food_preference_type = FoodPreferenceType(value)
                elif hasattr(user_profile, field):
                    setattr(user_profile, field, value)
            
            db.commit()
            db.refresh(user_profile)
            
            return {
                "status": "success",
                "message": "User profile updated successfully",
                "profile_id": user_profile.id
            }
        except Exception as e:
            app_logger.exceptionlogs(f"Error in update_user_profile: {e}")
            db.rollback()
            return None
