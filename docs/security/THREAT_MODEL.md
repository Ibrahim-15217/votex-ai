# Votex AI — Threat Model

| Field | Detail |
| --- | --- |
| **Status** | Draft v0.1 — Phase 0 |
| **Method** | STRIDE for system threats; LINDDUN for privacy threats |
| **Scope** | Web client, API, database, evidence storage, AI analysis, audit chain and national aggregation |
| **Out of scope** | Real INEC systems, third-party infrastructure, production identity providers and live threat-intelligence feeds |
| **Owner** | Security lead |
| **Last reviewed** | 9 November 2026 |
| **Next review** | End of Phase 1, then before submission |

> This is a prototype threat model for a controlled demonstration using synthetic data. It does not certify fitness for national deployment.

---

## 1. System overview

```text
Analyst / Reporter browser
        │  HTTPS
        ▼
Nginx static host + reverse proxy  ──────────►  FastAPI  /api/v1
                                                    │
                        ┌───────────────────────────┼───────────────────────────┐
                        ▼                           ▼                           ▼
                  PostgreSQL                  Evidence storage            AI engine
              (incidents, users,            (files + SHA-256)        (rules, TF-IDF,
               audit chain)                                            risk score)
                        │
                        ▼
              National aggregate queries
              (k-anonymity k ≥ 5)
```

### Assets

| Asset | Why it matters |
| --- | --- |
| User credentials and sessions | Compromise enables impersonation and unauthorised actions |
| Incident reports and free text | May contain sensitive operational context |
| Evidence files | Integrity underpins investigation and accountability |
| Audit chain | Proves who did what and exposes tampering |
| Organisation boundaries | Prevent cross-tenant intelligence leakage |
| National aggregates | Small cells could identify an organisation or incident |
| AI model and ruleset | Manipulation could hide threats or create false alarms |
| Configuration and secrets | Enable full system compromise if exposed |
| Availability of the console | Loss of access during an election period is operationally serious |

### Trust boundaries

1. **Browser ↔ Nginx/API** — untrusted input crosses here.
2. **API ↔ PostgreSQL** — privileged data access.
3. **API ↔ evidence storage** — file read/write boundary.
4. **API ↔ AI engine** — untrusted report text is processed.
5. **Organisation A ↔ Organisation B** — hard tenant boundary.
6. **Organisation data ↔ national aggregates** — privacy boundary with suppression.
7. **User ↔ administrator** — privilege boundary.
8. **Repository/CI ↔ runtime** — supply-chain boundary.

### Assumptions

- TLS terminates at the reverse proxy in any non-local deployment.
- The demo runs with synthetic data only.
- Administrators are trusted but still audited.
- The AI engine is advisory; a human makes consequential decisions.
- Local Docker Compose is a demonstration environment, not a hardened production deployment.

---

## 2. STRIDE threats and controls

Status values: **Planned** (not built yet), **In progress**, **Implemented**, **Deferred**.

### 2.1 Spoofing

| ID | Threat | Control | Status |
| --- | --- | --- | --- |
| S1 | Credential stuffing against demo or analyst accounts | Argon2id hashing, rate limiting, account lockout, generic login errors | Planned (Phase 1) |
| S2 | Stolen session token reused | Short-lived access tokens, refresh rotation, revocation on logout | Planned (Phase 1) |
| S3 | Attacker pretends to be another organisation's analyst | Server-side identity lookup; never trust organisation ID from the request body | Planned (Phase 1) |
| S4 | Phishing of project maintainers through fake repository links | Documented official repository URL; signed releases; no credential prompts | Planned (Phase 6) |
| S5 | Weak demo password reused outside the demo | Demo-only banner, synthetic accounts, password documented as non-production | Implemented (design) |

### 2.2 Tampering

| ID | Threat | Control | Status |
| --- | --- | --- | --- |
| T1 | Evidence file altered after upload | SHA-256 recorded at upload; verification endpoint; hash shown in UI | Planned (Phase 1) |
| T2 | Audit rows edited or deleted to hide activity | Append-only policy, `prev_hash`/`entry_hash` chain, verification command, restricted DB role | Planned (Phase 1) |
| T3 | Incident status changed without authorisation | Role checks on every transition; audit entry per change | Planned (Phase 1) |
| T4 | Malicious file uploaded as evidence | Extension/MIME/size validation, safe filename, isolated storage, malware scan stretch goal | Planned (Phase 1) |
| T5 | Request body overrides server-computed risk score | Risk score computed server-side only; client values ignored | Planned (Phase 2) |
| T6 | Dependency or image compromise | Pinned versions, lockfiles, dependency and image scanning in CI | Planned (Phase 6) |

### 2.3 Repudiation

| ID | Threat | Control | Status |
| --- | --- | --- | --- |
| R1 | User denies submitting or closing an incident | Authenticated actions recorded with actor, timestamp and resource | Planned (Phase 1) |
| R2 | Administrator denies changing a role | Administrative actions included in the audit chain | Planned (Phase 1) |
| R3 | Exported report disputed | Export event audited; report includes generation time and filters | Planned (Phase 3) |
| R4 | Audit timestamps inconsistent | UTC internally, consistent serialisation, monotonic sequence | Planned (Phase 1) |

### 2.4 Information disclosure

| ID | Threat | Control | Status |
| --- | --- | --- | --- |
| I1 | IDOR: Organisation A reads Organisation B's incident by guessing an ID | Every query scoped by the authenticated user's organisation; 404 for foreign IDs | Planned (Phase 1) |
| I2 | Cross-tenant evidence download | Evidence access checked through the parent incident and organisation | Planned (Phase 1) |
| I3 | National dashboard leaks a small cell | k-anonymity suppression (k ≥ 5) enforced in the query layer, not only the UI | Planned (Phase 3) |
| I4 | Free text or evidence exposed in national aggregates | Aggregate schema excludes text, notes, filenames and identifiers | Planned (Phase 3) |
| I5 | Sensitive data in logs or error traces | Structured logging with redaction; generic client errors; no secrets in responses | Planned (Phase 1) |
| I6 | Over-fetching in API responses | Explicit response schemas; no ORM object dumping | Planned (Phase 1) |
| I7 | Browser cache exposes another user's data on a shared device | `Cache-Control: no-store` for authenticated responses; logout clears state | Planned (Phase 4) |
| I8 | Demo screenshots reveal real data | Synthetic dataset only; review screenshots before publishing | In progress |

### 2.5 Denial of service

| ID | Threat | Control | Status |
| --- | --- | --- | --- |
| D1 | Upload flood fills disk | Per-file size cap (10 MB), per-user rate limit, storage quota | Planned (Phase 1) |
| D2 | Expensive analysis blocks the API | Input length cap, synchronous timeout, worker queue as the next step | Planned (Phase 2) |
| D3 | Login brute force exhausts resources | Rate limiting and lockout with audit | Planned (Phase 1) |
| D4 | Large pagination request exhausts memory | Maximum page size and bounded filters | Planned (Phase 1) |
| D5 | Demo laptop cannot run the stack | Offline-friendly compose profile, recorded fallback demo | Planned (Phase 6) |

### 2.6 Elevation of privilege

| ID | Threat | Control | Status |
| --- | --- | --- | --- |
| E1 | Reporter calls analyst or admin endpoints | Central dependency checks role on every route; default deny | Planned (Phase 1) |
| E2 | User changes their own role in a profile update | Role and organisation fields excluded from self-service updates | Planned (Phase 1) |
| E3 | JWT algorithm confusion or forged signature | Fixed algorithm, signature verification, issuer/audience claims, expiry | Planned (Phase 1) |
| E4 | Admin endpoint reachable without authentication | Explicit router-level auth; tests for anonymous access | Planned (Phase 1) |
| E5 | Container runs as root | Non-root user in the image; read-only mounts where practical | Implemented (backend image) |

---

## 3. LINDDUN privacy threats

| ID | Threat | Control | Status |
| --- | --- | --- | --- |
| L1 | **Linking** incident reports to an organisation through aggregates | k ≥ 5 suppression; no organisation labels in national cells | Planned (Phase 3) |
| L2 | **Identifying** a reporter from free text | Minimise personal fields; redact logs; advise reporters not to include personal data | Planned (Phase 1) |
| L3 | **Non-repudiation** used against a reporter | Reporter identity limited to authorised staff; no public exposure; retention limits | Planned (Phase 4) |
| L4 | **Detecting** that a report exists by timing or error differences | Uniform 404 responses for unauthorised access; no existence leaks | Planned (Phase 1) |
| L5 | **Data disclosure** through exports | Permission checks, export auditing and suppression applied to exports | Planned (Phase 3) |
| L6 | **Unawareness** of data use | Plain-language notice at intake; documented purpose and retention | Planned (Phase 4) |
| L7 | **Non-compliance** with NDPA 2023 | Data inventory, lawful basis, retention schedule, deletion procedure | In progress (documentation) |
| L8 | Re-identification through combined filters | Privacy tests that combine date, state and category filters to find small cells | Planned (Phase 3) |

---

## 4. Finding-to-control matrix

| Finding | Primary controls | Verification |
| --- | --- | --- |
| Cross-tenant incident access | Organisation-scoped query layer, 404 responses | Automated test with two seeded organisations |
| Cross-tenant evidence access | Parent incident authorisation, isolated storage | Automated test plus manual download attempt |
| Audit tampering | Hash chain, append-only role, verification command | Tamper test that edits a row and expects detection |
| Small-cell leakage | Query-layer suppression k ≥ 5, exports inherit suppression | Privacy tests across filters and date ranges |
| Credential compromise | Argon2id, rate limit, lockout, token expiry | Auth tests and manual review |
| Malicious upload | Type/size validation, safe names, isolation | Upload tests with rejected files |
| Prompt or text injection into analysis | Treat report text as data; no tool execution; bounded model input | Adversarial text tests |
| Information leakage in errors | Redaction and generic error responses | Log review and API tests |
| Supply-chain compromise | Pinned versions, lockfiles, scanning | CI report |
| Demo failure | Offline compose, seeded data, recorded fallback | Fresh-clone rehearsal |

---

## 5. Residual risk register

| Risk | Likelihood | Impact | Residual position | Owner |
| --- | --- | --- | --- | --- |
| Determined attacker with database access can rewrite the whole chain | Low | High | Hash chain makes tampering evident, not impossible; production requires external anchoring and restricted DB roles | Security lead |
| AI misclassifies a genuine report as benign | Medium | Medium | Human review, visible reasons, never auto-close on model output | AI lead |
| AI flags a benign security advisory as phishing | Medium | Medium | Analyst override, feedback capture, evaluation of hard negatives | AI lead |
| Small-cell suppression can be bypassed by repeated queries | Low | Medium | Deterministic suppression and query auditing; differential privacy is post-hackathon | Privacy lead |
| Demo environment is not hardened for public exposure | Medium | High | Run locally or behind an authenticated tunnel; do not expose as production | Security lead |
| Hausa translation contains errors | Medium | Medium | Native-speaker review before submission; English fallback | Product lead |
| Evidence malware scanning is absent | Medium | Medium | Upload restrictions and isolation; scanning listed as pre-pilot requirement | Security lead |
| Availability depends on a single host | Medium | Medium | Offline demo and recorded fallback; HA is post-hackathon | Backend lead |
| Synthetic data does not represent real reports | High | Medium | Documented limitation; rules provide a transparent fallback | AI lead |

---

## 6. Security requirements for a future pilot

Before any real deployment, the following must be completed:

1. Independent penetration test and threat-model validation.
2. Production identity provider, MFA enforcement and privileged-access review.
3. Managed secrets, key rotation and encryption-at-rest verification.
4. External anchoring or separate storage for audit hashes.
5. Malware scanning and content disarmament for uploads.
6. Backup, restore and disaster-recovery exercises.
7. Data-protection impact assessment and signed institutional agreement.
8. Retention, deletion and subject-request procedures tested end to end.
9. Security monitoring, alerting and an incident-response runbook.
10. Accessibility and language review with representative users.

---

## 7. Review log

| Date | Change | Reviewer |
| --- | --- | --- |
| 9 Nov 2026 | Initial draft for Phase 0 | Security lead |
