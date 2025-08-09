from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette.responses import JSONResponse

from db.db_conn import get_db
from db.models import User
from db.schemas import user_schema
from services.user_service import UserService
from utils import app_logger, resp_msgs
from utils.app_helper import generate_otp, verify_otp, create_refresh_token, create_auth_token, verify_user_from_token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/request-otp", status_code=status.HTTP_200_OK, name="request-otp")
async def request_otp(request: user_schema.UserRegistration):
    try:
        if request.phone_number:
            otp = generate_otp(identifier=request.phone_number, otp_type="mobile_verification")
            if not otp:
                return JSONResponse(
                    content={"status": "error", "message": resp_msgs.STATUS_404_MSG},
                    status_code=status.HTTP_400_BAD_REQUEST
                )
            # TODO : remove OTP from here. its just temporary for testing
            return JSONResponse(
                content={
                    "status": "success",
                    "message": "Otp sent to your mobile number. Please verify Using it",
                    "temp_otp": f"{otp}"
                },
                status_code=status.HTTP_201_CREATED
            )
    except Exception as e:
        app_logger.exceptionlogs(f"Error in register user, Error: {e}")
        return JSONResponse(
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.post("/verify-otp", status_code=status.HTTP_200_OK, name="verify-otp")
async def verify_mobile_and_otp(request: user_schema.OTPVerification, db: Session = Depends(get_db)):
    if not request.phone_number or not request.otp:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": "error", "message": "Please provide mobile number and OTP"}
        )

    is_verified = verify_otp(identifier=request.phone_number, otp_input=request.otp, otp_type="mobile_verification")

    if not is_verified:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": "error", "message": resp_msgs.INVALID_OTP}
        )

    try:
        user = UserService.create_user_by_phone_number(phone_number=request.phone_number, db=db)
        if not user:
            app_logger.exceptionlogs(f"Not able to create user get_or_create_user_by_phone_number")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"status": "error", "message": resp_msgs.INVALID_OTP}
            )

        auth_token = create_auth_token(user)
        refresh_token = create_refresh_token(user)
        
        # Check if profile is complete (has name and email)
        is_profile_complete = bool(user.name and user.email)
        
        return JSONResponse(
            content={
                "access_token": auth_token,
                "refresh_token": refresh_token,
                "is_profile_complete": is_profile_complete
            },
            status_code=status.HTTP_201_CREATED
        )
    except Exception as e:
        app_logger.exceptionlogs(f"Error while finding or creating the user, Error {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "error", "message": resp_msgs.STATUS_500_MSG}
        )
