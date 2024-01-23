from fastapi import APIRouter, Request, Depends
from typing import Annotated
from pymongo import MongoClient
from utils.chat import (
    get_all_messages,
    search_available_users,
    create_or_get_one_chat,
)
from db.dbUtils import get_client
from models.responses import AllMessagesResponse, AvailableUsersResponse

router = APIRouter()


@router.get("/")
async def get_all(
    request: Request, db: Annotated[MongoClient, Depends(get_client)]
) -> AllMessagesResponse:
    return await get_all_messages()


@router.get("/users")
async def users(
    request: Request, db: Annotated[MongoClient, Depends(get_client)]
) -> AvailableUsersResponse:
    return await search_available_users()

@router.post("/c/{receiverId}")
async def create_or_get_chat(
    receiverId: str,
    request: Request,
    db: Annotated[MongoClient, Depends(get_client)]
) -> AllMessagesResponse:
    return await create_or_get_one_chat()