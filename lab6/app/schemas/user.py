from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserLogin(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    token: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserMe(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True 