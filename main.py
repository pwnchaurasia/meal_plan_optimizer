from dotenv import load_dotenv
from sqladmin import Admin, ModelView

from admin.all_admin import admin_views
from db.db_conn import engine
from db.models import Base

load_dotenv('.env')
from fastapi import FastAPI

from api import main_api

app = FastAPI()

admin = Admin(app, engine)



app.include_router(main_api.api_router, prefix="/api/v1")


for view in admin_views:
    try:
        admin.add_view(view)
    except Exception as e:
        print(f"Error in {e}")