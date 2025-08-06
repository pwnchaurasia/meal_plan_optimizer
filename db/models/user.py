from db.models import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Enum, Text
from sqlalchemy import func

from utils.enums import GoalAchievementTimeFrameType, Gender, FoodPreferenceType, ActivityLevel


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone_number = Column(String, unique=True, index=True)
    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    profile_picture_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FitnessGoal(Base):
    __tablename__ = "fitness_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    daily_activity_level = Column(Enum(ActivityLevel),
                                  nullable=False,
                                  default=ActivityLevel.LIGHTLY_ACTIVE)
    goal_achievement_time_frame = Column(Enum(GoalAchievementTimeFrameType),
                                         nullable=False,
                                         default=GoalAchievementTimeFrameType.AVERAGE)
    current_weight = Column(Float)
    target_weight = Column(Float)

    current_daily_calories = Column(Float)
    calculated_daily_calories = Column(Float)


    is_active = Column(Boolean, default=True)
    achieved = Column(Boolean, default=False)
    achieved_date = Column(DateTime)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserProfile(Base):
    __tablename__ = "user_profile"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)

    gender = Column(Enum(Gender), nullable=False)

    # Dietary Preferences
    food_preference_type = Column(Enum(FoodPreferenceType), nullable=False)
    preferred_meal_frequency = Column(Integer, default=3)
    snack_preference = Column(Boolean, default=True)

    # Cooking and Meal Preferences
    cooking_skill_level = Column(Integer, default=3)  # 1-5 scale
    max_prep_time_minutes = Column(Integer, default=45)

    # # Timing Preferences
    # breakfast_time = Column(String(10))
    # lunch_time = Column(String(10))
    # dinner_time = Column(String(10))
    # early_eater = Column(Boolean, default=False)  # prefers eating earlier in the day

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

