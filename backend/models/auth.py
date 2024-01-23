from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime
from enum import Enum
from typing import Optional, Annotated

class UserRoles(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"

class UserLoginType(str, Enum):
    GOOGLE = "google"
    GITHUB = "github"
    EMAIL_PASSWORD = "email_password"

class Attachment(BaseModel):
    url: str
    location: str

class UserBase(BaseModel):
    username: Annotated[str, Field(min_length=3, max_length=50)]
    email: EmailStr
    role: UserRoles = UserRoles.USER

    @validator("username", "email", pre=True)
    def validate_fields(cls, value):
        return value.lower() if isinstance(value, str) else value

class UserRequest(UserBase):
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
    refreshToken: Optional[str] = None
    forgotPasswordToken: Optional[str] = None
    forgotPasswordExpiry: Optional[datetime] = None
    emailVerificationToken: str
    emailVerificationExpiry: datetime

    class Config:
        json_encoders = {
            Enum: lambda v: v.value,
        }

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
