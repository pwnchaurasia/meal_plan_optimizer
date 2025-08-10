from fastapi import APIRouter
from api import (auth_api, user_api, 
                 workout_api, recipe_api, tracker_api, meal_plan_api)
api_router = APIRouter()


api_router.include_router(auth_api.router)
api_router.include_router(user_api.router)
api_router.include_router(workout_api.router)
api_router.include_router(recipe_api.router)
api_router.include_router(tracker_api.router)
api_router.include_router(meal_plan_api.router)
