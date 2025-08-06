from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status
from db.schemas import user_schema
from services.user_service import UserService

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/me/update-fitness-goal",
            status_code=status.HTTP_200_OK, name="save-goal")
async def update_my_fitness_goal(request: user_schema.FitnessGoalRequestSchema):

    # save the database and then return
    return UserService.calculate_nutrition_targets(request)


@router.put("/me/update-fitness-goal",
             status_code=status.HTTP_200_OK, name="update-goal")
async def update_my_fitness_goal(request: user_schema.FitnessGoalRequestSchema):
    # save the database and then return
    return UserService.calculate_nutrition_targets(request)



@router.put("/me/get-daily-meals",
             status_code=status.HTTP_200_OK,
            name="get-daily-meals")
async def get_daily_meals(request):
    return UserService.today_meals(request)