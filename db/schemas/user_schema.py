from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, EmailStr, HttpUrl, computed_field, field_validator, root_validator, Field

class UserRegistration(BaseModel):
    phone_number: str

class OTPVerification(BaseModel):
    phone_number: str
    otp: str


class Token(BaseModel):
    access_token: str
    token_type: str

class UserProfile(BaseModel):
    email: EmailStr
    name: str
    profile_picture_url: Optional[HttpUrl] = None

    class Config:
        from_attributes = True


class FitnessGoalRequestSchema(BaseModel):
    goal_achievement_time_frame: str
    current_weight: float
    target_weight: float
    current_daily_calories: float
    daily_activity_level: str


class FitnessGoalUpdateSchema(BaseModel):
    goal_achievement_time_frame: Optional[str] = None
    current_weight: Optional[float] = None
    target_weight: Optional[float] = None
    current_daily_calories: Optional[float] = None
    daily_activity_level: Optional[str] = None


class UserProfileUpdateSchema(BaseModel):
    gender: Optional[str] = None
    food_preference_type: Optional[str] = None
    preferred_meal_frequency: Optional[int] = None
    snack_preference: Optional[bool] = None
    cooking_skill_level: Optional[int] = None
    max_prep_time_minutes: Optional[int] = None
    allergies: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
    disliked_foods: Optional[List[str]] = None
    preferred_cuisines: Optional[List[str]] = None


class FitnessAppConnectionRequestSchema(BaseModel):
    provider: str
    authtoken: str
    refreshtoken: str
