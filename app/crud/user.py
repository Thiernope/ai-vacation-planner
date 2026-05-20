from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models.user import User
from app.schemas.user import UserRegisterRequest


def get_user_by_email(database_session: Session, email_address: str) -> User | None:
    """Return the user with the given email, or None if no such user exists."""
    statement = select(User).where(User.email == email_address)
    return database_session.scalars(statement).first()


def create_user(database_session: Session, register_request: UserRegisterRequest) -> User:
    """Persist a new user with a freshly hashed password and return the ORM row."""
    new_user = User(
        email=register_request.email,
        full_name=register_request.full_name,
        hashed_password=hash_password(register_request.password),
    )
    database_session.add(new_user)
    database_session.commit()
    database_session.refresh(new_user)
    return new_user


def authenticate_user(
    database_session: Session, email_address: str, plain_text_password: str
) -> User | None:
    """Return the user if email + password are valid, else None."""
    candidate_user = get_user_by_email(database_session, email_address)
    if candidate_user is None:
        return None
    if not verify_password(plain_text_password, candidate_user.hashed_password):
        return None
    return candidate_user
