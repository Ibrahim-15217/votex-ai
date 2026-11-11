# Votex AI — Documentation

This folder contains the evidence package that complements the running prototype. Documents are updated as each phase lands.

| Document | Purpose | Status |
| --- | --- | --- |
| [security/THREAT_MODEL.md](./security/THREAT_MODEL.md) | STRIDE and LINDDUN analysis, controls and residual risk | Draft v0.1 |
| [model/MODEL_CARD.md](./model/MODEL_CARD.md) | Intended use, method, measured metrics and limitations | Complete v0.2 |
| [model/EVALUATION.md](./model/EVALUATION.md) | Held-out and challenge evaluation, failure analysis | Complete v0.2 |
| [data/DATASHEET.md](./data/DATASHEET.md) | Dataset provenance, composition and biases | Draft v0.1 |
| [safety/SAFETY_AND_LIMITATIONS.md](./safety/SAFETY_AND_LIMITATIONS.md) | Prohibited uses, residual risk and disclosure | Draft v0.1 |
| [security/PRIVACY_AND_CORRELATION.md](./security/PRIVACY_AND_CORRELATION.md) | k ≥ 5 suppression, tenant scoping, correlation and export evidence | Complete v0.3 |
| [security/ACCESSIBILITY_AND_LOCALISATION.md](./security/ACCESSIBILITY_AND_LOCALISATION.md) | WCAG 2.2 AA measures, four locales, keyboard proof and responsive sweep | Complete v0.4 |
| [submission/SUBMISSION_CHECKLIST.md](./submission/SUBMISSION_CHECKLIST.md) | Deadlines, artifact status, safety checks and fresh-clone steps | Active |
| [submission/APPLICATION_DRAFT.md](./submission/APPLICATION_DRAFT.md) | Draft answers and team placeholders for the application form | Active |
| [submission/APPLICATION_FORM_ANSWERS.md](./submission/APPLICATION_FORM_ANSWERS.md) | Field-by-field answers for the live 5-step portal form | Active |
| [submission/PROBLEM_STATEMENT.md](./submission/PROBLEM_STATEMENT.md) | One-page Track 4 problem statement | Complete v1.0 |
| [submission/METHODOLOGY.md](./submission/METHODOLOGY.md) | Approach, data, evaluation, security, privacy and inclusion | Complete v1.0 |
| [demo/DEMO_SCRIPT.md](./demo/DEMO_SCRIPT.md) | Three-minute demonstration and judge Q&A | Draft v0.2 |

## Visual evidence

- [Phase 0 login screen (1440×1000)](./demo/screenshots/phase0-login-1440x1000.png)
- [Phase 1 login, overview, queue, incident detail, audit and report](./demo/screenshots/)
- [Phase 2 high-risk analysis panel](./demo/screenshots/phase2-analysis-high-risk-1440x1000.png), [suspicious case](./demo/screenshots/phase2-analysis-suspicious-1440x1000.png), [payment-fraud case](./demo/screenshots/phase2-analysis-payment-fraud-1440x1000.png), [queue](./demo/screenshots/phase2-incidents-1440x1000.png) and [audit trail](./demo/screenshots/phase2-audit-1440x1000.png)
- [Phase 3 indicator intelligence](./demo/screenshots/phase3-intelligence-1440x1000.png), [organisation dashboard](./demo/screenshots/phase3-dashboard-organisation-1440x1000.png), [national dashboard with suppression](./demo/screenshots/phase3-dashboard-national-1440x1000.png), [linked incidents](./demo/screenshots/phase3-related-incidents-1440x1000.png), [audited exports](./demo/screenshots/phase3-audit-1440x1000.png) and [updated overview](./demo/screenshots/phase3-overview-1440x1000.png)
- [Phase 4 Hausa sign-in](./demo/screenshots/phase4-login-hausa-1440x1000.png), [Igbo keyboard intake](./demo/screenshots/phase4-report-igbo-1440x1000.png), [filled intake](./demo/screenshots/phase4-report-filled-igbo-1440x1000.png), [localised success](./demo/screenshots/phase4-detail-created-igbo-1440x1000.png), [Hausa overview](./demo/screenshots/phase4-overview-hausa-1440x1000.png), [Hausa queue](./demo/screenshots/phase4-queue-hausa-1440x1000.png) and [mobile screens](./demo/screenshots/phase4-report-mobile-hausa-390x844.png)

## Principles

- **Evidence over claims.** Every security or privacy statement should point to a test, command or artifact.
- **Honest limits.** State what the prototype cannot do and what a pilot would require.
- **Synthetic only.** No real personal data, voter records or confidential programme material.
- **Human control.** The system advises; people decide.
- **Non-endorsement.** Participation does not imply INEC or partner approval.

## Planned additions

| Phase | Document |
| --- | --- |
| ~~3~~ | ~~Privacy test evidence for k-anonymity and exports~~ — delivered in [security/PRIVACY_AND_CORRELATION.md](./security/PRIVACY_AND_CORRELATION.md) |
| ~~4~~ | ~~Accessibility checklist and localisation review~~ — delivered in [security/ACCESSIBILITY_AND_LOCALISATION.md](./security/ACCESSIBILITY_AND_LOCALISATION.md) |
| 6 | Final threat model, model card, datasheet, safety statement and evidence pack |
