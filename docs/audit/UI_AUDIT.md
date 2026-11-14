# Votex AI — UI Professionalism Audit

**Scope:** the eight authenticated routes plus `/login`, on the Phase 5 build
(`0.5.0`, commit `6c386af`).

**Mode:** read-only. This audit changed no product code, no copy and no
configuration. All evidence below was gathered from source review and headless
browser runs against the local demo instance.

**Purpose:** decide, before Phase 6 hardening, what to keep, rewrite and remove
so the prototype reads as a credible product rather than a build log.

---

## 1. Method

| Check | How | Result |
| --- | --- | --- |
| Responsive sweep | 320 / 360 / 390 / 768 / 1024 / 1280 / 1440 / 1920 px, all 8 routes | 0 px page overflow, 0 console errors |
| 200% zoom equivalent | 640 CSS px, all 8 routes | 0 px page overflow |
| Locale stress | `ha`, `yo`, `ig` at 390 px on `/`, `/incidents`, `/report` | 0 px overflow, 0 errors |
| Role check | `reporter` at 390 and 1280 px | 3 nav links, 0 overflow, 0 errors |
| Copy extraction | Full visible text per route, sticky header vs page header | Inventory in §5 |
| Failure probe | Per-route data endpoints blocked via CDP, then reload | Matrix in §6 |
| Source review | All pages, `ui.tsx`, `AppShell`, `format.ts`, `api.ts`, `en.ts` | Citations below |

Contained overflow was observed only inside the Audit table (`min-w-[860px]`)
and the Incidents table (`min-w-[720px]`). Both scroll inside their own card and
never produce a page scrollbar.

---

## 2. Verdict

The layout system is solid. The problems are almost entirely **what the
interface says** and **what it claims when something fails**.

Three themes:

1. **Failure states either hang or fabricate.** Four routes show an infinite
   spinner or an empty state that looks like real data after an error, and every
   error leaks `port 8000`.
2. **Build language is on the demo path.** `Phase 3`, `Phase 5`, `seeded`,
   `query layer`, `magic bytes`, `API endpoint` and a version badge appear on
   screen during the pitch.
3. **Some claims are not true of this build.** `TLS · DEMO` over plain HTTP,
   static telemetry that contradicts seeded data, and a checkbox that does
   nothing.

A judge will not test every endpoint. They will read the screen, scroll, and
click. Those three themes are exactly what they will find.

---

## 3. What is already strong — keep

- **Visual system.** Dark surface ramp, brand/violet accents, mono for
  identifiers and hashes, consistent 1 px borders and panel blur. It looks
  deliberate at every width.
- **Information architecture.** Overview → queue → case → intelligence →
  dashboards → resilience → audit is a coherent analyst journey with no dead
  ends.
- **Contained table scrolling.** Wide tables scroll inside cards without
  breaking the page at 320 px.
- **Four-language shell.** Navigation, intake and queue switch cleanly; the
  language switcher meets target size and exposes endonyms to assistive tech.
- **Honesty scaffolding.** The `k ≥ 5` suppression note, "never visits a link",
  SHA-256 evidence hashing and the append-only audit story are genuinely
  differentiating. Keep the substance, rewrite the phrasing.
- **Empty and error states exist.** Dashboards is the model: an explicit
  "Dashboard unavailable / Refresh to try again" panel. Most screens already
  have the components; they just do not use them on failure.

---

## 4. Findings by severity

### P0 — breaks trust or blocks the demo

**F-01 · Four failure states hang or fabricate data**

| Route | Observed | Cause |
| --- | --- | --- |
| `/` | `AUDIT INTEGRITY —` + "Verifying the chain" + spinner never resolves; Audit chain card stuck on "Recomputing the chain" | `OverviewPage.tsx:118-123` swallows `verifyAudit()` rejection; the render at `:211` and the audit card stay in the pending branch |
| `/audit` | Chain status card stuck on "Verifying the chain" with spinner while the table loads | `AuditPage.tsx:86-98` swallows the rejection; `:226` has no error branch |
| `/intelligence` | Selecting an indicator whose detail call fails shows "Loading correlated cases" forever | `IntelligencePage.tsx:137-141` sets `detail = null`, then `:437` treats `!detail` as loading |
| `/resilience` | Data endpoints down still renders `0` assessments, "No score yet", "No assessments yet" as if they were real | `ResiliencePage.tsx` renders summary/history regardless of load error; only one banner admits the failure |

Reproduce: load the route, block the specific endpoint, reload, wait 10 s.

**F-02 · Every error message leaks local infrastructure**

All routes print, verbatim:

> Cannot reach the Votex API. Check that the backend is running on port 8000.

Source: `frontend/src/lib/api.ts:500`. This is developer copy on a judge-facing
screen. It also contradicts the "never touches a real system" framing.

Secondary: when the API is fully unreachable the app silently redirects to
`/login` with no explanation, so the user believes they were signed out.

**F-03 · Error plus empty state are shown together**

- `/incidents`: error banner **and** "No incidents yet" **and**
  "Showing 0–0 of 0".
- `/intelligence`: error banner **and** "No indicators match this filter" plus
  zeroed counters.
- `/resilience`: error banner **and** zeroed KPIs **and** "No assessments yet".

The banner says "failed"; the body says "there is nothing here". On a quick
read the body wins.

**F-04 · Login makes claims the build does not support**

| Claim | Where | Reality |
| --- | --- | --- |
| `TLS · DEMO` | `LoginPage.tsx:200` | Dev server is plain HTTP; TLS is terminated nowhere in this prototype |
| `REPORTS TRIAGED 128`, `INDICATORS LINKED 09`, `AUDIT CHAIN 100%` | `LoginPage.tsx:177-179` | Hard-coded; the seeded tenant actually has 10 incidents, 10 indicators and 9 open findings |
| "Remember me" | `LoginPage.tsx:280-287` | Checkbox has no state and no handler; it changes nothing |
| "System ready" | `en.ts:77` | Static; no health call |

"Forgot password?" is fine: it shows an honest notice that resets are disabled
in the prototype (`en.ts:109-110`). Keep that.

A judge who signs in and compares the login telemetry to the dashboard sees two
different products.

**F-05 · Build-phase language appears on screen**

- `Phase 5 · Resilience & simulation` badge, sticky header, every route
  (`en.ts:69`, `AppShell.tsx:246`).
- `Phase 5 · …` / `Phase 3 · …` page eyebrows:
  `OverviewPage.tsx:144`, `IntelligencePage.tsx:180,195`,
  `DashboardsPage.tsx:138,153`, `ResiliencePage.tsx:542,557`.
- `v0.5.0 · Phase 5` on the login telemetry header (`en.ts:94`).
- `Track 04 · Electoral Cybersecurity & Resilience` above the login hero
  (`en.ts:78`).

This is sprint vocabulary, not product vocabulary. It tells the reader they are
looking at an unfinished internal build.

---

### P1 — visible professionalism defects

**F-06 · Duplicate page headers on six of eight routes**

`AppShell.tsx:231-236` renders the page eyebrow and title in the sticky header.
Each page then renders the same pair again through `PageHeader`
(`ui.tsx:228-253`).

| Route | Sticky | Page | Verdict |
| --- | --- | --- | --- |
| `/incidents` | Response workflow / Incident queue | Response workflow / Incident queue | Exact duplicate |
| `/audit` | Integrity / Audit trail | Integrity / Audit trail | Exact duplicate |
| `/dashboards` | Situational awareness / Threat dashboards | Phase 3 · Situational awareness / Threat dashboards | Duplicate + meta |
| `/resilience` | Readiness / Resilience & simulation | Phase 5 · Readiness / Resilience & simulation | Duplicate + meta |
| `/intelligence` | Correlation / Indicator intelligence | Phase 3 · Correlation live / Indicator intelligence | Duplicate + meta + eyebrow mismatch |
| `/report` | Intake / Report an incident | Intake / Report a threat | Near-duplicate + **title mismatch** |
| `/` | Command centre / Operations overview | Phase 5 · … / Good afternoon, Tunde | Eyebrow duplicate, title differs |
| `/incidents/:id` | Case workspace / Incident detail | (none) / incident title | Correct — the model to follow |

**F-07 · `humanise()` produces broken labels**

`format.ts:44-46` title-cases each word and does not know acronyms. Observed on
screen: `Ai Analysis — Amara Okafor` (timeline), `Incident reported through
Sms.` (timeline), and `Correlation linked 3 indicator(s): 1 url, 1 domain, 1
ipv4.` (AI explanation). Dictionary values elsewhere render correctly as `SMS`
and `IPv4`, so the same concept appears twice with different casing.

**F-08 · Risk colour contradicts the AI bands**

`RiskScore` (`ui.tsx:110-113`) uses 85 / 70 / 50. The AI panel classifies at
65 / 35. A case scored 61 shows a green bar in the queue and "Suspicious" amber
in the explanation. Same number, two stories.

**F-09 · Three summary-card implementations**

`OverviewPage.tsx:389` (`StatCard`), `DashboardsPage.tsx:442` (`StatTile`),
`DashboardsPage.tsx:469` (`Metric`), `ResiliencePage.tsx:1494` (`MiniStat`) and
`LoginPage.tsx:388` (`Metric`) are five near-duplicate tiles with different
padding, label casing, value size and tone handling. At 320 px they wrap
differently, which is visible when moving between tabs.

**F-10 · Neutral empty states use a warning icon**

`EmptyState` (`ui.tsx:169-190`) always renders `AlertTriangleIcon`, including
"No incidents yet" and "Select an indicator". Nothing is wrong in those states.

**F-11 · Language coverage is inconsistent and visibly so**

- The notice "Case records … remain in English in this prototype" is a
  full-width paragraph on detail, intelligence, dashboards, audit and
  resilience. It is accurate but dominates the first screen.
- `IncidentDetailPage` is almost entirely hard-coded English (`:682`, `:692`,
  form labels, timeline, controls) despite importing `t` at `:89`.
- Page eyebrows are literal English strings, so in `ha`/`yo`/`ig` the sticky
  header translates while the page header below it stays English.

**F-12 · Internal architecture copy in analyst screens**

| String | Location |
| --- | --- |
| "Mean seeded risk score" | `en.ts:262` |
| "Tenant isolation in the query layer" | `en.ts:290` |
| "National aggregates apply k ≥ 5 suppression in the backend query layer" | `en.ts:295` |
| "…suppressed before it leaves the server" | `DashboardsPage.tsx:155` |
| "Aggregates are computed in the query layer" | `DashboardsPage.tsx:390` |
| "magic bytes are validated before storage" | `IncidentDetailPage.tsx:682` |
| "Append-only API. There is no edit or delete endpoint." | `AuditPage.tsx:242` |
| "Design properties you can demonstrate live." | `AuditPage.tsx:233` |
| "Integrity footer" | `IncidentDetailPage.tsx:692` |
| "synthetic demo tenant" | `en.ts:147` |
| "Closed during the demonstration data setup." | `seed.py:1121` |
| "Recorded by the demonstration analyst during the synthetic run." | `seed.py:1162` |

**F-13 · Manual refresh errors are unhandled**

`IncidentDetailPage.tsx:289-299`: clicking Refresh with the API down rejects
silently — no notice, no state change. Other refresh handlers do surface errors,
so the behaviour is inconsistent as well as wrong.

---

### P2 — polish

- **F-14** Audit table scroller is not keyboard reachable (`AuditPage.tsx:287-288`);
  the Incidents table equivalent has the same pattern. Wheel/trackpad only.
- **F-15** Dates are always `en-GB` (`format.ts:52`), so a Yoruba interface
  shows English month abbreviations while relative times translate.
- **F-16** Button, pagination and tab treatments drift across pages
  (`btnPrimary` / `btnSubtle` / `btnGhost` plus local overrides).
- **F-17** Overview greeting ("Good afternoon, Tunde") is the only time-of-day
  personalisation and has no fallback for an unknown name.
- **F-18** Marketing register in analyst copy: "Core operations. Coordinated."
  panel subtitles, "Controls you can point to, not promises." These are fine on
  the login hero, less so inside the console.

---

## 5. Copy inventory

### Remove

| String | Where | Why |
| --- | --- | --- |
| `Phase 5 · Resilience & simulation` | sticky badge, all routes | Build phase |
| `Phase 5 · Resilience & simulation` | Overview eyebrow | Duplicate + build phase |
| `Phase 3 · Correlation live` | Intelligence eyebrow | Build phase + duplicate |
| `Phase 3 · Situational awareness` | Dashboards eyebrow | Build phase + duplicate |
| `Phase 5 · Readiness` | Resilience eyebrow | Build phase + duplicate |
| `v0.5.0 · Phase 5` | Login telemetry | Version meta |
| `Track 04 · Electoral Cybersecurity & Resilience` | Login hero | Category meta; belongs in footer/README |
| `TLS · DEMO` | Login secure access | False claim |
| `Remember me` | Login form | Checkbox does nothing |
| `System ready` | Login brand bar | Static claim |
| `Mean seeded risk score` | Overview | Test-fixture language |
| `magic bytes` | Case upload help | Implementation detail |
| `Append-only API … endpoint` | Audit explainer | Implementation detail |
| `Design properties you can demonstrate live.` | Audit explainer | Talks about the demo |
| `Integrity footer` | Case card heading | Internal name |
| `synthetic demo tenant` | Report privacy note | Fixture language |
| `query layer` / `backend` | Overview, Dashboards | Architecture jargon |
| Demonstration notes | Seeded timeline | Fixture voice |

### Rewrite

| Current | Proposed | Where |
| --- | --- | --- |
| "Cannot reach the Votex API. Check that the backend is running on port 8000." | "We can't reach the service right now. Check your connection and try again." | `api.ts:500` |
| "Verifying the chain" (pending forever) | "Chain check unavailable · Try again" | Overview / Audit |
| "No incidents yet" (after error) | Hidden while an error is shown | Incidents |
| "No indicators match this filter" (after error) | Hidden while an error is shown | Intelligence |
| "No assessments yet" (after error) | Hidden while an error is shown | Resilience |
| "Tenant-isolated queries" | "Organisation-isolated records" | Guardrails |
| "k ≥ 5 aggregate suppression" | "Small cells suppressed (k ≥ 5)" | Guardrails |
| "Tenant isolation in the query layer" | "Organisation isolation" | `en.ts:290` |
| "…in the backend query layer" | "…before any national total is shown" | `en.ts:295` |
| "…before it leaves the server" | "…before any total is shown" | `DashboardsPage.tsx:155` |
| "Aggregates are computed in the query layer." | "National totals are aggregated before display." | `DashboardsPage.tsx:390` |
| "Records outside your organisation, or reports submitted by another reporter, are hidden by design." | "Records from other organisations, or another reporter's reports, stay hidden." | Case detail |
| "Every authentication, incident change and evidence access is chained with SHA-256. Verification recomputes the full chain from genesis." | "Every sign-in, case change and evidence access is linked with SHA-256. Verification rechecks the whole chain from the first entry." | Audit |
| "Design properties you can demonstrate live." → | "How the chain holds" | Audit |
| Full-width English-only paragraph | Compact badge: "English · case data" with one-line tooltip | 5 routes |
| "Case records, AI explanations and analyst dashboards remain in English in this prototype…" | "Case data stays in English. Intake, queue and navigation are translated." | `en.ts:25` |
| "Controls you can point to, not promises." | "Controls in this build" | Overview |
| "Core operations. Coordinated." | "Core operations" | Overview |
| Login telemetry 128 / 09 / 100% | Live values from the same stats call the dashboard uses (10 incidents, 10 indicators, 9 open findings), or remove the panel | Login |

### Keep

- "One defensible workflow for electoral threats: report, analyse, correlate,
  coordinate the response and prove the record was not altered."
- "Explainable triage", "Integrity by design", "Privacy preserved"
- "Synthetic data only" (as a badge, not a paragraph)
- "Offline, never visits a link"
- "A single altered, removed or reordered entry breaks verification."
- "Every report in your organisation, scoped by tenant and ordered by recency."
  (rewrite "tenant" → "organisation")
- "Not affiliated with INEC, Rise Networks or any partner."
- "No real system access is granted."

---

## 6. State matrix (measured)

| Route | Blocked endpoint | What the screen shows | Correct? |
| --- | --- | --- | --- |
| `/` | `audit/verify` | "Verifying the chain" + spinner, forever | No — hangs |
| `/` | `incidents/stats` | Error banner, other panels load | Mostly; banner leaks port |
| `/incidents` | `incidents?` | Error + "No incidents yet" + "0–0 of 0" | No — contradictory |
| `/incidents/:id` | `incidents/*` | Error notice + "hidden by design" note | Partial; leaks port |
| `/intelligence` | `indicators*` | Error + "No indicators match this filter" + zero counters | No — contradictory |
| `/intelligence` | `indicators/{id}` | "Loading correlated cases" forever | No — hangs |
| `/dashboards` | `dashboards/*` | "Dashboard unavailable · Refresh to try again" | **Yes — model state** |
| `/resilience` | `resilience/*` | Error banner + zeroed KPIs + "No assessments yet" | No — contradictory |
| `/audit` | `audit/verify` | "Verifying the chain" + spinner, forever | No — hangs |
| `/audit` | `audit?` | Error + "No audit entries match this filter" | No — contradictory |
| all | everything | Silent redirect to `/login` | No — no explanation |

Positive states (loading, success, stale, empty) are otherwise consistent.
Zero console errors in every pass — the failures are swallowed, not thrown.

---

## 7. Responsive matrix (measured)

| Width | Page overflow | Notes |
| --- | --- | --- |
| 320 | 0 px | Audit/Incidents tables scroll inside cards; 255 contained offenders on `/audit` |
| 360 | 0 px | Same |
| 390 | 0 px | Same; `ha`/`yo`/`ig` also 0 px on three routes |
| 768 | 0 px | Tables switch to desktop layout |
| 1024 | 0 px | Org slug chip appears |
| 1280 | 0 px | Phase badge appears |
| 1440 | 0 px | Max content width reached |
| 1920 | 0 px | Centred, no stretch |
| 640 @ 200% zoom | 0 px | All routes |

No responsive fixes required in structure. The defects are density and text
length, not breakage.

---

## 8. Consistency findings

| Area | Inconsistency |
| --- | --- |
| Risk colour | 85/70/50 (`RiskScore`) vs 65/35 (AI bands) |
| Summary tiles | Five near-duplicates: `StatCard`, `StatTile`, two `Metric`, `MiniStat` |
| Buttons | Primary/ghost/subtle mixed with local overrides; icon-only buttons vary 32–40 px |
| Header | Sticky header vs `PageHeader` instead of one source of truth |
| Eyebrows | Some derived from `en.ts`, some literal strings, so only half translate |
| Empty state | Warning icon for neutral states; copy tone varies between "No X yet" and "No X match this filter" |
| Error state | Dashboards has a proper panel; every other route uses a raw banner |
| Dates | `en-GB` fixed while other copy localises |
| Casing | Dictionary labels ("SMS") vs `humanise()` ("Sms") |

---

## 9. Recommended polish order

Only the first four groups touch the demo path. Groups 5–6 can follow axe.

1. **Truthful failure states** (F-01 to F-03). Add error branches to the four
   hanging/contradictory routes, copy the Dashboards pattern, and give the
   connection error one plain-language message. ~1 focused pass.
2. **Remove build language** (F-05, F-12). Delete the phase badge, phase
   eyebrows, version chip, track eyebrow, "seeded", "query layer",
   "magic bytes", "endpoint", "fixture" notes. Replace with product nouns.
3. **Fix login claims** (F-04). Remove TLS and "System ready", wire the
   telemetry to real stats or remove the panel, and remove or implement
   Remember me.
4. **Collapse duplicate headers** (F-06, F-11). One header per page: keep the
   sticky bar as the location cue, and make `PageHeader` the single owner of
   eyebrow + H1 + description. Fix the Report title mismatch. Convert the
   English-only paragraph into a compact badge.
5. **Consistency pass** (F-08, F-09, F-10, F-16, F-17). Unify risk thresholds
   with the AI bands, one stat tile, one empty-state icon rule, one button
   scale.
6. **Remaining polish** (F-07, F-13, F-14, F-15, F-18). Acronym-safe labels,
   handled manual refresh, keyboard-scrollable tables, locale-aware dates,
   calmer analyst copy.

**Not in scope for this pass:** new features, layout redesign, new locales,
backend changes beyond seeded note text.

---

## 10. Decisions requested

1. Approve the **P0 fixes** (F-01 to F-05) as one batch.
2. Approve **removing** the phase badge, all phase eyebrows, the login version
   chip and the login track eyebrow.
3. Approve **replacing** the login telemetry with live stats, or removing the
   panel entirely.
4. Approve the **header model**: sticky bar = location cue only; page owns
   eyebrow + H1 + description.
5. Approve **compact English-only badge** rather than the full paragraph.
6. Approve **P2 items** now, or defer them until after axe and screenshots.

Nothing in §9 starts until these are confirmed.

---

## 11. Resolution log

Groups 1–4 of §9 were approved and implemented on 13 November 2026. P2 items
(F-07 to F-10, F-13 to F-18 except those noted below) remain deferred until
after the axe pass and final screenshots.

| Finding | Status | What changed |
| --- | --- | --- |
| F-01 | Fixed | Overview and Audit chain verification now render a named failure state with a retry instead of an endless spinner. |
| F-02 | Fixed | Indicator detail failures show an error panel; the loading state can no longer persist forever. |
| F-03 | Fixed | Incidents, intelligence, dashboards and resilience render `ErrorState` when the first load fails, with counters and pagination suppressed. Boot failure keeps the token and shows a service-unavailable screen with retry and sign out. |
| F-04 | Fixed | Login telemetry reads the new public `/demo/telemetry` endpoint; TLS, "System ready", the version chip, the track eyebrow and "Remember me" were removed. Forgot password keeps its prototype notice. |
| F-05 | Fixed | Phase badge, phase eyebrows and build language removed from the shell, pages and seed notes. |
| F-06 | Fixed | The sticky bar is now an organisation → page breadcrumb; each page owns a single H1 and description. |
| F-11 | Fixed | English-only disclosure is a compact badge on audit, intelligence, dashboards, resilience and incident detail. |
| F-12 | Fixed | "Query layer", "magic bytes", "Integrity footer" and "Design properties you can demonstrate live" replaced with product nouns. |
| F-07 to F-10, F-13 to F-18 | Deferred | Risk thresholds, unified stat tiles, empty-state icon, button scale, manual refresh, keyboard table scrolling, locale dates and the remaining consistency items. |

Verification for this batch:

- `pytest -q`: 55 passed (52 existing tests plus 3 telemetry tests).
- `npm run build`: TypeScript clean; 413.33 kB JS (117.35 kB gzip), 41.58 kB CSS (8.23 kB gzip).
- Failure probe: every route resolves to an honest error state with retry, no infinite spinners, 0 console errors.
- Boot-failure probe: token survives a fully blocked API, the unavailable screen appears, retry recovers the console.
- Responsive sweep: 320/360/390/768/1024/1280/1440/1920 across all eight routes, 200% zoom, three locales and the reporter role — 0 px page overflow and 0 console errors.
- Copy sweep: no banned build-language string on any route; badge present where expected; forgot-password notice confirmed.

---

## 12. Accessibility pass

Full results: [AXE_REPORT.md](./AXE_REPORT.md).

- axe-core 4.10.2 (WCAG 2.0/2.1 A + AA plus best practice) across nine screens at
  1280 × 900 and 390 × 844: **0 violations, 0 console errors** in 18 loads.
- Four interactive states (mobile navigation drawer, new assessment form,
  exercise task list, indicator detail): **0 violations**.
- Harness control: an injected unlabelled image was correctly reported as
  `image-alt`, confirming the run was not a false clean.
- axe cannot resolve contrast over the decorative grid, so a manual composite
  check covered 360 text/background pairs; every pair passes AA. Primary labels
  on the brand gradient measure 5.45:1 to 11.09:1.
- No product changes were required. P2 items stay deferred until after the
  final screenshots.

