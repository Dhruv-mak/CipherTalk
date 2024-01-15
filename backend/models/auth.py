from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class UserRoles(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserLoginType(Enum):
    GOOGLE = "google"
    GITHUB = "github"
    EMAIL_PASSWORD = "email_password"


class Attachment(BaseModel):
    url: str
    location: str


class User(BaseModel):
    avatar_url: Attachment = {
        "url": "https://via.placeholder.com/200x200.png",
        "location": "",
    }
    username: str
    email: str
    role: UserRoles
    password: str
    loginType: UserLoginType = UserLoginType.EMAIL_PASSWORD
    isEmailVerified: bool = False
    refreshToken: str
    forgotPasswordToken: str
    forgotPasswordExpiry: datetime
    emailVerificationToken: str
    emailVerificationExpiry: datetime
