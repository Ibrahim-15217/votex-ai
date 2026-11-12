# Votex AI

**Securing Elections Through Intelligent Cybersecurity**

Votex AI is an electoral cybersecurity intelligence and incident coordination prototype built for **Track 4 — Electoral Cybersecurity & Resilience** of the **#AI4Elections Hackathon 2026–2027**.

> **Status: Phase 5 — Resilience and simulation.** Phase 1 mounted the secure workflow spine (JWT authentication, organisation isolation, incident lifecycle, evidence hashing, hash-chained audit). Phase 2 added a trained, explainable hybrid analyser: URL and rule intelligence, NLP signals, a TF-IDF + Logistic Regression classifier and a published weighted risk score. Phase 3 turns reports into situational awareness: deterministic indicator extraction, tenant-scoped correlation, related-incident views, organisation and national dashboards, k ≥ 5 suppression in the query layer, and audited CSV exports. Phase 4 makes the prototype usable by the people who report threats: four complete interface locales (English, Hausa, Yoruba, Igbo), a keyboard-only intake path, WCAG 2.2 AA measures, low-bandwidth rendering and responsive layouts from 390 px to 1440 px. Phase 5 adds Track 4 depth: a fixed 12-control readiness assessment with auto-generated remediation findings, and a synthetic phishing-triage exercise with six tracked tasks and an after-action performance summary. See [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md).

---

## The problem

Electoral staff, observers, party agents and voters are targeted by phishing, impersonation and fake portals. Reports arrive through informal channels, indicators are not correlated, evidence integrity is hard to prove, and national visibility often conflicts with organisational privacy.

## What Votex AI does

One complete, defensible workflow:

**Report → AI analysis → correlation → assignment and response → audit**

- **Secure incident intake** with evidence hashing and organisation isolation.
- **Explainable hybrid analysis** — URL rules, NLP signals, TF-IDF classifier and a transparent weighted risk score.
- **Indicator correlation** across reports sharing domains, URLs, IPs or file hashes.
- **Response coordination** with assignment, status transitions, actions and a complete timeline.
- **Privacy-preserving national view** using k-anonymity suppression (k ≥ 5).
- **Resilience readiness** scored from a fixed 12-control questionnaire, with severity-ranked findings and tracked remediation.
- **Synthetic exercises** that rehearse phishing triage and record an audited after-action summary without touching a real system.
- **Tamper-evident audit** using a SHA-256 hash chain and a verification command.
- **Inclusive interface** in English, Hausa, Yoruba and Igbo, with WCAG 2.2 AA as the target and a keyboard-only reporting path.

> **Boundaries:** synthetic or authorised data only; no live electoral systems; no voter registers or biometrics; no scanning or exploitation of third-party systems. Votex AI is not affiliated with, endorsed by, or approved by INEC or any partner.

---

## Evidence at a glance

| Evidence | Result |
| --- | --- |
| Backend test suite | **52 passed** (`pytest -q`, 56.62s) |
| Resilience demo | Baseline assessment **50.0 (developing)** → latest **70.8 (resilient)** · 9/13 findings open · one completed exercise (5 done, 1 skipped) |
| Resilience isolation | Reporter sees the analyst-only notice and no readiness data · cross-tenant assessment and exercise reads return 404 |
| Correlation (live demo) | 5 shared indicators link 9 of 10 reports in the demo authority |
| Cross-tenant national view | PVC URL/domain linked to 5 incidents across 2 organisations: the smallest k cell that can surface |
| Privacy suppression (live) | 39 national cells returned as `null` before reaching the browser or CSV |
| Related incidents | A10002 → 3 linked cases; A10010 → A10001 via URL, domain and identical evidence SHA-256 |
| Audit | `intelligence.exported` recorded for indicator, organisation and national CSV exports; chain valid |
| Browser verification | Seven routes including `/resilience` rendered with **0 JS errors, 0 px horizontal overflow**; `/resilience` also verified at 390×844 |
| Localisation | Four complete locales; `<html lang>` and `localStorage` verified for `en`, `ha`, `yo`, `ig` |
| Keyboard-only intake | Tab to the Igbo switcher, `Enter`, type title and description, `Enter` to submit, localised success banner — no pointer used |
| Responsive sweep | 6 routes × 4 widths (390/768/1024/1440 px): **0 horizontal overflows, 0 console errors** |
| Held-out synthetic set (350 rows) | Precision / recall / F1 1.000 · Brier 0.0006 · 0 false positives, 0 false negatives |
| Hand-written challenge set (28 cases) | 0 errors · Brier 0.0265 · closest case 0.059 from the threshold |
| Honest limit | Synthetic and hand-written data only; real-world generalisation unknown |

Full method, failure analysis and reproduction steps: [docs/model/EVALUATION.md](./docs/model/EVALUATION.md). Privacy and correlation evidence: [docs/security/PRIVACY_AND_CORRELATION.md](./docs/security/PRIVACY_AND_CORRELATION.md).

---

## Architecture

```text
React + TypeScript + Tailwind
            │
            ▼
    FastAPI  /api/v1
            │
            ├── PostgreSQL (system of record)
            ├── Evidence storage (local / MinIO) + SHA-256
            ├── Hybrid AI engine
            │     ├── URL and NLP rules
            │     ├── TF-IDF + Logistic Regression
            │     └── explainable weighted risk score
            ├── IOC extraction and correlation
            ├── SHA-256 hash-chained audit log
            └── k-anonymity national aggregates
```

The prototype is designed to run offline with Docker Compose. Analysis is synchronous in the MVP so the demo cannot fail on a missing worker; service boundaries still allow a task queue later.

---

## Repository layout

```text
votex-ai/
├── backend/            FastAPI service, tests and container image
├── frontend/           React + TypeScript + Vite + Tailwind interface
├── ai-engine/          Dataset generator, training and evaluation
├── docs/               Threat model, model card, datasheet, safety, demo
├── docker-compose.yml  Reproducible local stack
├── .env.example        Environment template
├── AI4Elections.md     Target architecture and MVP scope
└── DEVELOPMENT_PLAN.md Phase-gated delivery plan
```

---

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

| Service | URL |
| --- | --- |
| Web interface | http://localhost:8080 |
| API | http://localhost:8000 |
| API health | http://localhost:8000/api/v1/health |
| API documentation | http://localhost:8000/api/docs |
| MinIO console | http://localhost:9001 |

## Quick start (local development)

**Backend**

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

The interface is served at http://localhost:5173. During development the API base defaults to `http://127.0.0.1:8000/api/v1`; override it with `VITE_API_BASE_URL` if needed.

**Demo data**

The backend creates the schema and seeds the synthetic demo tenant on first start. Run the API tests with:

```bash
cd backend
.venv\Scripts\python.exe -m pytest -q
```

**Synthetic dataset and model**

```bash
python ai-engine/training/generate_data.py
python ai-engine/training/train_model.py
```

The dataset generator writes a labelled dataset and manifest to
`ai-engine/datasets/`. Training writes the model artefact and measured metrics
to `ai-engine/models/`. Both outputs are committed so a fresh clone can run the
demo without retraining; regenerate them to reproduce the evaluation.

The backend loads `ai-engine/models/phishing_model.joblib` by default. If the
artefact is missing, the API still starts, `GET /api/v1/health` reports
`model-unavailable`, and analyses degrade honestly to the other three
components.

---

## Demo accounts

| Account | Role | Organisation |
| --- | --- | --- |
| `admin@votex.demo` | Administrator | Votex Demo Authority |
| `analyst@votex.demo` | Analyst | Votex Demo Authority |
| `reporter@votex.demo` | Reporter | Votex Demo Authority |
| `analyst@inec.demo` | Analyst | Demo Electoral Commission |
| `reporter@inec.demo` | Reporter | Demo Electoral Commission |

Password: `VotexDemo!23`

> Demo accounts and all data are synthetic. They are not real credentials and grant no access to any real system.

---

## Security and privacy commitments

- JWT authentication with role-based access control and organisation isolation.
- Argon2id password hashing, with rate limiting and MFA-ready design as hardening targets.
- Evidence validation, SHA-256 integrity hashes and access logging.
- Append-only audit entries chained with `prev_hash` and `entry_hash`.
- National aggregates suppress cells with fewer than **5** contributing incidents or organisations.
- NDPA 2023-aligned data handling; documented retention and deletion.
- No secrets committed; strict CORS, security headers and parameterised queries.
- Responsible disclosure route documented in [docs/safety/SAFETY_AND_LIMITATIONS.md](./docs/safety/SAFETY_AND_LIMITATIONS.md).

## Inclusion commitments

- Four complete interface locales in the MVP: English, Hausa, Yoruba and Igbo.
  Dictionaries are typed against the English key set, so a missing translation
  fails the build.
- WCAG 2.2 AA target: keyboard-only operation, visible focus, skip link, route
  focus management, labelled forms and screen-reader status messages.
- Severity is never communicated by colour alone.
- Low-bandwidth-friendly interface with no external font or media dependency;
  `prefers-reduced-data` removes decoration, blur, shadows and animation.
- Plain-language reporting for non-specialist users, with evidence limits,
  privacy notes and next steps written in the reporter’s language.
- Analyst case records, AI explanations and dashboards remain English-only in
  this phase and say so on screen rather than pretending to be translated.

Measured keyboard, locale, contrast and responsive evidence:
[docs/security/ACCESSIBILITY_AND_LOCALISATION.md](./docs/security/ACCESSIBILITY_AND_LOCALISATION.md).

---

## Documentation

| Document | Purpose |
| --- | --- |
| [AI4Elections.md](./AI4Elections.md) | Target architecture, hackathon alignment and realistic MVP |
| [DEVELOPMENT_PLAN.md](./DEVELOPMENT_PLAN.md) | Phase-by-phase delivery plan and definition of done |
| [docs/security/THREAT_MODEL.md](./docs/security/THREAT_MODEL.md) | STRIDE/LINDDUN threat model and controls |
| [docs/security/PRIVACY_AND_CORRELATION.md](./docs/security/PRIVACY_AND_CORRELATION.md) | Tenant isolation, k-anonymity suppression and audited exports |
| [docs/security/ACCESSIBILITY_AND_LOCALISATION.md](./docs/security/ACCESSIBILITY_AND_LOCALISATION.md) | WCAG 2.2 AA measures, locale coverage and keyboard evidence |
| [docs/security/RESILIENCE_AND_EXERCISES.md](./docs/security/RESILIENCE_AND_EXERCISES.md) | Readiness questionnaire, scoring, findings, exercise lifecycle, tenancy and audit events |
| [docs/submission/SUBMISSION_CHECKLIST.md](./docs/submission/SUBMISSION_CHECKLIST.md) | Application and prototype submission gates, safety checks, fresh-clone test |
| [docs/submission/APPLICATION_DRAFT.md](./docs/submission/APPLICATION_DRAFT.md) | Draft application answers and team placeholders |
| [docs/submission/APPLICATION_FORM_ANSWERS.md](./docs/submission/APPLICATION_FORM_ANSWERS.md) | Field-by-field answers for the live portal form |
| [docs/submission/PROBLEM_STATEMENT.md](./docs/submission/PROBLEM_STATEMENT.md) | One-page Track 4 problem statement |
| [docs/submission/METHODOLOGY.md](./docs/submission/METHODOLOGY.md) | Approach, data, evaluation, security, privacy and inclusion |
| [docs/model/MODEL_CARD.md](./docs/model/MODEL_CARD.md) | Intended use, measured metrics, limitations and failure modes |
| [docs/model/EVALUATION.md](./docs/model/EVALUATION.md) | Held-out and challenge-set evaluation, closest-to-threshold analysis |
| [docs/data/DATASHEET.md](./docs/data/DATASHEET.md) | Dataset provenance, labelling and biases |
| [docs/safety/SAFETY_AND_LIMITATIONS.md](./docs/safety/SAFETY_AND_LIMITATIONS.md) | Residual risk, safeguards and disclosure |
| [docs/demo/DEMO_SCRIPT.md](./docs/demo/DEMO_SCRIPT.md) | Three-minute demonstration narrative |

---

## Licence

Code is licensed under the **MIT License**. Documentation and synthetic data are intended for release under **CC BY 4.0**. See [LICENSE](./LICENSE).

## Acknowledgements

Built for the #AI4Elections Hackathon 2026–2027, organised by Rise Networks with INEC and partners. Programme material remains the property of its owners. This repository contains no confidential programme documents.

> **Non-endorsement:** participation in the programme does not imply endorsement, certification, procurement or approval for deployment by INEC, Rise Networks or any partner. Any future pilot requires separate written authorisation.
