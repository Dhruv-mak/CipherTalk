from fastapi import Request, Response, Depends
from typing import Annotated
from pymongo import MongoClient
from models.responses import AllMessagesResponse, AvailableUsersResponse
from db.dbUtils import get_client


async def common_chat_aggregation():
    return [
        {
            "$lookup": {
                "from": "users",
                "foreignField": "_id",
                "localField": "participants",
                "as": "participants",
                "pipeline": [
                    {
                        "$project": {
                            "password": 0,
                            "refreshToken": 0,
                            "forgotPasswordToken": 0,
                            "forgotPasswordTokenExpiry": 0,
                            "emailVerificationToken": 0,
                            "emailVerificationTokenExpiry": 0,
                        }
                    }
                ],
            }
        },
        {
            "$lookup": {
                "from": "chatmessages",
                "foreignField": "_id",
                "localField": "lastMessage",
                "as": "lastMessage",
                "pipeline": [
                    {
                        "$lookup": {
                            "from": "users",
                            "foreignField": "_id",
                            "localField": "sender",
                            "as": "sender",
                            "pipeline": [
                                {
                                    "$project": {
                                        "username": 1,
                                        "avatar": 1,
                                        "email": 1,
                                    }
                                }
                            ],
                        }
                    },
                    {"$addFields": {"sender": {"$first": "$sender"}}},
                ],
            }
        },
        {
            "$addFields": {
                "lastMessage": {"$first": "$lastMessage"},
            }
        },
    ]


async def get_all_messages(
    request: Request,
    db: Annotated[MongoClient, Depends(get_client)],
):
    pipeline = [
        {"$match": {"participants": {"$elemMatch": {"$eq": request.user._id}}}},
        {"$sort": {"last_updated": -1}},
        *common_chat_aggregation(),
    ]
    chats = db.chats.aggregate(pipeline)
    return AllMessagesResponse(
        success=True,
        statusCode=200,
        message="All messages fetched successfully",
        data={"messages": list(chats)},
    )


async def search_available_users(
    request: Request, db: Annotated[MongoClient, Depends(get_client)]
):
    pipeline = [
        {"$match": {"_id": {"$ne": request.user._id}}},
        {
            "$project": {
                "avatar": 1,
                "username": 1,
                "email": 1,
            }
        },
    ]
    users = db.chat.aggregate(pipeline)
    return AvailableUsersResponse(
        success=True,
        statusCode=200,
        message="Available users fetched successfully",
        data={"users": list(users)},
    )
