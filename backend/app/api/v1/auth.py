"""Authentication endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import CurrentUser
from app.core.config import settings
from app.core.security import create_access_token, verify_password
from app.core.time import utcnow
from app.db.models import User
from app.db.session import get_db
from app.schemas.auth import LoginRequest, LoginResponse
from app.schemas.users import UserOut
from app.services.audit import record_audit

router = APIRouter(prefix="/auth", tags=["authentication"])
DbSession = Annotated[Session, Depends(get_db)]


@router.post("/login", response_model=LoginResponse, summary="Sign in and receive a JWT")
def login(payload: LoginRequest, db: DbSession) -> LoginResponse:
    """Authenticate with email and password.

    Failures return one generic message so account existence is not disclosed.
    Successful and failed attempts are written to the audit chain.
    """

    user = db.scalar(
        select(User)
        .options(selectinload(User.organisation))
        .where(User.email == payload.email)
    )
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email or password is incorrect.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if user is None or not verify_password(user.password_hash, payload.password):
        if user is not None:
            record_audit(
                db,
                action="auth.login_failed",
                actor_id=user.id,
                organisation_id=user.organisation_id,
                detail={"reason": "invalid_credentials"},
            )
            db.commit()
        raise credentials_error

    if not user.is_active:
        record_audit(
            db,
            action="auth.login_blocked",
            actor_id=user.id,
            organisation_id=user.organisation_id,
            detail={"reason": "inactive_account"},
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This account is disabled. Contact your administrator.",
        )

    user.last_login_at = utcnow()
    access_token = create_access_token(user)
    record_audit(
        db,
        action="auth.login",
        actor_id=user.id,
        organisation_id=user.organisation_id,
        detail={"role": user.role},
    )
    db.commit()
    db.refresh(user)

    return LoginResponse(
        access_token=access_token,
        expires_in=settings.access_token_expire_minutes * 60,
        user=UserOut.model_validate(user),
    )


@router.get("/me", response_model=UserOut, summary="Return the signed-in profile")
def me(current_user: CurrentUser) -> UserOut:
    """Return the authenticated user, organisation and role."""

    return UserOut.model_validate(current_user)
