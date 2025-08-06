from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class IngredientBase(BaseModel):
    name: str
    category: str
    calories_per_100g: Optional[float] = None
    protein_per_100g: Optional[float] = None
    carbs_per_100g: Optional[float] = None
    fat_per_100g: Optional[float] = None


class IngredientCreate(IngredientBase):
    pass


class IngredientResponse(IngredientBase):
    id: int

    class Config:
        from_attributes = True


class RecipeIngredientBase(BaseModel):
    ingredient_id: int
    quantity: float
    unit: str


class RecipeIngredientCreate(RecipeIngredientBase):
    pass


class RecipeIngredientResponse(RecipeIngredientBase):
    id: int
    ingredient: IngredientResponse

    class Config:
        from_attributes = True


class RecipeBase(BaseModel):
    name: str
    description: Optional[str] = None
    calories_per_serving: float
    protein_g: float
    carbs_g: float
    fat_g: float
    prep_time_minutes: int
    cook_time_minutes: int
    servings: int
    instructions: str


class RecipeCreate(RecipeBase):
    ingredients: List[RecipeIngredientCreate]


class RecipeUpdate(BaseModel):
    name: Optional[str]
    description: Optional[str]
    calories_per_serving: Optional[float]
    protein_g: Optional[float]
    carbs_g: Optional[float]
    fat_g: Optional[float]
    prep_time_minutes: Optional[int]
    cook_time_minutes: Optional[int]
    servings: Optional[int]
    instructions: Optional[str]


class RecipeResponse(RecipeBase):
    id: int
    total_time_minutes: int  # prep + cook time
    is_active: bool
    created_at: datetime
    ingredients: List[RecipeIngredientResponse]

    class Config:
        from_attributes = True


class RecipeSearchQuery(BaseModel):
    q: Optional[str]
    category: Optional[str]
    max_prep_time: Optional[int]
    max_calories: Optional[int]
    limit: int
    offset: int