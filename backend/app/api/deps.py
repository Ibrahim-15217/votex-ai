"""Shared API dependencies: bearer authentication and role checks."""

from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.models import User
from app.db.session import get_db

bearer_scheme = HTTPBearer(auto_error=False, description="JWT access token issued by /auth/login")

_CREDENTIALS_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Your session is missing or has expired. Sign in again.",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    """Resolve the signed-in user from a validated bearer token."""

    if credentials is None:
        raise _CREDENTIALS_ERROR

    try:
        payload = decode_access_token(credentials.credentials)
    except jwt.InvalidTokenError as exc:  # covers expiry, signature and claims
        raise _CREDENTIALS_ERROR from exc

    subject = payload.get("sub")
    try:
        user_id = int(subject)
    except (TypeError, ValueError) as exc:
        raise _CREDENTIALS_ERROR from exc

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise _CREDENTIALS_ERROR
    if payload.get("org") != user.organisation_id:
        raise _CREDENTIALS_ERROR
    return user


def require_roles(*roles: str) -> Callable[..., User]:
    """Return a dependency that allows only the listed roles."""

    def dependency(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action.",
            )
        return current_user

    return dependency


CurrentUser = Annotated[User, Depends(get_current_user)]
AnalystUser = Annotated[User, Depends(require_roles("admin", "analyst"))]
AdminUser = Annotated[User, Depends(require_roles("admin"))]
