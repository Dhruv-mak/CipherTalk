from fastapi import APIRouter, HTTPException, Depends, status, Request
from models.auth import UserRequest, UserResponse, Token
from models.responses import (
    RegisterResponse,
    EmailVerificationResponse,
    LoginResponse,
    RefreshTokenResponse,
    BaseResponse,
)
from db.dbUtils import get_client
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from pymongo import MongoClient
from datetime import timedelta
import os
from utils.auth import (
    register_user,
    authenticate_user,
    create_access_token,
    get_current_user,
    login_user,
    refresh_access_token,
    verify_email,
    forgot_password,
    reset_password,
    logout_user,
    change_password,
    resend_email_verification,
)

router = APIRouter()


# unsecured routes
@router.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[MongoClient, Depends(get_client)],
) -> Token:
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(
        minutes=os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES")
    )
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/register")
async def register(
    user: UserRequest, request: Request, db=Depends(get_client)
) -> RegisterResponse:
    return await register_user(user, request, db)


@router.post("/login")
async def login(
    user: UserRequest, db: MongoClient = Depends(get_client)
) -> LoginResponse:
    return await login_user(user, db)


@router.get("/verify-email/{verification_token}")
async def verify(
    verification_token: str, db: MongoClient = Depends(get_client)
) -> EmailVerificationResponse:
    if not verification_token:
        raise HTTPException(
            status_code=400, detail="Email verification token is required"
        )
    return await verify_email(verification_token, db)


@router.post("/refresh-token")
async def refresh_token(
    current_user: Annotated[UserResponse, Depends(get_current_user)]
) -> RefreshTokenResponse:
    return await refresh_access_token(current_user)


@router.post("/forgot-password")
async def forgot(
    email: str, request: Request, db: MongoClient = Depends(get_client)
) -> EmailVerificationResponse:
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
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    db: Annotated[MongoClient, Depends(get_client)],
) -> BaseResponse:
    return logout_user(current_user, db)


@router.get("/current-user", response_model=UserResponse)
async def read_users_me(
    current_user: Annotated[UserResponse, Depends(get_current_user)]
):
    return current_user

@router.post("/change-password")
async def change(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    old_password: str,
    new_password: str,
    db: Annotated[MongoClient, Depends(get_client)],
) -> str:
    return change_password(current_user, old_password, new_password, db)

@router.post("/resent-email-verification")
async def re_verify_email(
    current_user: Annotated[UserResponse, Depends(get_current_user)],
    request: Request,
    db: Annotated[MongoClient, Depends(get_client)],
) -> EmailVerificationResponse:
    return resend_email_verification(current_user, request, db)