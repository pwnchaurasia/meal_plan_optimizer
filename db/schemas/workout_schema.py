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

