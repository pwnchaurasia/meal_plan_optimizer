from fastapi import APIRouter
from api import auth_api, user_api, workout_api
api_router = APIRouter()


api_router.include_router(auth_api.router)
api_router.include_router(user_api.router)
api_router.include_router(workout_api.router)




@api_router.get("/")
def read_root():
    return {"Hello": "World"}
