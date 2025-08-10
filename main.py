from dotenv import load_dotenv
from sqladmin import Admin

from admin.all_admin import admin_views
from db.db_conn import engine

# from admin.all_admin import admin_views
# from db.db_conn import engine

load_dotenv('.env')
from fastapi import FastAPI

from api import main_api

app = FastAPI()



app.include_router(main_api.api_router, prefix="/api/v1")


admin = Admin(app, engine)


for view in admin_views:
    try:
        admin.add_view(view)
    except Exception as e:
        print(f"Error in {e}")