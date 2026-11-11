# Portal Application — Field-by-Field Answers

For **https://ai4elections.risenetworks.org/application**.
Five steps. No character limits are set on the form, but keep every long answer
under about 1,000 characters so the server-side validator never truncates it.

Answer the fields in the order below. Fields marked `[YOU]` are personal facts
only you can supply; everything else is copy-paste ready.

> Reminder: this form is the **application**, not the prototype submission. The
> working prototype is entered in step 3 (`prototype_link`). The prototype is due
> 13 December 2026.

---

## Step 1 — Personal Information

| Portal field | Answer |
| --- | --- |
| First Name | `[YOU — first name]` |
| Last Name | `[YOU — last name]` |
| Email Address | `[YOU — reachable email]` |
| Phone Number | `[YOU — e.g. +234 80X XXX XXXX]` |
| Country of Residence | **Nigeria** |
| State of Residence | `[YOU — e.g. Federal Capital Territory]` |
| City | `[YOU — e.g. Abuja]` |
| What best describe your application? | **Team** |

`application_type` is the only option that unlocks the team block in step 4, so
choose **Team**.

## Step 1 — Your Background

| Portal field | Answer |
| --- | --- |
| Tell us about your experience * | see answer 1 |
| Primary Area of Expertise * | `Electoral cybersecurity, secure backend engineering and applied machine learning` |
| Years of Experience * | `[YOU — whole number, 0–80]` |
| Current Role / Occupation * | `[YOU — e.g. Software Engineer / Student]` |
| Organisation / Institution * | `[YOU — your employer, university, or "Cyber Defenders (independent team)"]` |
| Highest level of Education * | `[YOU — e.g. Bachelor's degree]` |
| Academic / Professional Field * | `[YOU — e.g. Computer Science]` |

**1. Tell us about your experience**

> We are a three-person team that designs and builds defensive software for civic and electoral use. Over the past months we have taken Votex AI from problem framing to a working, tested prototype: a React + TypeScript front end, a Python and FastAPI backend, PostgreSQL with a SQLite fallback, and a hybrid phishing analyser combining URL rules, NLP signals and a TF-IDF + Logistic Regression model. We work evidence-first: 40 backend tests, published model metrics, and browser-tested accessibility. Our combined background covers secure backend engineering, applied machine learning and inclusive interface design, and we document limitations instead of hiding them.

---

## Step 2 — Your Skills

| Portal field | Answer |
| --- | --- |
| Skills (Use (,) after each skill) * | see answer 2 |
| Tell us about your relevant experience * | see answer 3 |

**2. Skills** (comma after each skill, as the field asks)

> Python, FastAPI, TypeScript, React, scikit-learn, threat detection, incident response, secure API design, PostgreSQL, Docker, WCAG 2.2 accessibility, Hausa/Yorùbá/Igbo localisation, technical documentation

**3. Tell us about your relevant experience**

> We built Votex AI end to end for this challenge. It gives reporters a plain-language intake in four languages, analysts an explainable risk score with reasons and model version, tenant-scoped indicator correlation that links separate reports into one campaign, a k ≥ 5 suppressed national view, and a SHA-256 hash-chain audit trail. We validated it with 40 backend tests covering tenant isolation, evidence validation, audit tampering and k-anonymity suppression, plus browser tests for keyboard-only reporting, four locales and six routes at four screen widths. The repository is public, MIT-licensed and reproducible from a fresh clone.

---

## Step 2 — Your Interest

| Portal field | Answer |
| --- | --- |
| Which challenge track interests you most? * | `Track 4 — Electoral Cybersecurity & Resilience` |
| Why are you interested in this challenge area? * | see answer 4 |

**4. Why are you interested in this challenge area?**

> Electoral security is a defensive problem where small local signals matter, and where careless design can harm the very people who report them. Track 4 lets us work on the most attacked and least tooled part of the election stack: the human reporting channel. During elections, staff, observers, party agents and voters receive phishing, impersonation and fake-portal messages, but reports sit in separate WhatsApp and email inboxes and are never correlated. We want to build the boring, trustworthy plumbing that turns those reports into timely, explainable defence — without touching live systems, without real voter data, and without putting a reporter at risk.

---

## Step 3 — Your Idea

Answer **Yes, I have an idea**. Six text areas then appear, followed by idea
stage and prototype questions.

| Portal field | Answer |
| --- | --- |
| Do you already have a solution idea? * | **Yes, I have an idea** |
| If Yes, what problem are you trying to solve? * | see answer 5 |
| Who is affected by this problem? * | see answer 6 |
| Describe your proposed solution * | see answer 7 |
| How would AI or technology contribute to the solution? * | see answer 8 |
| Who would benefit from the solution? * | see answer 9 |
| What makes your approach different or useful? * | see answer 10 |
| What stage is your idea currently at? * | **Working prototype** |
| Do you already have a prototype? | **Yes** |
| If yes, prototype/project link | `https://github.com/Ibrahim-15217/votex-ai` |

**5. What problem are you trying to solve?**

> During elections, phishing, impersonation and fake portals target electoral staff, observers, party agents and voters. Reports arrive by WhatsApp, phone and email, live in separate inboxes, and are never correlated, so one campaign looks like dozens of unrelated complaints. Evidence is easy to alter and hard to authenticate later. National visibility also creates a privacy trap: a pattern can be exposed by identifying the single small organisation that reported it. Today's tools are either awareness material or dashboards with no intake, no explanation and no audit.

**6. Who is affected by this problem?**

> Electoral commission staff and ad hoc staff, observers and civil-society monitors, party agents, journalists, and ordinary voters — especially first-time and low-connectivity users who are most likely to trust a fake portal. The people harmed twice are the reporters: a badly designed system can expose the small organisation or individual whose report revealed a campaign.

**7. Describe your proposed solution**

> Votex AI is a defensive incident platform with one complete workflow: report → analysis → correlation → assignment and response → audit. Reporters submit a suspicious message, link or file with validated evidence and a SHA-256 integrity hash. A hybrid analyser combines URL and domain rules, NLP signals and a TF-IDF + Logistic Regression classifier into a published weighted risk score (R = 0.30U + 0.25N + 0.25M + 0.20I), shown with its reasons and model version. Indicators are extracted offline and correlated inside an organisation, so separate reports become one campaign. Analysts assign cases, record response actions and review a full timeline, and every step is chained into a tamper-evident audit log.

**8. How would AI or technology contribute to the solution?**

> AI does the triage, not the decision. The analyser scores each report and explains itself: URL and domain rules catch look-alike portals, text signals catch urgency and credential requests, and a TF-IDF + Logistic Regression model adds a learned signal. Each component and weight is published, so an analyst can see why a report scored 72 instead of trusting a black box. The score is advisory — a human decides, can override, and every action is audited. Analysis runs fully offline: the system never visits a submitted link and never scans a third-party system.

**9. Who would benefit from the solution?**

> Electoral staff and observers get a fast, low-friction way to report. Analysts get one queue with explainable triage and linked cases instead of scattered inboxes. Coordinators get aggregate visibility that suppresses any cell below k = 5, so national trends never expose a single reporter. Voters benefit indirectly from earlier detection of fake portals. Civil-society and electoral bodies get an auditable, reproducible design they can pilot under written authorisation.

**10. What makes your approach different or useful?**

> Most electoral-security entries are awareness content or a dashboard. Votex AI combines four things in one working prototype: explainable triage instead of a black box, cross-report indicator correlation, privacy-preserving national aggregates enforced in the query layer, and a tamper-evident audit chain. Inclusion is treated as an engineering requirement, not a slogan: four complete locales, a tested keyboard-only reporting path, WCAG 2.2 AA measures and a reduced-data mode for low-bandwidth devices. Everything is public, MIT-licensed and reproducible from a fresh clone.

---

## Step 4 — Applying as an existing team

This block appears because step 1 says **Team**. It is not marked required, but
fill it: it is how the judges identify the team.

| Portal field | Answer |
| --- | --- |
| Team Name | `Cyber Defenders` |
| Team Lead | `[YOU — full name]` |
| Team size | `3` |
| Team Description | see answer 11 |
| Names and Role of Team Members ( use (,) after each name and role) | see answer 12 |

**11. Team Description**

> Cyber Defenders is a three-person, multidisciplinary team building defensive technology for Nigerian elections. We combine cybersecurity and incident-response thinking, backend engineering and applied machine learning, and inclusive frontend design. Together we built Votex AI end to end: secure intake, explainable phishing analysis, tenant-scoped correlation, privacy-preserving national aggregates and a tamper-evident audit trail. We work evidence-first — every claim is backed by a test, screenshot or reproducible command — and we are committed to nonpartisan, human-supervised, NDPA-aligned use of AI.

**12. Names and Role of Team Members**

> `[MEMBER 1 NAME] - Team lead, product, problem framing and demo, [MEMBER 1 NAME] - Cybersecurity, backend, auth, privacy and audit, [MEMBER 3 NAME] - Engineering, AI, frontend and accessibility`

Use the real names and keep the comma-after-each-item format. Team size must
match the number of names: **3**.

### Accessibility & Participation needs

| Portal field | Answer |
| --- | --- |
| Do you have any accessibility or participation requirements you would like us to consider? | **No** (choose **Yes** and describe if anyone on the team needs support) |
| If yes, please tell us what support you may require | leave blank unless you chose Yes |

---

## Step 5 — Declarations

Read the text on the page, then tick:

- [ ] **I have read and understand the responsible participation requirements.**
- [ ] **I confirm that the information provided in this application is accurate to the best of my knowledge.**
- [ ] **I agree to the processing of my information for the purposes described in the Privacy Notice.**
- [ ] **I agree to the Applicant Declaration.**
- [ ] *(optional)* **I would like to opt in to the #AI4Elections Community of Practice and national registry.** — recommended: tick it, it is consent-based and you can withdraw.

All four required boxes must be ticked before **Submit Application** works.

---

## Before you press Submit

1. Every `[YOU]` and `[MEMBER …]` placeholder is replaced.
2. Team size says **3** and the member list has exactly three names.
3. `prototype_link` is `https://github.com/Ibrahim-15217/votex-ai` and it opens
   in a private browser window (the repo is public).
4. No confidential programme material, `.env` file, database or real voter data
   is linked anywhere in the application.
5. Screenshot the **Application Submitted** panel (or save the confirmation
   email) the moment it appears. That screenshot is your receipt.
6. Deadline: **12 November 2026, 11:59pm WAT**. Submit with time to spare —
   the portal does no draft saving, so keep this page open until it confirms.

## What the application does not ask for

These belong in the **13 December prototype submission**, not here:

- the three-minute demo video;
- the problem statement, methodology, model card, data sheet and threat model;
- the test evidence and screenshots.

Have them ready in the repository and in `docs/submission/` when the prototype
form opens.
