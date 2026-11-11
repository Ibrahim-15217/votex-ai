# Problem Statement

**Track 4 — Electoral Cybersecurity & Resilience**
**#AI4Elections Hackathon 2026–2027**

## The problem in one paragraph

Nigerian election periods produce a predictable wave of phishing, impersonation and
fake-portal attacks against the people who run and observe elections: presiding
officers, collation staff, party agents, observers and voters. Reports of these
attacks arrive through WhatsApp groups, phone calls, email and word of mouth. They
are handled one at a time, in different inboxes, by people with no shared view of
the campaign behind them. A lookalike portal reported in Kano and the same domain
reported in Lagos are never connected. Evidence screenshots are easy to alter and
hard to authenticate later. Meanwhile, any national picture risks exposing the
single small organisation whose report made a pattern visible. The result is slow
response, weak evidence and a privacy trade-off that discourages reporting.

## Who we are building for

| User | Need |
| --- | --- |
| Reporter — electoral staff, observer, party agent, voter | A short, plain-language way to report a suspicious message, link or file from a phone, with confidence that the evidence is preserved and the report is scoped to their organisation |
| Analyst — commission or civil-society security team | One queue, a defensible risk assessment with visible reasons, linked reports, assignment, response actions and an audit trail |
| Decision-maker — national or regional coordinator | Aggregate situational awareness that never exposes a single organisation's raw report |
| Auditor or oversight reviewer | Proof that records were not silently changed |

## What “good” looks like

A reporter submits a fake verification portal in under two minutes. The analyst
sees a risk score with the signals that produced it, not a black box. A second
report sharing the domain appears as a linked case, so two complaints become one
campaign. The analyst assigns the case, records a takedown request and moves it to
investigating. Every step is chained into a tamper-evident audit log. The national
view shows the trend while suppressing any cell with fewer than five contributors.
A keyboard-only user can complete the same journey in Hausa, Yoruba or Igbo.

## Scope of the prototype

**In scope:** secure incident intake with hashed evidence; explainable hybrid
analysis (URL rules, NLP signals, TF-IDF + Logistic Regression, published weighted
risk score); tenant-scoped indicator correlation; assignment and response
workflow; k ≥ 5 national aggregates; hash-chained audit and verification; four
interface locales; responsive, low-bandwidth interface.

**Out of scope:** any connection to live electoral systems, voter registers,
biometrics or real voter data; scanning or exploiting third-party infrastructure;
automated sanctions or result declarations; production-scale identity federation;
professional native-speaker translation sign-off.

## Why this team can build it

The prototype already runs end to end on synthetic data, with 40 backend tests
passing, a trained and evaluated model artefact, a live audit chain, and browser
evidence for keyboard-only reporting and responsive layouts. The remaining work is
hardening and a fresh-clone demonstration, not invention.

## Boundaries and ethics

All data is synthetic. The system advises; a human decides. It is not affiliated
with, endorsed by, or approved by INEC, Rise Networks or any partner, and winning
does not authorise deployment. Any pilot would require separate written
authorisation, native-language review, an independent security assessment and a
data-protection review under the Nigeria Data Protection Act 2023.
