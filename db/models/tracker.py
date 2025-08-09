from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, Enum, Text, Date, UniqueConstraint
from sqlalchemy import func
from sqlalchemy.orm import relationship

from db.models import Base
from utils.enums import FitnessProvider


class UserFitnessConnection(Base):
    __tablename__ = "user_fitness_connections"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(Enum(FitnessProvider),
                      nullable=False,
                      default=FitnessProvider.GOOGLE_FIT)

    # OAuth tokens
    access_token = Column(String(500))
    refresh_token = Column(String(500))
    token_expires_at = Column(DateTime)

    # Connection status
    is_active = Column(Boolean, default=True)
    last_sync_date = Column(Date)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="user_fitness_app_connection")
    fitness_data = relationship("DailyFitnessData", back_populates="app_connection")


    __table_args__ = (
        UniqueConstraint('user_id', 'provider', name='unique_user_provider'),
    )


class DailyFitnessData(Base):
    __tablename__ = "daily_fitness_data"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    connection_id = Column(Integer, ForeignKey("user_fitness_connections.id"), nullable=False)
    date = Column(Date, nullable=False)

    steps = Column(Integer)
    calories_burned = Column(Integer)
    active_minutes = Column(Integer)

    sleep_hours = Column(Float)
    sleep_quality_score = Column(Integer)
    bedtime = Column(DateTime)
    wake_time = Column(DateTime)

    activity_level_today = Column(String(20))
    extra_calories_needed = Column(Integer, default=0)

    is_complete = Column(Boolean, default=False)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    app_connection = relationship("UserFitnessConnection", back_populates="fitness_data")
    user = relationship("User", back_populates="daily_fitness_data")


    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='unique_user_date'),
    )