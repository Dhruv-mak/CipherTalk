from fastapi import APIRouter

router = APIRouter()

@router.get("/login")
async def login():
    return {"message": "Login"}

@router.get("/register")
async def register():
    return {"message": "Hello World auth"}