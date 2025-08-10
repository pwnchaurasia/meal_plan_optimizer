from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from db.db_conn import get_db
from db.schemas import meal_plan_schema
from services.meal_planning_service import MealPlanningService
from utils import app_logger, resp_msgs
from utils.dependencies import get_current_user

router = APIRouter(prefix="/meal-plans", tags=["Meal Planning"])


@router.post("/generate",
            status_code=status.HTTP_201_CREATED,
            name="generate-meal-plan")
async def generate_meal_plan(request_data: meal_plan_schema.MealPlanGenerationRequestSchema,
                           current_user=Depends(get_current_user),
                           db: Session = Depends(get_db)):
    """Generate a complete meal plan for a specific date"""
    try:
        meal_planning_service = MealPlanningService()
        
        # Prepare custom configuration
        custom_config = {
            "custom_calorie_target": request_data.custom_calorie_target,
            "llm_provider": "ollama",
            "model_name": "qwen2:7b",
            "temperature": 0.7
        }
        
        # Add custom preferences if provided
        if request_data.custom_preferences:
            custom_config.update(request_data.custom_preferences)
        
        result = await meal_planning_service.generate_meal_plan(
            user_id=current_user.id,
            target_date=request_data.target_date,
            custom_config=custom_config,
            regenerate_if_exists=request_data.regenerate_if_exists,
            db=db
        )
        
        if result.get("status") == "success":
            return JSONResponse(
                content=result,
                status_code=status.HTTP_201_CREATED
            )
        elif result.get("status") == "info":
            return JSONResponse(
                content=result,
                status_code=status.HTTP_200_OK
            )
        else:
            return JSONResponse(
                content=result,
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        app_logger.exceptionlogs(f"Error in generate_meal_plan: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


@router.get("/",
           status_code=status.HTTP_200_OK,
           name="get-meal-plan",
           response_model=meal_plan_schema.MealPlanResponseSchema)
async def get_meal_plan(target_date: date = Query(..., description="Date in YYYY-MM-DD format"),
                       current_user=Depends(get_current_user),
                       db: Session = Depends(get_db)):
    """Get meal plan for a specific date"""
    try:
        from db.models.meal_plan import MealPlan
        from sqlalchemy.orm import joinedload
        
        meal_plan = db.query(MealPlan).options(
            joinedload(MealPlan.meals)
        ).filter(
            MealPlan.user_id == current_user.id,
            MealPlan.date == target_date
        ).first()
        
        if meal_plan:
            return meal_plan
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No meal plan found for the specified date"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        app_logger.exceptionlogs(f"Error in get_meal_plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=resp_msgs.STATUS_500_MSG
        )


@router.get("/summary",
           status_code=status.HTTP_200_OK,
           name="get-meal-plan-summary",
           response_model=meal_plan_schema.MealPlanSummarySchema)
async def get_meal_plan_summary(target_date: date = Query(..., description="Date in YYYY-MM-DD format"),
                               current_user=Depends(get_current_user),
                               db: Session = Depends(get_db)):
    """Get a summary of the meal plan for a specific date"""
    try:
        from db.models.meal_plan import MealPlan
        
        meal_plan = db.query(MealPlan).filter(
            MealPlan.user_id == current_user.id,
            MealPlan.date == target_date
        ).first()
        
        if not meal_plan:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No meal plan found for the specified date"
            )
        
        # Calculate summary data
        calorie_difference = meal_plan.total_calories - meal_plan.target_calories
        total_calories = meal_plan.total_calories or 1  # Avoid division by zero
        protein_percentage = (meal_plan.total_protein_g * 4 / total_calories) * 100
        carbs_percentage = (meal_plan.total_carbs_g * 4 / total_calories) * 100
        fat_percentage = (meal_plan.total_fat_g * 9 / total_calories) * 100
        
        summary = meal_plan_schema.MealPlanSummarySchema(
            meal_plan_id=meal_plan.id,
            date=meal_plan.date,
            target_calories=meal_plan.target_calories,
            total_calories=meal_plan.total_calories,
            calorie_difference=round(calorie_difference, 1),
            protein_percentage=round(protein_percentage, 1),
            carbs_percentage=round(carbs_percentage, 1),
            fat_percentage=round(fat_percentage, 1),
            meals_count=len(meal_plan.meals),
            generation_time=meal_plan.generation_time_seconds,
            llm_model=meal_plan.llm_model_used
        )
        
        return summary
            
    except HTTPException:
        raise
    except Exception as e:
        app_logger.exceptionlogs(f"Error in get_meal_plan_summary: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=resp_msgs.STATUS_500_MSG
        )


@router.post("/quick-generate",
            status_code=status.HTTP_201_CREATED,
            name="quick-generate-meal-plan")
async def quick_generate_meal_plan(target_date: date = Query(default=None, description="Date in YYYY-MM-DD format (optional, defaults to today)"),
                                  custom_calories: Optional[float] = Query(default=None, description="Custom calorie target"),
                                  llm_provider: str = Query(default="ollama", description="LLM provider: openai, anthropic, ollama"),
                                  llm_model: str = Query(default="llama3:instruct", description="Model name (e.g., llama3:instruct, qwen2:7b, mistral:7b)"),
                                  regenerate: bool = Query(default=False, description="Regenerate if meal plan exists"),
                                  current_user=Depends(get_current_user),
                                  db: Session = Depends(get_db)):
    """Quick meal plan generation with query parameters"""
    try:
        # If no date provided, use today's date
        if target_date is None:
            target_date = date.today()
        
        meal_planning_service = MealPlanningService()
        
        # Prepare custom configuration
        custom_config = {
            "custom_calorie_target": custom_calories,
            "llm_provider": llm_provider,
            "model_name": llm_model if llm_provider == "ollama" else "gpt-4" if llm_provider == "openai" else "claude-3-sonnet-20240229",
            "temperature": 0.7
        }
        
        result = await meal_planning_service.generate_meal_plan(
            user_id=current_user.id,
            target_date=target_date,
            custom_config=custom_config,
            regenerate_if_exists=regenerate,
            db=db
        )
        
        if result.get("status") == "success":
            return JSONResponse(
                content=result,
                status_code=status.HTTP_201_CREATED
            )
        elif result.get("status") == "info":
            return JSONResponse(
                content=result,
                status_code=status.HTTP_200_OK
            )
        else:
            return JSONResponse(
                content=result,
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        app_logger.exceptionlogs(f"Error in quick_generate_meal_plan: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


@router.get("/today",
           status_code=status.HTTP_200_OK,
           name="get-today-meal-plan",
           response_model=meal_plan_schema.MealPlanResponseSchema)
async def get_today_meal_plan(current_user=Depends(get_current_user),
                             db: Session = Depends(get_db)):
    """Get today's meal plan"""
    try:
        from db.models.meal_plan import MealPlan
        from sqlalchemy.orm import joinedload
        
        today = date.today()
        meal_plan = db.query(MealPlan).options(
            joinedload(MealPlan.meals)
        ).filter(
            MealPlan.user_id == current_user.id,
            MealPlan.date == today
        ).first()
        
        if meal_plan:
            return meal_plan
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No meal plan found for today. Use POST /meal-plans/quick-generate to create today's meal plan"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        app_logger.exceptionlogs(f"Error in get_today_meal_plan: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=resp_msgs.STATUS_500_MSG
        )


@router.delete("/",
              status_code=status.HTTP_200_OK,
              name="delete-meal-plan")
async def delete_meal_plan(target_date: date = Query(..., description="Date in YYYY-MM-DD format"),
                          current_user=Depends(get_current_user),
                          db: Session = Depends(get_db)):
    """Delete meal plan for a specific date"""
    try:
        from db.models.meal_plan import MealPlan
        
        meal_plan = db.query(MealPlan).filter(
            MealPlan.user_id == current_user.id,
            MealPlan.date == target_date
        ).first()
        
        if not meal_plan:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": "No meal plan found for the specified date"}
            )
        
        db.delete(meal_plan)
        db.commit()
        
        return JSONResponse(
            content={
                "status": "success",
                "message": f"Meal plan for {target_date} deleted successfully"
            },
            status_code=status.HTTP_200_OK
        )
        
    except Exception as e:
        app_logger.exceptionlogs(f"Error in delete_meal_plan: {e}")
        db.rollback()
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


# Demo endpoint for interview
@router.post("/demo/generate-with-activity",
            status_code=status.HTTP_201_CREATED,
            name="demo-generate-meal-plan-with-activity")
async def demo_generate_meal_plan_with_activity(target_date: date = Query(..., description="Date in YYYY-MM-DD format"),
                                               current_user=Depends(get_current_user),
                                               db: Session = Depends(get_db)):
    """Demo endpoint: Generate meal plan considering user's workout activity"""
    try:
        meal_planning_service = MealPlanningService()
        
        # Always regenerate for demo purposes
        result = await meal_planning_service.generate_meal_plan(
            user_id=current_user.id,
            target_date=target_date,
            custom_config={
                "llm_provider": "ollama",
                "model_name": "qwen2:7b",
                "temperature": 0.7
            },
            regenerate_if_exists=True,  # Always regenerate for demo
            db=db
        )
        
        # Add demo information
        if result.get("status") == "success":
            result["demo_info"] = {
                "message": "This meal plan was generated considering your workout activity and fitness goals",
                "features_demonstrated": [
                    "Activity-based calorie adjustment",
                    "User dietary preferences integration",
                    "Fitness goal alignment",
                    "Real-time LLM generation",
                    "Complete nutritional breakdown"
                ]
            }
        
        return JSONResponse(
            content=result,
            status_code=status.HTTP_201_CREATED if result.get("status") == "success" else status.HTTP_400_BAD_REQUEST
        )
        
    except Exception as e:
        app_logger.exceptionlogs(f"Error in demo_generate_meal_plan_with_activity: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )
