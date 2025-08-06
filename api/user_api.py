from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status
from db.schemas import user_schema, workout_schema
from db.schemas.user_schema import UserProfile
from integrations.fitness_app_conn_service_provider import FitnessAppConnectionFactory, FitnessConnectionService
from services.meal_planning_rule_engine import MealPlanningRuleEngine
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/me/update-fitness-goal",
            status_code=status.HTTP_200_OK, name="save-goal")
async def update_my_fitness_goal(fitness_goal: user_schema.FitnessGoalRequestSchema):
    return UserService.calculate_nutrition_targets(fitness_goal)


@router.put("/me/update-fitness-goal",
             status_code=status.HTTP_200_OK, name="update-goal")
async def update_my_fitness_goal(fitness_goal: user_schema.FitnessGoalRequestSchema):
    return UserService.calculate_nutrition_targets(fitness_goal)



@router.put("/me/get-daily-meals",
             status_code=status.HTTP_200_OK,
            name="get-daily-meals")
async def get_daily_meals(request):
    return UserService.today_meals(request)



@router.post("/me/connect",
             status_code=status.HTTP_200_OK,
             name="connect-fitness-app")
async def connect_fitness_app(fitness_app_conn: user_schema.FitnessAppConnectionRequestSchema,
                              auth_code: str):
    service = FitnessConnectionService()
    current_user = {"id":1}
    result = service.connect_user_to_provider(
        user_id=current_user['id'],
        provider_type=fitness_app_conn.provider,
        authorization_code=auth_code
    )
    return result


@router.get("/me/generate-meal-plan")
async def generate_meal_plan(user_profile: user_schema.UserProfile,
                             workout_data: workout_schema.WorkoutDataSchema):

    engine = MealPlanningRuleEngine()
    meal_plan = engine.generate_meal_plan(user_profile, workout_data)

    return meal_plan
