from datetime import datetime, timedelta, timezone
from typing import Annotated
from bson import ObjectId
from fastapi import Depends, HTTPException, status, Request, Response, Cookie, Body
from jose import JWTError, jwt
from passlib.context import CryptContext
from passlib.hash import hex_sha256
from utils.dbUtils import get_client
from pymongo import MongoClient
import os
import secrets
from models.auth import TokenData, UserResponse, UserRegister, UserInDB, UserLoginType
from models.responses import (
    RegisterAndCurrentUserResponse,
    EmailVerificationResponse,
    EmailVerificationData,
    RefreshTokenResponse,
    LoginData,
    LoginResponse,
    BaseResponse,
)
from utils.mail import send_email, email_verification_content, forgot_password_content

ACCESS_TOKEN_SECRET = os.environ.get("ACCESS_TOKEN_SECRET")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES"))
REFRESH_TOKEN_SECRET = os.environ.get("REFRESH_TOKEN_SECRET")
ALGORITHM = "HS256"
REFRESH_TOKEN_EXPIRY = int(os.environ.get("REFRESH_TOKEN_EXPIRY"))


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_and_return_token(accessToken: Annotated[str | None, Cookie()] = None):
    if not accessToken:
        raise HTTPException(status_code=401, detail="Unauthorized request")
    try:
        decoded_token = jwt.decode(
            accessToken, ACCESS_TOKEN_SECRET, algorithms=[ALGORITHM]
        )
    except JWTError as error:
        raise HTTPException(
            status_code=401, detail=str(error) or "Invalid access token"
        )
    return decoded_token


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def authenticate_user(db, username: str, password: str):
    user = db.users.find_one({"username": username})
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def create_token(data: dict, key: str, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, key, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: dict, db: MongoClient) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
    )
    username: str = token.get("username")
    if username is None:
        raise credentials_exception
    user = db.users.find_one({"username": username})
    if user is None:
        raise credentials_exception
    return RegisterAndCurrentUserResponse(
        message="User retrieved successfully",
        statusCode=200,
        success=True,
        data=UserResponse(**user),
    )


def generate_temporary_token():
    unhashed_token = secrets.token_hex(20)
    hashed_token = hex_sha256.hash(unhashed_token)
    token_expiry = datetime.now() + timedelta(minutes=20)

    return unhashed_token, hashed_token, token_expiry


async def generate_access_token(data: dict):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_token(data, ACCESS_TOKEN_SECRET,expires_delta=access_token_expires)
    return access_token


async def generate_refresh_token(data: dict):
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRY)
    refresh_token = create_token(data, REFRESH_TOKEN_SECRET, expires_delta=refresh_token_expires)
    return refresh_token


async def register_user(
    user_request: UserRegister, request: Request, db: MongoClient
) -> UserResponse:
    users_collection = db.users

    if users_collection.find_one(
        {"$or": [{"username": user_request.username}, {"email": user_request.email}]}
    ):
        raise HTTPException(status_code=409, detail="Username or email already exists")

    hashed_password = get_password_hash(user_request.password)
    unhashed_token, hashed_token, token_expiry = generate_temporary_token()

    user_data = user_request.model_dump()
    user_data.update(
        {
            "password": hashed_password,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
            "emailVerificationToken": hashed_token,
            "emailVerificationExpiry": token_expiry,
            "loginType": UserLoginType.EMAIL_PASSWORD,
            "isEmailVerified": False,
            "refreshToken": None,
            "forgotPasswordToken": None,
            "forgotPasswordExpiry": None,
            "avatar": {
                "_id": ObjectId(),
                "url": "https://via.placeholder.com/200x200.png",
                "localPath": "",
            }
        }
    )

    users_collection.insert_one(user_data)

    verify_email_url = f"{request.base_url}users/verify-email/{unhashed_token}"
    html_content = email_verification_content(user_request.username, verify_email_url)
    await send_email(user_request.email, "Verify Your Email", html_content)

    # Remove sensitive data before returning the user object
    user_data.pop("emailVerificationToken", None)
    user_data.pop("emailVerificationExpiry", None)
    user_data.pop("refreshToken", None)

    user_data.update({"password": user_request.password})
    user_response = UserResponse(**user_data)
    return RegisterAndCurrentUserResponse(
        message="User registered successfully",
        statusCode=201,
        success=True,
        data=user_response,
    )


async def login_user(
    login_request: UserRegister,
    response: Response,
    db: MongoClient,
) -> LoginResponse:
    if not login_request.username and not login_request.email:
        raise HTTPException(status_code=400, detail="Username or email is required")

    user = db.users.find_one({"username": login_request.username})

    if not user:
        raise HTTPException(status_code=404, detail="User does not exist")

    is_password_valid = verify_password(login_request.password, user["password"])
    if not is_password_valid:
        raise HTTPException(status_code=401, detail="Invalid user credentials")

    user_id = str(user.get("_id"))
    access_token = await generate_access_token(
        {
            "_id": user_id,
            "username": user.get("username"),
            "email": user.get("email"),
            "role": user.get("role"),
        }
    )
    refresh_token = await generate_refresh_token(
        {
            "_id": user_id,
            "username": user.get("username"),
            "email": user.get("email"),
            "role": user.get("role"),
        }
    )

    response.set_cookie(
        key="accessToken", value=access_token, httponly=True, samesite='none'
    )
    response.set_cookie(
        key="refreshToken", value=refresh_token, httponly=True, samesite='none'
    )
    
    db.users.update_one({"_id": ObjectId(user_id)}, {"$set": {"refreshToken": refresh_token}})

    user.pop("password", None)
    user.pop("refreshToken", None)

    return LoginResponse(
        message="User logged in successfully",
        statusCode=200,
        success=True,
        data=LoginData(
            user=UserResponse(**user),
            accessToken=access_token,
            refreshToken=refresh_token,
        ),
    )


async def verify_email(
    verification_token: str, db: MongoClient
) -> EmailVerificationResponse:
    hashed_token = hex_sha256.hash(verification_token)

    user = db.users.find_one(
        {
            "emailVerificationToken": hashed_token,
            "emailVerificationExpiry": {"$gt": datetime.now()},
        }
    )
    if not user:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    db.users.update_one(
        {"emailVerificationToken": hashed_token},
        {
            "$set": {
                "isEmailVerified": True,
                "emailVerificationToken": None,
                "emailVerificationExpiry": None,
            }
        },
    )

    return EmailVerificationResponse(
        message="Email verified successfully",
        statusCode=200,
        success=True,
        data=EmailVerificationData(isEmailVerified=True),
    )


async def refresh_access_token(
    db: MongoClient,
    response: Response,
    refresh_token: str | None = None,
):
    refresh_token = refresh_token or Body()
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Unauthorized request")

    try:
        decoded_token = jwt.decode(
            refresh_token,
            os.environ.get("REFRESH_TOKEN_SECRET"),
            algorithms=[ALGORITHM],
        )
        user_id = decoded_token.get("_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user = db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        if refresh_token != user.get("refreshToken"):
            raise HTTPException(
                status_code=401, detail="Refresh token is expired or used"
            )

        access_token = await generate_access_token(
            {
                "_id": user_id,
                "username": user.get("username"),
                "email": user.get("email"),
                "role": user.get("role"),
            }
        )
        refresh_token = await generate_refresh_token(
            {
                "_id": user_id,
                "username": user.get("username"),
                "email": user.get("email"),
                "role": user.get("role"),
            }
        )

        db.users.update_one(
            {"username": decoded_token["username"]}, {"$set": {"refreshToken": refresh_token}}
        )
        data = {"accessToken": access_token, "refreshToken": refresh_token}

        response.set_cookie(
            key="accessToken",
            value=access_token,
            httponly=True,
            secure=True,
            samesite="Lax",
        )
        response.set_cookie(
            key="refreshToken",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="Lax",
        )

        return RefreshTokenResponse(
            statusCode=200, data=data, message="Access token refreshed", success=True
        )
    except JWTError as error:
        raise HTTPException(
            status_code=401, detail=str(error) or "Invalid refresh token"
        )


async def forgot_password(
    email: str, request: Request, db: MongoClient = Depends(get_client)
) -> BaseResponse:
    user = db.users.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    unHashedToken, hashedToken, tokenExpiry = generate_temporary_token()

    db.users.update_one(
        {"email": email},
        {
            "$set": {
                "forgotPasswordToken": hashedToken,
                "forgotPasswordExpiry": tokenExpiry,
            }
        },
    )
    # need to change the url when the frontend is up
    forgotPasswordUrl = f"{request.base_url}users/reset-password/{unHashedToken}"
    htmlContent = forgot_password_content(user["username"], forgotPasswordUrl)
    await send_email(user["email"], "Reset Your Password", htmlContent)
    return BaseResponse(
        message="Forgot password email sent successfully",
        statusCode=200,
        success=True,
    )


async def reset_password(
    resetPasswordToken: str, newPassword: str, db: MongoClient = Depends(get_client)
):
    hashedToken = hex_sha256.hash(resetPasswordToken)
    user = db.users.find_one(
        {
            "forgotPasswordToken": hashedToken,
            "forgotPasswordExpiry": {"$gt": datetime.now()},
        }
    )
    if not user:
        raise HTTPException(status_code=400, detail="Invalid reset password token")

    hashedPassword = get_password_hash(newPassword)

    db.users.update_one(
        {"forgotPasswordToken": hashedToken},
        {
            "$set": {
                "password": hashedPassword,
                "forgotPasswordToken": None,
                "forgotPasswordExpiry": None,
            }
        },
    )

    return BaseResponse(
        message="Password reset successfully",
        statusCode=200,
        success=True,
    )


async def logout_user(
    token: dict,
    response: Response,
    db: MongoClient,
):
    updated_user = db.users.update_one(
        {"_id": token["_id"]}, {"$set": {"refreshToken": ""}}
    )
    if not updated_user:
        raise HTTPException(status_code=400, detail="User not found")

    cookie_options = {"httponly": True, "secure": True, "samesite": "Lax"}
    response.delete_cookie("accessToken", **cookie_options)
    response.delete_cookie("refreshToken", **cookie_options)
    return BaseResponse(
        message="User logged out successfully",
        statusCode=200,
        success=True,
    )


async def change_password(
    token: dict,
    old_password: str,
    new_password: str,
    db: MongoClient = Depends(get_client),
):
    user = db.users.find_one({"_id": ObjectId(token["_id"])})
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    is_password_valid = verify_password(old_password, user["password"])
    if not is_password_valid:
        raise HTTPException(status_code=401, detail="Invalid user credentials")

    hashedPassword = get_password_hash(new_password)

    db.users.update_one(
        {"_id": ObjectId(token["_id"])}, {"$set": {"password": hashedPassword}}
    )

    return BaseResponse(
        message="Password changed successfully",
        statusCode=200,
        success=True,
    )


async def resend_email_verification(
    token: dict,
    request: Request,
    db: MongoClient,
):
    user = db.users.find_one({"_id": ObjectId(token["_id"])})
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    unhashedToken, hashedToken, tokenExpiry = generate_temporary_token()

    db.users.update_one(
        {"_id": ObjectId(token["_id"])},
        {
            "$set": {
                "emailVerificationToken": hashedToken,
                "emailVerificationExpiry": tokenExpiry,
            }
        },
    )

    verifyEmailUrl = f"{request.base_url}users/verify-email/{unhashedToken}"
    htmlContent = email_verification_content(user["username"], verifyEmailUrl)
    await send_email(user["email"], "Verify Your Email", htmlContent)

    return BaseResponse(
        message="Verification email sent successfully",
        statusCode=200,
        success=True,
    )
