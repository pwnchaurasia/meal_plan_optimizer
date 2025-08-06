from datetime import date
from typing import Optional

from pydantic import BaseModel


class WorkoutResponseSchema(BaseModel):
    id: int
    name: str
    workout_type: str
    exercise_type: str
    is_default : str

class ExerciseRequestSchema(BaseModel):
    name: str

class ExerciseResponseSchema(BaseModel):
    id: int
    workout_id: int
    name: str


class ExerciseSetRequestSchema(BaseModel):
    weight: float
    reps: int
    time: int


class ExerciseSetResponseSchema(BaseModel):
    id: int
    exercise_id: int
    weight: float
    reps: int
    time: int


class WorkoutDataSchema(BaseModel):
    date: date
    steps: Optional[int] = None
    active_minutes: Optional[int] = None
    calories_burned: Optional[int] = None
    workout_type: Optional[str] = None
