# Votex AI — Model Evaluation Report

| Field | Detail |
| --- | --- |
| **Model** | Votex Hybrid Electoral Phishing Analyser `hybrid-v0.2.0` |
| **Evaluated** | 9 November 2026 |
| **Datasets** | Synthetic template set (1,400 rows) + hand-written challenge set (28 rows) |
| **Artefacts** | `ai-engine/models/metrics.json`, `ai-engine/evaluation/challenge_results.json` |
| **Reproduce** | `python ai-engine/training/train_model.py` |
| **Full model card** | [MODEL_CARD.md](./MODEL_CARD.md) |

---

## 1. What was evaluated

Two questions are separate and must not be conflated:

1. **Can the classifier separate new samples from the same synthetic generator?**
   This is the held-out benchmark. It is a correctness check, not a field result.
2. **Does the classifier survive phrasing it was not trained on?**
   This is the 28-case challenge set. It is small, but it is independent of the
   generator templates.

The runtime risk score is also evaluated separately: the weighted engine
(`R = 0.30U + 0.25N + 0.25M + 0.20I`) is tested end-to-end through the API in
`backend/tests/test_analysis.py`, including a malicious vs benign ordering test
and a determinism test.

---

## 2. Data and split

| Item | Value |
| --- | --- |
| Dataset rows | 1,400 |
| Class balance | 700 phishing / 700 benign |
| Languages | 1,190 English / 210 Hausa |
| Split | 75/25 stratified, seed `20261109` |
| Train / test | 1,050 / 350 |
| Dataset SHA-256 | `7c7c05e3cef528de184760fe8cafcce01a6818d78578919cf92cc2dbc94603a0` |
| Challenge cases | 28 (14/14; 25 English, 3 Hausa) |
| Decision threshold | 0.5 |

The challenge cases were written after the dataset was frozen. They cover:
credential harvest with and without a URL, advance-fee payment fraud, macro
attachments, authority impersonation, fake accreditation, leaked results,
Hausa payment and awareness messages, security advisories, routine briefings,
media releases and result-verification guidance.

---

## 3. Held-out results

| Metric | Value |
| --- | --- |
| Accuracy | 1.000 |
| Precision | 1.000 |
| Recall | 1.000 |
| F1 | 1.000 |
| ROC AUC | 1.000 |
| Brier score | 0.0006 |
| TN / FP / FN / TP | 175 / 0 / 0 / 175 |
| False-positive rate | 0.000 |
| False-negative rate | 0.000 |

### Cross-validation

| Fold metric | Value |
| --- | --- |
| 5-fold stratified F1 | 1.000 |
| Standard deviation | 0.000 |

### Per language

| Language | Rows | Precision | Recall | F1 | Brier |
| --- | --- | --- | --- | --- | --- |
| English | 294 | 1.000 | 1.000 | 1.000 | 0.0004 |
| Hausa | 56 | 1.000 | 1.000 | 1.000 | 0.0013 |

### Per category (within-category accuracy)

All 14 categories scored 1.000 with zero errors:

- Benign: `media_release`, `observer_coordination`, `official_notice`, `public_awareness`, `result_verification_guidance`, `security_advisory`, `training_invitation`.
- Phishing: `credential_harvest`, `fake_accreditation`, `fake_portal`, `fake_result`, `impersonation`, `malware_attachment`, `payment_fraud`.

---

## 4. Challenge-set results

| Metric | Value |
| --- | --- |
| Accuracy | 1.000 |
| Precision | 1.000 |
| Recall | 1.000 |
| F1 | 1.000 |
| ROC AUC | 1.000 |
| Brier score | **0.0265** |
| Errors | **0 / 28** |
| False positives | 0 |
| False negatives | 0 |

| Language | Rows | F1 | Brier |
| --- | --- | --- | --- |
| English | 25 | 1.000 | 0.0260 |
| Hausa | 3 | 1.000 | 0.0301 |

### Closest-to-threshold cases

| Case | Label | Probability | Margin | Language | Note |
| --- | --- | --- | --- | --- | --- |
| `ch-024` | benign | 0.4407 | 0.0593 | en | Routine password-reset notification |
| `ch-027` | phishing | 0.6303 | 0.1303 | en | Polite credential request, no threat |
| `ch-003` | phishing | 0.7186 | 0.2186 | en | Advance-fee lure, no URL |
| `ch-018` | benign | 0.2682 | 0.2318 | ha | Hausa public notice, no link |

The challenge Brier score is **44× higher** than the held-out Brier score
(0.0265 vs 0.0006). Every label is still correct, but confidence drops sharply
on unseen phrasing. This is the main quantitative warning in the evaluation.

---

## 5. End-to-end engine tests

`backend/tests/test_analysis.py` verifies:

| Test | What it proves |
| --- | --- |
| Automatic analysis on create | A new report gets a stored score, band, reasons and indicators |
| Benign vs malicious ordering | A benign official notice scores materially lower than a payment-fraud lure |
| Factor arithmetic | The four weighted contributions sum to the stored risk score (±0.11) |
| Determinism | Re-running the same report produces identical component and total scores |
| Append-only history | Re-analysis creates a new row and preserves the previous result |
| Audit | Both automatic and manual runs write `incident.analysed` entries with model metadata |
| RBAC | Reporters cannot re-run the analyser (403) |
| Tenant isolation | A cross-tenant analyst gets 404 |
| Seeded backfill | Phase 1 incidents gain an analysis on startup |

Full backend suite: **32 passed**.

---

## 6. Conclusion

The model meets the Phase 2 exit criteria: one benign and one suspicious example
produce explainable, reproducible results with recorded metrics. The held-out
benchmark is clean, and the challenge set is also clean on labels but shows the
expected drop in confidence on unseen phrasing.

**Do not claim real-world accuracy.** The correct public statement is:

> On a 350-report synthetic held-out set the classifier scored F1 1.000
> (Brier 0.0006); on a 28-case hand-written challenge set it made 0 errors but
> its Brier score rose to 0.0265, with the closest case 0.059 from the decision
> boundary. Real-world generalisation is unknown and must be measured in an
> authorised pilot.

Before any pilot: expand the challenge set with native speakers, collect
authorised real reports, re-evaluate calibration, and review the false-positive
cost with analysts.
