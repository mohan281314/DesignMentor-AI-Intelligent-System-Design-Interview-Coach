"""User-related Pydantic schemas."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(BaseModel):
    """Schema for user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    full_name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserProfile(BaseModel):
    """User profile with performance metrics."""
    model_config = ConfigDict(from_attributes=True)
    
    score_correctness: float = 0.0
    score_scalability: float = 0.0
    score_tradeoffs: float = 0.0
    score_communication: float = 0.0
    score_depth: float = 0.0
    total_interviews: int = 0
    total_designs: int = 0
    total_diagrams: int = 0
    experience_level: str = "beginner"
    weak_topics: Optional[str] = None
    strong_topics: Optional[str] = None
    theme: str = "dark"


class User(UserBase):
    """User schema for API responses."""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_verified: bool = False
    is_superuser: bool = False
    oauth_provider: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: datetime
    last_login_at: Optional[datetime] = None
    profile: Optional[UserProfile] = None


class UserInDB(User):
    """User schema including hashed password (internal use only)."""
    hashed_password: Optional[str] = None
