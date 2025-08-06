from datetime import date

from db.schemas.recipe_schema import NutritionTargets, MealPlan
from db.schemas.user_schema import UserProfile
from db.schemas.workout_schema import WorkoutDataSchema
from services.nutrition_calculator_service import NutritionCalculatorService
from utils.enums import ActivityLevel, WeightGoal
from typing import List, Dict, Any


class MealPlanningRuleEngine:
    """Simple rule-based meal planning engine"""

    def __init__(self):
        self.meals_db = {
            "high_protein_breakfast": {
                "name": "Greek Yogurt with Berries",
                "calories": 250,
                "protein_g": 20,
                "carbs_g": 25,
                "fat_g": 8,
                "meal_type": "breakfast"
            },
            "moderate_breakfast": {
                "name": "Oatmeal with Banana",
                "calories": 300,
                "protein_g": 10,
                "carbs_g": 55,
                "fat_g": 6,
                "meal_type": "breakfast"
            },
            "light_breakfast": {
                "name": "Toast with Avocado",
                "calories": 200,
                "protein_g": 6,
                "carbs_g": 20,
                "fat_g": 12,
                "meal_type": "breakfast"
            },

            "high_protein_lunch": {
                "name": "Grilled Chicken Salad",
                "calories": 400,
                "protein_g": 35,
                "carbs_g": 15,
                "fat_g": 22,
                "meal_type": "lunch"
            },
            "moderate_lunch": {
                "name": "Quinoa Bowl with Vegetables",
                "calories": 450,
                "protein_g": 15,
                "carbs_g": 60,
                "fat_g": 18,
                "meal_type": "lunch"
            },
            "light_lunch": {
                "name": "Vegetable Soup with Bread",
                "calories": 300,
                "protein_g": 10,
                "carbs_g": 45,
                "fat_g": 8,
                "meal_type": "lunch"
            },

            "high_protein_dinner": {
                "name": "Salmon with Sweet Potato",
                "calories": 500,
                "protein_g": 40,
                "carbs_g": 35,
                "fat_g": 25,
                "meal_type": "dinner"
            },
            "moderate_dinner": {
                "name": "Pasta with Marinara",
                "calories": 450,
                "protein_g": 18,
                "carbs_g": 70,
                "fat_g": 12,
                "meal_type": "dinner"
            },
            "light_dinner": {
                "name": "Vegetable Stir Fry",
                "calories": 350,
                "protein_g": 12,
                "carbs_g": 50,
                "fat_g": 15,
                "meal_type": "dinner"
            },

            "protein_snack": {
                "name": "Protein Smoothie",
                "calories": 200,
                "protein_g": 25,
                "carbs_g": 15,
                "fat_g": 5,
                "meal_type": "snack"
            },
            "healthy_snack": {
                "name": "Apple with Almond Butter",
                "calories": 180,
                "protein_g": 6,
                "carbs_g": 20,
                "fat_g": 10,
                "meal_type": "snack"
            }
        }

    def calculate_nutrition_targets(self, user_profile: UserProfile, workout_data: WorkoutDataSchema) -> NutritionTargets:
        """Calculate daily nutrition targets based on user profile and yesterday's activity"""

        # Calculate BMR
        bmr = NutritionCalculatorService.calculate_bmr(
            user_profile.current_weight_kg,
            user_profile.height_cm,
            user_profile.age,
            user_profile.gender
        )

        # Determine activity level from yesterday's data
        activity_level = NutritionCalculatorService.classify_activity_level(workout_data)
        activity_multiplier = NutritionCalculatorService.calculate_activity_multiplier(activity_level)

        # Calculate TDEE (Total Daily Energy Expenditure)
        tdee = bmr * activity_multiplier

        # Adjust calories based on weight goal
        weight_goal = self._determine_weight_goal(user_profile)
        target_calories = self._adjust_calories_for_goal(tdee, weight_goal, activity_level)

        # Calculate macro targets
        protein_g = self._calculate_protein_target(user_profile, activity_level)
        fat_g = int(target_calories * 0.25 / 9)  # 25% of calories from fat
        carbs_g = int((target_calories - (protein_g * 4) - (fat_g * 9)) / 4)  # Remaining calories from carbs

        return NutritionTargets(
            total_calories=int(target_calories),
            protein_g=protein_g,
            carbs_g=carbs_g,
            fat_g=fat_g
        )

    def generate_meal_plan(self, user_profile: UserProfile, workout_data: WorkoutDataSchema) -> MealPlan:
        """Generate a daily meal plan using simple rules"""

        # Calculate nutrition targets
        targets = self.calculate_nutrition_targets(user_profile, workout_data)

        # Determine meal intensity based on activity and goals
        activity_level = NutritionCalculatorService.classify_activity_level(workout_data)
        meal_intensity = self._determine_meal_intensity(user_profile, activity_level)

        # Select meals based on rules
        selected_meals = self._select_meals(targets, meal_intensity, workout_data)

        # Generate recommendations
        recommendations = self._generate_recommendations(user_profile, workout_data, activity_level)

        # Calculate actual nutrition from selected meals
        actual_nutrition = self._calculate_total_nutrition(selected_meals)

        return MealPlan(
            date=date.today(),
            total_calories=actual_nutrition["calories"],
            meals=selected_meals,
            nutrition_summary=actual_nutrition,
            recommendations=recommendations
        )

    def _determine_weight_goal(self, user_profile: UserProfile) -> WeightGoal:
        """Determine user's weight goal"""
        if user_profile.target_weight_kg < user_profile.current_weight_kg:
            return WeightGoal.LOSE
        elif user_profile.target_weight_kg > user_profile.current_weight_kg:
            return WeightGoal.GAIN
        else:
            return WeightGoal.MAINTAIN

    def _adjust_calories_for_goal(self, tdee: float, weight_goal: WeightGoal, activity_level: ActivityLevel) -> float:
        """Adjust calories based on weight goal and activity level"""

        # Base calorie adjustment for weight goals
        if weight_goal == WeightGoal.LOSE:
            # Create deficit (500 cal = ~1 lb per week)
            adjustment = -400 if activity_level == ActivityLevel.EXTREMELY_ACTIVE else -300
        elif weight_goal == WeightGoal.GAIN:
            # Create surplus (500 cal = ~1 lb per week)
            adjustment = +400 if activity_level == ActivityLevel.VERY_ACTIVE else +300
        else:
            adjustment = 0

        return tdee + adjustment

    def _calculate_protein_target(self, user_profile: UserProfile, activity_level: ActivityLevel) -> int:
        """Calculate protein target based on weight and activity"""

        # Protein per kg body weight based on activity
        protein_per_kg = {
            ActivityLevel.LIGHTLY_ACTIVE: 0.8,
            ActivityLevel.MODERATELY_ACTIVE: 1.2,
            ActivityLevel.EXTREMELY_ACTIVE: 1.6
        }

        return int(user_profile.current_weight_kg * protein_per_kg[activity_level])

    def _determine_meal_intensity(self, user_profile: UserProfile, activity_level: ActivityLevel) -> str:
        """Determine meal intensity (high_protein, moderate, light)"""

        weight_goal = self._determine_weight_goal(user_profile)

        # Rules for meal intensity
        if activity_level == ActivityLevel.EXTREMELY_ACTIVE:
            return "high_protein"
        elif weight_goal == WeightGoal.LOSE:
            return "light"
        else:
            return "moderate"

    def _select_meals(self, targets: NutritionTargets, intensity: str, workout_data: WorkoutDataSchema) -> List[
        Dict[str, Any]]:
        """Select meals based on targets and intensity"""

        selected_meals = []

        # Select breakfast
        breakfast_key = f"{intensity}_breakfast"
        selected_meals.append(self.meals_db.get(breakfast_key, self.meals_db["moderate_breakfast"]))

        # Select lunch
        lunch_key = f"{intensity}_lunch"
        selected_meals.append(self.meals_db.get(lunch_key, self.meals_db["moderate_lunch"]))

        # Select dinner
        dinner_key = f"{intensity}_dinner"
        selected_meals.append(self.meals_db.get(dinner_key, self.meals_db["moderate_dinner"]))

        # Add snack if high activity or high calorie target
        current_calories = sum(meal["calories"] for meal in selected_meals)
        if current_calories < targets.total_calories - 150:
            if intensity == "high_protein":
                selected_meals.append(self.meals_db["protein_snack"])
            else:
                selected_meals.append(self.meals_db["healthy_snack"])

        return selected_meals

    def _calculate_total_nutrition(self, meals: List[Dict[str, Any]]) -> Dict[str, int]:
        """Calculate total nutrition from selected meals"""

        total = {
            "calories": 0,
            "protein_g": 0,
            "carbs_g": 0,
            "fat_g": 0
        }

        for meal in meals:
            total["calories"] += meal["calories"]
            total["protein_g"] += meal["protein_g"]
            total["carbs_g"] += meal["carbs_g"]
            total["fat_g"] += meal["fat_g"]

        return total

    def _generate_recommendations(self, user_profile: UserProfile,
                                  workout_data: WorkoutDataSchema,
                                  activity_level: ActivityLevel) -> List[str]:

        recommendations = []

        # Activity-based recommendations
        if activity_level == ActivityLevel.EXTREMELY_ACTIVE:
            recommendations.append("Great workout yesterday! Added extra protein to support muscle recovery.")
            recommendations.append("Consider having a post-workout snack within 30 minutes of exercising.")
        elif activity_level == ActivityLevel.LIGHTLY_ACTIVE:
            recommendations.append("Try to increase your daily steps today. Even a 10-minute walk helps!")

        # Weight goal recommendations
        weight_goal = self._determine_weight_goal(user_profile)
        if weight_goal == WeightGoal.LOSE:
            recommendations.append("Focus on protein-rich foods to maintain muscle while losing weight.")
            recommendations.append("Drink water before meals to help with portion control.")
        elif weight_goal == WeightGoal.GAIN:
            recommendations.append("Add healthy fats like nuts, avocado, and olive oil to increase calories.")
            recommendations.append("Consider eating more frequent, smaller meals throughout the day.")

        # Workout-specific recommendations
        if workout_data.workout_type == "strength":
            recommendations.append("After strength training, prioritize protein within 2 hours for muscle building.")
        elif workout_data.workout_type == "cardio":
            recommendations.append("Replenish carbohydrates after cardio to restore energy levels.")

        return recommendations
