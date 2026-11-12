# Votex AI — Development & Winning Plan

**Programme:** #AI4Elections Hackathon 2026–2027
**Track:** Track 4 — Electoral Cybersecurity and Resilience
**Goal:** Win the overall grand prize and the Cybersecurity and Resilience Award.

> **Win condition:** a polished, working, reproducible prototype with a clear electoral story, measurable AI evaluation, visible privacy and inclusion, and a demo that cannot break. Architecture breadth does not win; evidence does.

---

## 1. Where we are now

| Item | Status |
| --- | --- |
| Architecture specification | Complete in `AI4Elections.md` |
| Hackathon alignment and MVP scope | Complete in `AI4Elections.md` (Sections 18–19) |
| Development plan | This document |
| Application submission | Due **12 November 2026, 11:59pm WAT** |
| Prototype sprint | **28 November – 13 December 2026** |
| Demo Day / Grand Finale | **15–16 December 2026** |
| Working prototype | Phase 3 complete — secure workflow spine, explainable hybrid AI analysis, indicator correlation and privacy-preserving dashboards |
| Submission documentation | Drafts started (threat model, model card, datasheet, safety, demo script) |
| Demo video | Not started |

### Non-negotiable dates

- **12 Nov 2026:** application closes.
- **18–19 Nov 2026:** onboarding and kickoff.
- **23–27 Nov 2026:** bootcamp, problem validation and mentor matching.
- **28 Nov – 13 Dec 2026:** build sprint and submission.
- **15–16 Dec 2026:** demo day, judging and grand finale.

We can start building before the sprint. That is an advantage. Use 9–27 November to build the foundation and the AI dataset so the sprint is about finishing, not starting.

---

## 2. The winning strategy

Track 4 rewards defensive, responsible, reproducible work. We will win by being the team that:

1. **Actually runs** a complete incident workflow — report, analyse, explain, correlate, assign, respond, audit.
2. **Proves integrity** with a SHA-256 hash chain, not just an audit-log table.
3. **Proves privacy** with k-anonymity suppression and re-identification tests.
4. **Proves inclusion** with Hausa, Yoruba and Igbo support, WCAG 2.2 AA and a low-bandwidth mode.
5. **Proves rigour** with a threat model, model card, datasheet, precision/recall/F1 metrics and a residual-risk register.
6. **Tells a human story** about an electoral officer receiving a fake INEC portal link, not a feature tour.

### The five demo moments judges must remember

1. A suspicious electoral phishing message becomes an incident with a risk score and reasons.
2. A second report shares an indicator and is automatically linked.
3. The national dashboard suppresses a small cell to protect organisations.
4. The audit chain detects tampering.
5. A user switches to Hausa and completes the workflow with a keyboard only.

---

## 3. Team model

Adapt to the actual team size. For two people, combine roles.

| Role | Responsibilities |
| --- | --- |
| Product / electoral lead | Problem statement, user journeys, demo script, judging narrative, partner/stakeholder language |
| Backend / security engineer | FastAPI, database, RBAC, evidence hashing, audit chain, k-anonymity, tests |
| AI / data engineer | Synthetic dataset, TF-IDF classifier, rules, risk scoring, evaluation, model card |
| Frontend / design engineer | React interface, design system, charts, accessibility, localisation, demo polish |
| Documentation / QA | Threat model, datasheet, safety statement, test evidence, video, submission package |

**Rule:** every feature has one owner and one reviewer. Nothing is "everyone's job".

---

## 4. Architecture at a glance

```text
React + TypeScript + Tailwind
        │
        ▼
FastAPI REST API  /api/v1
        │
        ├── PostgreSQL (system of record)
        ├── Local/MinIO evidence storage (SHA-256)
        ├── Hybrid AI engine
        │     ├── URL rules
        │     ├── NLP rules
        │     ├── TF-IDF + Logistic Regression
        │     └── weighted, explainable risk score
        ├── IOC extraction and correlation
        ├── Hash-chained audit log
        └── k-anonymity national aggregates
```

The prototype runs with **Docker Compose**. Analysis is synchronous in the MVP for demo reliability; the service boundaries allow a Celery worker later.

---

## 5. Phase plan

### Phase 0 — Foundation and application (9–12 November 2026)

**Objective:** Submit a strong application and leave a repository that can be built immediately.

- [ ] Confirm team, eligibility and 2–4 member rule with organisers. *(user action)*
- [ ] Submit the application before 12 November, 11:59pm WAT. *(user action)*
- [ ] Create the public repository from the hackathon template. *(blocked on GitHub account)*
- [x] Add `README.md`, `.env.example`, `.gitignore`, licence and Docker Compose.
- [x] Scaffold FastAPI, React + TypeScript + Vite and Tailwind.
- [x] Define the design system and colour tokens.
- [x] Create the synthetic-data generator and generate the dataset.
- [x] Draft the threat model, model card, datasheet and safety statement.
- [x] Freeze the MVP scope from `AI4Elections.md` Section 19.

**Exit criteria:** a fresh clone can start the stack and open a branded login screen.
**Status: met locally.** Docker could not be verified on this machine, so both services were started directly: backend health responded and the production frontend build rendered the login screen.

#### Phase 0 verification (9 November 2026)

| Check | Result |
| --- | --- |
| Synthetic dataset | 1,400 rows · 700/700 classes · 210 Hausa · SHA-256 `7c7c05e3…603a0` |
| Backend dependencies | Installed in `backend/.venv` |
| Backend tests | `4 passed` (`pytest`) |
| Backend health | `GET /api/v1/health` → `status: ok`, version `0.1.0` |
| Frontend dependencies | 180 packages installed |
| Frontend production build | TypeScript check passed; built in 7.11s (51.25 kB JS gzip, 5.19 kB CSS gzip) |
| Login screen | Rendered successfully on desktop and mobile viewports |
| Docker | Not verified — CLI unavailable or unresponsive on this machine |

#### Remaining Phase 0 user actions

1. Confirm team eligibility with the organisers.
2. Submit the application before **12 November 2026, 11:59pm WAT**.
3. Create the public repository from the official template and push this code.

> Phase 1 starts only after these are acknowledged, because repository and application status affect the submission.

### Phase 1 — Core platform (13–19 November 2026)

**Objective:** Build the secure workflow spine.

- [x] Organisations, users, roles and JWT authentication.
- [x] Organisation isolation on every incident and evidence query.
- [x] Incident submission, reference generation, list, detail and timeline.
- [x] Assignment, status transitions and response actions.
- [x] Evidence upload, MIME/size validation, SHA-256 and access logging.
- [x] Hash-chained audit log with verification endpoint.
- [x] Seed two organisations and synthetic incidents.

**Exit criteria:** Organisation A cannot read Organisation B's incident or evidence; the audit chain verifies.

#### Phase 1 verification (9 November 2026)

| Check | Result |
| --- | --- |
| Backend tests | `25 passed` (`pytest -q`, 27.03s) |
| Auth | Argon2id hashing, HS256 JWT, `admin`/`analyst`/`reporter` roles, generic credential errors |
| Tenant isolation | Cross-tenant incident and evidence reads return 404; verified by API tests |
| Reporter scope | Reporters list and open only their own submissions; verified by API and browser checks |
| Evidence | MIME, extension, magic-byte and size validation · SHA-256 · UUID storage names · audited download |
| Audit chain | 39 entries verify from genesis; tampering is detected at the altered entry and restore re-verifies |
| Live API | `health: ok` · `database: ok` · `evidence: ok` · 6 org-1 incidents · 32 org-1 audit entries |
| Frontend build | `npm run build` passed · 275.23 kB JS (83.15 kB gzip) · 32.28 kB CSS (6.99 kB gzip) |
| Browser verification | Login, overview, queue, incident detail, audit, reporter restriction and report form rendered with **0 JS errors** |
| Screenshots | `docs/demo/screenshots/phase1-{login,overview,incidents,incident-detail,audit,report}-1440x1000.png` |

**Status: met locally.** Both services were started directly rather than through Docker. The live database contains the deterministic demo tenant and a valid audit chain.

### Phase 2 — Hybrid AI engine (20–26 November 2026)

**Objective:** Make the intelligence credible and explainable.

- [x] Generate a labelled synthetic electoral-phishing dataset.
- [x] Train TF-IDF + Logistic Regression; save model and metrics.
- [x] Implement URL feature extraction and security rules.
- [x] Implement NLP signals for urgency, credential requests and impersonation.
- [x] Combine URL, NLP, ML and rules with the 0.30/0.25/0.25/0.20 weights.
- [x] Return reasons, confidence, model version and analysis timestamp.
- [x] Evaluate precision, recall, F1, false positives and false negatives.
- [x] Build the analysis UI with a risk gauge and reason list.

**Exit criteria:** one benign and one suspicious example produce explainable, reproducible results with recorded metrics.

#### Phase 2 verification (9 November 2026)

| Check | Result |
| --- | --- |
| Training dependencies | scikit-learn 1.6.0 · joblib 1.4.2 · NumPy 2.2.1 · SciPy 1.15.0 |
| Model | `hybrid-v0.2.0` · 435,834-byte artefact · dataset SHA-256 `7c7c05e3…603a0` |
| Held-out set | 350 rows · precision/recall/F1 1.000 · Brier 0.0006 · TN 175 / FP 0 / FN 0 / TP 175 |
| Cross-validation | 5-fold F1 1.000 ± 0.000 |
| Challenge set | 28 hand-written cases · 0 errors · F1 1.000 · Brier 0.0265 |
| Closest cases | `ch-024` benign p=0.4407 (margin 0.059); `ch-027` phishing p=0.6303 |
| Honest limit | Perfect synthetic scores; challenge Brier 44× worse; no real-world claim |
| Backend tests | `32 passed` (`pytest -q`, 22.54s) |
| Live API | 6/6 incidents analysed · audit chain valid (58 entries) · `incident.analysed` recorded |
| Frontend build | `npm run build` passed · 286.70 kB JS (85.95 kB gzip) · 33.87 kB CSS (7.24 kB gzip) |
| Browser verification | Analysis panel, risk gauge, formula, band, model chip, reasons, indicators, confidence, re-run and audit entries rendered with **0 JS errors** |
| Screenshots | `docs/demo/screenshots/phase2-{analysis-high-risk,analysis-suspicious,analysis-payment-fraud,incidents,audit}-1440x1000.png` |
| Engine tests | Automatic analysis, benign vs malicious ordering, determinism, RBAC, tenant isolation, backfill |
| Docs | Model card and evaluation report published with measured values |

**Status: met locally.** Analysis is advisory, deterministic, offline and explainable. The model does not inspect images or attachments.

### Phase 3 — Intelligence and dashboards (27 November – 2 December 2026)

**Objective:** Turn incidents into situational awareness.

- [x] Extract URLs, domains, IPs and file hashes.
- [x] Link incidents sharing an indicator.
- [x] Build the indicator search and related-incidents view.
- [x] Build organisation and national dashboards.
- [x] Apply k-anonymity suppression (k ≥ 5) in the query layer.
- [x] Add trend, severity and category charts.
- [x] Add CSV export with permission checks.

**Exit criteria:** two synthetic incidents link through a shared indicator; a small national cell is suppressed.

#### Phase 3 verification (11 November 2026)

| Check | Result |
| --- | --- |
| Indicator extraction | Deterministic, offline, no link resolution · URL, domain, IPv4, SHA-256 and MD5 · source priority `reported_url` → report text → evidence · official, platform and documentation hosts excluded |
| Correlation | Organisation-scoped exact matching · 5 shared indicators in the demo authority · 9 of 10 reports linked |
| Related incidents | `GET /incidents/{id}/related` returns shared indicator values; A10002 shows 3 linked cases, A10010 links to A10001 through URL, domain and an identical evidence SHA-256 |
| Indicator intelligence | Search, kind filter, pagination, linked-incident detail and permission-checked CSV · reporters receive `403` |
| Organisation dashboard | Exact counts: 10 incidents, 9 open, 7 high-risk, 5 shared indicators, mean risk 65.2 |
| National dashboard | 13 incidents across 2 organisations · top PVC URL/domain: 5 linked incidents each across 2 tenants · 39 cells suppressed |
| k-anonymity | Suppression applied in `backend/app/services/correlation.py`, not the browser; suppressed values are `null` in JSON and blank in CSV |
| CSV exports | Indicator, organisation and national exports emit CSV · every export writes `intelligence.exported` to the audit chain |
| Backend tests | **`40 passed`** (`pytest -q`, 47.07s) including `test_iocs.py` and `test_correlation.py` |
| Frontend build | `npm run build` passed · 324.36 kB JS (94.55 kB gzip) · 38.95 kB CSS (7.86 kB gzip) |
| Browser verification | Intelligence, organisation dashboard, national dashboard, related incidents, audit and overview rendered with **0 JS errors** |
| Screenshots | `docs/demo/screenshots/phase3-{intelligence,dashboard-organisation,dashboard-national,related-incidents,audit,overview}-1440x1000.png` |
| Demo data | Enriched seed creates overlapping indicators across both tenants so a fresh clone demonstrates correlation without manual setup |

**Status: met locally.** Correlation is advisory and explainable; the extractor never visits a link. National aggregates are suppressed before serialisation, and every export is audited.

### Phase 4 — Inclusion and experience (3–7 December 2026)

**Objective:** Convert a good tool into an inclusive, memorable product.

- [x] English + Hausa interface for key screens.
- [x] Yoruba and Igbo coverage if time allows.
- [x] WCAG 2.2 AA: keyboard, focus, labels, contrast, screen-reader text.
- [x] Low-bandwidth layout and compressed assets.
- [x] Plain-language incident reporting.
- [x] Responsive desktop, tablet and mobile layouts.
- [x] Empty, loading, error and success states.
- [x] Design polish: typography, spacing, charts and severity cues.

**Exit criteria:** a keyboard-only user can submit a report and switch language.

| Evidence | Result |
| --- | --- |
| Locales | Four complete dictionaries (`en`, `ha`, `yo`, `ig`) typed against the English key set; missing keys fail `tsc` |
| Language persistence | `<html lang>` and `localStorage["votex.lang"]` verified for all four locales |
| Keyboard-only exit test | `Tab` to the Igbo switcher, `Enter`, type title and description, `Enter` on **“Zipu akụkọ”**, land on `/incidents/{uuid}` with the Igbo success banner |
| Responsive sweep | `/`, `/incidents`, `/report`, `/intelligence`, `/dashboards`, `/audit` × 390/768/1024/1440 px: **0 horizontal overflows, 0 browser errors** |
| Accessibility mechanics | Skip link, route-change focus, live page announcement, `role="alert"` errors, `role="status"` success, localised status/priority/category, contrast sweep |
| Low bandwidth | `prefers-reduced-data` drops grid, blur, shadows and animation; `prefers-reduced-motion` stops animation; no external fonts or media |
| Frontend build | `npm run build` passed · 377.90 kB JS (109.88 kB gzip) · 39.70 kB CSS (7.96 kB gzip) |
| Backend regression | **`40 passed`** (`pytest -q`, 47.07s) |
| Screenshots | `docs/demo/screenshots/phase4-*.png` (nine images) |
| Evidence document | [docs/security/ACCESSIBILITY_AND_LOCALISATION.md](./docs/security/ACCESSIBILITY_AND_LOCALISATION.md) |

**Status: met locally.** The keyboard-only exit criterion passed against live
synthetic data. Analyst case records, AI explanations and dashboards remain
English-only and display a visible notice; native-speaker review and an
automated axe run are listed as Phase 6 hardening, not claimed as done.

### Phase 5 — Resilience and simulation (8–10 December 2026)

**Objective:** Add Track 4 depth if the MVP is already safe.

- [x] Lightweight resilience assessment with findings and remediation status.
- [x] One synthetic phishing-triage exercise with task tracking.
- [x] Exercise performance summary.
- [ ] Offline-tolerant incident draft queue. *(deferred: outside the Phase 5 scope chosen for this cycle and listed for Phase 6 hardening)*

**Exit criteria:** one assessment and one exercise complete without touching a real system.

| Evidence | Result |
| --- | --- |
| Questionnaire | Fixed 12 controls across 6 categories · maturity 0–4 · equal weights · score = mean maturity × 100 |
| Bands | `fragile < 40`, `developing 40–69.9`, `resilient >= 70`; bands and severity colours match the rest of the interface |
| Findings | Auto-generated for answers ≤ 2 (0 = critical, 1 = high, 2 = medium) with remediation status, owner and audit note persisted per finding |
| Exercise | One fixed synthetic phishing-wave triage with six tracked tasks (boundary check, triage, indicators, containment, notification, decision note) |
| Performance | Completion percentage, elapsed time, resolved/skipped counts and a `ready` / `developing` / `needs_review` grade |
| API | 11 endpoints under `/api/v1/resilience`; every read and write is organisation-scoped and cross-tenant reads return 404 |
| Audit | `resilience.assessment_created`, `resilience.finding_updated`, `resilience.exercise_created`, `resilience.exercise_task_updated`, `resilience.exercise_completed` |
| Demo data | Baseline assessment **50.0 (developing)** and latest assessment **70.8 (resilient)** with 9/13 open findings; one completed exercise (5 done, 1 skipped) |
| Backend tests | **`52 passed`** (`pytest -q`, 56.62s) — 40 existing + 12 Phase 5 tests |
| Frontend build | `npm run build` passed · 410.76 kB JS (116.96 kB gzip) · 41.49 kB CSS (8.21 kB gzip) |
| Browser verification | `/resilience` assessments, new-assessment form, exercises and 390×844 mobile: **0 console errors, 0 px horizontal overflow** |
| Role check | Reporter sees the analyst-only notice, no nav entry and no assessment/exercise data |
| Screenshots | `docs/demo/screenshots/phase5-resilience-{assessments,new-assessment,exercises}-1440x1000.png` and `phase5-resilience-mobile-390x844.png` |
| Evidence document | [docs/security/RESILIENCE_AND_EXERCISES.md](./docs/security/RESILIENCE_AND_EXERCISES.md) |

**Status: met locally.** The exit criterion passed: an analyst completed an
assessment and the synthetic exercise without contacting any real system. The
module is analyst-only and English-only with the visible `common.englishOnly`
notice; nav and page chrome are localised in all four languages. The
offline-tolerant draft queue was consciously deferred.

> If the MVP is behind, skip this phase. Never trade core reliability for extra modules.

### Phase 6 — Hardening and submission (11–13 December 2026)

**Objective:** Make the work defensible and submittable.

- [ ] Full test pass: unit, API, tenant isolation, privacy, audit, accessibility.
- [ ] Fresh-clone test on a clean machine.
- [ ] Threat model and finding-to-control matrix.
- [ ] Model card, datasheet and safety/limitations statement.
- [ ] Problem statement, methodology and evidence pack.
- [ ] Three-minute demo video.
- [ ] Final README and architecture diagram.
- [ ] Public repository and open licence.
- [ ] Submit before the 13 December deadline.

**Exit criteria:** the submission package is complete and the demo runs twice from a clean environment.

### Phase 7 — Demo and finale (14–16 December 2026)

- [ ] Rehearse the three-minute demo at least five times.
- [ ] Prepare a 60-second backup pitch.
- [ ] Prepare answers for security, privacy, bias and feasibility questions.
- [ ] Test the demo on the presentation machine and a backup laptop.
- [ ] Record a screen capture as a fallback.
- [ ] Prepare the judging narrative: problem, evidence, safeguards, impact.

---

## 6. Backlog

### Must-have

| ID | Feature | Phase | Acceptance |
| --- | --- | --- | --- |
| M1 | JWT login and RBAC | 1 | Demo users log in; unauthorised role is denied |
| M2 | Organisation isolation | 1 | Cross-tenant incident and evidence access returns 403/404 |
| M3 | Incident lifecycle | 1 | Submit, assign, respond, close with timeline |
| M4 | Evidence integrity | 1 | Upload, hash, download and verify |
| M5 | Hash-chained audit | 1 | Verify passes; tampering is detected |
| M6 | Hybrid analysis | 2 | Score, reasons and model version returned |
| M7 | AI evaluation | 2 | Precision, recall, F1 and failure cases documented |
| M8 | IOC correlation | 3 | Two incidents link through a shared indicator |
| M9 | National dashboard | 3 | k ≥ 5 suppression demonstrated |
| M10 | Inclusion baseline | 4 | English + Hausa, keyboard-only flow, WCAG checks |
| M11 | Reproducible demo | 6 | Fresh clone starts and seeds with one command |
| M12 | Submission docs | 6 | Model card, datasheet, safety, video, README |

### Should-have

- Yoruba, Igbo and Pidgin translations.
- Resilience assessment.
- One simulation exercise.
- CSV export.
- Analyst feedback capture.
- Notification centre.
- Indicator relationship graph.
- Offline draft queue.
- Isolation Forest anomaly detection.

### Deferred

- MFA/SSO.
- Differential privacy.
- Kubernetes or multi-cloud.
- SIEM/threat-intel integrations.
- Mobile apps.
- Deep learning or LLMs.
- Full 13-screen product.
- Real institutional integrations.

---

## 7. Design system

### Colour tokens

| Token | Hex | Use |
| --- | --- | --- |
| `void` | `#05080F` | Page background |
| `surface` | `#0A1220` | Panels and cards |
| `surface-2` | `#101C30` | Elevated panels |
| `line` | `#1C2C46` | Borders and dividers |
| `text` | `#E9F1FB` | Primary text |
| `muted` | `#8BA2BD` | Secondary text |
| `brand` | `#22D3EE` | Primary accent, active states |
| `brand-2` | `#3B82F6` | Secondary accent, charts |
| `violet` | `#A78BFA` | AI/intelligence accents |
| `success` | `#34D399` | Resolved, verified |
| `warning` | `#FBBF24` | Moderate risk |
| `danger` | `#F87171` | High/critical risk |
| `critical` | `#FB7185` | Critical incidents |

### Visual language

- Dark-first cybersecurity operations centre.
- Subtle radial gradients and a faint grid background.
- Glass panels with 1px borders and soft cyan glow on active elements.
- Severity is never colour-only: pair colour with text and an icon.
- Typography: Inter for interface, JetBrains Mono for references, hashes and indicators.
- Motion: 150–220ms ease-out; no decorative animation during incident data.
- Charts: restrained cyan/blue; amber and red only for risk.

### Component rules

- Every page has a title, a one-line purpose and a primary action.
- Every async view has loading, empty, error and success states.
- Every destructive action asks for confirmation.
- Every table has a clear empty state and accessible headers.
- Every form field has a visible label and inline error.
- Focus rings are always visible.

---

## 8. Definition of done

- [ ] Fresh clone starts with Docker Compose and one seed command.
- [ ] All 13 demonstration tests pass twice.
- [ ] Cross-tenant access is denied for incidents and evidence.
- [ ] Audit chain verifies and tamper detection works.
- [ ] National aggregates suppress cells below k = 5.
- [ ] AI results include reasons and version.
- [ ] English + Hausa and keyboard-only flow work.
- [ ] Threat model, model card, datasheet and safety statement are complete.
- [ ] Three-minute video is recorded.
- [ ] No live systems, real personal data or confidential material.
- [ ] Public repository with open licence.

---

## 9. Risk register

| Risk | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- |
| Scope creep | High | High | Freeze MVP; cut should-haves first |
| Demo fails on the day | Medium | High | Offline demo, seeded data, recorded fallback |
| AI metrics are weak | Medium | Medium | Small labelled synthetic set, report honestly, show rules fallback |
| Frontend takes too long | Medium | High | Build core screens first; use a small component library |
| Team member unavailable | Medium | High | Pair on critical modules; document setup |
| Docker unavailable on demo machine | Medium | High | Provide local run instructions and a recorded demo |
| Security claim is challenged | Low | High | Threat model, tests, residual-risk register |
| Inclusion is an afterthought | Medium | Medium | i18n and accessibility in Phase 4, not the last day |
| Confidential material leaked | Low | High | Keep PDFs out of the public repo; add `.gitignore` |

---

## 10. Daily cadence

- **Morning (15 min):** what shipped, what is blocked, what is the demo moment today.
- **Build:** one vertical slice at a time; merge small.
- **Evening (10 min):** update this plan, run tests, record a screenshot or clip.
- **Friday:** full demo run and cut-line review.

---

## 11. Immediate next build order

1. Repository, README, Docker Compose and design tokens.
2. FastAPI health endpoint, database models and seed.
3. Authentication and tenant isolation.
4. Incident workflow.
5. Evidence and audit chain.
6. AI dataset, model and analysis endpoint.
7. Frontend shell and login.
8. Dashboard, incidents and incident detail.
9. IOC correlation and audit screens.
10. Inclusion, docs and demo.

> Build the demo backwards: start with the five demo moments and implement only what makes them real.
