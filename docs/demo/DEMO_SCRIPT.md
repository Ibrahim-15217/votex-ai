# Votex AI — Three-Minute Demo Script

| Field | Detail |
| --- | --- |
| **Status** | Draft v0.5 — copy, accounts and screens aligned to the released build |
| **Target length** | 3:00 maximum |
| **Audience** | Track 4 judges and grand-prize panel |
| **Demo data** | Synthetic only — Votex Demo Authority tenant |
| **Owner** | Product lead |

> Win condition: five memorable moments — explainable triage, correlation, privacy suppression, tamper detection and inclusive access. Do not tour features.

---

## 1. Pre-flight checklist

Run this 15 minutes before presenting.

- [ ] API and frontend healthy (`docker compose up`, or the local fallback: API on `127.0.0.1:8000`, Vite on `localhost:5173`). `/api/v1/health` returns 200 and `/api/v1/ready` reports `resilience-and-simulation`.
- [ ] Seed complete; every demo account signs in. Accounts on the sign-in card: `admin@votex.demo`, `analyst@votex.demo`, `reporter@votex.demo`, `analyst@inec.demo`. Shared password `VotexDemo!23`.
- [ ] Browser zoom at 100%; notifications silenced; one tab only.
- [ ] Signed in as `analyst@votex.demo`: open `VX-2026-A10002` and confirm **Linked incidents** lists three cases — `A10007`, `A10008`, `A10009`.
- [ ] Signed in as `admin@votex.demo`: **Threat dashboards → National picture** shows the PVC URL and domain at **5 links** across **2 organisations**, and the suppression banner reports how many small cells were withheld.
- [ ] **Audit trail → Verify chain** shows *Chain verified* and the number of entries checked.
- [ ] Isolation URL copied (see below).
- [ ] Hausa switch works; the keyboard path to Igbo works (`Tab` to the Igbo target, `Enter`).
- [ ] Four language targets visible in the header: `EN`, `HA`, `YO`, `IG`.
- [ ] Mobile viewport at 390 × 844 renders without horizontal scrolling.
- [ ] Resilience workspace shows latest score **70.8 (resilient)**, **9 of 13** findings open and **1 completed** exercise.
- [ ] Screen recording available as fallback.
- [ ] Back-up laptop and hotspot tested.

### Isolation URL (prepare during pre-flight)

1. Sign in as `analyst@inec.demo` and open `VX-2026-B10001`.
2. Copy the full address-bar URL into a scratch note.
3. Sign out and sign back in as `admin@votex.demo`.
4. Keep the URL for 2:20. Opening it in the demo shows **Incident not found** with the tenant-isolation explanation.

### Reset between runs

Stop the API, delete `backend/votex.db`, restart, and the seed recreates the same tenant, incidents and scores. Every sign-in adds audit entries, so reseed before a recorded run to keep the chain tidy.

### Fallback order

1. Live Docker demo.
2. Live local demo (SQLite + local storage).
3. Recorded three-minute video.
4. Screenshots with narration.

Never debug live. Switch to the next fallback immediately.

---

## 2. Script

### 0:00–0:20 — The problem

**Say:**

> "In an election period, a fake verification portal can reach thousands of staff and voters in minutes. Reports arrive through WhatsApp, email and phone calls. Nobody can see the pattern, and nobody can prove the evidence was not changed. Votex AI coordinates that response."

**Show:** The sign-in screen — "Electoral cybersecurity, coordinated." — with the three capability cards (explainable triage, integrity by design, privacy preserved) and the live telemetry strip: reports, indicators linked and audit-chain entries.

**Do not:** explain the architecture or read the capability cards aloud.

---

### 0:20–0:50 — Report and evidence

**Say:**

> "A presiding officer receives a message asking them to re-enter voter details on a lookalike portal. They report it with the original message and a screenshot."

**Do:**

1. Sign in as `reporter@votex.demo`.
2. Open **Report incident**; the page itself is titled **Report a threat**.
3. Give the report a short title, set **Threat category** to *Phishing / credential theft*, **How it reached you** to *WhatsApp*, and paste the synthetic URL into **Reported URL**.
4. Select **Submit report**.
5. On the new case, open **Evidence vault**, use **Attach evidence**, select **Upload and hash**, and point to the recorded SHA-256 hash.

**Say:**

> "The evidence hash is recorded at upload, so any later change is detectable."

*Fallback:* if typing is slow, open the seeded case `VX-2026-A10004` and show its evidence hash instead.

---

### 0:50–1:20 — Explainable analysis

**Say:**

> "The analyst sees a risk score — not a black box."

**Do:**

1. Sign out and sign in as `analyst@votex.demo`.
2. Open `VX-2026-A10001` (*Phishing email impersonating the Commission Chairman*): it already has a completed analysis. You can also use the report just submitted — triage runs automatically when a report is created.
3. Show **Explainable AI analysis**: the gauge, the band and **Why this score**:
   - lookalike domain,
   - HTTP rather than HTTPS,
   - credential request,
   - urgency language.
4. Point to the model and ruleset versions, and the **AI triage** panel in **Triage controls**.

**Say:**

> "Every result names the signals that produced it. The analyst can override, and the override is recorded."

**Do not:** claim the score is certainty.

---

### 1:20–1:50 — Response and correlation

**Say:**

> "This is not just a dashboard. Work gets assigned and recorded."

**Do:**

1. Open `VX-2026-A10002` (*Fake voter registration portal targeting first-time registrants*), currently **Under review**.
2. In **Triage controls**, set **Assigned analyst** to Tunde Balogun.
3. In **Record a response action**, choose *Public or staff warning issued*, note "warning issued to ward officers", and select **Record action**.
4. Move the case to **Investigating** with the **Lifecycle** selector (only valid next stages are offered).
5. Show **Linked incidents**: `A10007`, `A10008` and `A10009` all reuse the portal.

**Say:**

> "Two separate reports just became one campaign."

**Do not:** close the incident before showing the timeline; closure comes at the end.

---

### 1:50–2:20 — Privacy-preserving national view

**Say:**

> "National visibility must not expose a single organisation's report."

**Do:**

1. Switch to `admin@votex.demo` and open **Threat dashboards**.
2. Select **National picture** — labelled *Admin only · k ≥ 5*.
3. Read the suppression banner aloud: "k ≥ 5 suppression active. *N* small cells hidden before the response reaches this browser."
4. Point to categories, channels, states and the pipeline reading **K < 5**.
5. Show **Surging indicators**: the PVC URL and domain at exactly **5 links** across **2 organisations**.

**Say:**

> "Cells below five contributors are suppressed in the query layer, not just hidden in the interface. The same rule applies to exports."

**Do not:** show raw report text in the national view.

---

### 2:20–2:40 — Integrity and isolation

**Say:**

> "Two claims need proof, not slides."

**Do:**

1. Open **Audit trail** and select **Verify chain**.
2. Show *Chain verified*, the entries checked and the latest entry hash.
3. Run the prepared tamper (an edited test row) and verify again; show the first broken entry.
4. Paste the isolation URL copied in pre-flight while signed in to Votex Demo Authority; show **Incident not found** and the line "Records outside your organisation … are hidden by design."

**Say:**

> "Tampering is evident, and tenants cannot read each other's evidence."

**Do not:** tamper with the live demo database without a prepared reset.

---

### 2:40–3:00 — Inclusion and close

**Say:**

> "Security is only useful if people can use it."

**Do:**

1. Use the header switcher (`EN` `HA` `YO` `IG`) to switch to Hausa and show the intake heading **Kai rahoton barazana**.
2. Switch to Igbo with the keyboard only: `Tab` to the **Igbo** target and press `Enter`. The heading becomes **Kọọ ihe iyi egwu**.
3. With the keyboard alone, move through title and description, then submit with `Enter`; show the Igbo success banner **E zipuru akụkọ** and the generated reference.
4. On the resulting case, point to the compact **English · case data** badge: analyst-only modules stay English-only, and the interface says so.

**Say:**

> "Four languages — English, Hausa, Yoruba and Igbo — WCAG 2.2 AA as the target, and a low-bandwidth layout that strips decoration when the device asks to save data. The keyboard-only path is a tested exit criterion, not a claim. Votex AI is a working, reproducible prototype with a threat model, model card and a clear statement of residual risk. Thank you."

**Do not:** end on a roadmap slide.

---

## 3. Judge questions and concise answers

| Question | Answer |
| --- | --- |
| Is this endorsed by INEC? | No. It is a prototype. Any pilot needs written authorisation. |
| Does it use real data? | No. Synthetic only; no voter records or private messages. |
| How accurate is the AI? | Measured precision, recall and F1 on a held-out synthetic test set are published in the model card, including failure cases. |
| What if the model is wrong? | The analyst sees reasons, can override, and every action is audited. The model never closes an incident. |
| How is privacy protected? | Tenant isolation, minimal fields, no raw text in national views and k ≥ 5 suppression in the query layer. |
| Why did the INEC analyst get "Incident not found"? | Cross-tenant reads return 404 by design, so another organisation's case cannot even be confirmed to exist. |
| Can the audit log be rewritten? | The hash chain makes tampering evident. Production would add external anchoring and restricted database roles. |
| How does this scale? | Stateless API, PostgreSQL, object storage and a worker boundary. The MVP avoids infrastructure that is not justified. |
| Why four languages? | Reports come from staff, observers and voters with different first languages. English, Hausa, Yoruba and Igbo cover the demo audience; dictionaries are typed so an untranslated key fails the build. |
| Is the translation professionally reviewed? | Not yet. The prototype dictionaries are consistent but need native-speaker sign-off before a pilot; the evidence document says so explicitly. |
| What is the biggest weakness? | The synthetic dataset and the absence of real-world validation. Both are stated openly and are the first pilot tasks. |
| What is genuinely innovative? | A complete defensive workflow that combines explainable triage, correlation, privacy-preserving aggregates and tamper-evident audit in one reproducible prototype. |
| What would you do with funding? | Independent security review, real-language data with consent, differential privacy, offline reporting and an authorised pilot. |

---

## 4. Rehearsal rules

- Rehearse at least five times, twice with a timer.
- Keep one person narrating and one driving.
- Never read slides during the demo.
- Cut a feature before exceeding three minutes.
- Re-run the entire demo from a clean seed before submission.
- Record the final run and watch it without commentary to find gaps.

---

## 5. Recording cue sheet

Use this to line the narration up with what is on screen. All reference images
are in [`screenshots/`](./screenshots/).

| Time | What is on screen | Action | Reference |
| --- | --- | --- | --- |
| 0:00 | Sign-in | No clicks; let the capability cards and telemetry settle | `final-login-1440x1000.png` |
| 0:20 | Report a threat | Type the report, submit, then open **Evidence vault** | `final-report-1440x1000.png` |
| 0:35 | New case | Point to the reference, the SHA-256 hash and the timeline | `final-incident-detail-1440x1000.png` |
| 0:50 | Explainable AI panel | Scroll from the score to **Why this score** | `final-incident-detail-1440x1000.png` |
| 1:20 | Triage controls on `A10002` | Assign, record a response action, move to **Investigating** | `final-incident-detail-1440x1000.png` |
| 1:30 | Linked incidents on `A10002` | Show the three linked cases below the triage panel | `final-linked-incidents-1440x1000.png` |
| 1:50 | National picture | Select the tab, read the suppression banner, show `K < 5` cells | `final-dashboards-national-1440x1000.png` |
| 2:05 | Surging indicators | Point to the PVC URL: 5 links, 2 organisations | `final-dashboards-national-1440x1000.png` |
| 2:20 | Audit trail | **Verify chain**; show the intact result and the tamper result | `final-audit-1440x1000.png` |
| 2:30 | Cross-tenant read | Paste the prepared URL; show **Incident not found** | capture while recording |
| 2:40 | Igbo intake | Keyboard-only language switch and submission | `final-report-igbo-1440x1000.png` |
| 2:50 | Igbo success | Show **E zipuru akụkọ** and the **English · case data** badge | capture while recording |

---

## 6. Evidence to capture

- Explainable analysis and suppression: `final-incident-detail-1440x1000.png`, `final-dashboards-national-1440x1000.png`.
- Correlation evidence: `final-linked-incidents-1440x1000.png` (three cases on `A10002`).
- Audit verification success and tamper detection: `final-audit-1440x1000.png` plus the tamper run captured during recording.
- Hausa interface: `final-login-hausa-1440x1000.png`, `final-overview-hausa-1440x1000.png`.
- Igbo keyboard-only intake and localised success: `final-report-igbo-1440x1000.png` plus the success screen.
- Mobile intake and queue: `final-report-mobile-390x844.png`, `final-incidents-mobile-390x844.png`.
- Terminal output of the test suite and the fresh-clone start and seed output.
