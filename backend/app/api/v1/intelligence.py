"""Indicator search, related-incident correlation and dashboard endpoints."""

from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import AdminUser, AnalystUser
from app.db.session import get_db
from app.schemas.intelligence import (
    DashboardResponse,
    IndicatorDetail,
    IndicatorKind,
    IndicatorPage,
)
from app.services import correlation as correlation_service

router = APIRouter(tags=["intelligence"])
DbSession = Annotated[Session, Depends(get_db)]


def _csv_response(content: str, filename: str) -> Response:
    return Response(
        content=content.encode("utf-8-sig"),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
        },
    )


@router.get(
    "/indicators",
    response_model=IndicatorPage,
    summary="Search correlated indicators",
)
def list_indicators(
    current_user: AnalystUser,
    db: DbSession,
    q: Annotated[str | None, Query(max_length=160)] = None,
    kind: IndicatorKind | None = None,
    page: Annotated[int, Query(ge=1, le=10_000)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> IndicatorPage:
    """Search URLs, domains, IPs and file hashes inside the caller's tenant."""

    return correlation_service.indicator_page(
        db, current_user, query=q, kind=kind, page=page, page_size=page_size
    )


@router.get(
    "/indicators/export",
    summary="Export indicators as CSV",
    response_class=Response,
)
def export_indicators(
    current_user: AnalystUser,
    db: DbSession,
    q: Annotated[str | None, Query(max_length=160)] = None,
    kind: IndicatorKind | None = None,
) -> Response:
    """Export every matching indicator. Reporters never reach this route."""

    items: list[dict] = []
    page = 1
    while True:
        batch = correlation_service.indicator_page(
            db, current_user, query=q, kind=kind, page=page, page_size=500
        )
        items.extend(batch["items"])
        if not batch["items"] or len(items) >= batch["total"]:
            break
        page += 1

    content = correlation_service.indicator_csv(items)
    correlation_service.record_export(
        db, current_user, scope="indicators", row_count=len(items)
    )
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    return _csv_response(content, f"votex-indicators-{stamp}.csv")


@router.get(
    "/indicators/{indicator_id}",
    response_model=IndicatorDetail,
    summary="Indicator detail and linked incidents",
)
def get_indicator(
    indicator_id: int, current_user: AnalystUser, db: DbSession
) -> IndicatorDetail:
    """Return one indicator plus the visible incidents that share it."""

    detail = correlation_service.indicator_detail(db, current_user, indicator_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Indicator not found."
        )
    return detail


@router.get(
    "/dashboards/organisation",
    response_model=DashboardResponse,
    summary="Organisation threat dashboard",
)
def organisation_dashboard(current_user: AnalystUser, db: DbSession) -> DashboardResponse:
    """Exact counts for the caller's organisation, with trend and severity charts."""

    return correlation_service.organisation_dashboard(db, current_user)


@router.get(
    "/dashboards/national",
    response_model=DashboardResponse,
    summary="National aggregate dashboard (k >= 5)",
)
def national_dashboard(current_user: AdminUser, db: DbSession) -> DashboardResponse:
    """Aggregate every tenant with k-anonymity suppression applied in SQL."""

    return correlation_service.national_dashboard(db, current_user)


@router.get(
    "/dashboards/organisation/export",
    summary="Export the organisation dashboard as CSV",
    response_class=Response,
)
def export_organisation_dashboard(current_user: AnalystUser, db: DbSession) -> Response:
    """Export organisation counts. Small cells are exact for the owning tenant."""

    dashboard = correlation_service.organisation_dashboard(db, current_user)
    content = correlation_service.dashboard_csv(dashboard)
    correlation_service.record_export(
        db,
        current_user,
        scope="organisation",
        row_count=len(content.splitlines()) - 1,
        suppressed_cells=dashboard["summary"]["suppressed_cells"],
    )
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    return _csv_response(content, f"votex-organisation-dashboard-{stamp}.csv")


@router.get(
    "/dashboards/national/export",
    summary="Export the suppressed national dashboard as CSV",
    response_class=Response,
)
def export_national_dashboard(current_user: AdminUser, db: DbSession) -> Response:
    """Export national aggregates; suppressed raw values are never written."""

    dashboard = correlation_service.national_dashboard(db, current_user)
    content = correlation_service.dashboard_csv(dashboard)
    correlation_service.record_export(
        db,
        current_user,
        scope="national",
        row_count=len(content.splitlines()) - 1,
        suppressed_cells=dashboard["summary"]["suppressed_cells"],
    )
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    return _csv_response(content, f"votex-national-dashboard-{stamp}.csv")
