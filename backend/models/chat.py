from pydantic import BaseModel, Field
from typing import ForwardRef
from datetime import datetime
from enum import Enum
from models.auth import UserResponse, Attachment

Chat = ForwardRef('Chat')

class Message(BaseModel):
    sender: UserResponse
    content: str
    attachments: list[Attachment] = Field(default_factory=list)
    chat: Chat

class Chat(BaseModel):
    name: str
    isGroupChat: bool
    lastMessage: Message
    participants: list[UserResponse] = Field(default_factory=list)
    admin: UserResponse

Message.model_rebuild()