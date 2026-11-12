# Submission Checklist

**Application deadline:** 12 November 2026, 11:59pm WAT
**Prototype deadline:** 13 December 2026

Status as of **12 November 2026**. The application has been submitted; work now
targets the **13 December 2026** prototype deadline. Items marked **User** need
a human decision, credentials or a recording; items marked **Done** are in the
repository.

---

## 1. Application (submitted 12 November 2026)

| Item | Status | Notes |
| --- | --- | --- |
| Team size 2–4 and eligibility confirmed | **Done** | Cyber Defenders — three members |
| Track selected | **Done** | Track 4 — Electoral Cybersecurity & Resilience |
| Project name and one-line pitch | **Done** | Votex AI — securing elections through intelligent cybersecurity |
| Problem statement (max one page) | **Done** | [PROBLEM_STATEMENT.md](./PROBLEM_STATEMENT.md) |
| Methodology summary | **Done** | [METHODOLOGY.md](./METHODOLOGY.md) |
| Working prototype link | **Done** | https://github.com/Ibrahim-15217/votex-ai |
| Declarations: nonpartisan, no live systems, synthetic data, human oversight | **Done** | Confirmed on the form |
| AI-tool assistance disclosed | **Done** | Section 9 of [METHODOLOGY.md](./METHODOLOGY.md) |
| Contact person and phone | **Done** | Ibrahim Musa Mahmud |
| Application submitted and receipt saved | **Partial** | Submitted 12 Nov 2026 — **save the confirmation screenshot/email** |

Application answer drafts with placeholders: [APPLICATION_DRAFT.md](./APPLICATION_DRAFT.md).
Field-by-field, copy-paste answers for the live portal (5 steps):
[APPLICATION_FORM_ANSWERS.md](./APPLICATION_FORM_ANSWERS.md).

---

## 2. Minimum submission package

| Artifact | Status | Location |
| --- | --- | --- |
| Working prototype | **Done** | `backend/`, `frontend/`, `docker-compose.yml` |
| Public repository with open licence | **Done** | https://github.com/Ibrahim-15217/votex-ai — MIT in [LICENSE](../../LICENSE) |
| Problem statement | **Done** | [PROBLEM_STATEMENT.md](./PROBLEM_STATEMENT.md) |
| Methodology | **Done** | [METHODOLOGY.md](./METHODOLOGY.md) |
| Evidence: metrics, screenshots, failure cases | **Done** | [../model/EVALUATION.md](../model/EVALUATION.md), [../demo/screenshots/](../demo/screenshots/) |
| Model / system card | **Done** | [../model/MODEL_CARD.md](../model/MODEL_CARD.md) |
| Safety and limitations | **Done** | [../safety/SAFETY_AND_LIMITATIONS.md](../safety/SAFETY_AND_LIMITATIONS.md) |
| Data sheet | **Done** | [../data/DATASHEET.md](../data/DATASHEET.md) |
| Threat model | **Done** | [../security/THREAT_MODEL.md](../security/THREAT_MODEL.md) |
| Privacy evidence | **Done** | [../security/PRIVACY_AND_CORRELATION.md](../security/PRIVACY_AND_CORRELATION.md) |
| Accessibility evidence | **Done** | [../security/ACCESSIBILITY_AND_LOCALISATION.md](../security/ACCESSIBILITY_AND_LOCALISATION.md) |
| Three-minute demo video | **User** | Script: [../demo/DEMO_SCRIPT.md](../demo/DEMO_SCRIPT.md) |
| Fresh-clone test | **Done** | **PASS** at `f67cd47` — [FRESH_CLONE_VERIFICATION.md](./FRESH_CLONE_VERIFICATION.md) |
| Demonstration tests (13 scenarios) | **Partial** | Covered by the demo script; record the run |

---

## 3. Repository safety checks (run before every push)

```powershell
# 1. Confidential programme material must never be tracked
git ls-files | Select-String -Pattern "Concept_Doc_|INEC_ICT_Director_Remarks"

# 2. No environment secrets, databases or uploads
git ls-files | Select-String -Pattern "^\.env$|\.db$|\.sqlite3$|storage/"

# 3. No node_modules or virtual environments
git ls-files | Select-String -Pattern "node_modules/|\.venv/"

# 4. No live data, real names or personal contact details
git grep -n -I -E "password\s*=\s*['\"][^'\"]+|BEGIN (RSA|OPENSSH) PRIVATE KEY"
```

Expected result for checks 1–3: **no output**. The confidential PDFs and local
database are already listed in [.gitignore](../../.gitignore).

> If a confidential file was ever committed, do not simply delete it in a new
> commit. Treat the history as exposed, rotate anything sensitive, and rewrite
> history before publishing.

---

## 4. Fresh-clone test

**Result (12 November 2026): PASS at `f67cd47`.** Full commands, outputs and the
PASS/FAIL table are in
[FRESH_CLONE_VERIFICATION.md](./FRESH_CLONE_VERIFICATION.md). Screenshots of all
six routes from the clean checkout are in
[evidence/fresh-clone/](./evidence/fresh-clone/).

Run again on a machine that has never seen the project:

```bash
git clone <public-repo-url> votex-ai
cd votex-ai

# Frontend
cd frontend
npm ci
npm run build

# Backend
cd ../backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m pytest -q        # expect 40 passed

# Run
uvicorn app.main:app --host 127.0.0.1 --port 8000
# in a second terminal
cd ../frontend
npm run dev
```

Then sign in as `reporter@votex.demo` / `VotexDemo!23`, submit one synthetic
report, and confirm:

- [x] Overview, queue, intake, intelligence, dashboards and audit load.
- [x] The audit chain verifies.
- [x] The national dashboard shows a suppressed cell.
- [x] No browser console errors.
- [x] A keyboard-only user can switch language and submit a report — verified in
      the Phase 4 accessibility run on the same code, recorded in
      [../security/ACCESSIBILITY_AND_LOCALISATION.md](../security/ACCESSIBILITY_AND_LOCALISATION.md).

The first four were re-confirmed on the clean checkout on 12 November 2026;
re-run all five on the final frozen commit.

Record the terminal output and one screenshot per step.

---

## 5. Demo video shot list (3:00)

Follow [../demo/DEMO_SCRIPT.md](../demo/DEMO_SCRIPT.md). Required evidence:

- [ ] Explainable analysis with reasons and versions.
- [ ] Two reports linked by a shared indicator.
- [ ] A suppressed national cell labelled k ≥ 5.
- [ ] Audit verification success, then tamper detection on a prepared copy.
- [ ] Cross-tenant denial.
- [ ] Keyboard-only Igbo or Hausa report submission.
- [ ] Closing statement with honest limits.

Rules: 100% browser zoom, synthetic data only, no live system, no confidential
slide, no unsupported claim. Keep a recorded fallback.

---

## 6. Suggested timeline

| When | Action |
| --- | --- |
| **11 Nov 2026** | Team, application draft, repository, safety checks — **done** |
| **12 Nov 2026** | Application submitted — **done**; fresh-clone verification — **done** |
| 13 Nov – 30 Nov | axe-core accessibility run, native-language review, 13-scenario demonstration run |
| 1 Dec – 8 Dec | Record and rehearse the three-minute demo |
| 9 Dec – 12 Dec | Final test pass, frozen build, evidence pack |
| **13 Dec** | Submit prototype before the deadline |

---

## 7. Day-of submission

- [ ] Freeze the repository and tag the submitted commit.
- [ ] Re-run `pytest -q` and `npm run build` on the tagged commit.
- [ ] Confirm the public repository opens in a private browser window.
- [ ] Confirm no confidential PDFs, `.env` files or databases are tracked.
- [ ] Upload the video with the required title and track label.
- [ ] Submit the prototype form and archive the confirmation.
