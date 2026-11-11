# Votex AI — Safety, Limitations and Responsible Disclosure

| Field | Detail |
| --- | --- |
| **Status** | Draft v0.1 — Phase 0 |
| **Applies to** | The Votex AI prototype and demonstration |
| **Owner** | Product lead and security lead |
| **Last updated** | 9 November 2026 |

> Votex AI is a prototype built for a hackathon. It is not a certified, approved or production-ready electoral system. It must not be used to monitor, accuse or sanction any person or organisation.

---

## 1. What Votex AI is

A defensive, human-in-the-loop tool that helps authorised electoral teams:

- receive and organise reports of phishing, impersonation and fake portals;
- understand why a message looks suspicious;
- connect reports that share indicators;
- coordinate a response and keep a tamper-evident record.

## 2. What Votex AI is not

- **Not an authority.** It does not determine whether an election result is valid.
- **Not an attribution system.** It does not identify who sent a message.
- **Not an enforcement tool.** It does not block, suspend, prosecute or sanction.
- **Not a surveillance system.** It does not monitor private communications or social media.
- **Not a source of truth.** It produces advisory signals with uncertainty.
- **Not an INEC or partner product.** It is not endorsed, certified or approved.
- **Not complete.** Several controls are planned for later phases, as recorded in the threat model.

---

## 3. Human oversight

Every consequential action requires a person:

| Action | Human requirement |
| --- | --- |
| Classifying a report | Analyst reviews the score, reasons and evidence |
| Closing an incident | Analyst records a resolution and rationale |
| Escalating | Analyst or supervisor decides; the tool only highlights |
| Exporting data | Permission check and audit entry |
| Changing a role | Administrator action with audit |
| Publishing national statistics | Suppression applied and reviewed |

The AI never closes incidents, sanctions users or publishes conclusions automatically.

---

## 4. Known limitations

### Data

- The dataset is synthetic and template-generated.
- Real reports are more varied, ambiguous and noisy.
- Hausa coverage is limited and needs native-speaker review.
- Yoruba, Igbo and Nigerian Pidgin are not in the MVP.

### Model

- The classifier may produce false positives on security advisories.
- The classifier may miss novel phishing phrasing or lookalike domains.
- URL heuristics do not resolve homoglyphs or newly registered domains reliably.
- Attachments are not analysed in the MVP.
- There is no live threat-intelligence feed.
- Confidence is not a guarantee of correctness.
- Template repetition may inflate apparent performance.

### System

- The demo runs on a single host without high availability.
- Malware scanning is not implemented.
- Audit hashes are local and can be rewritten by someone with full database access; the chain makes tampering evident, not impossible.
- National aggregation uses suppression, not formal differential privacy.
- The prototype does not integrate with real institutional systems.
- Docker may be unavailable on some demo machines; local and recorded fallbacks are required.

### Inclusion

- Accessibility targets WCAG 2.2 AA but has not yet been independently audited.
- Translations are drafts until reviewed by native speakers.
- Low-bandwidth mode is a design goal, not yet measured on real networks.

---

## 5. Residual risks and safeguards

| Residual risk | Safeguard | What remains |
| --- | --- | --- |
| False negative hides a threat | Analyst review, rules, easy manual escalation | Novel attacks can still be missed |
| False positive alarms an analyst | Reasons shown, hard negatives, feedback capture | Some workload remains |
| Cross-tenant leakage | Organisation-scoped queries and tests | A code defect could still introduce a gap |
| Small-cell re-identification | k ≥ 5 suppression and privacy tests | Repeated querying is not fully prevented |
| Audit rewrite by database owner | Hash chain and verification | Requires external anchoring in production |
| Malicious evidence file | Type/size validation, isolation | No malware scan yet |
| Demo failure | Offline stack, seed, recorded video | Hardware failure remains possible |
| Translation error | Native review, English fallback | Some nuance may be lost |
| Misuse of findings | Non-attribution language, human review | Motivated misuse cannot be prevented by design alone |

---

## 6. Prohibited uses

Do not use Votex AI to:

- monitor, profile or target voters, journalists, observers or political actors;
- scrape private communications or social-media accounts;
- scan, probe or attack any live system;
- make or support claims that a person or party committed an offence;
- decide election outcomes or validate results;
- collect voter registers, biometrics or personal voter records;
- claim official INEC, Rise Networks or partner endorsement;
- operate during a real election without written authorisation and independent security review.

---

## 7. Responsible AI commitments

1. **Nonpartisan.** No campaign optimisation, voter persuasion or microtargeting.
2. **Human control.** People make the decisions that matter.
3. **Transparency.** Reasons, versions and limits are visible.
4. **Privacy.** Data minimisation, tenant isolation and aggregate suppression.
5. **Security.** Defensive design, integrity checks and responsible disclosure.
6. **Inclusion.** Plain language, local languages and accessibility.
7. **Honesty.** Report failures and uncertainty; never overstate capability.
8. **Accountability.** Every important action is audited.

---

## 8. Data protection

- The prototype uses synthetic data only.
- No real personal data is required to run the demo.
- A future pilot must complete a data-protection impact assessment under the **Nigeria Data Protection Act 2023**.
- Purpose, lawful basis, retention and deletion must be documented for every personal-data category.
- Personal data must be minimised, access-controlled and excluded from national aggregates.
- Data-subject request procedures must be defined before any pilot.
- Synthetic demo data should be deleted after evaluation where it is no longer needed.

---

## 9. Responsible disclosure

If you find a vulnerability:

1. **Do not** exploit it, access real data or disclose it publicly.
2. Open a **private security advisory** through the repository's security tab, or contact the maintainers through the published project channel.
3. Include affected version, reproduction steps, impact and any suggested fix.
4. Allow reasonable time for triage and remediation before publication.
5. Do not test any third-party or live electoral system under any circumstances.

### Our commitments

- Acknowledge a report within 5 working days during the hackathon period.
- Provide a remediation plan or a clear explanation.
- Credit reporters who wish to be named.
- Publish a summary after remediation where appropriate.

### Scope

In scope: this repository, its Docker images and the local demo deployment.

Out of scope: INEC systems, partner systems, third-party services and any host you do not own or have written permission to test.

---

## 10. Before any pilot

A future pilot requires, at minimum:

1. Written institutional authorisation and a defined scope.
2. Independent security review and penetration test.
3. Data-protection impact assessment and legal review.
4. MFA, production identity and privileged-access management.
5. Managed secrets, encryption verification and key rotation.
6. Malware scanning and evidence-handling procedures.
7. External anchoring or separate storage for audit hashes.
8. Backup, restore and disaster-recovery tests.
9. Accessibility and language validation with representative users.
10. Monitoring, incident-response runbooks and a rollback plan.
11. A published privacy notice and retention schedule.
12. Clear non-attribution and human-review policies.

Winning or participating in the hackathon is **not** approval for deployment.

---

## 11. Contact

- **Security:** private repository security advisory.
- **General:** repository issue tracker.
- **Programme:** follow the official #AI4Elections channels.

## 12. Review log

| Date | Change | Reviewer |
| --- | --- | --- |
| 9 Nov 2026 | Initial draft for Phase 0 | Product lead |
| Phase 6 | Final review before submission | Security lead |
