import uuid
from sqlalchemy import Column, String, Boolean, DateTime, func ,Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from enum import Enum

class Role(str, Enum):
    user = "user"
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True, index=True)
    phone = Column(String, nullable=True, unique=True, index=True)
    password = Column(String, nullable=True)

    role = Column(
        SQLEnum(Role, name="role"),
        nullable=False,
        default=Role.user
    )

    is_active = Column(Boolean, nullable=False, default=True)
    is_verified = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now(), server_default=func.now())