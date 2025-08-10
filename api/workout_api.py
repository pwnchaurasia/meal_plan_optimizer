from datetime import date
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from db.db_conn import get_db
from db.schemas import workout_schema
from services.workout_service import WorkoutService
from utils import app_logger, resp_msgs
from utils.dependencies import get_current_user

router = APIRouter(prefix="/workouts", tags=["Workout"])


@router.get("/", 
           status_code=status.HTTP_200_OK,
           name="get-workouts",
           response_model=List[workout_schema.WorkoutResponseSchema])
async def get_workouts(db: Session = Depends(get_db)):
    """Get all available workouts"""
    try:
        workouts = WorkoutService.get_all_workouts(db)
        return workouts
    except Exception as e:
        app_logger.exceptionlogs(f"Error in get_workouts: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


@router.get("/{workout_id}/exercises",
           status_code=status.HTTP_200_OK, 
           name="get-workout-exercises",
           response_model=List[workout_schema.ExerciseResponseSchema])
async def get_workout_exercises(workout_id: int, db: Session = Depends(get_db)):
    """Get all exercises for a specific workout"""
    try:
        exercises = WorkoutService.get_workout_exercises(workout_id, db)
        return exercises
    except Exception as e:
        app_logger.exceptionlogs(f"Error in get_workout_exercises: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


@router.post("/exercises/{exercise_id}/set",
            status_code=status.HTTP_201_CREATED, 
            name="create-exercise-set")
async def create_exercise_set(exercise_id: int,
                             set_data: workout_schema.ExerciseSetRequestSchema,
                             current_user=Depends(get_current_user),
                             db: Session = Depends(get_db)):
    """Create a new exercise set for a user"""
    try:
        result = WorkoutService.create_exercise_set(current_user.id, exercise_id, set_data, db)
        if result:
            return JSONResponse(
                content=result,
                status_code=status.HTTP_201_CREATED
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "error", "message": "Failed to create exercise set"}
            )
    except Exception as e:
        app_logger.exceptionlogs(f"Error in create_exercise_set: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


@router.get("/daily",
           status_code=status.HTTP_200_OK, 
           name="get-daily-workout")
async def get_daily_workout(workout_date: date = Query(default=None, description="Date in YYYY-MM-DD format (optional, defaults to today)"),
                           current_user=Depends(get_current_user),
                           db: Session = Depends(get_db)):
    """Get all exercises and sets performed by user on a specific date"""
    try:
        result = WorkoutService.get_daily_workout(current_user.id, workout_date, db)
        if result:
            return JSONResponse(
                content=result,
                status_code=status.HTTP_200_OK
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": "No workout data found for the specified date"}
            )
    except Exception as e:
        app_logger.exceptionlogs(f"Error in get_daily_workout: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


@router.post("/generate-smart-ppl-workout",
            status_code=status.HTTP_201_CREATED,
            name="generate-smart-ppl-workout")
async def generate_smart_ppl_workout(target_date: date = Query(default=None, description="Date to generate workout for (optional, defaults to today)"),
                                    current_user=Depends(get_current_user),
                                    db: Session = Depends(get_db)):
    """Generate smart PPL workout based on user's previous workout history"""
    try:
        # If no date provided, use today's date
        if target_date is None:
            target_date = date.today()
            
        result = WorkoutService.generate_smart_ppl_workout(current_user.id, target_date, db)
        if result:
            if result.get("status") == "info":
                return JSONResponse(
                    content=result,
                    status_code=status.HTTP_200_OK
                )
            else:
                return JSONResponse(
                    content=result,
                    status_code=status.HTTP_201_CREATED
                )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "error", "message": "Failed to generate smart PPL workout"}
            )
    except Exception as e:
        app_logger.exceptionlogs(f"Error in generate_smart_ppl_workout: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


# Admin endpoint to populate default workouts and exercises
@router.post("/admin/populate-defaults",
            status_code=status.HTTP_201_CREATED,
            name="populate-default-workouts")
async def populate_default_workouts(db: Session = Depends(get_db)):
    """ For creating the default workouts and exercises in that """
    try:
        result = WorkoutService.populate_default_workouts_and_exercises(db)
        if result:
            if result.get("status") == "info":
                return JSONResponse(
                    content=result,
                    status_code=status.HTTP_200_OK
                )
            else:
                return JSONResponse(
                    content=result,
                    status_code=status.HTTP_201_CREATED
                )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "error", "message": "Failed to populate default workouts"}
            )
    except Exception as e:
        app_logger.exceptionlogs(f"Error in populate_default_workouts: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )
