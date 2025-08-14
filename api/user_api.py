import json

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from db.db_conn import get_db
from db.models.user import FitnessGoal, UserProfile as UserProfileModel
from db.schemas import user_schema
from integrations.fitness_app_conn_service_provider import FitnessConnectionService
from services.user_service import UserService
from utils import app_logger, resp_msgs
from utils.dependencies import get_current_user

router = APIRouter(prefix="/users", tags=["User"])


@router.get("/me",
           status_code=status.HTTP_200_OK, 
           name="get-current-user-data")
async def get_current_user_data(current_user=Depends(get_current_user),
                               db: Session = Depends(get_db)):
    """
    Get comprehensive current user data including profile and fitness goals
    """
    try:
        # Get user basic information
        user_data = {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "phone_number": current_user.phone_number,
            "is_email_verified": current_user.is_email_verified,
            "is_phone_verified": current_user.is_phone_verified,
            "is_active": current_user.is_active,
            "profile_picture_url": current_user.profile_picture_url,
            "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
            "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None
        }
        
        # Get user profile data
        user_profile = db.query(UserProfileModel).filter(
            UserProfileModel.user_id == current_user.id
        ).first()
        
        profile_data = None
        if user_profile:
            # Parse JSON fields
            allergies = json.loads(user_profile.allergies) if user_profile.allergies else []
            dietary_restrictions = json.loads(user_profile.dietary_restrictions) if user_profile.dietary_restrictions else []
            disliked_foods = json.loads(user_profile.disliked_foods) if user_profile.disliked_foods else []
            preferred_cuisines = json.loads(user_profile.preferred_cuisines) if user_profile.preferred_cuisines else []
            
            profile_data = {
                "id": user_profile.id,
                "gender": user_profile.gender.value if user_profile.gender else None,
                "food_preference_type": user_profile.food_preference_type.value if user_profile.food_preference_type else None,
                "preferred_meal_frequency": user_profile.preferred_meal_frequency,
                "snack_preference": user_profile.snack_preference,
                "cooking_skill_level": user_profile.cooking_skill_level,
                "max_prep_time_minutes": user_profile.max_prep_time_minutes,
                "allergies": allergies,
                "dietary_restrictions": dietary_restrictions,
                "disliked_foods": disliked_foods,
                "preferred_cuisines": preferred_cuisines,
                "created_at": user_profile.created_at.isoformat() if user_profile.created_at else None,
                "updated_at": user_profile.updated_at.isoformat() if user_profile.updated_at else None
            }
        
        # Get active fitness goal data
        fitness_goal = db.query(FitnessGoal).filter(
            FitnessGoal.user_id == current_user.id,
            FitnessGoal.is_active == True
        ).first()
        
        fitness_goal_data = None
        if fitness_goal:
            fitness_goal_data = {
                "id": fitness_goal.id,
                "daily_activity_level": fitness_goal.daily_activity_level.value if fitness_goal.daily_activity_level else None,
                "goal_achievement_time_frame": fitness_goal.goal_achievement_time_frame.value if fitness_goal.goal_achievement_time_frame else None,
                "current_weight": fitness_goal.current_weight,
                "target_weight": fitness_goal.target_weight,
                "current_daily_calories": fitness_goal.current_daily_calories,
                "calculated_daily_calories": fitness_goal.calculated_daily_calories,
                "is_active": fitness_goal.is_active,
                "achieved": fitness_goal.achieved,
                "achieved_date": fitness_goal.achieved_date.isoformat() if fitness_goal.achieved_date else None,
                "created_at": fitness_goal.created_at.isoformat() if fitness_goal.created_at else None,
                "updated_at": fitness_goal.updated_at.isoformat() if fitness_goal.updated_at else None
            }
        
        # Combine all data
        response_data = {
            "status": "success",
            "message": "User data retrieved successfully",
            "data": {
                "user": user_data,
                "profile": profile_data,
                "fitness_goal": fitness_goal_data
            }
        }
        
        return JSONResponse(
            content=response_data,
            status_code=status.HTTP_200_OK
        )
        
    except Exception as e:
        app_logger.exceptionlogs(f"Error in get_current_user_data, Error: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


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


# @router.post("/me/generate-meal-plan")
# async def generate_meal_plan(user_profile: user_schema.UserProfile,
#                              workout_data: workout_schema.WorkoutDataSchema,
#                              current_user=Depends(get_current_user),
#                              db: Session = Depends(get_db)):
#     try:
#         engine = MealPlanningRuleEngine()
#         meal_plan = engine.generate_meal_plan(user_profile, workout_data)
#         return JSONResponse(
#             content=meal_plan,
#             status_code=status.HTTP_200_OK
#         )
#     except Exception as e:
#         app_logger.exceptionlogs(f"Error in generate_meal_plan, Error: {e}")
#         return JSONResponse(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
#         )
