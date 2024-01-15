from fastapi import APIRouter

router = APIRouter()

router.get("/")
async def index():
    return {"message": "Hello World"}

@router.get("/chat")
async def chat():
    return {"message": "Chat"}