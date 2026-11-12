"""Fixed resilience questionnaire, scoring and synthetic exercise scenario.

Everything here is pure: constants and arithmetic only, with no database
access. The API, the demo seed and the unit tests share this one definition so
a score can always be reproduced from the recorded answers.

The questionnaire is a prototype readiness check, not a certified index. Equal
weights are used deliberately; the assessment stores the answers so any future
weighting can be recomputed without losing the evidence.
"""

from __future__ import annotations

from dataclasses import dataclass

MATURITY_LABELS: dict[int, str] = {
    0: "Not started",
    1: "Planned",
    2: "Partially implemented",
    3: "Implemented",
    4: "Implemented and verified",
}

SEVERITY_ORDER = ("critical", "high", "medium", "low")


@dataclass(frozen=True)
class Control:
    """One readiness control in the fixed questionnaire."""

    key: str
    category: str
    title: str
    detail: str
    remediation: str


CONTROLS: tuple[Control, ...] = (
    Control(
        key="governance.owner",
        category="governance",
        title="Named security owner",
        detail=(
            "A named person owns cyber risk, approves exceptions and is the first "
            "contact when an electoral system is suspected of compromise."
        ),
        remediation=(
            "Assign a named security owner and publish the escalation path to every "
            "electoral team."
        ),
    ),
    Control(
        key="governance.plan",
        category="governance",
        title="Tested incident-response plan",
        detail=(
            "A written plan defines roles, severity levels and communication steps, "
            "and has been reviewed or exercised in the last 12 months."
        ),
        remediation=(
            "Write or refresh the incident-response plan, name the decision makers "
            "and schedule a tabletop review."
        ),
    ),
    Control(
        key="governance.vendor",
        category="governance",
        title="Third-party and supplier checks",
        detail=(
            "Technology suppliers, hosting providers and temporary staff are "
            "assessed before they receive access to election infrastructure."
        ),
        remediation=(
            "Add a short security questionnaire and access clause to every supplier "
            "and temporary-staff agreement."
        ),
    ),
    Control(
        key="identity.mfa",
        category="identity",
        title="Multi-factor authentication",
        detail=(
            "Every staff account, including temporary field staff, requires a second "
            "factor before reaching email or internal portals."
        ),
        remediation=(
            "Enable multi-factor authentication for all staff accounts and track "
            "coverage weekly."
        ),
    ),
    Control(
        key="identity.privileged",
        category="identity",
        title="Least privilege and access review",
        detail=(
            "Administrative access is limited to the people who need it and is "
            "reviewed at least every quarter, including departures."
        ),
        remediation=(
            "Remove standing administrator rights, adopt just-in-time elevation and "
            "review the access list each quarter."
        ),
    ),
    Control(
        key="identity.phishing_resistant",
        category="identity",
        title="Phishing-resistant privileged access",
        detail=(
            "Privileged and election-result systems require hardware-backed or "
            "passkey authentication rather than passwords or SMS codes."
        ),
        remediation=(
            "Introduce passkeys or hardware security keys for privileged accounts "
            "and result-handling systems."
        ),
    ),
    Control(
        key="network.inventory",
        category="network",
        title="Asset inventory and patch cadence",
        detail=(
            "Internet-facing portals, servers and field devices are inventoried and "
            "patched on a defined schedule."
        ),
        remediation=(
            "Maintain one asset register, assign patch owners and set a maximum "
            "remediation window for critical updates."
        ),
    ),
    Control(
        key="network.email",
        category="network",
        title="Email authentication enforcement",
        detail=(
            "SPF, DKIM and a DMARC policy at enforcement are published for every "
            "official domain used to contact staff or voters."
        ),
        remediation=(
            "Publish SPF and DKIM records, move DMARC to enforcement and monitor "
            "reports for lookalike senders."
        ),
    ),
    Control(
        key="data.backup",
        category="data",
        title="Encrypted backups and restore tests",
        detail=(
            "Critical systems and audit records are backed up, encrypted and restored "
            "in a test at least once a quarter."
        ),
        remediation=(
            "Encrypt backups, store one copy offline and record a successful restore "
            "test each quarter."
        ),
    ),
    Control(
        key="data.retention",
        category="data",
        title="Data minimisation and retention",
        detail=(
            "Only the data needed for an operational purpose is collected, and a "
            "retention schedule deletes the rest on time."
        ),
        remediation=(
            "Document each data field's purpose, set a retention period and automate "
            "deletion."
        ),
    ),
    Control(
        key="response.exercise",
        category="response",
        title="Tabletop exercise in the last 12 months",
        detail=(
            "The response team has rehearsed a phishing, denial-of-service or "
            "disinformation scenario and recorded lessons learned."
        ),
        remediation=(
            "Run a synthetic tabletop exercise, record decisions and assign owners "
            "to the lessons learned."
        ),
    ),
    Control(
        key="people.awareness",
        category="people",
        title="Role-based security awareness",
        detail=(
            "Field staff, permanent staff and election officials receive awareness "
            "training matched to the threats they actually face."
        ),
        remediation=(
            "Replace generic awareness slides with short, role-specific briefings and "
            "a clear reporting channel."
        ),
    ),
)

CONTROL_BY_KEY: dict[str, Control] = {control.key: control for control in CONTROLS}
CONTROL_KEYS: tuple[str, ...] = tuple(control.key for control in CONTROLS)
QUESTIONNAIRE_SIZE = len(CONTROLS)
MAX_CONTROL_SCORE = 4


def score_answers(answers: dict[str, int]) -> float:
    """Return a 0–100 readiness score for a complete answer set.

    Raises ``KeyError`` if a control is missing and ``ValueError`` if any answer
    falls outside 0–4, so callers cannot persist an invalid score.
    """

    total = 0
    for key in CONTROL_KEYS:
        value = answers[key]
        if not isinstance(value, int) or not 0 <= value <= MAX_CONTROL_SCORE:
            raise ValueError(f"Control {key} must be an integer from 0 to 4.")
        total += value
    return round(100 * total / (MAX_CONTROL_SCORE * QUESTIONNAIRE_SIZE), 1)


def band_for(score: float) -> str:
    """Map a readiness score to a three-level band."""

    if score >= 70:
        return "resilient"
    if score >= 40:
        return "developing"
    return "fragile"


def derive_findings(answers: dict[str, int]) -> list[dict[str, str]]:
    """Return one finding for every control answered below "implemented".

    Severity follows the gap: not started is critical, planned is high and
    partially implemented is medium. Implemented and verified controls produce
    no finding.
    """

    severity_by_score = {0: "critical", 1: "high", 2: "medium"}
    findings: list[dict[str, str]] = []
    for control in CONTROLS:
        severity = severity_by_score.get(answers.get(control.key, 0))
        if severity is None:
            continue
        findings.append(
            {
                "category": control.category,
                "title": control.title,
                "detail": control.remediation,
                "severity": severity,
            }
        )
    return findings


def summary_for(score: float, band: str, findings: list[dict[str, str]]) -> str:
    """Build the one-line explanation stored with an assessment."""

    implemented = QUESTIONNAIRE_SIZE - len(findings)
    return (
        f"Readiness score {score:.1f}/100 ({band}). "
        f"{implemented} of {QUESTIONNAIRE_SIZE} controls are implemented or verified; "
        f"{len(findings)} findings were opened for the rest."
    )


EXERCISE_SCENARIO: dict[str, object] = {
    "key": "phishing-triage-v1",
    "title": "Synthetic phishing-wave triage",
    "summary": (
        "A simulated wave of credential-phishing reports targets ad-hoc staff. "
        "Triage the reports, link the campaign, recommend containment and record "
        "the decision. Nothing leaves this environment and no real system is "
        "contacted."
    ),
    "tasks": [
        {
            "sequence": 1,
            "title": "Confirm the safe exercise boundary",
            "description": (
                "Open the exercise brief and confirm that every artefact is synthetic, "
                "that no real mailbox or portal will be opened and that no personal "
                "data is used."
            ),
            "expected_action": (
                "State the boundary and confirm the exercise uses synthetic data only."
            ),
        },
        {
            "sequence": 2,
            "title": "Triage the first report",
            "description": (
                "Read the injected report about a staff-verification email. Decide the "
                "category, severity and who is targeted, without opening the link."
            ),
            "expected_action": (
                "Classify the report as credential phishing and identify ad-hoc field "
                "staff as the target group."
            ),
        },
        {
            "sequence": 3,
            "title": "Extract and record indicators",
            "description": (
                "Record the sender domain, the lookalike URL and the attachment hash "
                "from the synthetic report."
            ),
            "expected_action": (
                "Add the domain, URL and SHA-256 hash to the indicator list."
            ),
        },
        {
            "sequence": 4,
            "title": "Link the second report",
            "description": (
                "A second synthetic report arrives with the same URL and a byte-identical "
                "attachment. Link it to the first as one campaign."
            ),
            "expected_action": (
                "Connect both reports through the shared indicator and note the match."
            ),
        },
        {
            "sequence": 5,
            "title": "Recommend containment",
            "description": (
                "Propose the immediate containment actions for the mail provider and the "
                "affected staff group."
            ),
            "expected_action": (
                "Block the sender domain, warn the affected staff and reset exposed "
                "credentials through the approved channel."
            ),
        },
        {
            "sequence": 6,
            "title": "Record the decision and close",
            "description": (
                "Write a short decision note that separates what was observed from what "
                "was inferred, and close the exercise."
            ),
            "expected_action": (
                "Record the decision, the evidence used and any open follow-up."
            ),
        },
    ],
}

EXERCISE_TASKS: tuple[dict[str, object], ...] = tuple(EXERCISE_SCENARIO["tasks"])  # type: ignore[arg-type]
