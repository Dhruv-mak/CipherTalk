from fastapi import FastAPI, APIRouter
from fastapi.staticfiles import StaticFiles
from routes.auth import router as auth_router
from routes.chat import router as chat_router
from contextlib import asynccontextmanager
from utils.dbUtils import get_client, close_client
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
import socketio
from utils.socket_events import create_socket_events, get_socketio
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    root_path="/chat"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
sio = get_socketio()
socket_app = socketio.ASGIApp(socketio_server=sio, other_asgi_app=app)
app.mount("/images", StaticFiles(directory="./public/images"), name="images")
app.mount('/socket', socket_app)

app.include_router(auth_router, prefix="/users", tags=["Authentications"])
app.include_router(chat_router, prefix="/chat-app", tags=["Chat"])
