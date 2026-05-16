from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_database_session
from app.core.security import create_access_token
from app.crud.user import authenticate_user, create_user, get_user_by_email
from app.schemas.user import (
    AccessTokenResponse,
    LoginRequest,
    UserPublicResponse,
    UserRegisterRequest,
)

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    "/register",
    response_model=UserPublicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register_new_user(
    register_request: UserRegisterRequest,
    database_session: Annotated[Session, Depends(get_database_session)],
) -> UserPublicResponse:
    if get_user_by_email(database_session, register_request.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )
    created_user = create_user(database_session, register_request)
    return UserPublicResponse.model_validate(created_user)


@auth_router.post(
    "/login",
    response_model=AccessTokenResponse,
    summary="Exchange email + password for a JWT access token",
)
def log_in_existing_user(
    login_request: LoginRequest,
    database_session: Annotated[Session, Depends(get_database_session)],
) -> AccessTokenResponse:
    authenticated_user = authenticate_user(
        database_session, login_request.email, login_request.password
    )
    if authenticated_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    signed_jwt = create_access_token(subject=authenticated_user.email)
    return AccessTokenResponse(access_token=signed_jwt)
