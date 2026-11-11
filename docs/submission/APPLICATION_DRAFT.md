# Application Draft

Fill every `[PLACEHOLDER]` before submitting. Keep answers within the form's
character limits; the short versions below are safe for typical 500–1,000
character fields.

---

## Project basics

| Field | Draft |
| --- | --- |
| Project name | **Votex AI** |
| Tagline | Securing elections through intelligent cybersecurity |
| Track | **Track 4 — Electoral Cybersecurity & Resilience** |
| Repository | `[PUBLIC_REPO_URL]` |
| Demo video | `[VIDEO_URL — due with the prototype]` |
| Contact person | `[NAME, EMAIL, PHONE]` |
| Location | `[CITY, STATE, NIGERIA]` |

## Team (2–4 members required)

| # | Name | Role | Email | Affiliation |
| --- | --- | --- | --- | --- |
| 1 | `[NAME]` | Product lead / demo | `[EMAIL]` | `[ORG / UNIVERSITY]` |
| 2 | `[NAME]` | Backend and security | `[EMAIL]` | `[ORG / UNIVERSITY]` |
| 3 | `[NAME]` | Frontend and inclusion | `[EMAIL]` | `[ORG / UNIVERSITY]` |
| 4 | `[NAME — optional]` | AI / evaluation | `[EMAIL]` | `[ORG / UNIVERSITY]` |

> Remove row 4 if the team has three members. The rules allow 2–4.

---

## Short answers

### 1. What problem are you solving? (≈700 characters)

Electoral staff, observers, party agents and voters are targeted by phishing,
impersonation and fake portals during elections. Reports arrive through WhatsApp,
phone calls and email, are handled in separate inboxes, and are never correlated.
Evidence is easy to alter and hard to authenticate later. National visibility
risks exposing the single small organisation whose report revealed a pattern.
Votex AI gives reporters a plain-language intake, gives analysts one queue with an
explainable risk assessment and linked cases, and gives coordinators aggregate
visibility that suppresses small cells. Every step is captured in a tamper-evident
audit chain.

### 2. What does your prototype do? (≈800 characters)

Votex AI implements one complete defensive workflow: report → AI analysis →
correlation → assignment and response → audit.

- Reporters submit a suspicious message, link or file with validated evidence and
  a SHA-256 integrity hash.
- A hybrid analyser combines URL/domain rules, NLP signals and a TF-IDF +
  Logistic Regression classifier into a published weighted risk score, with the
  reasons and model version shown beside it.
- Indicators (URLs, domains, IPv4, file hashes) are extracted offline and
  correlated inside the organisation, so separate reports become one campaign.
- Analysts assign cases, record response actions, move status and review a
  complete timeline.
- A SHA-256 hash chain makes tampering evident, and national aggregates suppress
  any cell with fewer than five contributors.

### 3. What is innovative about it? (≈600 characters)

Most electoral-security entries are either awareness content or a dashboard.
Votex AI combines four things in one reproducible prototype: explainable triage
instead of a black box, cross-report indicator correlation, privacy-preserving
national aggregates enforced in the query layer, and tamper-evident audit. It also
treats inclusion as an engineering requirement: four interface locales, a tested
keyboard-only reporting path, WCAG 2.2 AA measures and a low-bandwidth mode that
strips decoration when a device asks to save data.

### 4. What data did you use? (≈400 characters)

Synthetic data only. A seeded generator produced 1,400 labelled electoral-phishing
rows for training and a held-out evaluation, plus 28 hand-written challenge cases
and a synthetic demo tenant with two organisations. No voter records, biometrics,
private messages or live electoral systems were used. The data sheet documents
provenance, composition and bias.

### 5. How did you evaluate it? (≈600 characters)

The classifier is evaluated on a 350-row held-out synthetic set and a separate
28-case hand-written challenge set; precision, recall, F1, Brier score and
closest-to-threshold cases are published in the model card and evaluation
document. The system is tested end to end with 40 backend tests covering tenant
isolation, evidence validation, audit tampering and k-anonymity suppression.
Browser checks verify keyboard-only reporting, four locales, six routes at four
screen widths, zero horizontal overflow and zero console errors. We state openly
that synthetic results do not prove real-world accuracy.

### 6. How is privacy protected? (≈500 characters)

Organisation isolation is enforced in the backend query layer. Reporters see only
their own reports; analysts see their organisation; national views are
admin-only. National aggregates suppress cells below k = 5 before serialisation,
so suppressed values never reach the browser or a CSV. Exports are
permission-checked and audited. Evidence is stored under UUID filenames with
access logging. The design is aligned with the Nigeria Data Protection Act 2023
and uses no real personal data.

### 7. How is AI kept responsible? (≈500 characters)

The risk score is advisory and fully explained: each component and its weight is
published, and the model version sits beside the score. A human analyst decides,
can override, and every action is audited. The system never closes an incident,
declares a result or sanctions a person. Intended use, failure modes and
limitations are documented. Analysis runs offline, never visits a submitted link
and never scans a third-party system.

### 8. How inclusive and accessible is it? (≈500 characters)

The interface ships in English, Hausa, Yorùbá and Igbo. English is the typed
source of truth, so an untranslated key fails the build. A keyboard-only user can
switch language and submit a report; this passed as a live browser test. The
design targets WCAG 2.2 AA with a skip link, visible focus, route focus
management, labelled forms and status announcements. A reduced-data mode removes
decoration, blur and animation for low-bandwidth connections.

### 9. Is it feasible and reproducible? (≈400 characters)

Yes. The stack is React + FastAPI with PostgreSQL and a SQLite fallback, started
with Docker Compose or directly from the README. Model artefacts and synthetic
seed data are committed, so a fresh clone runs the demo without retraining. The
frontend production bundle is under 110 kB gzipped. The open MIT licence and
modular services support a later pilot without a rewrite.

### 10. What can it not do? (≈500 characters)

It cannot detect real-world attacks reliably: the evaluation is synthetic and
template overlap inflates the held-out score. It cannot resist an attacker with
source-code access, guarantee production scale, or substitute professional
translation review. Analyst case narratives and dashboards remain English-only.
It is not affiliated with or endorsed by INEC or any partner, and winning does not
authorise deployment. Any pilot needs written authorisation, a security
assessment and a data-protection review.

### 11. What would you do with the prize or support? (≈400 characters)

Independent security review, native-speaker review of the four locales,
accessibility testing with representative users, differential-privacy research
for national aggregates, offline-first reporting for low-connectivity areas, and
an authorised pilot with a civil-society or electoral body under a written
agreement.

---

## Declarations to confirm on the form

- [ ] The project is nonpartisan and does not persuade, target or manipulate
      voters.
- [ ] No live electoral or institutional system was scanned, probed, exploited or
      load-tested.
- [ ] Only synthetic, public or explicitly authorised data was used.
- [ ] A human remains responsible for every consequential action.
- [ ] AI-tool assistance is disclosed in the project documentation.
- [ ] Confidential programme material is not included in the public repository.
- [ ] I have read the general challenge rules and the Track 4 brief.
- [ ] The team has 2–4 eligible members.
