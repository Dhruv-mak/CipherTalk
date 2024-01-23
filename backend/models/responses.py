from pydantic import BaseModel
from models.auth import UserResponse
from models.chat import Chat
class BaseResponse(BaseModel):
    message: str
    statusCode: int
    success: bool

class RegisterResponse(BaseResponse):
    data: UserResponse
    
class EmailVerificationData(BaseModel):
    isEmailVerified: bool

class EmailVerificationResponse(BaseResponse):
    data: EmailVerificationData
    
class RefreshTokenData(BaseModel):
    accessToken: str
    refreshToken: str

class RefreshTokenResponse(BaseResponse):
    data: RefreshTokenData

class LoginData(BaseModel):
    accessToken: str
    refreshToken: str
    user: UserResponse

class LoginResponse(BaseResponse):
    data: LoginData

class AllMessagesData(BaseModel):
    messages: list[Chat]

class AllMessagesResponse(BaseResponse):
    data: AllMessagesData

class AvailableUsersData(BaseModel):
    users: list[UserResponse]

class AvailableUsersResponse(BaseResponse):
    data: AvailableUsersData