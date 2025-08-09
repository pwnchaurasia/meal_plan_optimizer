from typing import Union

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from db.db_conn import get_db
from db.schemas import user_schema, workout_schema
from db.schemas.user_schema import UserProfile
from integrations.fitness_app_conn_service_provider import FitnessAppConnectionFactory, FitnessConnectionService
from services.meal_planning_rule_engine import MealPlanningRuleEngine
from services.user_service import UserService
from utils import app_logger, resp_msgs
from utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["User"])


@router.post("/me/fitness-goal",
            status_code=status.HTTP_201_CREATED, name="create-fitness-goal")
async def create_my_fitness_goal(fitness_goal: user_schema.FitnessGoalRequestSchema, 
                                current_user=Depends(get_current_user),
                                db: Session = Depends(get_db)):
    try:
        result = UserService.create_fitness_goal(current_user.id, fitness_goal, db)
        if result:
            return JSONResponse(
                content=result,
                status_code=status.HTTP_201_CREATED
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "error", "message": "Failed to create fitness goal"}
            )
    except Exception as e:
        app_logger.exceptionlogs(f"Error in create_my_fitness_goal, Error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


@router.put("/me/fitness-goal",
           status_code=status.HTTP_200_OK, name="update-fitness-goal")
async def update_my_fitness_goal(fitness_goal: user_schema.FitnessGoalUpdateSchema,
                                current_user=Depends(get_current_user),
                                db: Session = Depends(get_db)):
    try:
        result = UserService.update_fitness_goal(current_user.id, fitness_goal, db)
        if result:
            return JSONResponse(
                content=result,
                status_code=status.HTTP_200_OK
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": "No active fitness goal found"}
            )
    except Exception as e:
        app_logger.exceptionlogs(f"Error in update_my_fitness_goal, Error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


@router.get("/me/get-daily-meals",
             status_code=status.HTTP_200_OK,
            name="get-daily-meals")
async def get_daily_meals(current_user=Depends(get_current_user),
                         db: Session = Depends(get_db)):
    try:
        # Create a mock request object with user_id
        class MockRequest:
            def __init__(self, user_id):
                self.user_id = user_id
        
        request = MockRequest(current_user.id)
        result = UserService.today_meals(request)
        return JSONResponse(
            content=result,
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        app_logger.exceptionlogs(f"Error in get_daily_meals, Error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


@router.post("/me/connect",
             status_code=status.HTTP_200_OK,
             name="connect-fitness-app")
async def connect_fitness_app(fitness_app_conn: user_schema.FitnessAppConnectionRequestSchema,
                              auth_code: str,
                              current_user=Depends(get_current_user),
                              db: Session = Depends(get_db)):
    try:
        service = FitnessConnectionService()
        result = service.connect_user_to_provider(
            user_id=current_user.id,
            provider_type=fitness_app_conn.provider,
            authorization_code=auth_code
        )
        return JSONResponse(
            content=result,
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        app_logger.exceptionlogs(f"Error in connect_fitness_app, Error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


@router.post("/me/profile",
            status_code=status.HTTP_201_CREATED, name="create-user-profile")
async def create_user_profile(profile_data: user_schema.UserProfileUpdateSchema,
                             current_user=Depends(get_current_user),
                             db: Session = Depends(get_db)):
    try:
        result = UserService.create_or_update_user_profile(current_user.id, profile_data, db)
        if result:
            return JSONResponse(
                content=result,
                status_code=status.HTTP_201_CREATED
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "error", "message": "Failed to create user profile"}
            )
    except Exception as e:
        app_logger.exceptionlogs(f"Error in create_user_profile, Error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


@router.put("/me/profile",
           status_code=status.HTTP_200_OK, name="update-user-profile")
async def update_user_profile(profile_data: user_schema.UserProfileUpdateSchema,
                             current_user=Depends(get_current_user),
                             db: Session = Depends(get_db)):
    try:
        result = UserService.create_or_update_user_profile(current_user.id, profile_data, db)
        if result:
            return JSONResponse(
                content=result,
                status_code=status.HTTP_200_OK
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "error", "message": "Failed to update user profile"}
            )
    except Exception as e:
        app_logger.exceptionlogs(f"Error in update_user_profile, Error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


@router.post("/me/generate-meal-plan")
async def generate_meal_plan(user_profile: user_schema.UserProfile,
                             workout_data: workout_schema.WorkoutDataSchema,
                             current_user=Depends(get_current_user),
                             db: Session = Depends(get_db)):
    try:
        engine = MealPlanningRuleEngine()
        meal_plan = engine.generate_meal_plan(user_profile, workout_data)
        return JSONResponse(
            content=meal_plan,
            status_code=status.HTTP_200_OK
        )
    except Exception as e:
        app_logger.exceptionlogs(f"Error in generate_meal_plan, Error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )
