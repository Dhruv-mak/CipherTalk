from pydantic import BaseModel, Field
from typing import Annotated
from datetime import datetime
from enum import Enum
from models.auth import UserResponse, Attachment, PyObjectId

class ChatEventType(str, Enum):
    CONNECTED_EVENT = 'connected'
    DISCONNECT_EVENT = 'disconnect'
    JOIN_CHAT_EVENT = 'joinChat'
    LEAVE_CHAT_EVENT = 'leaveChat'
    UPDATE_GROUP_NAME_EVENT = 'updateGroupName'
    MESSAGE_RECEIVED_EVENT = 'messageReceived'
    NEW_CHAT_EVENT= "newChat"
    SOCKET_ERROR_EVENT = 'socketError'
    STOP_TYPING_EVENT = 'stopTyping'
    TYPING_EVENT = 'typing'

class ChatUser(BaseModel):
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias='_id')]
    username: str
    email: str
    avatar: Attachment
    
class Message(BaseModel):
    v : Annotated[int, Field(alias='__v')] = 0
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias='_id')]
    createdAt: datetime
    updatedAt: datetime
    sender: ChatUser
    content: str
    attachments: Annotated[list[Attachment], Field(default_factory=list)]
    chat: Annotated[PyObjectId, Field(default_factory=PyObjectId)]

class Chat(BaseModel):
    id: Annotated[PyObjectId, Field(default_factory=PyObjectId, alias='_id')]
    v: Annotated[int, Field(alias='__v')] = 0
    name: str
    isGroupChat: bool
    participants: Annotated[list[UserResponse], Field(default_factory=list)]
    admin: Annotated[PyObjectId, Field(default_factory=PyObjectId)]
    createdAt: datetime
    updatedAt: datetime

class ChatWithLastMessage(Chat):
    lastMessage: Message | None = None
