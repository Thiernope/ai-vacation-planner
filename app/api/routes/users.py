from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.deps import get_current_authenticated_user
from app.models.user import User
from app.schemas.user import UserPublicResponse

users_router = APIRouter(prefix="/users", tags=["users"])


@users_router.get(
    "/me",
    response_model=UserPublicResponse,
    summary="Return the profile of the currently logged-in user",
)
def read_current_user_profile(
    current_user: Annotated[User, Depends(get_current_authenticated_user)],
) -> UserPublicResponse:
    return UserPublicResponse.model_validate(current_user)
