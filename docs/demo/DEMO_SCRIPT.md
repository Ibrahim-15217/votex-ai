# Votex AI — Three-Minute Demo Script

| Field | Detail |
| --- | --- |
| **Status** | Draft v0.4 — Phase 5 resilience module ready; three-minute timing unchanged |
| **Target length** | 3:00 maximum |
| **Audience** | Track 4 judges and grand-prize panel |
| **Demo data** | Synthetic only |
| **Owner** | Product lead |

> Win condition: five memorable moments — explainable triage, correlation, privacy suppression, tamper detection and inclusive access. Do not tour features.

---

## 1. Pre-flight checklist

Run this 15 minutes before presenting.

- [ ] `docker compose up` is healthy, or the local fallback is running.
- [ ] Seed command completed; demo accounts can sign in. The enriched seed already contains overlapping indicators, so correlation is visible without live data entry.
- [ ] Browser zoom at 100%; notifications silenced.
- [ ] Synthetic incident with a shared indicator is ready — open `VX-2026-A10002` and confirm the **Linked incidents** panel shows three cases.
- [ ] National dashboard shows the PVC URL/domain at 5 linked incidents and a suppressed small cell.
- [ ] Audit verification command works.
- [ ] Hausa language switch works.
- [ ] Keyboard-only flow works: `Tab` to a language target, `Enter`, then `Tab` through the intake and `Enter` to submit.
- [ ] Four locales visible on sign-in: English, Hausa, Yorùbá, Igbo.
- [ ] Mobile viewport renders without horizontal scrolling.
- [ ] Resilience workspace shows latest score **70.8 (resilient)**, 9/13 open findings and one completed exercise.
- [ ] Screen recording available as fallback.
- [ ] Back-up laptop and hotspot tested.

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

**Show:** Login screen with the Track 4 framing and four capability cards.

**Do not:** explain the architecture.

---

### 0:20–0:50 — Report and evidence

**Say:**

> "A presiding officer receives a message asking them to re-enter voter details on a lookalike portal. They report it with the original message and a screenshot."

**Do:**

1. Sign in as `reporter@inec.demo`.
2. Open **Report an incident**.
3. Paste the synthetic message and URL.
4. Upload the synthetic screenshot.
5. Submit.

**Show:** Generated reference and recorded SHA-256 evidence hash.

**Say:**

> "The evidence hash is recorded at upload, so any later change is detectable."

---

### 0:50–1:20 — Explainable analysis

**Say:**

> "The analyst sees a risk score — not a black box."

**Do:**

1. Sign in as `analyst@inec.demo` (or switch role).
2. Open the new incident.
3. Show the score gauge, band and reasons:
   - lookalike domain,
   - HTTP rather than HTTPS,
   - credential request,
   - urgency language.
4. Point to the model and ruleset version.

**Say:**

> "Every result names the signals that produced it. The analyst can override, and the override is recorded."

**Do not:** claim the score is certainty.

---

### 1:20–1:50 — Response and correlation

**Say:**

> "This is not just a dashboard. Work gets assigned and recorded."

**Do:**

1. Assign the incident to yourself or a colleague.
2. Record a response action — for example, "warning issued to ward officers".
3. Move the incident to **Investigating**.
4. Open a second synthetic report that shares the same domain.
5. Show **Linked incidents**. The seeded cases `VX-2026-A10007`, `A10008` and `A10009` all reuse the portal from `A10002`.

**Say:**

> "Two separate reports just became one campaign."

**Do not:** close the incident before showing the timeline; closure comes at the end.

---

### 1:50–2:20 — Privacy-preserving national view

**Say:**

> "National visibility must not expose a single organisation's report."

**Do:**

1. Open the **National dashboard**.
2. Show aggregate trends.
3. Point to a suppressed cell labelled with the k ≥ 5 rule.
4. Show the PVC URL/domain in **Surging indicators** at exactly 5 linked incidents across 2 organisations.

**Say:**

> "Cells below five contributors are suppressed in the query layer, not just hidden in the interface. The same rule applies to exports."

**Do not:** show raw report text in the national view.

---

### 2:20–2:40 — Integrity and isolation

**Say:**

> "Two claims need proof, not slides."

**Do:**

1. Run the audit verification command or click **Verify chain**.
2. Show the success result.
3. Tamper with a test row in the seeded environment (prepared beforehand) and re-run; show the first broken entry.
4. Attempt to open Organisation B's incident while signed in to Organisation A; show denial.

**Say:**

> "Tampering is evident, and tenants cannot read each other's evidence."

**Do not:** tamper with the live demo database without a prepared reset.

---

### 2:40–3:00 — Inclusion and close

**Say:**

> "Security is only useful if people can use it."

**Do:**

1. Switch the interface to **Hausa** with the header switcher, then switch to **Igbo** using the keyboard only: `Tab` to the **Igbo** target and press `Enter`.
2. Show the intake heading change to **“Kọọ ihe iyi egwu”**.
3. With the keyboard alone, move through title and description, then submit with `Enter`; show the Igbo success banner **“E zipuru akụkọ”** and the generated reference.
4. Point to the visible English-only notice on analyst screens so the localisation boundary is honest.

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

## 5. Evidence to capture

- Screenshot of the explainable analysis.
- Screenshot of related incidents.
- Screenshot of a suppressed small cell.
- Screenshot of audit verification success and tamper detection.
- Screenshot of the Hausa interface.
- Screenshot of the Igbo keyboard-only intake and localised success banner.
- Screenshot of the mobile intake and queue.
- Terminal output of the test suite.
- Fresh-clone start and seed output.
