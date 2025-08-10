from datetime import date
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from db.db_conn import get_db
from db.schemas import tracker_schema
from services.tracker_service import TrackerService
from utils import app_logger, resp_msgs
from utils.dependencies import get_current_user

router = APIRouter(prefix="/tracker", tags=["Activity Tracker"])


@router.post("/daily-activity",
            status_code=status.HTTP_201_CREATED, 
            name="create-daily-activity-tracker")
async def create_daily_activity_tracker(tracker_data: tracker_schema.DailyActivityTrackerRequestSchema,
                                       current_user=Depends(get_current_user),
                                       db: Session = Depends(get_db)):
    """Create a new daily activity tracker entry"""
    try:
        result = TrackerService.create_daily_activity_tracker(current_user.id, tracker_data, db)
        if result:
            if result.get("status") == "error":
                return JSONResponse(
                    content=result,
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            else:
                return JSONResponse(
                    content=result,
                    status_code=status.HTTP_201_CREATED
                )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "error", "message": "Failed to create daily activity tracker"}
            )
    except Exception as e:
        app_logger.exceptionlogs(f"Error in create_daily_activity_tracker: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


@router.put("/daily-activity",
           status_code=status.HTTP_200_OK, 
           name="update-daily-activity-tracker")
async def update_daily_activity_tracker(tracker_data: tracker_schema.DailyActivityTrackerUpdateSchema,
                                       tracker_date: date = Query(..., description="Date to update in YYYY-MM-DD format"),
                                       current_user=Depends(get_current_user),
                                       db: Session = Depends(get_db)):
    """Update existing daily activity tracker entry"""
    try:
        result = TrackerService.update_daily_activity_tracker(current_user.id, tracker_date, tracker_data, db)
        if result:
            if result.get("status") == "error":
                return JSONResponse(
                    content=result,
                    status_code=status.HTTP_404_NOT_FOUND
                )
            else:
                return JSONResponse(
                    content=result,
                    status_code=status.HTTP_200_OK
                )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "error", "message": "Failed to update daily activity tracker"}
            )
    except Exception as e:
        app_logger.exceptionlogs(f"Error in update_daily_activity_tracker: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


@router.get("/daily-activity",
           status_code=status.HTTP_200_OK, 
           name="get-daily-activity-tracker",
           response_model=tracker_schema.DailyActivityTrackerResponseSchema)
async def get_daily_activity_tracker(tracker_date: date = Query(default=None, description="Date in YYYY-MM-DD format (optional, defaults to today)"),
                                    current_user=Depends(get_current_user),
                                    db: Session = Depends(get_db)):
    try:
        if tracker_date is None:
            tracker_date = date.today()

        result = TrackerService.get_daily_activity_tracker(current_user.id, tracker_date, db)
        if result:
            return result
        else:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"status": "error", "message": "No activity tracker data found for the specified date"}
            )
    except Exception as e:
        app_logger.exceptionlogs(f"Error in get_daily_activity_tracker: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


@router.post("/calculate-activity-data",
            status_code=status.HTTP_201_CREATED, 
            name="calculate-and-populate-activity-data")
async def calculate_and_populate_activity_data(target_date: date = Query(..., description="Date to calculate data for in YYYY-MM-DD format"),
                                              current_user=Depends(get_current_user),
                                              db: Session = Depends(get_db)):
    try:
        result = TrackerService.calculate_and_populate_activity_data(current_user.id, target_date, db)
        if result:
            if result.get("status") == "info":
                return JSONResponse(
                    content=result,
                    status_code=status.HTTP_200_OK
                )
            else:
                return JSONResponse(
                    content=result,
                    status_code=status.HTTP_201_CREATED
                )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "error", "message": "Failed to calculate and populate activity data"}
            )
    except Exception as e:
        app_logger.exceptionlogs(f"Error in calculate_and_populate_activity_data: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )


# Admin endpoint to calculate activity data for a specific user and date
@router.post("/admin/calculate-activity-data",
            status_code=status.HTTP_201_CREATED,
            name="admin-calculate-activity-data")
async def admin_calculate_activity_data(request_data: tracker_schema.CalculateActivityDataRequestSchema,
                                       db: Session = Depends(get_db)):
    """Admin endpoint to calculate activity data for any user and date"""
    try:
        result = TrackerService.calculate_and_populate_activity_data(request_data.user_id, request_data.date, db)
        if result:
            if result.get("status") == "info":
                return JSONResponse(
                    content=result,
                    status_code=status.HTTP_200_OK
                )
            else:
                return JSONResponse(
                    content=result,
                    status_code=status.HTTP_201_CREATED
                )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "error", "message": "Failed to calculate and populate activity data"}
            )
    except Exception as e:
        app_logger.exceptionlogs(f"Error in admin_calculate_activity_data: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )
