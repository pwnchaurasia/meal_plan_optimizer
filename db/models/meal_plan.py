from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Text, Date, UniqueConstraint
from sqlalchemy import func
from sqlalchemy.orm import relationship

from db.models import Base


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    
    # Nutritional targets for the day
    target_calories = Column(Float, nullable=False)
    target_protein_g = Column(Float, default=0.0)
    target_carbs_g = Column(Float, default=0.0)
    target_fat_g = Column(Float, default=0.0)
    target_fiber_g = Column(Float, default=0.0)
    
    # Calculated totals from all meals
    total_calories = Column(Float, default=0.0)
    total_protein_g = Column(Float, default=0.0)
    total_carbs_g = Column(Float, default=0.0)
    total_fat_g = Column(Float, default=0.0)
    total_fiber_g = Column(Float, default=0.0)
    
    # Generation metadata
    generation_prompt = Column(Text)  # Store the prompt used for generation
    llm_model_used = Column(String(100))  # Track which LLM was used
    generation_time_seconds = Column(Float)
    
    # Status
    is_active = Column(Boolean, default=True)
    user_feedback = Column(Text)  # User can provide feedback
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="meal_plans")
    meals = relationship("Meal", back_populates="meal_plan", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='unique_user_meal_plan_date'),
    )


class Meal(Base):
    __tablename__ = "meals"

    id = Column(Integer, primary_key=True, index=True)
    meal_plan_id = Column(Integer, ForeignKey("meal_plans.id"), nullable=False)
    
    # Meal details
    meal_type = Column(String(50), nullable=False)  # breakfast, lunch, dinner, snack_1, snack_2
    meal_name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Nutritional information
    calories = Column(Float, nullable=False)
    protein_g = Column(Float, default=0.0)
    carbs_g = Column(Float, default=0.0)
    fat_g = Column(Float, default=0.0)
    fiber_g = Column(Float, default=0.0)
    
    # Additional nutritional info
    sodium_mg = Column(Float, default=0.0)
    sugar_g = Column(Float, default=0.0)
    calcium_mg = Column(Float, default=0.0)
    iron_mg = Column(Float, default=0.0)
    vitamin_c_mg = Column(Float, default=0.0)
    
    # Meal metadata
    prep_time_minutes = Column(Integer, default=0)
    cooking_time_minutes = Column(Integer, default=0)
    difficulty_level = Column(Integer, default=1)  # 1-5 scale
    cuisine_type = Column(String(50))
    
    # Ingredients and instructions (JSON stored as text)
    ingredients = Column(Text)  # JSON array of ingredients
    instructions = Column(Text)  # JSON array of cooking steps
    
    # Dietary flags
    is_vegetarian = Column(Boolean, default=False)
    is_vegan = Column(Boolean, default=False)
    is_gluten_free = Column(Boolean, default=False)
    is_dairy_free = Column(Boolean, default=False)
    is_low_carb = Column(Boolean, default=False)
    is_high_protein = Column(Boolean, default=False)
    
    # User interaction
    user_rating = Column(Integer)  # 1-5 stars
    user_notes = Column(Text)
    is_favorite = Column(Boolean, default=False)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    meal_plan = relationship("MealPlan", back_populates="meals")
