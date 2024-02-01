from fastapi import APIRouter, HTTPException, Depends, status, Request, Response, Cookie
from models.auth import UserRegister, UserResponse, Token, UserLogin
from models.responses import (
    RegisterAndCurrentUserResponse,
    EmailVerificationResponse,
    LoginResponse,
    RefreshTokenResponse,
    BaseResponse
)
from utils.dbUtils import get_client
from typing import Annotated
from pymongo import MongoClient
from datetime import timedelta
from utils.auth import (
    register_user,
    get_current_user,
    login_user,
    refresh_access_token,
    verify_email,
    forgot_password,
    reset_password,
    logout_user,
    change_password,
    resend_email_verification,
    verify_and_return_token
)
router = APIRouter()


@router.post("/register")
async def register(
    user: UserRegister, request: Request, db: Annotated[MongoClient, Depends(get_client)]
) -> RegisterAndCurrentUserResponse:
    return await register_user(user, request, db)


@router.post("/login")
async def login(
    user: UserLogin, response: Response, db: Annotated[MongoClient, Depends(get_client)]
) -> LoginResponse:
    return await login_user(user, response, db)


@router.get("/verify-email/{verification_token}")
async def verify(
    verification_token: str,
    db: Annotated[MongoClient, Depends(get_client)]
) -> EmailVerificationResponse:
    if not verification_token:
        raise HTTPException(
            status_code=400, detail="Email verification token is required"
        )
    return await verify_email(verification_token, db)


@router.post("/refresh-token")
async def refresh_token(
    db: Annotated[MongoClient, Depends(get_client)],
    response: Response,
    refreshToken: str = Cookie(None),
) -> RefreshTokenResponse:
    return await refresh_access_token(db, response, refreshToken)


@router.post("/forgot-password")
async def forgot(
    email: str, request: Request, db: Annotated[MongoClient, Depends(get_client)]
) -> BaseResponse:
    return await forgot_password(email, request, db)


@router.post("/reset-password/{reset_token}")
async def reset_password(
    reset_token: str, password: str, db: MongoClient = Depends(get_client)
) -> EmailVerificationResponse:
    if not reset_token:
        raise HTTPException(status_code=400, detail="Reset token is required")
    if not password:
        raise HTTPException(status_code=400, detail="Password is required")
    return await reset_password(reset_token, password, db)


# secured routes
@router.post("/logout")
async def logout(
    token: Annotated[dict, Depends(verify_and_return_token)],
    response: Response,
    db: Annotated[MongoClient, Depends(get_client)],
) -> BaseResponse:
    return await logout_user(token, response, db)


@router.get("/current-user")
async def read_users_me(
    token: Annotated[dict, Depends(verify_and_return_token)],
    db: Annotated[MongoClient, Depends(get_client)],
) -> RegisterAndCurrentUserResponse:
    return await get_current_user(token, db)

@router.post("/change-password")
async def change(
    old_password: str,
    new_password: str,
    token: Annotated[dict, Depends(verify_and_return_token)],
    db: Annotated[MongoClient, Depends(get_client)],
) -> BaseResponse:
    return await change_password(token, old_password, new_password, db)

@router.post("/resent-email-verification")
async def re_verify_email(
    token: Annotated[dict, Depends(verify_and_return_token)],
    request: Request,
    db: Annotated[MongoClient, Depends(get_client)],
) -> BaseResponse:
    return await resend_email_verification(token, request, db)
