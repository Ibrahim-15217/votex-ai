"""Shared schema helpers."""

from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, PlainSerializer

from app.core.time import to_iso_utc

UTCDateTime = Annotated[
    datetime,
    PlainSerializer(to_iso_utc, return_type=str, when_used="json"),
]


class ORMModel(BaseModel):
    """Base model for objects read from SQLAlchemy."""

    model_config = ConfigDict(from_attributes=True)
