import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base

# SQLite database configuration
DB_NAME = os.getenv("DB_NAME", "meal_optimizer.db")  # Default database name
DB_PATH = os.getenv("DB_PATH", "./")  # Default to current directory

# Create SQLite database URL
DB_URL = f"sqlite:///{DB_PATH}{DB_NAME}"
print(f"DB URL {DB_URL}")

# SQLite specific engine configuration
engine = create_engine(
   DB_URL,
   pool_pre_ping=True,
   connect_args={"check_same_thread": False}  # Required for SQLite with FastAPI
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

def get_db():
   db = SessionLocal()
   try:
       yield db
   finally:
       db.close()