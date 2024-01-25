from fastapi import FastAPI
from routes.auth import router as auth_router
from routes.chat import router as chat_router
from contextlib import asynccontextmanager
from db.dbUtils import get_client, close_client
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
import socketio
from socketUtils.event_handler import create_socket_events

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

app = FastAPI()

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
create_socket_events(sio)
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        get_client()
        create_socket_events(sio)
        yield
    finally:
        close_client()

app.include_router(auth_router, prefix="/users", tags=["Authentications"])
app.include_router(chat_router, prefix="/chat-app", tags=["Chat"])

@app.get("/")
async def index():
    return {"message": "Hello World"}

app.mount('/', socket_app)
