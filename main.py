from dotenv import load_dotenv
load_dotenv('.env')
from fastapi import FastAPI

from api import main_api
app = FastAPI()



app.include_router(main_api.api_router, prefix="/api/v1")
