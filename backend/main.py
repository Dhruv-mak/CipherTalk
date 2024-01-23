from fastapi import FastAPI
from routes.auth import router as auth_router
from routes.chat import router as chat_router
from contextlib import asynccontextmanager
from db.dbUtils import get_client, close_client
from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer

load_dotenv()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        get_client()
        yield
    finally:
        close_client()


app = FastAPI()
app.include_router(auth_router, prefix="/users", tags=["Authentications"])
app.include_router(chat_router, prefix="/chat-app", tags=["Chat"])


@app.get("/")
async def index():
    return {"message": "Hello World"}
