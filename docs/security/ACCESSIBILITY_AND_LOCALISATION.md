# Accessibility and Localisation Evidence

Phase 4 turns the Votex AI prototype from an English-only analyst tool into an
inclusive intake and triage surface. This document records what was built, how it
maps to WCAG 2.2 AA, and the browser evidence captured on **11 November 2026**.

Scope: sign-in, application shell and navigation, incident intake, incident
queue, overview, statuses, priorities, categories, channels and relative time.
Analyst-only case records, AI explanations and dashboards remain in English, and
each of those screens carries a visible English-only notice so the boundary is
honest rather than hidden.

---

## 1. Language coverage

| Locale | Code | Coverage | Endonym in switcher |
| --- | --- | --- | --- |
| English | `en` | Source of truth for every key | English |
| Hausa | `ha` | Complete dictionary | Hausa |
| Yoruba | `yo` | Complete dictionary | Yorùbá |
| Igbo | `ig` | Complete dictionary | Igbo |

Implementation:

- `frontend/src/lib/locales/en.ts` defines `TranslationKey` from the English
  object, so a missing or misspelt key fails `tsc`.
- `ha.ts`, `yo.ts` and `ig.ts` are typed as `Record<TranslationKey, string>`.
  Adding an English key without translating it therefore breaks the build instead
  of silently falling back.
- `frontend/src/lib/language.tsx` provides `LanguageProvider`, `useI18n`,
  `formatRelative` and locale tags (`en-GB`, `ha-NG`, `yo-NG`, `ig-NG`).
- The choice is stored in `localStorage["votex.lang"]` and mirrored to
  `<html lang>` on every change, so screen readers and the browser pick the right
  pronunciation rules.
- `frontend/src/components/LanguageSwitcher.tsx` uses endonyms, `aria-pressed`,
  `lang` on each button, visible labels and targets of at least 28 × 32 px.
- The switcher appears on the sign-in screen and in the console header, so a user
  never has to sign in to change language.

Translation quality note: the dictionaries were written for this prototype and
reviewed for consistent electoral vocabulary, but they have **not** been through
professional native-speaker sign-off. A pilot must add that review before public
deployment.

---

## 2. WCAG 2.2 AA measures

### Perceivable

- Text contrast was swept across the interface. Low-opacity muted text below 80%
  was raised to `text-muted` or `text-muted/80`; input placeholders use
  `placeholder:text-muted/80`.
- Status is never communicated by colour alone: every pill carries a text label,
  and list rows pair colour with status, priority and risk values.
- Charts expose text summaries, `role="img"` labels and per-point titles.
- The interface has no external font, icon font or media dependency, so text
  remains readable if third-party assets are blocked.

### Operable

- Every interactive control is a native `button`, `a`, `input`, `select` or
  `textarea`; no click-only `div` handlers.
- A skip link is the first focusable element on the sign-in screen and in the
  console, targeting `#main`.
- Focus is moved to `<main>` after client-side navigation and the new page title
  is announced through a polite live region.
- `:focus-visible` draws a 2 px cyan outline with a 2 px offset; `scroll-padding-top`
  keeps focused fields clear of the sticky console header.
- Mobile menu and sign-out controls are at least 32–40 px, and the queue filter
  controls keep a 42 px minimum height.
- There are no keyboard traps and no drag-only interactions.

### Understandable

- Landmarks and headings: one `h1` per screen via `PageHeader`, labelled forms,
  `aria-label` on icon-only controls, `aria-describedby` on hints and counters.
- Errors use `role="alert"` and receive programmatic focus on the intake form;
  success uses `role="status"`.
- Relative time, statuses, priorities and categories are localised rather than
  left as raw database values.
- Language is declared per button and on the document, so mixed-language content
  is announced correctly.

### Robust

- Semantic table markup with `scope="col"` headers.
- The queue has a real table on desktop and a list on mobile instead of a
  horizontally squeezed table.
- Guardrail and privacy statements are available as text, not only as icons.

### WCAG 2.2-specific checks

- **2.4.11 Focus Not Obscured:** sticky header offset handled with
  `scroll-margin`/`scroll-padding`.
- **2.5.8 Target Size (Minimum):** language targets ≥ 28 × 32 px; primary and
  filter controls ≥ 42 px tall where practical.
- **3.2.6 Consistent Help:** language switching is in the same position on every
  screen.
- **3.3.7 Redundant Entry:** reporters are not asked to re-enter previously
  supplied details in a single session.
- **3.3.8 Accessible Authentication:** the demo form supports password managers
  and offers a show/hide toggle without a cognitive test.

Known gaps: no automated axe run is committed yet, and the analyst workspace has
not been translated. Both are listed as Phase 5 hardening work rather than
claimed as complete.

---

## 3. Low-bandwidth and low-end device behaviour

`frontend/src/index.css` adds two media-query layers:

```css
@media (prefers-reduced-motion: reduce) { /* near-zero animation and transitions */ }

@media (prefers-reduced-data: reduce) {
  /* removes the grid, blur, glow, shadows, animations and backdrop filters */
}
```

The low-data mode is deliberate for Nigerian mobile networks: it turns the
console into a text-first layout, drops decorative large blurs, removes
animation, and disables backdrop filters that are expensive on low-end GPUs.
The same build ships no web fonts, no chart library and no tracking scripts.
The production bundle is **377.90 kB of JavaScript (109.88 kB gzip)** and
**39.70 kB of CSS (7.96 kB gzip)** as measured on 11 November 2026.

---

## 4. Measured browser evidence

Harness: headless Chrome 157 driven over CDP, Vite dev server on
`http://localhost:5173`, API on `http://127.0.0.1:8000`, synthetic data only.

### 4.1 Locale sweep on sign-in

Each switcher target was activated and the following were asserted:

| Locale | `<html lang>` | `localStorage["votex.lang"]` | Localised heading present |
| --- | --- | --- | --- |
| Hausa | `ha` | `ha` | Yes |
| Yoruba | `yo` | `yo` | Yes |
| Igbo | `ig` | `ig` | Yes |
| English | `en` | `en` | Yes |

### 4.2 Keyboard-only exit criterion

This is the Phase 4 exit criterion and it passed without a pointer:

1. Focus starts at the skip link. Pressing `Tab` walks the header and reaches the
   **Igbo** switcher button (`BUTTON | aria-label=Igbo`).
2. `Enter` activates it: `<html lang>` becomes `ig` and the intake heading becomes
   **“Kọọ ihe iyi egwu”**.
3. `Tab` reaches `#title`; text is typed with real key events.
4. `Tab` reaches `#description`; text is typed.
5. `Tab` reaches the submit button (**“Zipu akụkọ”**); `Enter` submits.
6. The app lands on `/incidents/{uuid}` and shows the Igbo success banner
   **“E zipuru akụkọ”** with the generated `VX-2026-…` reference.

A synthetic incident was created in the demo tenant by this test, as intended.

### 4.3 Responsive sweep

Six routes were checked at 390, 768, 1024 and 1440 px:

| Route | 390 | 768 | 1024 | 1440 |
| --- | --- | --- | --- | --- |
| `/` overview | Pass | Pass | Pass | Pass |
| `/incidents` queue | Pass | Pass | Pass | Pass |
| `/report` intake | Pass | Pass | Pass | Pass |
| `/intelligence` | Pass | Pass | Pass | Pass |
| `/dashboards` | Pass | Pass | Pass | Pass |
| `/audit` | Pass | Pass | Pass | Pass |

“Pass” means `documentElement.scrollWidth` never exceeded `clientWidth`, and the
browser console and runtime had **0 errors** across all 24 combinations. An
earlier run found that the recent-incidents table could force an implicit grid
track past the viewport at 768/1024 px; the grids now use `grid-cols-1` and
`minmax(0, …)` tracks, and cards are `min-w-0`. The sweep above is the
post-fix result.

Sign-in was additionally checked at the same four widths, and the intake, queue
and overview were captured at mobile width.

### 4.4 Reduced motion / reduced data

With `prefers-reduced-motion: reduce` emulated, the queue rendered at 390 × 844
with no overflow. The reduced-data CSS path is exercised by the same build and
documented above.

### 4.5 Screenshots

| File | Shows |
| --- | --- |
| `phase4-login-hausa-1440x1000.png` | Four-language switcher on sign-in, Hausa copy |
| `phase4-report-igbo-1440x1000.png` | Igbo intake reached by keyboard |
| `phase4-report-filled-igbo-1440x1000.png` | Keyboard-entered title and description |
| `phase4-detail-created-igbo-1440x1000.png` | Igbo success banner after Enter submit |
| `phase4-overview-hausa-1440x1000.png` | Localised overview and console chrome |
| `phase4-queue-hausa-1440x1000.png` | Localised queue, filters and relative time |
| `phase4-report-mobile-hausa-390x844.png` | Intake at mobile width |
| `phase4-overview-mobile-hausa-390x844.png` | Overview at mobile width |
| `phase4-queue-mobile-reduced-390x844.png` | Queue under reduced-motion emulation |

Screenshots are stored in `docs/demo/screenshots/`.

---

## 5. Reproduction

```bash
# Backend
cd backend
.venv\Scripts\python.exe -m pytest -q          # 40 passed

# Frontend
cd frontend
npm run typecheck
npm run build                                  # tsc + vite build
npm run dev
```

The browser checks were driven by a local CDP script against the running dev
server. The assertions (locale, keyboard path, overflow, console errors) are
listed above so they can be repeated manually or automated in CI.

---

## 6. Residual risks

- Machine translation was not used, but human translation still needs native
  review before a real election.
- English-only analyst screens are a deliberate scope boundary; a pilot should
  translate case narratives and AI explanations next.
- Diaspora and low-literacy users may need audio or icon-led intake; not built in
  this phase.
- The current contrast sweep is manual. Adding `axe-core` to CI is the next
  measurable step.
- Reduced-data support depends on the operating system exposing
  `prefers-reduced-data`; the interface still works without it, just with more
  decoration.
