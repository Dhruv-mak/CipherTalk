from fastapi import Request, Response, Depends, HTTPException, UploadFile
from typing import Annotated
from pymongo import MongoClient
from models.responses import (
    AllChatResponse,
    AvailableUsersResponse,
    ChatResponse,
    CreateGroupChatRequest,
    UpdateGroupNameRequest,
    BaseResponse,
    ChatWithoutLastMessageResponse,
    AllMessagesResponse,
    SendMessageResponse,
)
from utils.dbUtils import get_client
from bson import ObjectId
from utils.socket_events import emit_socket_event
from datetime import datetime
from models.chat import Chat
from models.auth import PyObjectId
from socketio import AsyncServer
from models.chat import ChatEventType
import os
import uuid
import shutil
from utils.file_handling import upload_file


def common_chat_aggregation():
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


def common_message_aggregation():
    return [
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
    ]


async def get_all_messages(
    token: dict,
    db: MongoClient,
):
    pipeline = [
        {"$match": {"participants": {"$elemMatch": {"$eq": ObjectId(token["_id"])}}}},
        {"$sort": {"updatedAt": -1}},
        *common_chat_aggregation(),
    ]
    chats = db.chats.aggregate(pipeline)
    chats = list(chats)
    return AllChatResponse(
        success=True,
        statusCode=200,
        message="All messages fetched successfully",
        data=chats,
    )


async def search_available_users(token: dict, db: MongoClient):
    pipeline = [
        {"$match": {"_id": {"$ne": ObjectId(token["_id"])}}},
        {
            "$project": {
                "avatar": 1,
                "username": 1,
                "email": 1,
            }
        },
    ]
    users = list(db.users.aggregate(pipeline))
    return AvailableUsersResponse(
        success=True,
        statusCode=200,
        message="Available users fetched successfully",
        data=users,
    )


async def create_or_get_one_on_one_chat(
    token: dict, receiver_id: str, db: MongoClient, sio: AsyncServer
):
    user_id = token["_id"]
    receiver = db.users.find_one({"_id": ObjectId(receiver_id)})
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver does not exist")

    if receiver_id == user_id:
        raise HTTPException(status_code=400, detail="You cannot chat with yourself")

    chat_aggregation = common_chat_aggregation()
    chat = db.chats.aggregate(
        [
            {
                "$match": {
                    "isGroupChat": False,
                    "participants": {
                        "$all": [ObjectId(user_id), ObjectId(receiver_id)]
                    },
                }
            },
            *chat_aggregation,
        ]
    )

    chat = list(chat)
    if chat:
        data = chat[0]
        return ChatResponse(
            statusCode=200, data=data, message="Chat already exists", success=True
        )

    new_chat_instance = db.chats.insert_one(
        {
            "name": "One on one chat",
            "participants": [ObjectId(user_id), ObjectId(receiver_id)],
            "admin": ObjectId(user_id),
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
            "isGroupChat": False,
            "__v": 0,
        }
    )

    created_chat = db.chats.aggregate(
        [{"$match": {"_id": new_chat_instance.inserted_id}}, *chat_aggregation]
    )

    created_chat = list(created_chat)
    if not created_chat:
        raise HTTPException(status_code=500, detail="Internal server error")

    payload = created_chat[0]
    await emit_socket_event(sio, payload["_id"], ChatEventType.NEW_CHAT_EVENT, payload)

    return ChatResponse(
        statusCode=201, data=payload, message="Chat created successfully", success=True
    )


async def create_group_chat(
    token: dict, req: CreateGroupChatRequest, db: MongoClient, sio: AsyncServer
):
    user_id = token["_id"]
    participants = req.participants
    if user_id in req.participants:
        raise HTTPException(
            status_code=400, detail="You cannot add yourself as a participant"
        )
    participants.append(user_id)
    participants = list(set(participants))
    participants = [ObjectId(p) for p in participants]
    if len(participants) < 3:
        raise HTTPException(
            status_code=400, detail="You need to add atleast 2 participants"
        )

    users = db.users.find({"_id": {"$in": participants}})
    users = list(users)
    if len(users) != len(participants):
        raise HTTPException(
            status_code=404, detail="One or more participants do not exist"
        )

    chat = db.chats.insert_one(
        {
            "name": req.name,
            "participants": participants,
            "admin": ObjectId(user_id),
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
            "isGroupChat": True,
            "__v": 0,
        }
    )

    chat = db.chats.aggregate(
        [{"$match": {"_id": chat.inserted_id}}, *common_chat_aggregation()]
    )

    chat = list(chat)
    if not chat:
        raise HTTPException(status_code=500, detail="Internal server error")

    for participant in participants:
        if str(participant) == user_id:
            continue
        else:
            await emit_socket_event(
                sio, str(participant), ChatEventType.NEW_CHAT_EVENT, chat[0]
            )

    return ChatResponse(
        statusCode=201, data=chat[0], message="Chat created successfully", success=True
    )


async def remove_one_on_one_chat(
    token: dict, chat_id: str, db: MongoClient, sio: AsyncServer
):
    user_id = token["_id"]
    pipeline = [
        {
            "$match": {
                "_id": ObjectId(chat_id),
            },
        },
        *common_chat_aggregation(),
    ]
    chat = list(db.chats.aggregate(pipeline))[0]
    if not chat:
        raise HTTPException(status_code=404, detail="Chat does not exist")

    if chat["isGroupChat"]:
        raise HTTPException(
            status_code=400, detail="You cannot delete a group chat this way"
        )

    if ObjectId(user_id) not in list(x["_id"] for x in chat["participants"]):
        raise HTTPException(
            status_code=400, detail="You are not a participant of this chat"
        )

    if len(chat["participants"]) > 2:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete a group chat this way. Please leave the group instead",
        )

    db.chats.delete_one({"_id": ObjectId(chat_id)})
    await delete_cascade_chat_meessages(chat_id, db)

    for participant in chat["participants"]:
        if str(participant) == user_id:
            continue
        else:
            other_user = str(participant)
    await emit_socket_event(sio, participant, ChatEventType.LEAVE_CHAT_EVENT, chat)
    return BaseResponse(
        statusCode=204, message="Chat deleted successfully", success=True
    )


async def delete_cascade_chat_meessages(chatID: str, db: MongoClient):
    messages = db.chatmessages.find({"chat": ObjectId(chatID)})
    attachments = []
    for message in messages:
        attachments.extend(message["attachments"])
    for attachment in attachments:
        os.remove(attachment["localPath"])
    db.chatmessages.delete_many({"chat": ObjectId(chatID)})


async def get_group_chat_details(
    token: dict,
    chat_id: str,
    db: MongoClient,
):
    user_id = token["_id"]
    pipeline = [
        {
            "$match": {
                "_id": ObjectId(chat_id),
                "isGroupChat": True,
            },
        },
        *common_chat_aggregation(),
    ]
    chat = db.chats.aggregate(pipeline)[0]
    if not chat:
        raise HTTPException(status_code=404, detail="Group Chat does not exist")

    if not chat["isGroupChat"]:
        raise HTTPException(
            status_code=400,
            detail="You cannot get details of a one on one chat this way",
        )

    if ObjectId(user_id) not in chat["participants"]:
        raise HTTPException(
            status_code=400, detail="You are not a participant of this chat"
        )

    return ChatResponse(
        statusCode=200,
        data=chat,
        message="Chat details fetched successfully",
        success=True,
    )


async def delete_group_chat(
    token: dict,
    chat_id: str,
    db: MongoClient,
    sio: AsyncServer,
):
    user_id = token["_id"]
    pipeline = [
        {
            "$match": {
                "_id": ObjectId(chat_id),
                "isGroupChat": True,
            },
        },
        *common_chat_aggregation(),
    ]
    chat = list(db.chats.aggregate(pipeline))[0]
    if not chat:
        raise HTTPException(status_code=404, detail="Group Chat does not exist")

    if not chat["isGroupChat"]:
        raise HTTPException(
            status_code=400, detail="You cannot delete a one on one chat this way"
        )

    if str(chat["admin"]) != user_id:
        raise HTTPException(
            status_code=400, detail="You are not the admin of this chat"
        )

    db.chats.delete_one({"_id": ObjectId(chat_id)})
    await delete_cascade_chat_meessages(chat_id, db)
    for participant in chat["participants"]:
        if str(participant) == user_id:
            continue
        else:
            emit_socket_event(
                sio, str(participant), ChatEventType.LEAVE_CHAT_EVENT, chat
            )

    return BaseResponse(
        statusCode=204, message="Chat deleted successfully", success=True
    )


async def update_group_name(
    token: dict, chat_id: str, name: str, db: MongoClient, sio: AsyncServer
):
    user_id = token["_id"]
    pipeline = [
        {
            "$match": {
                "_id": ObjectId(chat_id),
                "isGroupChat": True,
            },
        },
        *common_chat_aggregation(),
    ]
    chat = list(db.chats.aggregate(pipeline))[0]
    if not chat:
        raise HTTPException(status_code=404, detail="Group Chat does not exist")

    if not chat["isGroupChat"]:
        raise HTTPException(
            status_code=400, detail="You cannot update a one on one chat"
        )

    if str(chat["admin"]) != user_id:
        raise HTTPException(
            status_code=400, detail="You are not the admin of this chat"
        )

    db.chats.update_one({"_id": ObjectId(chat_id)}, {"$set": {"name": name}})
    chat = list(db.chats.aggregate(pipeline))[0]
    if not chat:
        raise HTTPException(status_code=500, detail="Internal server error")
    for participant in chat["participants"]:
        await emit_socket_event(
            sio, str(participant), ChatEventType.UPDATE_GROUP_NAME_EVENT, chat
        )
    return ChatWithoutLastMessageResponse(
        statusCode=200,
        data=chat,
        message="Chat name updated successfully",
        success=True,
    )


async def add_participant_to_group(
    token: dict, chat_id: str, participant_id: str, db: MongoClient, sio: AsyncServer
):
    user_id = token["_id"]
    pipeline = [
        {
            "$match": {
                "_id": ObjectId(chat_id),
                "isGroupChat": True,
            },
        },
        *common_chat_aggregation(),
    ]
    chat = list(db.chats.aggregate(pipeline))[0]
    if not chat:
        raise HTTPException(status_code=404, detail="Group Chat does not exist")

    if not chat["isGroupChat"]:
        raise HTTPException(
            status_code=400, detail="You cannot update a one on one chat"
        )

    if str(chat["admin"]) != user_id:
        raise HTTPException(
            status_code=400, detail="You are not the admin of this chat"
        )

    user = db.users.find_one({"_id": ObjectId(participant_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")

    if ObjectId(participant_id) in chat["participants"]:
        raise HTTPException(
            status_code=400, detail="User is already a participant of this chat"
        )

    old_participants = chat["participants"]
    for participant in old_participants:
        if str(participant) == participant_id:
            raise HTTPException(
                status_code=409, detail="User is already a participant of this chat"
            )

    db.chats.update_one(
        {"_id": ObjectId(chat_id)},
        {"$push": {"participants": ObjectId(participant_id)}},
    )
    chat = list(db.chats.aggregate(pipeline))[0]
    if not chat:
        raise HTTPException(status_code=500, detail="Internal server error")
    await emit_socket_event(
        sio, str(participant_id), ChatEventType.NEW_CHAT_EVENT, chat
    )
    return ChatWithoutLastMessageResponse(
        statusCode=200,
        data=chat,
        message="User added successfully",
        success=True,
    )


async def remove_participant_from_group(
    token: dict, chat_id: str, participant_id: str, db: MongoClient, sio: AsyncServer
) -> ChatWithoutLastMessageResponse:
    user_id = token["_id"]
    pipeline = [
        {
            "$match": {
                "_id": ObjectId(chat_id),
                "isGroupChat": True,
            },
        },
        *common_chat_aggregation(),
    ]
    chat = list(db.chats.aggregate(pipeline))[0]
    if not chat:
        raise HTTPException(status_code=404, detail="Group Chat does not exist")

    if not chat["isGroupChat"]:
        raise HTTPException(
            status_code=400, detail="You cannot update a one on one chat"
        )

    if str(chat["admin"]) != user_id:
        raise HTTPException(
            status_code=400, detail="You are not the admin of this chat"
        )

    user = db.users.find_one({"_id": ObjectId(participant_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")

    if ObjectId(participant_id) not in list(x["_id"] for x in chat["participants"]):
        raise HTTPException(
            status_code=400, detail="User is not a participant of this chat"
        )

    db.chats.update_one(
        {"_id": ObjectId(chat_id)},
        {"$pull": {"participants": ObjectId(participant_id)}},
    )
    chat = list(db.chats.aggregate(pipeline))[0]
    if not chat:
        raise HTTPException(status_code=500, detail="Internal server error")
    await emit_socket_event(
        sio, str(participant_id), ChatEventType.LEAVE_CHAT_EVENT, chat
    )
    return ChatWithoutLastMessageResponse(
        statusCode=200, data=chat, message="User removed successfully", success=True
    )


async def leave_group_chat(
    token: dict, chat_id: str, db: MongoClient, sio: AsyncServer
):
    user_id = token["_id"]
    pipeline = [
        {
            "$match": {
                "_id": ObjectId(chat_id),
                "isGroupChat": True,
            },
        },
        *common_chat_aggregation(),
    ]
    chat = db.chats.aggregate(pipeline)[0]
    if not chat:
        raise HTTPException(status_code=404, detail="Group Chat does not exist")

    if not chat["isGroupChat"]:
        raise HTTPException(
            status_code=400, detail="You cannot leave a one on one chat"
        )

    if str(chat["admin"]) == user_id:
        raise HTTPException(
            status_code=400, detail="You cannot leave a group chat you created"
        )

    if ObjectId(user_id) not in chat["participants"]:
        raise HTTPException(
            status_code=400, detail="You are not a participant of this chat"
        )

    db.chats.update_one(
        {"_id": ObjectId(chat_id)}, {"$pull": {"participants": ObjectId(user_id)}}
    )
    chat = db.chats.aggregate(pipeline)[0]
    if not chat:
        raise HTTPException(status_code=500, detail="Internal server error")
    return ChatResponse(
        statusCode=200, data=chat, message="User removed successfully", success=True
    )


async def get_all_messages_for_chat(
    token: dict,
    chat_id: str,
    db: MongoClient,
):
    user_id = token["_id"]
    chat = db.chats.find_one({"_id": ObjectId(chat_id)})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat does not exist")
    if ObjectId(user_id) not in chat["participants"]:
        raise HTTPException(
            status_code=400, detail="User is not a participant of this chat"
        )

    messages = db.chatmessages.aggregate(
        [
            {
                "$match": {
                    "chat": ObjectId(chat_id),
                },
            },
            *common_message_aggregation(),
            {
                "$sort": {
                    "createdAt": -1,
                }
            },
        ]
    )
    messages = list(messages)
    return AllMessagesResponse(
        statusCode=200,
        data=messages,
        message="Messages fetched successfully",
        success=True,
    )


async def send_message_to_chat(
    token: dict,
    chat_id: str,
    content: str,
    attachments: list[UploadFile] | None,
    db: MongoClient,
    sio: AsyncServer,
    request: Request,
):
    user_id = token["_id"]
    if not content and not attachments:
        raise HTTPException(
            status_code=400, detail="Message content or attachment is required"
        )

    chat = db.chats.find_one({"_id": ObjectId(chat_id)})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat does not exist")

    message_files = []
    for file in attachments:
        upload_file_response = await upload_file(file, request)
        message_files.append(
            {
                "name": file.filename,
                "url": upload_file_response["url"],
                "localPath": upload_file_response["localPath"],
            }
        )

    message_data = {
        "__v": 0,
        "sender": ObjectId(user_id),
        "content": content,
        "chat": ObjectId(chat_id),
        "attachments": message_files,
        "createdAt": datetime.now(),
        "updatedAt": datetime.now(),
    }

    new_message = db.chatmessages.insert_one(message_data)
    message_data["_id"] = new_message.inserted_id

    db.chats.update_one(
        {"_id": ObjectId(chat_id)}, {"$set": {"lastMessage": new_message.inserted_id}}
    )

    for participant in chat.get("participants", []):
        if str(participant) != user_id:
            await emit_socket_event(
                sio, participant, ChatEventType.MESSAGE_RECEIVED_EVENT, message_data
            )
    message_data = db.chatmessages.aggregate(
        [
            {
                "$match": {
                    "_id": new_message.inserted_id,
                },
            },
            *common_message_aggregation(),
        ]
    )
    message_data = list(message_data)[0]
    return SendMessageResponse(
        statusCode=201,
        data=message_data,
        message="Message sent successfully",
        success=True,
    )
