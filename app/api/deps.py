from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_database_session
from app.core.security import JWTError, decode_access_token
from app.crud.user import get_user_by_email
from app.models.user import User

# The tokenUrl makes Swagger's "Authorize" button work — it points at the login
# endpoint that returns the access token.
oauth2_bearer_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_authenticated_user(
    access_token: Annotated[str, Depends(oauth2_bearer_scheme)],
    database_session: Annotated[Session, Depends(get_database_session)],
) -> User:
    """FastAPI dependency that resolves the bearer token to a User row, or 401s."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_claims = decode_access_token(access_token)
    except JWTError as exc:
        raise credentials_exception from exc

    user_email = token_claims.get("sub")
    if not isinstance(user_email, str):
        raise credentials_exception

    authenticated_user = get_user_by_email(database_session, user_email)
    if authenticated_user is None:
        raise credentials_exception

    return authenticated_user
