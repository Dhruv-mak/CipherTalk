from pydantic import BaseModel, Field
from typing import ForwardRef
from datetime import datetime
from enum import Enum
from models.auth import User, Attachment

Chat = ForwardRef('Chat')

class Message(BaseModel):
    sender: User
    content: str
    attachments: list[Attachment] = Field(default_factory=list)
    chat: Chat

class Chat(BaseModel):
    name: str
    isGroupChat: bool
    lastMessage: Message
    participants: list[User] = Field(default_factory=list)
    admin: User

Message.model_rebuild()