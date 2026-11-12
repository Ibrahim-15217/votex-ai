# Resilience Assessment and Synthetic Exercise Evidence

Phase 5 adds the Track 4 depth layer that sits on top of the incident workflow:
a reproducible organisational readiness assessment and one synthetic
phishing-triage exercise with task tracking and an after-action summary. This
document records the questionnaire, the scoring rules, the exercise lifecycle,
the tenancy and audit guarantees, and the browser evidence captured on
**12 November 2026**.

Scope: `/resilience` in the analyst console and the `/api/v1/resilience` API. The
module is analyst-only and English-only, with the same visible
`common.englishOnly` notice used by the analyst dashboards and case records. Nav
and page chrome are localised in all four interface languages.

The module never contacts a real mailbox, portal, mail provider or electoral
system. Every artefact in the exercise is written text created for the demo.

---

## 1. Access model

| Role | Can open `/resilience` | Can read assessments | Can read exercises |
| --- | --- | --- | --- |
| `admin` | Yes | Yes, own organisation | Yes, own organisation |
| `analyst` | Yes | Yes, own organisation | Yes, own organisation |
| `reporter` | Direct URL only | No (`403`) | No (`403`) |

- The navigation item is rendered only for `admin` and `analyst`
  (`analystOnly: true` in `frontend/src/components/AppShell.tsx`).
- A reporter who types `/resilience` sees the role notice, not the workspace. The
  page short-circuits before any resilience request is sent, so no readiness data
  reaches the browser.
- Every endpoint depends on `AnalystUser`, which rejects reporters with `403`
  before the service layer runs.
- Every service query filters on `organisation_id == user.organisation_id`. A
  record owned by another tenant returns `404`, not `403`, so the response does not
  disclose that the record exists. This matches the incident and evidence rules.

Verified in the browser on 12 November 2026: reporter session → 0 px overflow,
no nav entry, role notice visible, no assessment or exercise content rendered,
0 console errors.

---

## 2. Readiness questionnaire

The questionnaire is fixed in `backend/app/core/resilience.py` and is identical
for every organisation. A fixed instrument keeps scores comparable over time and
prevents a user from quietly redefining what "resilient" means.

Twelve controls across six categories:

| Category | Control keys | Focus |
| --- | --- | --- |
| Governance & planning | `governance.owner`, `governance.plan`, `governance.vendor` | Named owner, tested response plan, supplier checks |
| Identity & access | `identity.mfa`, `identity.privileged`, `identity.phishing_resistant` | MFA, least privilege, phishing-resistant privileged access |
| Network & email | `network.inventory`, `network.email` | Asset and patch cadence, SPF/DKIM/DMARC enforcement |
| Data protection | `data.backup`, `data.retention` | Encrypted restore-tested backups, minimisation and retention |
| Response & recovery | `response.exercise` | Tabletop exercise in the last 12 months |
| People & awareness | `people.awareness` | Role-based security awareness |

The split is three governance controls, three identity controls, two network,
two data, one response and one people control — twelve in total.

Each control is answered on a five-point maturity scale:

| Value | Label |
| --- | --- |
| 0 | Not started |
| 1 | Planned |
| 2 | Partially implemented |
| 3 | Implemented |
| 4 | Implemented and verified |

The API validates that every control is present, that no unknown keys are sent,
and that every answer is an integer from 0 to 4. An incomplete or malformed
answer set is rejected with a `422` and nothing is written.

---

## 3. Scoring

Equal weights are used deliberately. The score is the mean maturity across the
fixed controls, scaled to 100:

```
score = round(100 × Σ answerᵢ / (4 × 12), 1)
```

Bands:

| Score | Band | Interface tone |
| --- | --- | --- |
| `< 40` | `fragile` | Danger (red) |
| `40 – 69.9` | `developing` | Warning (amber) |
| `>= 70` | `resilient` | Success (green) |

The same computation exists in one place
(`backend/app/core/resilience.py::score_answers`) and is shared by the API, the
demo seed and the tests. The recorded answers are stored with the assessment, so
the score can always be recomputed. An assessment is never edited in place; a new
one is created when the posture changes.

The interface also shows a live projected score and band while the form is being
filled, using the same arithmetic, so the analyst can see the effect of an answer
before submitting.

---

## 4. Findings and remediation

A control answered at **2 or below** opens one finding, because "partially
implemented" is not yet a defensible control:

| Answer | Finding severity |
| --- | --- |
| 0 | `critical` |
| 1 | `high` |
| 2 | `medium` |
| 3 or 4 | No finding |

Each finding carries the control title, a remediation sentence written for that
control, its severity, a remediation status, an optional owner, an optional due
date and timestamps. Findings are stored per organisation, not just per
assessment, so the readiness summary can count open findings across the history.

Remediation status lifecycle:

```
open → in_progress → resolved
       ↘ accepted (risk consciously retained)
```

- `resolved` findings drop out of the open count; `accepted` findings stay open
  because the risk is still present.
- An update can change the status, owner or due date and can attach a short audit
  note. Every update appends `resilience.finding_updated` with the before/after
  status, the severity and the note.
- Findings reference the fixed control text, not free-form user input, so a
  finding cannot be reworded into something the questionnaire did not measure.

---

## 5. Synthetic exercise

One fixed scenario, `phishing-triage-v1`, titled **Synthetic phishing-wave
triage**. Starting an exercise creates a fresh copy of the scenario with six
ordered tasks:

| # | Task | Expected action |
| --- | --- | --- |
| 1 | Confirm the safe exercise boundary | State the boundary and confirm synthetic data only |
| 2 | Triage the first report | Classify credential phishing and identify the target group |
| 3 | Extract and record indicators | Record the sender domain, lookalike URL and SHA-256 hash |
| 4 | Link the second report | Connect both reports through the shared indicator |
| 5 | Recommend containment | Block the domain, warn staff, reset exposed credentials |
| 6 | Record the decision and close | Separate observed facts from inferences and note follow-ups |

Task statuses:

```
pending → in_progress → done
                      ↘ skipped
```

- Recording `done` or `skipped` stamps `completed_at` and the acting user.
  Moving a task back to `pending` or `in_progress` clears those fields.
- An exercise can only be completed when every task is `done` or `skipped`;
  otherwise the API returns `409` with the number of tasks still open.
- Once completed, the exercise and its task record are read-only. A task update
  returns `409` rather than silently rewriting the after-action record. Completion
  is idempotent.
- The scenario text, task order and expected actions are fixed in
  `backend/app/core/resilience.py`, so two organisations rehearse the same
  scenario and exercise results are comparable.

---

## 6. Performance summary

The performance summary is computed from the recorded task states:

| Field | Meaning |
| --- | --- |
| `tasks_total` | Number of tasks in the scenario |
| `tasks_done` | Tasks recorded as `done` |
| `tasks_skipped` | Tasks recorded as `skipped` |
| `tasks_resolved` | `done + skipped` |
| `completion_pct` | `100 × done / total`, one decimal |
| `elapsed_seconds` | Completed/current time minus start time, never negative |
| `grade` | `ready`, `developing` or `needs_review` |
| `note` | One-line explanation of the grade |

Grade rules:

- **ready** — every task resolved and at least 80% done.
- **developing** — at least 50% done.
- **needs_review** — less than 50% done.

SQLite returns naive timestamps while insertion uses timezone-aware UTC. The
service normalises both sides with `_as_utc()` before subtracting, which fixes the
naive/aware crash that appeared during development and keeps the elapsed time
identical on SQLite and PostgreSQL.

---

## 7. API surface

Eleven endpoints under `/api/v1/resilience`. All require an analyst or admin and
are scoped to the caller's organisation.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/questionnaire` | Fixed controls, maturity labels and scoring note |
| `GET` | `/summary` | Latest score, totals and open findings by severity |
| `GET` | `/assessments` | Assessment history, newest first |
| `POST` | `/assessments` | Score a complete answer set and open findings |
| `GET` | `/assessments/{id}` | Assessment detail with answers and findings |
| `PATCH` | `/findings/{id}` | Update remediation status, owner, due date or note |
| `GET` | `/exercises` | Exercise history, newest first |
| `POST` | `/exercises` | Start the fixed scenario with six tasks |
| `GET` | `/exercises/{id}` | Exercise detail with tasks and performance |
| `PATCH` | `/exercises/{id}/tasks/{task_id}` | Record task status and decision note |
| `POST` | `/exercises/{id}/complete` | Close an exercise once every task is resolved |

Errors:

| Code | When |
| --- | --- |
| `401` | Missing or invalid bearer token |
| `403` | Reporter calls an analyst endpoint |
| `404` | Record missing **or** owned by another tenant |
| `409` | Updating a closed exercise, or completing one with open tasks |
| `422` | Missing control, unknown control key, answer outside 0–4, invalid field |

---

## 8. Data model

Four tables, all carrying `organisation_id`:

| Table | Key fields |
| --- | --- |
| `resilience_assessments` | `id` (UUID), `organisation_id`, `created_by_id`, `title`, `notes`, `status`, `assessment_date`, `score`, `band`, `answers_json`, `summary` |
| `resilience_findings` | `id`, `assessment_id`, `organisation_id`, `category`, `title`, `detail`, `severity`, `remediation_status`, `owner`, `due_date` |
| `exercises` | `id` (UUID), `organisation_id`, `created_by_id`, `scenario_key`, `title`, `summary`, `status`, `started_at`, `completed_at` |
| `exercise_tasks` | `id`, `exercise_id`, `organisation_id`, `sequence`, `title`, `description`, `expected_action`, `status`, `notes`, `completed_by_id`, `completed_at` |

Indexes cover organisation + assessment date, organisation + finding status,
organisation + exercise creation, and exercise + task sequence. Deleting an
assessment cascades to its findings; deleting an exercise cascades to its tasks.
Deleting a user sets the author/completer references to `NULL` rather than
deleting organisational records.

---

## 9. Audit events

Every write appends to the existing SHA-256 hash-chained audit log:

| Action | Recorded detail |
| --- | --- |
| `resilience.assessment_created` | Score, band, number of findings, title |
| `resilience.finding_updated` | Assessment id, from/to status, severity, note |
| `resilience.exercise_created` | Scenario key and task count |
| `resilience.exercise_task_updated` | Exercise id, sequence, from/to status |
| `resilience.exercise_completed` | Completion percentage, done/skipped counts, grade |

Phase 5 writes go through the same `record_audit()` helper as incidents and
exports, so the chain remains global across tenants and `GET /api/v1/audit/verify`
still reports a valid chain after resilience activity. A dedicated test asserts
this after creating an assessment, a finding update and a completed exercise.

---

## 10. Demo data

`seed_resilience_demo()` creates deterministic data for the Votex Demo Authority
when no assessment exists yet:

- **Baseline assessment — 50.0 (`developing`)** with a weaker answer set, kept to
  show the improvement over time.
- **Latest assessment — 70.8 (`resilient`)** from the answers in
  `seeded_answers()`. Four controls are still below "implemented", so four
  findings are opened from this assessment.
- **9 of 13 findings open** across both assessments, with severity counts shown
  in the summary tiles.
- **One completed exercise** with five tasks done and one skipped, producing a
  `ready` grade and a realistic elapsed time.

The seed is idempotent: it only runs when the organisation has no assessments, so
restarting the API does not duplicate records.

---

## 11. Safety boundaries

- The exercise uses written synthetic artefacts only. It does not open a URL,
  resolve a domain, send an email or contact a mail provider.
- No real mailbox, credential, voter record, biometric or live electoral system is
  involved. The expected actions are advisory text for a tabletop discussion.
- Assessment and simulation results are decision-support material, not a certified
  audit or compliance attestation. The questionnaire is explicitly described as a
  prototype readiness check, not a certified index.
- The module cannot create, edit or delete incidents, evidence or audit entries; it
  only appends its own audited records.

---

## 12. Verification evidence

Captured on **12 November 2026** against a freshly seeded SQLite database.

| Check | Result |
| --- | --- |
| Backend suite | **`52 passed`** (`pytest -q`, 56.62s) — 40 existing + 12 Phase 5 |
| Questionnaire | `200` · 12 controls · 6 categories |
| Summary | 2 assessments · 9/13 findings open · latest **70.8 (`resilient`)** |
| Exercises | 1 total · 1 completed |
| Desktop assessments | 0 console errors · 0 px horizontal overflow |
| New-assessment form | 0 console errors · 0 px horizontal overflow |
| Exercises tab | 0 console errors · 0 px horizontal overflow |
| Mobile 390 × 844 | 0 console errors · 0 px horizontal overflow |
| Reporter direct access | Role notice shown · no nav entry · no resilience data · 0 console errors · 0 px overflow |
| Frontend build | `npm run build` passed · 410.76 kB JS (116.96 kB gzip) · 41.49 kB CSS (8.21 kB gzip) |

Screenshots:

- `docs/demo/screenshots/phase5-resilience-assessments-1440x1000.png`
- `docs/demo/screenshots/phase5-resilience-new-assessment-1440x1000.png`
- `docs/demo/screenshots/phase5-resilience-exercises-1440x1000.png`
- `docs/demo/screenshots/phase5-resilience-mobile-390x844.png`

Phase 5 tests in `backend/tests/test_resilience.py` cover the fixed control set,
scoring and finding generation, perfect scores with no findings, incomplete and
unknown answers, reporter denial, assessment and exercise tenancy, finding
remediation auditing, summary ordering, the full exercise lifecycle, seeded demo
data, and audit-chain validity after resilience writes.

---

## 13. Reproduce

```powershell
# Backend (from backend/)
Remove-Item votex.db -ErrorAction SilentlyContinue
.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
.venv\Scripts\python.exe -m pytest -q          # expect 52 passed

# Frontend (from frontend/)
npm run dev                                     # http://localhost:5173
npm run build                                   # expect the sizes above
```

Sign in as `analyst@votex.demo` with `VotexDemo!23`, open **Resilience**, then:

1. Open the latest assessment and expand a finding; change its status and save.
2. Open **New**, answer the 12 controls and watch the live score, then submit.
3. Switch to **Synthetic exercises**, open the completed run, or start a fresh one
   and record tasks until **Complete exercise** is enabled.

Sign in as `reporter@votex.demo` and open `/resilience` directly: the role notice
appears and no readiness data is rendered.

---

## 14. Limitations

- Equal weights are a deliberate prototype choice; a real deployment needs a
  sector-reviewed weighting scheme, and the stored answers allow it to be
  recomputed.
- Twelve controls are a summary instrument, not a substitute for a full control
  framework or an independent audit.
- The exercise is a single fixed scenario. Task completion is self-reported and not
  timed against a service-level objective.
- Scores and grades are advisory. They do not certify readiness and must not be
  presented as compliance attestations.
- The module is English-only in this phase; localisation of assessment content is
  future work, and the interface says so.
- The offline-tolerant draft queue was deferred and is not claimed as delivered.
