from fastapi import APIRouter, Depends, HTTPException, status

from db.schemas import user_schema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/request-otp", status_code=status.HTTP_200_OK, name="request-otp")
async def request_otp(request: user_schema.UserRegistration):
    pass


@router.post("/verify-otp", status_code=status.HTTP_200_OK, name="verify-otp")
async def verify_otp(request: user_schema.OTPVerification):
    pass