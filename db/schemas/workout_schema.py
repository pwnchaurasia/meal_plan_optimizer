from datetime import date
from typing import Optional, List

from pydantic import BaseModel


class WorkoutResponseSchema(BaseModel):
    id: int
    name: str
    workout_type: str
    exercise_type: str
    is_default: bool

    class Config:
        from_attributes = True


class ExerciseRequestSchema(BaseModel):
    name: str


class ExerciseResponseSchema(BaseModel):
    id: int
    workout_id: Optional[int] = None
    name: str

    class Config:
        from_attributes = True


class ExerciseSetRequestSchema(BaseModel):
    weight: float
    reps: int
    time: float


class ExerciseSetResponseSchema(BaseModel):
    id: int
    exercise_id: int
    weight: float
    reps: int
    time: float

    class Config:
        from_attributes = True


class WorkoutDataSchema(BaseModel):
    date: date
    steps: Optional[int] = None
    active_minutes: Optional[int] = None
    calories_burned: Optional[int] = None
    workout_type: Optional[str] = None


class DailyWorkoutRequestSchema(BaseModel):
    date: date


class SetResponseSchema(BaseModel):
    set_id: int
    weight: float
    reps: int
    time: float
    created_at: str


class ExerciseWithSetsSchema(BaseModel):
    exercise_id: int
    exercise_name: str
    sets: List[SetResponseSchema]


class WorkoutWithExercisesSchema(BaseModel):
    workout_id: int
    workout_name: str
    workout_type: str
    exercises: List[ExerciseWithSetsSchema]


class DailyWorkoutResponseSchema(BaseModel):
    status: str
    date: str
    workouts: List[WorkoutWithExercisesSchema]
    total_workouts: int
