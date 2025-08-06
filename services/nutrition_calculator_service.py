from db.schemas.workout_schema import WorkoutDataSchema
from utils.enums import ActivityLevel


class NutritionCalculatorService:

    @staticmethod
    def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
        if gender.lower() == "male":
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
        else:
            bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161
        return bmr

    @staticmethod
    def classify_activity_level(workout_data: WorkoutDataSchema) -> ActivityLevel:
        steps = workout_data.steps or 0
        active_minutes = workout_data.active_minutes or 0

        if steps > 10000 or active_minutes > 60:
            return ActivityLevel.EXTREMELY_ACTIVE
        elif steps > 5000 or active_minutes > 30:
            return ActivityLevel.MODERATELY_ACTIVE
        else:
            return ActivityLevel.LIGHTLY_ACTIVE

    @staticmethod
    def calculate_activity_multiplier(activity_level: ActivityLevel) -> float:
        """Get activity multiplier for TDEE calculation"""
        multipliers = {
            ActivityLevel.LIGHTLY_ACTIVE: 1.2,
            ActivityLevel.MODERATELY_ACTIVE: 1.375,
            ActivityLevel.EXTREMELY_ACTIVE: 1.55
        }
        return multipliers[activity_level]
