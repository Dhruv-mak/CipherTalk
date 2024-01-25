import socketio
from models.auth import UserInDB
from jose import jwt
from db.dbUtils import get_client
import os
from models.chat import ChatEventType

def create_socket_events(sio: socketio.AsyncServer):
    @sio.event
    async def connect(sid, environ, auth):
        try:
            db = get_client()
            token = auth.get('token') if auth else None
            if not token:
                raise ValueError("Un-authorized handshake. Token is missing")

            decoded_token = jwt.decode(token, os.environ.get("ACCESS_TOKEN_SECRET"), algorithms=["HS256"])
            user_id = decoded_token.get('_id')

            user = await db.users.find_one({"_id": user_id})
            if not user:
                raise ValueError("Un-authorized handshake. Token is invalid")

            sio.enter_room(sid, user_id)
            await sio.emit(ChatEventType.CONNECTED_EVENT, room=user_id)
            print(f"User connected. userId: {user_id}")

            # You can call your other event handlers here
        except Exception as e:
            await sio.emit(ChatEventType.SOCKET_ERROR_EVENT, str(e), room=sid)


    @sio.on(ChatEventType.JOIN_CHAT_EVENT)
    async def join_chat(sid, chat_id):
        print(f"User joined the chat. chatId: {chat_id}")
        sio.enter_room(sid, chat_id)


    @sio.on(ChatEventType.TYPING_EVENT)
    async def participant_typing(sid, chat_id):
        await sio.emit(ChatEventType.TYPING_EVENT, chat_id, room=chat_id)


    @sio.on(ChatEventType.STOP_TYPING_EVENT)
    async def participant_stopped_typing(sid, chat_id):
        await sio.emit(ChatEventType.STOP_TYPING_EVENT, chat_id, room=chat_id)


    @sio.on(ChatEventType.DISCONNECT_EVENT)
    async def disconnect(sid):
        print(f"User has disconnected. userId: {sid}")
        # Here, you need to handle disconnection and room leaving logic


async def emit_socket_event(io, room_id, event, payload):
    await io.emit(event, payload, room=room_id)
