# Methodology

**Votex AI — Track 4: Electoral Cybersecurity & Resilience**

This document describes how the prototype works, what it was evaluated on, and
what the evaluation does not prove. Every number below is reproducible from the
repository; commands are in [SUBMISSION_CHECKLIST.md](./SUBMISSION_CHECKLIST.md).

---

## 1. System approach

Votex AI is a defensive coordination tool, not an offensive scanner. It implements
one complete workflow:

**Report → AI analysis → correlation → assignment and response → audit**

| Layer | Implementation | Why |
| --- | --- | --- |
| Interface | React, TypeScript, Vite, Tailwind | Fast, static, no external font or chart dependency |
| API | Python, FastAPI, SQLAlchemy, Pydantic | Typed contracts and testable service layer |
| Database | PostgreSQL target, SQLite fallback | Reproducible local demo without infrastructure |
| Analysis | Deterministic rules + TF-IDF/Logistic Regression | Explainable, offline, no third-party API |
| Evidence | MIME/extension/magic validation, UUID names, SHA-256 | Integrity and safe storage |
| Audit | Append-only SHA-256 hash chain | Tamper evidence without a blockchain |
| Deployment | Docker Compose | Fresh-clone demonstration |

Analysis is synchronous in the MVP so a live demo cannot fail on a missing worker.
The service boundaries still allow a task queue later.

---

## 2. Data

- **Synthetic only.** No voter records, biometrics, private messages or live
  system data were used.
- The generator in `ai-engine/training/generate_data.py` produced **1,400 labelled
  rows** with seed `20261109`. The manifest records SHA-256
  `7c7c05e3cef528de184760fe8cafcce01a6818d78578919cf92cc2dbc94603a0`.
- Labels cover benign and malicious electoral phishing/impersonation patterns,
  including lookalike domains, credential requests, urgency language, payment
  fraud, fake results and malware lures.
- A separate **28-case hand-written challenge set** probes phrasing that was not
  generated from the same templates.
- Provenance, composition and known biases are documented in
  [../data/DATASHEET.md](../data/DATASHEET.md).

**Important:** the synthetic generator and the classifier share a domain
vocabulary. The near-perfect held-out score therefore measures internal
consistency, not real-world accuracy. The hand-written set is the more honest
signal, and still not a field evaluation.

---

## 3. Hybrid analysis and risk score

The analyser combines four components and publishes the reason for each:

1. **URL and domain rules** — lookalike strings, suspicious TLDs, HTTP rather than
   HTTPS, embedded credentials, punycode and redirect patterns.
2. **NLP signals** — urgency, credential requests, authority impersonation,
   payment instructions and threat language.
3. **TF-IDF + Logistic Regression** — word 1–2 grams plus `char_wb` 3–5 grams,
   `C=4.0`, `liblinear`, `class_weight="balanced"`, seed `20261109`, 75/25
   stratified split, threshold 0.5, artefact version `hybrid-v0.2.0`.
4. **Weighted risk score** — fixed and published:

```text
R = 0.30·U + 0.25·N + 0.25·M + 0.20·I
```

where **U** is URL/domain risk, **N** NLP signal strength, **M** model probability
and **I** incident context. Bands: **benign < 35**, **suspicious 35–64.9**,
**high risk ≥ 65**.

The model and ruleset versions are shown beside every score. The score is
advisory; the analyst can override, and the override is audited. The model never
closes an incident.

### Measured results

| Evaluation | Result |
| --- | --- |
| Held-out synthetic set (350 rows) | Precision / recall / F1 **1.000**, Brier **0.0006**, 0 false positives, 0 false negatives |
| Hand-written challenge set (28 cases) | **0 errors**, Brier **0.0265**, closest case **0.059** from the threshold |
| Honest limit | Template overlap inflates the held-out score; real-world generalisation is unknown |

Full analysis, including the closest-to-threshold case and failure modes:
[../model/EVALUATION.md](../model/EVALUATION.md). Intended use and limitations:
[../model/MODEL_CARD.md](../model/MODEL_CARD.md).

---

## 4. Correlation

- Deterministic, offline extraction of indicators from incident text and reported
  URLs: `url`, `domain`, `ipv4`, `sha256`, `md5`.
- Official, platform and documentation hosts are excluded to avoid false links.
- Indicators are organisation-owned and linked through `incident_indicators`.
- Correlation is tenant-scoped. Reporters see only their own incidents; analysts
  see their organisation; national aggregates are admin-only.
- The extractor never visits a submitted link. There is no scanning or
  exploitation of third-party systems.

Demo evidence: five shared indicators link nine of ten reports in the demo
authority, and one PVC URL/domain links five incidents across two organisations —
the smallest k cell that can surface.

---

## 5. Privacy and national aggregates

- **k-anonymity threshold k = 5.** Any cell with fewer than five contributing
  incidents or organisations is suppressed in the backend query/service layer, not
  hidden in the browser.
- Suppressed raw values never reach the browser or a CSV export.
- Exports are permission-checked and audited with `intelligence.exported`.
- National views contain aggregates only; no raw report text.
- Evidence lives outside the database under UUID filenames; access is logged.
- Privacy test evidence: [../security/PRIVACY_AND_CORRELATION.md](../security/PRIVACY_AND_CORRELATION.md).

---

## 6. Security design

| Control | Implementation |
| --- | --- |
| Authentication | JWT (HS256), Argon2id password hashing, role claims |
| Authorisation | Roles `admin`, `analyst`, `reporter`; tenant checks in the query layer |
| Tenant isolation | Organisation-scoped queries and reporter scoping; cross-tenant denial tested |
| Evidence upload | Extension + MIME + magic-byte validation, 10 MB limit, UUID storage names, SHA-256 |
| Audit | Append-only entries with `prev_hash` and `entry_hash`, genesis `"0"*64`, recomputation endpoint |
| Input handling | Pydantic validation, parameterised queries, strict CORS, security headers |
| Secrets | No secrets committed; `.env.example` only; confidential PDFs git-ignored |

Threat model and finding-to-control matrix:
[../security/THREAT_MODEL.md](../security/THREAT_MODEL.md).
Residual risk and prohibited uses:
[../safety/SAFETY_AND_LIMITATIONS.md](../safety/SAFETY_AND_LIMITATIONS.md).

Tamper detection is demonstrated by altering a test row and re-running
verification: the first broken entry is reported. Production would add external
anchoring and restricted database roles.

---

## 7. Inclusion and accessibility

- Four complete interface locales: English, Hausa, Yorùbá and Igbo. English is the
  typed source of truth; other dictionaries are `Record<TranslationKey, string>`,
  so missing keys fail the build.
- The Phase 4 exit test passed: a keyboard-only user switched to Igbo, typed a
  title and description, submitted with `Enter`, and received the localised success
  banner.
- WCAG 2.2 AA measures: skip link, visible focus, route-change focus, live
  announcements, labelled forms, `role="alert"` errors, `role="status"` success,
  text labels alongside colour, and target-size minimums.
- Low bandwidth: `prefers-reduced-data` removes grid, blur, shadows and animation;
  no web fonts, chart library or tracking scripts.
- Responsive sweep: six routes × 390/768/1024/1440 px with zero overflow and zero
  browser errors.
- Analyst case records, AI explanations and dashboards remain English-only and say
  so on screen.

Evidence: [../security/ACCESSIBILITY_AND_LOCALISATION.md](../security/ACCESSIBILITY_AND_LOCALISATION.md).

---

## 8. Reproducibility

- Backend: **40 tests pass** with `pytest -q`.
- Frontend: `npm run typecheck` and `npm run build` pass; production bundle
  **377.90 kB JS (109.88 kB gzip)** and **39.70 kB CSS (7.96 kB gzip)**.
- Model artefacts and synthetic data are committed so a fresh clone can run the
  demo without retraining. Regeneration commands are in the README.
- The application creates the schema and seeds both demo tenants on first start.
- Docker Compose is the documented path; the same services were also verified by
  direct local startup on Windows.

The remaining submission gate is a **fresh-clone test on a clean machine** and a
recorded **three-minute demo video**.

---

## 9. AI-tool assistance disclosure

This prototype was built with AI coding assistance. The team remains responsible
for the design, the security claims, the evaluation and every statement in the
submission. No confidential programme material was used as model input, and no
real personal data was processed.

---

## 10. What this methodology does not prove

- Real-world detection accuracy on Nigerian electoral phishing.
- Resistance to a determined attacker with source-code access.
- Production availability, scale or incident-response staffing.
- Professional translation quality.
- Legal adequacy for a live election; that requires a pilot agreement and a
  data-protection review.
