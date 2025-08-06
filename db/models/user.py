import uuid
from db.models import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import UUID

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    phone_number = Column(String, unique=True, index=True)
    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)
    is_active = Column(Boolean, default=False)
    profile_picture_url = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())