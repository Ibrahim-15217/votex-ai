"""Persistence and orchestration for explainable AI analyses."""

from __future__ import annotations

import logging
from time import perf_counter

from sqlalchemy import exists, select
from sqlalchemy.orm import Session

from app.ai import analyse_incident as run_engine
from app.core.time import utcnow
from app.db.models import Incident, IncidentAnalysis, IncidentEvent, User
from app.services.audit import record_audit
from app.services.correlation import sync_incident_indicators

logger = logging.getLogger(__name__)


def _status_for(result) -> str:
    return "complete" if result.model_available else "degraded"


def analyse_and_store(
    db: Session,
    incident: Incident,
    actor: User | None,
    *,
    automatic: bool = False,
) -> IncidentAnalysis:
    """Run the hybrid engine, persist a new analysis row and audit it.

    The caller owns transaction boundaries through this function. Analysis
    failure never destroys the report: the incident keeps a failure state and
    the API can retry.
    """

    started = perf_counter()
    try:
        result = run_engine(
            title=incident.title,
            description=incident.description,
            category=incident.category,
            channel=incident.channel,
            reported_url=incident.reported_url,
            state=incident.state,
        )
    except Exception:
        incident.ai_status = "failed"
        incident.updated_at = utcnow()
        db.add(
            IncidentEvent(
                incident_id=incident.id,
                actor_id=actor.id if actor else None,
                event_type="ai_failed",
                message="AI analysis failed. The report is unchanged and can be re-analysed.",
                event_metadata={"automatic": automatic},
                created_at=utcnow(),
            )
        )
        db.commit()
        logger.exception("AI analysis failed for incident %s", incident.id)
        raise

    latency_ms = int((perf_counter() - started) * 1000)
    status = _status_for(result)

    record = IncidentAnalysis(
        incident_id=incident.id,
        organisation_id=incident.organisation_id,
        requested_by_id=actor.id if actor else None,
        status=status,
        model_version=result.model_version,
        ruleset_version=result.ruleset_version,
        classification=result.classification,
        risk_score=result.risk_score,
        confidence=result.confidence,
        url_score=result.url_score,
        nlp_score=result.nlp_score,
        ml_score=result.ml_score,
        indicator_score=result.indicator_score,
        summary=result.summary,
        reasons_json=result.reasons,
        indicators_json=result.indicators,
        factors_json=result.factors,
        features_json=result.features,
        warnings_json=result.warnings,
        latency_ms=latency_ms,
        created_at=utcnow(),
    )
    db.add(record)

    incident.risk_score = result.risk_score
    incident.classification = result.classification
    incident.ai_status = status
    incident.updated_at = utcnow()

    db.add(
        IncidentEvent(
            incident_id=incident.id,
            actor_id=actor.id if actor else None,
            event_type="ai_analysis",
            message=(
                f"AI analysis complete: {result.classification.replace('_', ' ')} "
                f"({result.risk_score:.1f}/100, {result.confidence * 100:.0f}% confidence)."
            ),
            event_metadata={
                "classification": result.classification,
                "risk_score": result.risk_score,
                "confidence": result.confidence,
                "model_version": result.model_version,
                "ruleset_version": result.ruleset_version,
                "automatic": automatic,
            },
            created_at=utcnow(),
        )
    )
    record_audit(
        db,
        action="incident.analysed",
        actor_id=actor.id if actor else None,
        organisation_id=incident.organisation_id,
        resource_type="incident",
        resource_id=incident.id,
        detail={
            "reference": incident.reference,
            "classification": result.classification,
            "risk_score": result.risk_score,
            "confidence": result.confidence,
            "model_version": result.model_version,
            "ruleset_version": result.ruleset_version,
            "automatic": automatic,
        },
    )
    db.commit()
    db.refresh(record)

    # Phase 3: derive correlation links from the same stored report. A failure
    # here must never remove the completed analysis.
    try:
        sync_incident_indicators(db, incident, actor)
        db.refresh(record)
    except Exception:
        db.rollback()
        logger.exception("Indicator correlation failed for incident %s", incident.id)
    return record


def backfill_missing_analyses(db: Session) -> int:
    """Analyse incidents created before Phase 2 shipped.

    Safe to call on every start: incidents that already have an analysis are
    skipped. Returns the number of newly analysed incidents.
    """

    incidents = list(
        db.scalars(
            select(Incident).where(
                ~exists().where(IncidentAnalysis.incident_id == Incident.id)
            )
        ).all()
    )
    analysed = 0
    for incident in incidents:
        # Analysis is derived from synthetic demo data; attribute it to the
        # original reporter so the audit trail stays internally consistent.
        actor = db.get(User, incident.reporter_id)
        try:
            analyse_and_store(db, incident, actor, automatic=True)
            analysed += 1
        except Exception:  # keep the API available even if one report fails
            db.rollback()
            logger.exception("Backfill analysis failed for incident %s", incident.id)
    return analysed
