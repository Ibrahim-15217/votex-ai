"""Deterministic demo data for the Votex AI prototype.

Everything here is synthetic. Two tenant organisations, five demo accounts,
eight incidents with realistic timelines, one hashed evidence file and a valid
audit chain are created once on first start.
"""

from __future__ import annotations

from datetime import timedelta
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import hash_password
from app.core.time import utcnow
from app.db.models import (
    Evidence,
    Exercise,
    Incident,
    IncidentEvent,
    Organisation,
    ResilienceAssessment,
    ResilienceFinding,
    User,
)
from app.db.session import SessionLocal
from app.schemas.resilience import (
    AssessmentCreate,
    ExerciseCreate,
    ExerciseTaskUpdate,
    FindingUpdate,
)
from app.services import resilience as resilience_service
from app.services.audit import record_audit

DEMO_ORGS = [
    {"name": "Votex Demo Authority", "slug": "votex-demo-authority"},
    {"name": "Demo Electoral Commission", "slug": "demo-electoral-commission"},
]

DEMO_USERS = [
    {
        "org": "votex-demo-authority",
        "email": "admin@votex.demo",
        "full_name": "Amara Okafor",
        "role": "admin",
    },
    {
        "org": "votex-demo-authority",
        "email": "analyst@votex.demo",
        "full_name": "Tunde Balogun",
        "role": "analyst",
    },
    {
        "org": "votex-demo-authority",
        "email": "reporter@votex.demo",
        "full_name": "Ngozi Eze",
        "role": "reporter",
    },
    {
        "org": "demo-electoral-commission",
        "email": "analyst@inec.demo",
        "full_name": "Ibrahim Musa",
        "role": "analyst",
    },
    {
        "org": "demo-electoral-commission",
        "email": "reporter@inec.demo",
        "full_name": "Fatima Bello",
        "role": "reporter",
    },
]

EVIDENCE_BODY = """SYNTHETIC DEMO EVIDENCE - NOT A REAL ELECTION RECORD
From: "Commission Chairman" <chairman@inec-staff-verify.example>
To: adhoc-staff@example.org
Subject: URGENT: Staff verification before deployment

Dear staff member,

You must complete the 2026 staff verification before reporting to your ward.
Sign in to the portal below with your INEC staff credentials:

https://inec-staff-verify.example/login

Failure to verify within 24 hours will result in removal from the deployment list.

Office of the Chairman
Independent National Electoral Commission

---
This file is generated for the Votex AI #AI4Elections prototype.
It contains no real addresses, credentials or voter information.
"""

INCIDENTS = [
    {
        "org": "votex-demo-authority",
        "reporter": "reporter@votex.demo",
        "assignee": "analyst@votex.demo",
        "reference": "VX-2026-A10001",
        "title": "Phishing email impersonating the Commission Chairman",
        "description": (
            "A bulk email using the Commission Chairman's name and photograph asks voter "
            "registration officers to open a 'staff verification' link and enter their portal "
            "credentials. Three ad-hoc staff forwarded it to the support desk. The link "
            "resolves to a lookalike domain registered eight days ago."
        ),
        "category": "phishing",
        "channel": "email",
        "reported_url": "https://inec-staff-verify.example/login",
        "state": "Federal Capital Territory",
        "status": "investigating",
        "priority": "high",
        "risk_score": 87.4,
        "classification": "credential_phishing",
        "ai_status": "complete",
        "days_ago": 4,
        "events": [
            {
                "type": "created",
                "actor": "reporter",
                "minutes": 0,
                "message": "Incident reported through Email.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 35,
                "status": "under_review",
                "message": "Status changed from Submitted to Under review. Triage began within 30 minutes.",
            },
            {
                "type": "assigned",
                "actor": "analyst",
                "minutes": 60,
                "message": "Assigned to Tunde Balogun.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 95,
                "status": "investigating",
                "message": "Status changed from Assigned to Investigating.",
            },
            {
                "type": "comment",
                "actor": "analyst",
                "minutes": 240,
                "message": (
                    "Domain registered eight days ago behind a privacy proxy. Two staff clicked "
                    "but did not submit credentials. Mailbox logs requested from the service desk."
                ),
            },
            {
                "type": "response_action",
                "actor": "analyst",
                "minutes": 330,
                "action_type": "warning_issued",
                "message": (
                    "Public warning drafted with the communications desk and a staff reminder "
                    "to use only the official portal was issued."
                ),
            },
        ],
        "evidence": {
            "filename": "chairman-phishing-sample.txt",
            "content_type": "text/plain",
            "body": EVIDENCE_BODY,
        },
    },
    {
        "org": "votex-demo-authority",
        "reporter": "admin@votex.demo",
        "assignee": None,
        "reference": "VX-2026-A10002",
        "title": "Fake voter registration portal targeting first-time registrants",
        "description": (
            "A lookalike registration portal collects PVC requests and national identification "
            "numbers, then asks for a payment before showing a confirmation screen. The page "
            "uses the Commission's colours and a copied FAQ. It is being promoted in community "
            "WhatsApp groups in Lagos."
        ),
        "category": "fake_portal",
        "channel": "web_form",
        "reported_url": "https://pvc-registration-ng.example/start",
        "state": "Lagos",
        "status": "under_review",
        "priority": "critical",
        "risk_score": 93.2,
        "classification": "fake_registration_portal",
        "ai_status": "complete",
        "days_ago": 1,
        "events": [
            {
                "type": "created",
                "actor": "reporter",
                "minutes": 0,
                "message": "Incident reported through Web form.",
            },
            {
                "type": "status_changed",
                "actor": "admin",
                "minutes": 25,
                "status": "under_review",
                "message": "Status changed from Submitted to Under review. Escalated for urgent triage.",
            },
            {
                "type": "comment",
                "actor": "admin",
                "minutes": 70,
                "message": "Hosting provider identified. Awaiting analyst assignment before takedown contact.",
            },
        ],
    },
    {
        "org": "votex-demo-authority",
        "reporter": "reporter@votex.demo",
        "assignee": None,
        "reference": "VX-2026-A10003",
        "title": "WhatsApp voice note claims results were pre-loaded",
        "description": (
            "A forty-second voice note in Hausa claims that result sheets were pre-filled before "
            "polls opened and names two fictional ward officials. It is spreading in a ward-level "
            "group with more than 400 members."
        ),
        "category": "fake_result",
        "channel": "whatsapp",
        "reported_url": None,
        "state": "Kano",
        "status": "submitted",
        "priority": "high",
        "risk_score": None,
        "classification": None,
        "ai_status": "pending",
        "days_ago": 0,
        "events": [
            {
                "type": "created",
                "actor": "reporter",
                "minutes": 0,
                "message": "Incident reported through WhatsApp.",
            }
        ],
    },
    {
        "org": "votex-demo-authority",
        "reporter": "admin@votex.demo",
        "assignee": "analyst@votex.demo",
        "reference": "VX-2026-A10004",
        "title": "SMS demands a verification fee for PVC collection",
        "description": (
            "Residents in Port Harcourt received SMS messages asking them to pay N2,500 to "
            "'activate' a permanent voter card. The message includes a suspicious short code and "
            "a payment link. At least six residents reported paying before the alert."
        ),
        "category": "payment_fraud",
        "channel": "sms",
        "reported_url": "https://pvc-activation.example/pay",
        "state": "Rivers",
        "status": "escalated",
        "priority": "critical",
        "risk_score": 91.8,
        "classification": "payment_fraud",
        "ai_status": "complete",
        "days_ago": 6,
        "events": [
            {
                "type": "created",
                "actor": "reporter",
                "minutes": 0,
                "message": "Incident reported through SMS.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 20,
                "status": "under_review",
                "message": "Status changed from Submitted to Under review.",
            },
            {
                "type": "assigned",
                "actor": "analyst",
                "minutes": 40,
                "message": "Assigned to Tunde Balogun.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 90,
                "status": "investigating",
                "message": "Status changed from Assigned to Investigating.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 300,
                "status": "escalated",
                "message": "Status changed from Investigating to Escalated. Referred to the police cybercrime unit.",
            },
            {
                "type": "response_action",
                "actor": "analyst",
                "minutes": 320,
                "action_type": "escalation",
                "message": "Case file with the payment short code and six victim reports sent to the cybercrime unit.",
            },
        ],
    },
    {
        "org": "votex-demo-authority",
        "reporter": "reporter@votex.demo",
        "assignee": "analyst@votex.demo",
        "reference": "VX-2026-A10005",
        "title": "Impersonation page reusing the official logo on Facebook",
        "description": (
            "A Facebook page with 1,200 followers copies the Commission's name, logo and banner "
            "and posts a fake recruitment notice for election observers. Applicants are asked to "
            "send a passport photograph and a processing fee."
        ),
        "category": "impersonation",
        "channel": "web_form",
        "reported_url": "https://facebook.example/votex-fake-page",
        "state": "Enugu",
        "status": "contained",
        "priority": "medium",
        "risk_score": 68.5,
        "classification": "brand_impersonation",
        "ai_status": "complete",
        "days_ago": 9,
        "events": [
            {
                "type": "created",
                "actor": "reporter",
                "minutes": 0,
                "message": "Incident reported through Web form.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 55,
                "status": "under_review",
                "message": "Status changed from Submitted to Under review.",
            },
            {
                "type": "assigned",
                "actor": "analyst",
                "minutes": 75,
                "message": "Assigned to Tunde Balogun.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 130,
                "status": "investigating",
                "message": "Status changed from Assigned to Investigating.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 420,
                "status": "contained",
                "message": "Status changed from Investigating to Contained. Page access restricted pending takedown.",
            },
            {
                "type": "response_action",
                "actor": "analyst",
                "minutes": 440,
                "action_type": "takedown_requested",
                "message": "Takedown request submitted through the platform's impersonation reporting flow.",
            },
        ],
    },
    {
        "org": "votex-demo-authority",
        "reporter": "admin@votex.demo",
        "assignee": "analyst@votex.demo",
        "reference": "VX-2026-A10006",
        "title": "Malicious spreadsheet disguised as a voter register",
        "description": (
            "An email attachment named 'updated-voter-register.xlsm' contains a macro that "
            "downloads a remote access tool. Two ward assistants opened it on shared machines. "
            "The machines were isolated and reimaged within two days. The endpoint tool recorded "
            "the sample as d41d8cd98f00b204e9800998ecf8427e."
        ),
        "category": "malware",
        "channel": "email",
        "reported_url": None,
        "state": "Federal Capital Territory",
        "status": "closed",
        "priority": "high",
        "risk_score": 84.1,
        "classification": "malware_delivery",
        "ai_status": "complete",
        "days_ago": 14,
        "closed_minutes": 2880,
        "events": [
            {
                "type": "created",
                "actor": "reporter",
                "minutes": 0,
                "message": "Incident reported through Email.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 30,
                "status": "under_review",
                "message": "Status changed from Submitted to Under review.",
            },
            {
                "type": "assigned",
                "actor": "analyst",
                "minutes": 50,
                "message": "Assigned to Tunde Balogun.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 120,
                "status": "investigating",
                "message": "Status changed from Assigned to Investigating.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 600,
                "status": "contained",
                "message": "Status changed from Investigating to Contained. Both machines isolated from the network.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 1440,
                "status": "remediated",
                "message": "Status changed from Contained to Remediated. Machines reimaged and credentials rotated.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 2160,
                "status": "recovered",
                "message": "Status changed from Remediated to Recovered. Monitoring showed no further beacon traffic.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 2880,
                "status": "closed",
                "message": "Status changed from Recovered to Closed. Lessons learned added to the staff bulletin.",
            },
        ],
    },
    {
        "org": "votex-demo-authority",
        "reporter": "reporter@votex.demo",
        "assignee": "analyst@votex.demo",
        "reference": "VX-2026-A10007",
        "title": "Cloned PVC portal resurfaces in a second WhatsApp campaign",
        "description": (
            "A new wave of WhatsApp broadcasts points registrants to the same lookalike PVC "
            "registration portal seen in case VX-2026-A10002. The landing page at "
            "https://pvc-registration-ng.example/start now shows a countdown timer and asks for a "
            "N1,500 'express processing' fee. Twenty-two residents in Surulere forwarded the link "
            "to the ward support line within one afternoon."
        ),
        "category": "fake_portal",
        "channel": "whatsapp",
        "reported_url": "https://pvc-registration-ng.example/start",
        "state": "Lagos",
        "status": "investigating",
        "priority": "critical",
        "risk_score": 90.1,
        "classification": "fake_registration_portal",
        "ai_status": "complete",
        "days_ago": 2,
        "events": [
            {
                "type": "created",
                "actor": "reporter",
                "minutes": 0,
                "message": "Incident reported through WhatsApp.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 18,
                "status": "under_review",
                "message": "Status changed from Submitted to Under review. Linked to an earlier portal case.",
            },
            {
                "type": "assigned",
                "actor": "analyst",
                "minutes": 32,
                "message": "Assigned to Tunde Balogun.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 70,
                "status": "investigating",
                "message": "Status changed from Assigned to Investigating.",
            },
            {
                "type": "comment",
                "actor": "analyst",
                "minutes": 150,
                "message": (
                    "Same template and domain as VX-2026-A10002. Only the campaign parameter and "
                    "the fee amount changed, so the two cases are correlated automatically."
                ),
            },
        ],
    },
    {
        "org": "votex-demo-authority",
        "reporter": "reporter@votex.demo",
        "assignee": None,
        "reference": "VX-2026-A10008",
        "title": "Payment page on the cloned PVC portal asks for card details",
        "description": (
            "A registrant who reached the fake portal at https://pvc-registration-ng.example/start "
            "was redirected to a card payment form hosted on 203.0.113.42. The form asked for the "
            "card number, expiry date and the three-digit security code. No payment was completed."
        ),
        "category": "fake_portal",
        "channel": "web_form",
        "reported_url": "https://pvc-registration-ng.example/start",
        "state": "Oyo",
        "status": "under_review",
        "priority": "high",
        "risk_score": 82.7,
        "classification": "fake_registration_portal",
        "ai_status": "complete",
        "days_ago": 1,
        "events": [
            {
                "type": "created",
                "actor": "reporter",
                "minutes": 0,
                "message": "Incident reported through Web form.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 26,
                "status": "under_review",
                "message": "Status changed from Submitted to Under review. Payment flow captured for evidence.",
            },
            {
                "type": "comment",
                "actor": "analyst",
                "minutes": 58,
                "message": (
                    "The card form posts to the same host as the landing page. Registrar and "
                    "hosting provider contacts are being prepared."
                ),
            },
        ],
    },
    {
        "org": "votex-demo-authority",
        "reporter": "admin@votex.demo",
        "assignee": None,
        "reference": "VX-2026-A10009",
        "title": "Student group shares the fake PVC portal before registration closes",
        "description": (
            "A campus group administrator posted the lookalike portal at "
            "https://pvc-registration-ng.example/start with the caption 'last chance to register'. "
            "The same payment host at 203.0.113.42 appears in the page source. The post was taken "
            "down by the group after a moderator was alerted."
        ),
        "category": "fake_portal",
        "channel": "sms",
        "reported_url": "https://pvc-registration-ng.example/start",
        "state": "Kano",
        "status": "submitted",
        "priority": "medium",
        "risk_score": None,
        "classification": None,
        "ai_status": "pending",
        "days_ago": 0,
        "events": [
            {
                "type": "created",
                "actor": "reporter",
                "minutes": 0,
                "message": "Incident reported through SMS.",
            }
        ],
    },
    {
        "org": "votex-demo-authority",
        "reporter": "reporter@votex.demo",
        "assignee": "analyst@votex.demo",
        "reference": "VX-2026-A10010",
        "title": "Forwarded staff verification email reuses the same phishing kit",
        "description": (
            "A forwarded message matches the wording, sender display name and link in case "
            "VX-2026-A10001. It again points to https://inec-staff-verify.example/login and asks "
            "ad-hoc staff to confirm their portal credentials before deployment. The forwarded "
            "attachment is byte-identical to the earlier sample."
        ),
        "category": "phishing",
        "channel": "email",
        "reported_url": "https://inec-staff-verify.example/login",
        "state": "Federal Capital Territory",
        "status": "escalated",
        "priority": "high",
        "risk_score": 86.3,
        "classification": "credential_phishing",
        "ai_status": "complete",
        "days_ago": 3,
        "events": [
            {
                "type": "created",
                "actor": "reporter",
                "minutes": 0,
                "message": "Incident reported through Email.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 40,
                "status": "under_review",
                "message": "Status changed from Submitted to Under review.",
            },
            {
                "type": "assigned",
                "actor": "analyst",
                "minutes": 55,
                "message": "Assigned to Tunde Balogun.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 110,
                "status": "investigating",
                "message": "Status changed from Assigned to Investigating.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 260,
                "status": "escalated",
                "message": "Status changed from Investigating to Escalated. Same evidence hash as the earlier wave.",
            },
            {
                "type": "response_action",
                "actor": "analyst",
                "minutes": 280,
                "action_type": "escalation",
                "message": (
                    "Hash match confirmed with VX-2026-A10001. The shared evidence hash and link "
                    "were sent to the mail provider's abuse desk as one campaign."
                ),
            },
        ],
        "evidence": {
            "filename": "staff-verification-forwarded.txt",
            "content_type": "text/plain",
            "body": EVIDENCE_BODY,
        },
    },
    {
        "org": "demo-electoral-commission",
        "reporter": "reporter@inec.demo",
        "assignee": None,
        "reference": "VX-2026-B10003",
        "title": "Lookalike registration portal also targets voters in Ekiti",
        "description": (
            "A partner organisation flagged the same lookalike registration portal at "
            "https://pvc-registration-ng.example/start after it appeared in Ekiti community groups. "
            "The page requests a fee before showing a confirmation screen and reuses the "
            "Commission's visual identity."
        ),
        "category": "fake_portal",
        "channel": "whatsapp",
        "reported_url": "https://pvc-registration-ng.example/start",
        "state": "Ekiti",
        "status": "under_review",
        "priority": "high",
        "risk_score": 77.9,
        "classification": "fake_registration_portal",
        "ai_status": "complete",
        "days_ago": 2,
        "events": [
            {
                "type": "created",
                "actor": "reporter",
                "minutes": 0,
                "message": "Incident reported through WhatsApp.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 35,
                "status": "under_review",
                "message": "Status changed from Submitted to Under review. National picture updated.",
            },
            {
                "type": "comment",
                "actor": "analyst",
                "minutes": 90,
                "message": (
                    "Identical template and payment host to the outbreak reported in Lagos and "
                    "Oyo. Awaiting a national takedown decision."
                ),
            },
        ],
    },
    {
        "org": "demo-electoral-commission",
        "reporter": "reporter@inec.demo",
        "assignee": "analyst@inec.demo",
        "reference": "VX-2026-B10001",
        "title": "Doctored result sheet screenshot circulating on X",
        "description": (
            "A doctored screenshot of a ward result sheet with altered figures is circulating on "
            "X and Telegram. The image reuses a real form layout but names a polling unit that "
            "does not exist in the synthetic demo register."
        ),
        "category": "fake_result",
        "channel": "other",
        "reported_url": "https://social.example/doctored-sheet",
        "state": "Oyo",
        "status": "investigating",
        "priority": "high",
        "risk_score": 88.9,
        "classification": "disinformation",
        "ai_status": "complete",
        "days_ago": 3,
        "events": [
            {
                "type": "created",
                "actor": "reporter",
                "minutes": 0,
                "message": "Incident reported through Other.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 45,
                "status": "under_review",
                "message": "Status changed from Submitted to Under review.",
            },
            {
                "type": "assigned",
                "actor": "analyst",
                "minutes": 80,
                "message": "Assigned to Ibrahim Musa.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 150,
                "status": "investigating",
                "message": "Status changed from Assigned to Investigating.",
            },
            {
                "type": "comment",
                "actor": "analyst",
                "minutes": 210,
                "message": "Metadata points to a single account created this week. Coordinated amplification suspected.",
            },
        ],
    },
    {
        "org": "demo-electoral-commission",
        "reporter": "reporter@inec.demo",
        "assignee": None,
        "reference": "VX-2026-B10002",
        "title": "Phishing SMS sent to ad-hoc staff",
        "description": (
            "Ad-hoc staff received an SMS asking them to confirm their banking details for "
            "allowance payment through a shortened link. The link imitates a payroll portal and "
            "requests an account number and OTP."
        ),
        "category": "phishing",
        "channel": "sms",
        "reported_url": "https://staff-allowance.example/verify",
        "state": "Kaduna",
        "status": "under_review",
        "priority": "medium",
        "risk_score": 72.3,
        "classification": "credential_phishing",
        "ai_status": "complete",
        "days_ago": 2,
        "events": [
            {
                "type": "created",
                "actor": "reporter",
                "minutes": 0,
                "message": "Incident reported through SMS.",
            },
            {
                "type": "status_changed",
                "actor": "analyst",
                "minutes": 60,
                "status": "under_review",
                "message": "Status changed from Submitted to Under review.",
            },
        ],
    },
]


def _seed_users(db: Session, orgs: dict[str, Organisation]) -> dict[str, User]:
    users: dict[str, User] = {}
    for spec in DEMO_USERS:
        user = User(
            organisation_id=orgs[spec["org"]].id,
            email=spec["email"],
            full_name=spec["full_name"],
            role=spec["role"],
            password_hash=hash_password(settings.demo_password),
            is_active=True,
            created_at=utcnow(),
        )
        db.add(user)
        users[spec["email"]] = user
    db.flush()
    return users


def _event_actor(item: dict, users: dict[str, User], key: str) -> User | None:
    if key == "reporter":
        return users[item["reporter"]]
    if key == "assignee":
        return users[item["assignee"]] if item["assignee"] else None
    # "admin" or "analyst" resolves to the investigator for that organisation.
    org_emails = [email for email, user in users.items() if user.organisation_id == users[item["reporter"]].organisation_id]
    for email in org_emails:
        if users[email].role in {"admin", "analyst"}:
            return users[email]
    return users[item["reporter"]]


def _seed_incident(db: Session, item: dict, users: dict[str, User]) -> Incident:
    reporter = users[item["reporter"]]
    assignee = users[item["assignee"]] if item["assignee"] else None
    created_at = utcnow() - timedelta(days=item["days_ago"])

    incident = Incident(
        reference=item["reference"],
        organisation_id=reporter.organisation_id,
        reporter_id=reporter.id,
        assignee_id=assignee.id if assignee else None,
        title=item["title"],
        description=item["description"],
        category=item["category"],
        channel=item["channel"],
        reported_url=item["reported_url"],
        state=item["state"],
        status=item["status"],
        priority=item["priority"],
        ai_status=item["ai_status"],
        risk_score=item["risk_score"],
        classification=item["classification"],
        created_at=created_at,
        updated_at=created_at,
        closed_at=(
            created_at + timedelta(minutes=item["closed_minutes"])
            if item["status"] == "closed" and item.get("closed_minutes")
            else None
        ),
    )
    db.add(incident)
    db.flush()

    record_audit(
        db,
        action="incident.created",
        actor_id=reporter.id,
        organisation_id=reporter.organisation_id,
        resource_type="incident",
        resource_id=incident.id,
        detail={
            "reference": incident.reference,
            "category": incident.category,
            "channel": incident.channel,
            "priority": incident.priority,
            "status": "submitted",
        },
    )

    current_status = "submitted"
    for spec in item["events"]:
        actor = _event_actor(item, users, spec["actor"])
        event_time = created_at + timedelta(minutes=spec["minutes"])
        metadata: dict = {}
        event_type = spec["type"]

        if event_type == "created":
            metadata = {"status": "submitted"}
        elif event_type == "status_changed":
            previous_status = current_status
            current_status = spec["status"]
            metadata = {"previous_status": previous_status, "status": current_status}
        elif event_type == "assigned":
            current_status = "assigned"
            metadata = {
                "assignee_id": assignee.id if assignee else None,
                "status": "assigned",
            }
        elif event_type == "response_action":
            metadata = {"action_type": spec["action_type"]}
        elif event_type == "comment":
            metadata = {}

        db.add(
            IncidentEvent(
                incident_id=incident.id,
                actor_id=actor.id if actor else None,
                event_type=event_type,
                message=spec["message"],
                event_metadata=metadata,
                created_at=event_time,
            )
        )

        detail = {"reference": incident.reference}
        action: str | None = None
        if event_type == "status_changed":
            action = "incident.status_changed"
            detail.update(
                {
                    "previous_status": metadata["previous_status"],
                    "status": metadata["status"],
                }
            )
        elif event_type == "assigned":
            action = "incident.assigned"
            detail.update(
                {
                    "assignee_id": metadata["assignee_id"],
                    "previous_assignee_id": None,
                    "status": "assigned",
                }
            )
        elif event_type == "response_action":
            action = "incident.response_recorded"
            detail.update({"action_type": metadata["action_type"]})
        elif event_type == "comment":
            action = "incident.comment_added"

        if action:
            record_audit(
                db,
                action=action,
                actor_id=actor.id if actor else None,
                organisation_id=reporter.organisation_id,
                resource_type="incident",
                resource_id=incident.id,
                detail=detail,
            )

    evidence_spec = item.get("evidence")
    if evidence_spec:
        stored_filename = f"{uuid4().hex}.txt"
        target = Path(settings.evidence_dir).resolve() / incident.id / stored_filename
        target.parent.mkdir(parents=True, exist_ok=True)
        body = evidence_spec["body"]
        target.write_text(body, encoding="utf-8")
        digest = sha256(body.encode("utf-8")).hexdigest()

        evidence = Evidence(
            incident_id=incident.id,
            organisation_id=reporter.organisation_id,
            uploaded_by_id=reporter.id,
            original_filename=evidence_spec["filename"],
            stored_filename=stored_filename,
            content_type=evidence_spec["content_type"],
            size_bytes=len(body.encode("utf-8")),
            sha256=digest,
            created_at=created_at + timedelta(minutes=30),
        )
        db.add(evidence)
        db.flush()

        db.add(
            IncidentEvent(
                incident_id=incident.id,
                actor_id=reporter.id,
                event_type="evidence_added",
                message=f"Evidence uploaded: {evidence.original_filename} ({evidence.size_bytes:,} bytes).",
                event_metadata={
                    "filename": evidence.original_filename,
                    "sha256": digest,
                    "size_bytes": evidence.size_bytes,
                },
                created_at=created_at + timedelta(minutes=30),
            )
        )
        record_audit(
            db,
            action="evidence.uploaded",
            actor_id=reporter.id,
            organisation_id=reporter.organisation_id,
            resource_type="evidence",
            resource_id=evidence.id,
            detail={
                "incident_reference": incident.reference,
                "filename": evidence.original_filename,
                "content_type": evidence.content_type,
                "size_bytes": evidence.size_bytes,
                "sha256": digest,
            },
        )

    return incident


def seed_demo_data() -> bool:
    """Create demo organisations, users, incidents and audit history once.

    Returns ``True`` when seeding ran, ``False`` when the demo tenant already
    exists. Safe to call on every application start.
    """

    with SessionLocal() as db:
        existing = db.scalar(
            select(Organisation).where(Organisation.slug == "votex-demo-authority")
        )
        if existing is not None:
            return False

        orgs: dict[str, Organisation] = {}
        for spec in DEMO_ORGS:
            organisation = Organisation(
                name=spec["name"], slug=spec["slug"], created_at=utcnow()
            )
            db.add(organisation)
            orgs[spec["slug"]] = organisation
        db.flush()

        users = _seed_users(db, orgs)

        for item in INCIDENTS:
            _seed_incident(db, item, users)

        db.commit()
    return True


OLDER_ANSWERS = {
    "governance.owner": 3,
    "governance.plan": 2,
    "governance.vendor": 2,
    "identity.mfa": 3,
    "identity.privileged": 2,
    "identity.phishing_resistant": 1,
    "network.inventory": 2,
    "network.email": 3,
    "data.backup": 2,
    "data.retention": 1,
    "response.exercise": 1,
    "people.awareness": 2,
}


def seed_resilience_demo() -> bool:
    """Create two readiness assessments and one completed exercise.

    Returns ``True`` when the demo records were created and ``False`` when the
    organisation already has assessments or the demo tenant is missing. Safe to
    call on every application start.
    """

    with SessionLocal() as db:
        organisation = db.scalar(
            select(Organisation).where(Organisation.slug == "votex-demo-authority")
        )
        analyst = db.scalar(select(User).where(User.email == "analyst@votex.demo"))
        if organisation is None or analyst is None:
            return False
        if db.scalar(select(ResilienceAssessment).limit(1)) is not None:
            return False

        older = resilience_service.create_assessment(
            db,
            analyst,
            AssessmentCreate(
                title="Pre-exercise readiness baseline",
                notes=(
                    "Synthetic baseline taken before the first tabletop exercise. "
                    "Scores are illustrative and use no real assessment data."
                ),
                answers=OLDER_ANSWERS,
            ),
        )
        older_date = utcnow() - timedelta(days=30)
        for finding in db.scalars(
            select(ResilienceFinding).where(
                ResilienceFinding.assessment_id == older.id
            )
        ):
            finding.created_at = older_date
            finding.updated_at = older_date
        db.commit()

        for finding in older.findings:
            if finding.title in {
                "Phishing-resistant privileged access",
                "Third-party and supplier checks",
                "Encrypted backups and restore tests",
                "Role-based security awareness",
            }:
                resilience_service.update_finding(
                    db,
                    analyst,
                    finding.id,
                    FindingUpdate(
                        remediation_status="resolved",
                        owner="Response team",
                        note="Closed by the response team after the follow-up review.",
                    ),
                )

        latest = resilience_service.create_assessment(
            db,
            analyst,
            AssessmentCreate(
                title="Post-exercise readiness review",
                notes=(
                    "Synthetic review after the tabletop exercise. The score reflects "
                    "the recorded answers only and is not a certified audit."
                ),
                answers=resilience_service.seeded_answers(),
            ),
        )
        for finding in latest.findings:
            if finding.title == "Phishing-resistant privileged access":
                resilience_service.update_finding(
                    db,
                    analyst,
                    finding.id,
                    FindingUpdate(
                        remediation_status="in_progress",
                        owner="Identity workstream",
                        note="Passkey pilot scheduled for two privileged accounts.",
                    ),
                )

        older_row = db.get(ResilienceAssessment, older.id)
        latest_row = db.get(ResilienceAssessment, latest.id)
        if older_row is not None:
            older_row.assessment_date = older_date
        if latest_row is not None:
            latest_row.assessment_date = utcnow() - timedelta(days=7)
        db.commit()

        exercise = resilience_service.create_exercise(db, analyst, ExerciseCreate())
        for task in exercise.tasks:
            status = "done" if task.sequence <= 5 else "skipped"
            notes = (
                "Completed by the response team during the exercise."
                if status == "done"
                else "Deferred when the exercise was closed at the decision note."
            )
            resilience_service.update_exercise_task(
                db,
                analyst,
                exercise.id,
                task.id,
                ExerciseTaskUpdate(status=status, notes=notes),
            )
        resilience_service.complete_exercise(db, analyst, exercise.id)

        exercise_row = db.get(Exercise, exercise.id)
        if exercise_row is not None:
            started = utcnow() - timedelta(days=12)
            exercise_row.started_at = started
            exercise_row.completed_at = started + timedelta(minutes=41)
            db.commit()
    return True
