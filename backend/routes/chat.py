from fastapi import APIRouter, Request, Depends, Form, Body, File, UploadFile
from typing import Annotated
from pymongo import MongoClient
from utils.chat import (
    get_all_messages,
    search_available_users,
    create_or_get_one_on_one_chat,
    create_group_chat,
    remove_one_on_one_chat,
    get_group_chat_details,
    delete_group_chat,
    update_group_name,
    add_participant_to_group,
    remove_participant_from_group,
    leave_group_chat,
    get_all_messages_for_chat,
    send_message_to_chat,
)
from utils.dbUtils import get_client
from models.responses import (
    AllChatResponse,
    AvailableUsersResponse,
    ChatResponse,
    CreateGroupChatRequest,
    BaseResponse,
    UpdateGroupNameRequest,
    ChatWithoutLastMessageResponse,
    AllMessagesResponse,
    SendMessageResponse,
)
from models.auth import UserResponse
from utils.auth import verify_and_return_token
from utils.socket_events import get_socketio
from socketio import AsyncServer


router = APIRouter()


@router.get("/chats")
async def get_all(
    token: Annotated[dict, Depends(verify_and_return_token)],
    db: Annotated[MongoClient, Depends(get_client)],
) -> AllChatResponse:
    return await get_all_messages(token, db)


@router.get("/chats/users")
async def users(
    token: Annotated[dict, Depends(verify_and_return_token)],
    db: Annotated[MongoClient, Depends(get_client)],
) -> AvailableUsersResponse:
    return await search_available_users(token, db)


@router.post("/chats/c/{receiverId}")
async def create_or_get_chat(
    token: Annotated[dict, Depends(verify_and_return_token)],
    receiverId: str,
    db: Annotated[MongoClient, Depends(get_client)],
    sio: AsyncServer = Depends(get_socketio),
) -> ChatResponse:
    return await create_or_get_one_on_one_chat(token, receiverId, db, sio)


@router.post("/chats/group")
async def create_group(
    token: Annotated[dict, Depends(verify_and_return_token)],
    req: CreateGroupChatRequest,
    db: Annotated[MongoClient, Depends(get_client)],
    sio: AsyncServer = Depends(get_socketio),
):
    return await create_group_chat(token, req, db, sio)


@router.delete("/chats/remove/{chatId}")
async def remove_chat(
    token: Annotated[dict, Depends(verify_and_return_token)],
    chatId: str,
    db: Annotated[MongoClient, Depends(get_client)],
    sio: AsyncServer = Depends(get_socketio),
) -> BaseResponse:
    return await remove_one_on_one_chat(token, chatId, db, sio)


@router.get("/chats/group/{chatId}")
async def group_chat(
    token: Annotated[dict, Depends(verify_and_return_token)],
    chatId: str,
    db: Annotated[MongoClient, Depends(get_client)],
):
    return await get_group_chat_details(token, chatId, db)


@router.delete("/chats/group/{chatId}")
async def delete_chat(
    token: Annotated[dict, Depends(verify_and_return_token)],
    chatId: str,
    db: Annotated[MongoClient, Depends(get_client)],
    sio: AsyncServer = Depends(get_socketio),
) -> BaseResponse:
    return await delete_group_chat(token, chatId, db, sio)


@router.patch("/chats/group/{chatId}")
async def update_name(
    token: Annotated[dict, Depends(verify_and_return_token)],
    chatId: str,
    request_body: UpdateGroupNameRequest,
    db: Annotated[MongoClient, Depends(get_client)],
    sio: AsyncServer = Depends(get_socketio),
) -> ChatWithoutLastMessageResponse:
    return await update_group_name(token, chatId, request_body.name, db, sio)


@router.post("/chats/group/{chatId}/{participantId}")
async def add_participant(
    token: Annotated[dict, Depends(verify_and_return_token)],
    chatId: str,
    participantId: str,
    db: Annotated[MongoClient, Depends(get_client)],
    sio: AsyncServer = Depends(get_socketio),
) -> ChatWithoutLastMessageResponse:
    return await add_participant_to_group(token, chatId, participantId, db, sio)


@router.delete("/chats/group/{chatId}/{participantId}")
async def remove_participant(
    token: Annotated[dict, Depends(verify_and_return_token)],
    chatId: str,
    participantId: str,
    db: Annotated[MongoClient, Depends(get_client)],
    sio: AsyncServer = Depends(get_socketio),
) -> ChatWithoutLastMessageResponse:
    return await remove_participant_from_group(token, chatId, participantId, db, sio)


@router.delete("/chats/leave/group/{chatId}")
async def leave_group(
    token: Annotated[dict, Depends(verify_and_return_token)],
    chatId: str,
    db: Annotated[MongoClient, Depends(get_client)],
    sio: AsyncServer = Depends(get_socketio),
):
    return await leave_group_chat(token, chatId, token.get("_id"), db, sio)


@router.get("/messages/{chatId}")
async def get_messages(
    token: Annotated[dict, Depends(verify_and_return_token)],
    chatId: str,
    db: Annotated[MongoClient, Depends(get_client)],
) -> AllMessagesResponse:
    return await get_all_messages_for_chat(token, chatId, db)


@router.post("/messages/{chatId}")
async def send_message(
    token: Annotated[dict, Depends(verify_and_return_token)],
    chatId: str,
    content: Annotated[str, Body()],
    db: Annotated[MongoClient, Depends(get_client)],
    sio: Annotated[AsyncServer, Depends(get_socketio)],
    request: Request,
    attachments: Annotated[list[UploadFile], File()],
) -> SendMessageResponse:
    return await send_message_to_chat(token, chatId, content, attachments, db, sio, request)