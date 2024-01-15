from fastapi import FastAPI
from routes.auth import router as auth_router
from routes.chat import router as chat_router

app = FastAPI()
app.include_router(auth_router, prefix="/users", tags=["auth"])
app.include_router(chat_router, prefix="/chat-app", tags=["chat"])

@app.get("/")
async def index():
    return {"message": "Hello World"}