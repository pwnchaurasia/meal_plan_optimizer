from datetime import date
from typing import Optional, List
from pydantic import BaseModel


class DailyActivityTrackerRequestSchema(BaseModel):
    date: date
    total_exercises_done: Optional[int] = 0
    total_sets_completed: Optional[int] = 0
    total_weight_lifted: Optional[float] = 0.0
    total_reps_completed: Optional[int] = 0
    total_workout_time: Optional[float] = 0.0
    calories_burned_from_activity: Optional[float] = 0.0
    calories_consumed: Optional[float] = 0.0
    protein_consumed_g: Optional[float] = 0.0
    carbs_consumed_g: Optional[float] = 0.0
    fat_consumed_g: Optional[float] = 0.0
    fiber_consumed_g: Optional[float] = 0.0
    workout_types_done: Optional[List[str]] = []
    notes: Optional[str] = None


class DailyActivityTrackerUpdateSchema(BaseModel):
    total_exercises_done: Optional[int] = None
    total_sets_completed: Optional[int] = None
    total_weight_lifted: Optional[float] = None
    total_reps_completed: Optional[int] = None
    total_workout_time: Optional[float] = None
    calories_burned_from_activity: Optional[float] = None
    calories_consumed: Optional[float] = None
    protein_consumed_g: Optional[float] = None
    carbs_consumed_g: Optional[float] = None
    fat_consumed_g: Optional[float] = None
    fiber_consumed_g: Optional[float] = None
    workout_types_done: Optional[List[str]] = None
    notes: Optional[str] = None


class DailyActivityTrackerResponseSchema(BaseModel):
    id: int
    user_id: int
    date: date
    total_exercises_done: int
    total_sets_completed: int
    total_weight_lifted: float
    total_reps_completed: int
    total_workout_time: float
    calories_burned_from_activity: float
    calories_consumed: float
    protein_consumed_g: float
    carbs_consumed_g: float
    fat_consumed_g: float
    fiber_consumed_g: float
    net_calorie_balance: float
    workout_types_done: Optional[str] = None
    notes: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class CalculateActivityDataRequestSchema(BaseModel):
    user_id: int
    date: date
