"""Organisation-scoped user directory."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import AnalystUser
from app.db.models import User
from app.db.session import get_db
from app.schemas.users import UserSummary

router = APIRouter(prefix="/users", tags=["users"])
DbSession = Annotated[Session, Depends(get_db)]


@router.get(
    "",
    response_model=list[UserSummary],
    summary="List active users in your organisation",
)
def list_users(current_user: AnalystUser, db: DbSession) -> list[User]:
    """Return the active responders available for assignment.

    Only administrators and analysts can read the directory, and the query is
    hard-scoped to the caller's organisation.
    """

    return list(
        db.scalars(
            select(User)
            .where(
                User.organisation_id == current_user.organisation_id,
                User.is_active.is_(True),
            )
            .order_by(User.role, User.full_name)
        ).all()
    )
