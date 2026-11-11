"""User and organisation response schemas."""

from app.schemas.common import ORMModel


class OrganisationOut(ORMModel):
    id: int
    name: str
    slug: str


class UserSummary(ORMModel):
    id: int
    full_name: str
    email: str
    role: str


class UserOut(UserSummary):
    organisation_id: int
    organisation: OrganisationOut
    is_active: bool
