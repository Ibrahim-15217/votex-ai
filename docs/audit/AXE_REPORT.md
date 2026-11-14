# Accessibility audit — axe-core

Run: 13–14 November 2026
Tool: axe-core 4.10.2
Ruleset: WCAG 2.0 / 2.1 A + AA plus the best-practice rules
Result types: violations

## Scope

| Screen | Route |
| --- | --- |
| Sign in | `/login` |
| Operations overview | `/` |
| Incident queue | `/incidents` |
| Incident detail | `/incidents/:id` |
| Report a threat | `/report` |
| Indicator intelligence | `/intelligence` |
| Dashboards | `/dashboards` |
| Resilience | `/resilience` |
| Audit trail | `/audit` |

Each screen was loaded as the analyst account at **1280 × 900** and
**390 × 844**, giving 18 page loads. Four interactive states were also audited:

- mobile navigation drawer open at 390 px,
- new resilience assessment form open,
- synthetic exercise selected (task list visible),
- indicator detail loaded.

## Result

**0 violations** across all 18 page loads and all four interactive states.
**0 console errors** in the same runs.

The suite was re-run after the later copy, date and keyboard-scroll changes
(F-07, F-14, F-15) with the same result: 0 violations, 0 console errors.

No critical or serious issues were found, so this pass required no product
changes.

### Harness validation

A clean result is only meaningful if the harness can fail. As a control, an
`<img>` without an `alt` attribute was injected into the overview page and the
same call reported `image-alt: 1`. The injected build reported
`axe.version === "4.10.2"`, and the same pages reported 40+ passing rules and
260–970 evaluated nodes each.

## Colour contrast

axe reports `color-contrast` as **incomplete** rather than pass/fail wherever a
decorative grid or gradient overlay sits behind text. The overlays are part of
the visual identity and sit under the content, so removing them purely to
satisfy the tool would be the wrong trade-off.

A separate script therefore composited semi-transparent backgrounds down to the
opaque page colour and computed WCAG 2.1 contrast ratios for every visible text
element: **360 unique text/background pairs across the nine screens**.

- 353 pairs pass their threshold (4.5:1 normal, 3:1 large).
- The other 7 are the primary-button labels shown on gradient fills. The script
  does not model gradients, so it compared the dark label against the dark page
  colour. Measured against the actual gradient stops:

| Pair | Ratio | Threshold |
| --- | --- | --- |
| `#05080F` label on `#22D3EE` (brand) | 11.09:1 | 4.5:1 |
| `#05080F` label on `#3B82F6` (brand-2) | 5.45:1 | 4.5:1 |
| `#E9F1FB` text on `#0A1220` surface | 16.46:1 | 4.5:1 |
| `#8BA2BD` muted on `#05080F` void | 7.63:1 | 4.5:1 |
| `#8BA2BD` muted on `#0A1220` surface | 7.14:1 | 4.5:1 |

Every text pair measured is above the WCAG AA threshold.

## Not covered by automation

axe cannot judge focus visibility, focus order, keyboard traps, screen-reader
announcements or reduced-motion behaviour. The earlier UI audit and Phase 4
verification cover the structural parts (skip link, one H1 per page, labelled
landmarks, `aria-live` route announcements, keyboard-only reporting). A
screen-reader walkthrough with a native speaker remains a manual Phase 6 item.
