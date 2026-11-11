# Votex AI — Privacy and Correlation Evidence

| Field | Detail |
| --- | --- |
| **Status** | Complete v0.3 — Phase 3 |
| **Verified** | 11 November 2026 |
| **Scope** | Indicator extraction, tenant-scoped correlation, k ≥ 5 national suppression, CSV exports and audit |
| **Data** | Synthetic demo records only; no voter, staff or partner data |

This note records what Phase 3 claims, how each claim is enforced and the exact evidence produced during live verification. It complements the threat model and the development plan.

---

## 1. Claims and controls

| Claim | Control | Where it lives |
| --- | --- | --- |
| Correlation never visits a link | The extractor parses text, URLs and stored hashes only. It performs no DNS lookup, HTTP request or file execution. | `backend/app/ai/iocs.py` |
| Correlation stays inside one organisation | Indicators are owned by an organisation. Search, detail, related incidents and dashboards filter on the caller's organisation. | `backend/app/services/correlation.py` |
| Reporters only see their own reports | Related-incident queries add `Incident.reporter_id == user.id` for the `reporter` role. Indicator search and dashboards are analyst/admin only. | `related_incidents()`, `backend/app/api/v1/intelligence.py` |
| National visibility cannot expose a small cell | Every aggregate passes through `_suppressed()`; values where `0 < count < 5` become `null`. Top national indicators use a `HAVING count >= 5` query. | `_dashboard_data()` |
| Suppressed values never reach a file | CSV serialisers write an empty value when the cell is suppressed. Raw values are never fetched into the export payload. | `indicator_csv()`, `dashboard_csv()` |
| Exports are accountable | Every CSV export writes an `intelligence.exported` entry to the SHA-256 audit chain after permission checks. | `record_audit()` in `correlation.py` |
| Official and generic hosts do not create noise | `inec.gov.ng`, `cert.gov.ng`, `nccc.gov.ng`, reserved documentation domains and social platforms are excluded. Ambiguous file-extension hosts are also skipped. | `OFFICIAL_DOMAINS`, `GENERIC_DOCUMENTATION_DOMAINS`, `PLATFORM_DOMAINS` |

### Suppression mechanics

`_suppressed(value, enabled=True)` returns `(None, True)` when a positive count is below the threshold. This is applied to:

- summary tiles (total, open, high-risk open, linked incidents, shared indicators);
- the 30-day trend (daily total and daily high-risk count);
- severity, category, channel, state and status breakdowns;
- national top indicators, which are filtered in SQL with `HAVING count(incident_id) >= 5`.

A value of exactly zero is returned as zero rather than suppressed, because zero cannot identify a contributor. The browser receives `null`; the UI renders a “k < 5” chip.

---

## 2. Live verification (11 November 2026)

The demo database was reset to the enriched synthetic seed and analysed end to end.

| Check | Result |
| --- | --- |
| Demo authority incidents | 10 · 9 open · 7 high-risk open · mean risk 65.2 |
| Shared indicators | 5 indicators used by 2 or more incidents · 9 of 10 incidents linked |
| Top organisation indicator | `https://pvc-registration-ng.example/start` — 4 incidents |
| Related incidents | `VX-2026-A10002` → 3 linked cases · `VX-2026-A10010` → `VX-2026-A10001` via URL, domain and identical evidence SHA-256 |
| National incidents | 13 across 2 organisations |
| National top indicators | PVC URL and PVC domain — 5 linked incidents each, across 2 organisations (exactly at the k threshold) |
| Suppressed national cells | **39** returned as `null` |
| National CSV | 39 rows marked `suppressed = yes` with blank values |
| Export audit | `GET /audit?action=intelligence.exported` → 3 entries after three exports |
| Audit chain | `GET /audit/verify` → `valid: true` |
| Reporter access | `GET /indicators` as `reporter@votex.demo` → `403` |
| Backend tests | `40 passed` |
| Browser errors | 0 across six Phase 3 screens |

### Visual evidence

- `docs/demo/screenshots/phase3-intelligence-1440x1000.png`
- `docs/demo/screenshots/phase3-dashboard-organisation-1440x1000.png`
- `docs/demo/screenshots/phase3-dashboard-national-1440x1000.png`
- `docs/demo/screenshots/phase3-related-incidents-1440x1000.png`
- `docs/demo/screenshots/phase3-audit-1440x1000.png`
- `docs/demo/screenshots/phase3-overview-1440x1000.png`

---

## 3. Reproduce

From `backend`:

```bash
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\python.exe -m pytest tests/test_correlation.py tests/test_iocs.py -q
```

The correlation suite covers:

- shared-domain linking and cross-tenant exclusion;
- reporter-scoped related incidents;
- evidence text and hash extraction;
- organisation and national dashboards with suppressed cells;
- permission-checked CSV exports and `intelligence.exported` audit entries.

With the backend running, sign in as `admin@votex.demo` and request:

```text
GET /api/v1/indicators?q=pvc-registration-ng.example
GET /api/v1/dashboards/organisation
GET /api/v1/dashboards/national
GET /api/v1/dashboards/national/export
GET /api/v1/audit?action=intelligence.exported
GET /api/v1/audit/verify
```

Check that the national response contains `null` counts with `suppressed: true`, that the national CSV leaves the same values blank, and that the export appears on the audit chain.

---

## 4. Residual risk and pilot hardening

| Risk | Current mitigation | Pilot hardening |
| --- | --- | --- |
| Differencing across repeated queries | k ≥ 5 on every response; no per-tenant slice in the national view | Query budgets, complementary suppression and differential privacy for repeated national queries |
| A unique URL can describe one victim | URLs are only visible inside the reporting tenant; national views aggregate them | Strip query strings and fragments by default; allow analysts to redact sensitive paths |
| Authorised export of raw indicators | Exports are role-checked and audited | Retention policy, watermarking, download expiry and periodic access review |
| Correlation can be wrong | Exact normalised matching, human review and visible source labels | Analyst merge/split controls with audit records |
| Small organisations can be inferred from totals | No national per-organisation breakdown | Minimum organisation population and suppression of organisation counts below k |
| Hash reuse can be coincidental | Hashes are exact and shown with their source | Reviewer confirmation before a hash link drives escalation |

The prototype does not claim formal differential privacy. It implements a defensible k-anonymity floor and states the remaining inference risk openly.
