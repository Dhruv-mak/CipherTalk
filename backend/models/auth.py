from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from enum import Enum
from typing import Optional
from bson import ObjectId

class UserRoles(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class UserLoginType(str, Enum):
    GOOGLE = "google"
    GITHUB = "github"
    EMAIL_PASSWORD = "email_password"

class Attachment(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    url: str
    location: str

class UserLogin(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str
    
    @validator("username", pre=True)
    def validate_username(cls, value):
        return value.lower() if isinstance(value, str) else value

class UserBase(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr = Field(max_length=50)
    role: UserRoles = UserRoles.USER

    @validator("email", "username", pre=True)
    def validate_email(cls, value):
        return value.lower() if isinstance(value, str) else value

class UserRegister(UserBase):
    password: str

class UserResponse(UserBase):
    avatar: Attachment = Attachment(
        url="https://via.placeholder.com/200x200.png", location=""
    )
    createdAt: datetime
    updatedAt: datetime
    isEmailVerified: bool = False
    loginType: UserLoginType = UserLoginType.EMAIL_PASSWORD

class UserInDB(UserResponse):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    refreshToken: str | None = None
    forgotPasswordToken: str | None = None
    forgotPasswordExpiry: datetime | None = None
    emailVerificationToken: str | None = None
    emailVerificationExpiry: datetime | None = None
    v: int = Field(0, alias="__v")

    class Config:
        json_encoders = {
            Enum: lambda v: v.value,
        }
        allow_population_by_field_name = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None