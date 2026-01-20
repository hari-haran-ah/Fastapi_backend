from pydantic import BaseModel, EmailStr, field_validator
from enum import Enum
import re
from uuid import UUID

class Role(str, Enum):
    admin = "admin"
    user = "user"


class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    password: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str):
        if len(v.strip()) < 2:
            raise ValueError("Name must be at least 2 characters long")
        return v.strip()


    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str):

        if not re.match(r"^\+?[1-9]\d{9,14}$", v):
            raise ValueError("Invalid phone number format")
        return v
    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*()_+=-]", v):
            raise ValueError("Password must contain at least one special character")
        return v


class UserOut(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    role: Role
    is_active: bool
    is_verified: bool

    class Config:
        from_attributes = True
