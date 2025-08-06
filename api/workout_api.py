from fastapi import APIRouter, Depends, HTTPException, status

from db.schemas import workout_schema

router = APIRouter(prefix="/workouts", tags=["workout"])

# few of the post apis I have not created as it's very straight forward
# all these would have current_user, which will be fetched from the auth token

@router.get("/", status_code=status.HTTP_200_OK,
            name="get-workouts")
async def get_workouts(request: workout_schema.WorkoutResponseSchema):
    pass



@router.get("/{workout_id}/exercises",
            status_code=status.HTTP_200_OK, name="get-exercise")
async def get_exercise(workout_id:int, request: workout_schema.ExerciseResponseSchema):
    pass


@router.post("/{workout_id}/exercises/{exercise_id}",
             status_code=status.HTTP_200_OK, name="create-exercise")
async def create_exercise(workout_id: int,
                          exercise_id: int,
                          request: workout_schema.ExerciseRequestSchema):
    pass


@router.get("/{workout_id}/exercises/{exercise_id}",
            status_code=status.HTTP_200_OK, name="get-exercise")
async def get_exercise(workout_id: int,
                       exercise_id: int,
                       request: workout_schema.ExerciseResponseSchema):
    pass





@router.post("/{workout_id}/exercises/{exercise_id}/set",
             status_code=status.HTTP_200_OK, name="create-exercise-set")
async def get_exercise(workout_id: int,
                       exercise_id: int,
                       request: workout_schema.ExerciseSetRequestSchema):
    pass



@router.get("/{workout_id}/exercises/{exercise_id}/set",
            status_code=status.HTTP_200_OK, name="exercise-set")
async def get_exercise(workout_id: int,
                       exercise_id: int,
                       request: workout_schema.ExerciseSetRequestSchema):
    pass


