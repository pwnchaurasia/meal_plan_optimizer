from db.models.user import UserProfile


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


