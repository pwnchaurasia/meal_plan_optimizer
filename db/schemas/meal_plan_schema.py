from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field


class MealRequestSchema(BaseModel):
    meal_type: str = Field(..., description="breakfast, lunch, dinner, snack_1, snack_2")
    meal_name: str
    description: Optional[str] = None
    calories: float
    protein_g: Optional[float] = 0.0
    carbs_g: Optional[float] = 0.0
    fat_g: Optional[float] = 0.0
    fiber_g: Optional[float] = 0.0
    sodium_mg: Optional[float] = 0.0
    sugar_g: Optional[float] = 0.0
    prep_time_minutes: Optional[int] = 0
    cooking_time_minutes: Optional[int] = 0
    difficulty_level: Optional[int] = 1
    cuisine_type: Optional[str] = None
    ingredients: Optional[List[str]] = list
    instructions: Optional[List[str]] = list
    is_vegetarian: Optional[bool] = False
    is_vegan: Optional[bool] = False
    is_gluten_free: Optional[bool] = False
    is_dairy_free: Optional[bool] = False


class MealResponseSchema(BaseModel):
    id: int
    meal_type: str
    meal_name: str
    description: Optional[str]
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sodium_mg: float
    sugar_g: float
    prep_time_minutes: int
    cooking_time_minutes: int
    difficulty_level: int
    cuisine_type: Optional[str]
    ingredients: Optional[str]  # JSON string
    instructions: Optional[str]  # JSON string
    is_vegetarian: bool
    is_vegan: bool
    is_gluten_free: bool
    is_dairy_free: bool
    user_rating: Optional[int]
    is_favorite: bool

    class Config:
        from_attributes = True


class MealPlanGenerationRequestSchema(BaseModel):
    target_date: date
    custom_calorie_target: Optional[float] = None
    custom_preferences: Optional[dict] = None
    regenerate_if_exists: Optional[bool] = False


class MealPlanResponseSchema(BaseModel):
    id: int
    user_id: int
    date: date
    target_calories: float
    target_protein_g: float
    target_carbs_g: float
    target_fat_g: float
    target_fiber_g: float
    total_calories: float
    total_protein_g: float
    total_carbs_g: float
    total_fat_g: float
    total_fiber_g: float
    llm_model_used: Optional[str]
    generation_time_seconds: Optional[float]
    is_active: bool
    created_at: str
    updated_at: str
    meals: List[MealResponseSchema] = []

    class Config:
        from_attributes = True


class MealPlanSummarySchema(BaseModel):
    meal_plan_id: int
    date: date
    target_calories: float
    total_calories: float
    calorie_difference: float
    protein_percentage: float
    carbs_percentage: float
    fat_percentage: float
    meals_count: int
    generation_time: Optional[float]
    llm_model: Optional[str]


class NutritionTargetsSchema(BaseModel):
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    protein_percentage: float
    carbs_percentage: float
    fat_percentage: float


class LLMGeneratedMealPlanSchema(BaseModel):
    """Schema for LLM response - what we expect from the AI"""
    breakfast: dict
    lunch: dict
    dinner: dict
    snack_1: dict
    snack_2: dict
    daily_summary: dict


class MealPlanConfigurationSchema(BaseModel):
    """Configuration for meal plan generation"""
    llm_provider: str = "openai"  # openai, anthropic, ollama
    model_name: str = "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 4000
    include_recipes: bool = True
    include_nutrition_breakdown: bool = True
    cuisine_variety: bool = True
    consider_prep_time: bool = True
