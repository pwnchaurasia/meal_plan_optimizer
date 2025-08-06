from fastapi import HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from starlette import status

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/verify-otp")

async def verify_user_from_token(toke, db):
    user = {}
    return True, "success", user


async def get_current_user(db: Session, token: str = Depends(oauth2_scheme)):
    is_verified, msg, user = verify_user_from_token(token, db=db)
    if not is_verified:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=msg,
        headers={"WWW-Authenticate": "Bearer"},
    )

    return user
