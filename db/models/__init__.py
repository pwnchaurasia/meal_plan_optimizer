from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Import all models so that Alembic sees them
from db.models.user import User, FitnessGoal, UserProfile
from db.models.recipe import *
from db.models.workout import *
from db.models.inventory import *
from db.models.tracker import *
