# backend/app/models/user.py
from typing import Optional
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    AUTHORITY = "authority"
    DRIVER = "driver"
    EMERGENCY = "emergency"

class User(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    email: EmailStr
    hashed_password: str
    full_name: str
    role: UserRole
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "email": "admin@twinflow.ai",
                "full_name": "System Admin",
                "role": "admin",
            }
        }

class UserInDB(User):
    pass