"""Schemas for resilience assessments and synthetic exercises."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.core.resilience import CONTROL_BY_KEY, CONTROL_KEYS
from app.schemas.common import ORMModel, UTCDateTime
from app.schemas.users import UserSummary

Maturity = Literal[0, 1, 2, 3, 4]
ReadinessBand = Literal["fragile", "developing", "resilient"]
FindingSeverity = Literal["critical", "high", "medium", "low"]
RemediationStatus = Literal["open", "in_progress", "resolved", "accepted"]
ExerciseStatus = Literal["running", "completed"]
TaskStatus = Literal["pending", "in_progress", "done", "skipped"]


class ControlOut(BaseModel):
    key: str
    category: str
    title: str
    detail: str
    remediation: str


class QuestionnaireOut(BaseModel):
    controls: list[ControlOut]
    maturity_levels: dict[int, str]
    scoring_note: str


class AssessmentCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=3, max_length=160)
    notes: str | None = Field(default=None, max_length=2_000)
    answers: dict[str, Maturity]

    @field_validator("answers")
    @classmethod
    def answers_cover_every_control(cls, value: dict[str, int]) -> dict[str, int]:
        missing = [key for key in CONTROL_KEYS if key not in value]
        unknown = [key for key in value if key not in CONTROL_BY_KEY]
        if missing:
            raise ValueError(
                "Every control needs an answer. Missing: " + ", ".join(missing)
            )
        if unknown:
            raise ValueError("Unknown control keys: " + ", ".join(unknown))
        return value


class FindingOut(ORMModel):
    id: int
    category: str
    title: str
    detail: str
    severity: FindingSeverity
    remediation_status: RemediationStatus
    owner: str | None = None
    due_date: UTCDateTime | None = None
    created_at: UTCDateTime
    updated_at: UTCDateTime


class FindingUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    remediation_status: RemediationStatus | None = None
    owner: str | None = Field(default=None, max_length=160)
    due_date: datetime | None = None
    note: str | None = Field(default=None, max_length=1_000)


class AssessmentListItem(ORMModel):
    id: str
    title: str
    status: str
    score: float
    band: ReadinessBand
    assessment_date: UTCDateTime
    created_at: UTCDateTime
    total_findings: int
    open_findings: int


class AssessmentDetail(AssessmentListItem):
    notes: str
    summary: str
    answers: dict[str, int]
    controls: list[ControlOut]
    findings: list[FindingOut]
    created_by: UserSummary | None = None


class ResilienceSummary(BaseModel):
    total_assessments: int
    latest: AssessmentListItem | None = None
    total_findings: int
    open_findings: int
    resolved_findings: int
    open_by_severity: dict[str, int]


class ExerciseCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, max_length=160)


class ExerciseTaskOut(ORMModel):
    id: int
    sequence: int
    title: str
    description: str
    expected_action: str
    status: TaskStatus
    notes: str
    completed_at: UTCDateTime | None = None
    completed_by: UserSummary | None = None


class ExercisePerformance(BaseModel):
    tasks_total: int
    tasks_done: int
    tasks_skipped: int
    tasks_resolved: int
    completion_pct: float
    elapsed_seconds: int
    grade: Literal["ready", "developing", "needs_review"]
    note: str


class ExerciseListItem(ORMModel):
    id: str
    scenario_key: str
    title: str
    summary: str
    status: ExerciseStatus
    started_at: UTCDateTime
    completed_at: UTCDateTime | None = None
    created_at: UTCDateTime
    tasks_total: int
    tasks_done: int


class ExerciseDetail(ExerciseListItem):
    tasks: list[ExerciseTaskOut]
    performance: ExercisePerformance
    created_by: UserSummary | None = None


class ExerciseTaskUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    status: TaskStatus
    notes: str | None = Field(default=None, max_length=1_000)
