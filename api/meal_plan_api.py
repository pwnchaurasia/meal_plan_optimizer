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
        meal_planning_service = MealPlanningService()
        meal_plan = await meal_planning_service.get_meal_plan(current_user.id, target_date, db)
        
        if meal_plan:
            return meal_plan
        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": "No meal plan found for the specified date"}
            )
            
    except Exception as e:
        app_logger.exceptionlogs(f"Error in get_meal_plan: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


@router.get("/summary",
           status_code=status.HTTP_200_OK,
           name="get-meal-plan-summary")
async def get_meal_plan_summary(target_date: date = Query(..., description="Date in YYYY-MM-DD format"),
                               current_user=Depends(get_current_user),
                               db: Session = Depends(get_db)):
    """Get a summary of the meal plan for a specific date"""
    try:
        meal_planning_service = MealPlanningService()
        result = await meal_planning_service.get_meal_plan_summary(current_user.id, target_date, db)
        
        if result.get("status") == "success":
            return JSONResponse(
                content=result,
                status_code=status.HTTP_200_OK
            )
        elif result.get("status") == "not_found":
            return JSONResponse(
                content=result,
                status_code=status.HTTP_404_NOT_FOUND
            )
        else:
            return JSONResponse(
                content=result,
                status_code=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        app_logger.exceptionlogs(f"Error in get_meal_plan_summary: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
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
           name="get-today-meal-plan")
async def get_today_meal_plan(current_user=Depends(get_current_user),
                             db: Session = Depends(get_db)):
    """Get today's meal plan"""
    try:
        today = date.today()
        meal_planning_service = MealPlanningService()
        meal_plan = await meal_planning_service.get_meal_plan(current_user.id, today, db)
        
        if meal_plan:
            return meal_plan
        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={
                    "status": "not_found", 
                    "message": "No meal plan found for today",
                    "suggestion": "Use POST /meal-plans/quick-generate to create today's meal plan"
                }
            )
            
    except Exception as e:
        app_logger.exceptionlogs(f"Error in get_today_meal_plan: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
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
                "llm_provider": "openai",
                "model_name": "gpt-4",
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
