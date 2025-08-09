from db.db_conn import get_db

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from db.db_conn import get_db
from db.schemas import recipe_schema
from utils.dependencies import get_current_user

router = APIRouter(prefix="/recipe", tags=["Recipe"])



@router.post("/", name="create-recipe")
async def create_recipe(recipe: recipe_schema.RecipeCreate,):
    pass


@router.get("/", name='get-recipe')
async def get_recipes(recipe_search_query: recipe_schema.RecipeSearchQuery,
        db: Session = Depends(get_db)
):
    pass


@router.get("/{recipe_id}", name='get-recipe')
async def get_recipe_by_id(
        recipe_id: int,
        db: Session = Depends(get_db)
):
    pass


@router.put("/{recipe_id}", name='update-recipe')
async def update_recipe(recipe_id: int,
                        recipe_update: recipe_schema.RecipeUpdate,
                        db: Session = Depends(get_db),
):
    pass


@router.delete("/{recipe_id}", name='delete-recipe')
async def delete_recipe(recipe_id: int):
    pass




# Ingredient endpoints
@router.post("/ingredients/", name='create-ingredients')
async def create_ingredient(ingredient: recipe_schema.IngredientCreate):
    pass




@router.get("/ingredients/{ingredient_id}", name='get-ingredient')
async def get_ingredient_by_id(
        ingredient_id: int,
        db: Session = Depends(get_db)
):
    pass