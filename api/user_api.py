from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status
from db.schemas import user_schema
from integrations.fitness_app_conn_service_provider import FitnessAppConnectionFactory, FitnessConnectionService
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/me/update-fitness-goal",
            status_code=status.HTTP_200_OK, name="save-goal")
async def update_my_fitness_goal(request: user_schema.FitnessGoalRequestSchema):
    return UserService.calculate_nutrition_targets(request)


@router.put("/me/update-fitness-goal",
             status_code=status.HTTP_200_OK, name="update-goal")
async def update_my_fitness_goal(request: user_schema.FitnessGoalRequestSchema):
    return UserService.calculate_nutrition_targets(request)



@router.put("/me/get-daily-meals",
             status_code=status.HTTP_200_OK,
            name="get-daily-meals")
async def get_daily_meals(request):
    return UserService.today_meals(request)



@router.post("/me/connect",
             status_code=status.HTTP_200_OK,
             name="connect-fitness-app")
async def connect_fitness_app(request: user_schema.FitnessAppConnectionRequestSchema,
                              auth_code: str):
    service = FitnessConnectionService()
    current_user = {"id":1}
    result = service.connect_user_to_provider(
        user_id=current_user['id'],
        provider_type=request.provider,
        authorization_code=auth_code
    )
    return result


