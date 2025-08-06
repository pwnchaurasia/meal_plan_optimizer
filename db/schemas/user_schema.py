from typing import Optional
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