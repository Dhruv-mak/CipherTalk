from pydantic import BaseModel
from models.auth import UserResponse
from models.chat import Chat, ChatUser, ChatWithLastMessage, Message


class BaseResponse(BaseModel):
    message: str
    statusCode: int
    success: bool


class RegisterAndCurrentUserResponse(BaseResponse):
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


class AllChatResponse(BaseResponse):
    data: list[ChatWithLastMessage]


class AvailableUsersResponse(BaseResponse):
    data: list[ChatUser]


class ChatResponse(BaseResponse):
    data: Chat


class ChatWithoutLastMessageResponse(BaseResponse):
    data: Chat


class CreateGroupChatRequest(BaseModel):
    name: str
    participants: list[str]


class UpdateGroupNameRequest(BaseModel):
    name: str


class AllMessagesResponse(BaseResponse):
    data: list[Message]

class SendMessageResponse(BaseResponse):
    data: Message
