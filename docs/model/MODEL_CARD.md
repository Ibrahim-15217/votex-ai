# Votex AI — Model Card

| Field | Detail |
| --- | --- |
| **Model name** | Votex Hybrid Electoral Phishing Analyser |
| **Version** | `hybrid-v0.2.0` |
| **Status** | Trained and evaluated — Phase 2 complete |
| **Owner** | AI lead |
| **Last updated** | 9 November 2026 |
| **Model type** | URL rules + NLP signals + policy rules + TF-IDF Logistic Regression, combined by a published weighted risk score |
| **Licence** | MIT for code; CC BY 4.0 for documentation and synthetic data |
| **Artefact** | `ai-engine/models/phishing_model.joblib` (435,834 bytes) |
| **Measured results** | `ai-engine/models/metrics.json` and `ai-engine/evaluation/challenge_results.json` |

> **Read this first.** All training and evaluation data is synthetic. The held-out
> and challenge scores are perfect, which is expected for template-generated
> text and is **not** evidence of real-world performance. Section 6 explains why
> and what the closest-to-threshold cases reveal. No performance claim in this
> card should be read as a claim about live electoral traffic.

---

## 1. Purpose

Votex AI helps authorised electoral teams triage reports of phishing, impersonation and fake electoral portals. The analyser produces:

- a classification band (**benign**, **suspicious**, **high risk**);
- a 0–100 risk score;
- human-readable reasons and extracted indicators;
- the model version, ruleset version, latency and analysis timestamp.

The output supports a human analyst. It does not block traffic, sanction people, declare an incident resolved or attribute an attack to a group.

---

## 2. Intended use

| Use | Detail |
| --- | --- |
| Primary users | Electoral security analysts, incident responders, trained administrators |
| Setting | Controlled demonstration with synthetic data; future authorised pilot |
| Inputs | Report text and an optional URL, written in English or Hausa |
| Outputs | Advisory classification, score, reasons, indicators and version metadata |
| Human role | Every consequential decision is made by a person |
| Languages | English and Hausa in the MVP; Yoruba, Igbo and Pidgin later |

## 3. Out-of-scope use

- Automatic blocking, takedown requests or account suspension.
- Accusing or profiling an individual, party, campaign or organisation.
- Monitoring private communications or social-media surveillance.
- Processing voter registers, biometrics or personal voter records.
- Deciding whether an election result is valid.
- Deployment against live electoral infrastructure without written authorisation.
- Any high-stakes decision without human review.

---

## 4. How the analysis works

```text
Report text + URL
        │
        ├──► U  URL analysis      → official-domain allowlist, scheme, IP host,
        │                            reserved hosts, shorteners, lookalike tokens
        ├──► N  NLP signals       → urgency, credential request, payment demand,
        │                            impersonation, secrecy, attachments, reassurance
        ├──► M  ML classifier     → TF-IDF (word + character n-grams) + Logistic Regression
        └──► I  Rules engine      → category prior, channel, payment amounts,
                                     macro attachments, credential-action pairs
                                      │
                                      ▼
                    R = 0.30U + 0.25N + 0.25M + 0.20I
                                      │
                                      ▼
                Band + score + reasons + indicators + versions
```

### Bands

| Band | Score | Meaning |
| --- | --- | --- |
| Benign | `< 35` | No strong phishing pattern detected |
| Suspicious | `35 – 64.9` | Analyst review required before closing |
| High risk | `≥ 65` | Pattern consistent with phishing, impersonation or a fake portal |

### Why hybrid?

A pure ML model is harder to explain and can be fooled by unfamiliar phrasing. A pure ruleset is transparent but brittle. The hybrid keeps the demo explainable: every result names the signals that contributed, and the rules provide a safe, inspectable fallback if the model artefact is missing.

### Component design

**`U` — URL and domain intelligence.** Never resolves, fetches or contacts a link. It reasons only about the submitted string. It rewards an official-domain allowlist (`inec.gov.ng`, `cert.gov.ng`, `nccc.gov.ng`) and penalises plain HTTP, IP-literal hosts, reserved `.example`/`.test` hosts, punycode, user-info tricks, shorteners, high-abuse TLDs, hyphenation, deep subdomains, brand tokens on unofficial hosts, lure words in the host or path, long hosts, non-standard ports and percent-encoding.

**`N` — NLP social-engineering signals.** Fourteen positive signals (urgency, credential request, sensitive identity, payment demand, threat, authority claim, secrecy, attachment lure, result manipulation, reward, registration threat, call to action, account pressure) and four negative signals (anti-fraud disclaimer, official-channel guidance, routine administration, routine security notification). Every signal maps to a readable phrase and a matched snippet.

**`M` — ML classifier.** A scikit-learn pipeline of word TF-IDF (1–2 grams, 20,000 features), character TF-IDF (`char_wb`, 3–5 grams, 30,000 features) and Logistic Regression (`C=4.0`, `liblinear`, balanced class weights, seed `20261109`). Loading is lazy and cached; if the artefact is unavailable the component returns a neutral 50/100 and the analysis is marked **degraded**, never silently trusted.

**`I` — Indicators and policy rules.** Category priors, channel weight, named payment amounts, macro/executable attachments, credential-action pairs, phone and non-official email contacts, impersonation plus unofficial destination, official-destination credit and explicit no-fee negatives.

---

## 5. Training data

| Item | Detail |
| --- | --- |
| Dataset | `electoral_phishing_synthetic` v0.1.0 |
| Generator | `ai-engine/training/generate_data.py` |
| Seed | `20261109` |
| Rows | 1,400 (700 phishing, 700 benign) |
| Languages | English (1,190) and Hausa (210) |
| Source | Template-generated synthetic text only |
| Real personal data | None |
| Dataset SHA-256 | `7c7c05e3cef528de184760fe8cafcce01a6818d78578919cf92cc2dbc94603a0` |
| Datasheet | [../data/DATASHEET.md](../data/DATASHEET.md) |

### Label definition

- **Phishing (1):** the message attempts to obtain credentials, payment, malware execution or sensitive data, or impersonates an electoral authority to create a false action.
- **Benign (0):** official information, training, security guidance, public awareness, observer coordination, result-verification guidance or media release with no deceptive action.

Labels describe the message, not the intent of a real sender.

### Split

- Stratified 75/25 split: **1,050 train / 350 test** rows.
- Fixed seed `20261109`, so the split reproduces exactly.
- The test set is never used for fitting; it is only used once for the headline metrics.

### Challenge set (independent, hand-written)

`ai-engine/evaluation/challenge_cases.jsonl` contains **28 hand-written cases**
(14 phishing, 14 benign; 25 English, 3 Hausa). These were written by hand after
the template dataset was frozen, specifically to test phrasing the generator
does not produce. They include credential harvests with no URL, advance-fee
lures, macro attachments, authority impersonation, leaked-result claims,
Hausa payment requests and benign messages that deliberately contain words such
as *password*, *accreditation* and *results*.

---

## 6. Evaluation results (measured 9 November 2026)

Reproduce with:

```bash
python ai-engine/training/train_model.py
```

### 6.1 Held-out test set (350 rows)

| Metric | Value |
| --- | --- |
| Accuracy | 1.000 |
| Precision (phishing) | 1.000 |
| Recall (phishing) | 1.000 |
| F1 (phishing) | 1.000 |
| ROC AUC | 1.000 |
| Brier score | 0.0006 |
| True negatives / false positives | 175 / 0 |
| False negatives / true positives | 0 / 175 |
| False-positive rate | 0.000 |
| False-negative rate | 0.000 |
| 5-fold cross-validated F1 | 1.000 ± 0.000 |

Per language (held-out): English 294 rows, precision/recall/F1 1.000, Brier 0.0004; Hausa 56 rows, precision/recall/F1 1.000, Brier 0.0013.

Per category (held-out, within-category accuracy): all 14 categories 1.000; zero errors in each.

### 6.2 Hand-written challenge set (28 rows)

| Metric | Value |
| --- | --- |
| Accuracy / precision / recall / F1 | 1.000 / 1.000 / 1.000 / 1.000 |
| ROC AUC | 1.000 |
| Brier score | **0.0265** |
| Errors | **0 / 28** |
| English (25 rows) | 1.000 F1, Brier 0.0260 |
| Hausa (3 rows) | 1.000 F1, Brier 0.0301 |

### 6.3 The honest interpretation

The held-out set is **template-distributed**: the test rows are new samples from
the same generator that produced the training rows. A linear model can learn
template markers almost perfectly, so 1.000 is a statement about the benchmark,
not about electoral phishing in the wild.

Three facts keep this honest:

1. **The challenge set is harder.** Its Brier score is **0.0265**, roughly 44×
   worse than the held-out Brier score, even though every challenge label is
   correct. The model is right but less certain on wording it did not see.
2. **Two challenge cases sit close to the 0.5 boundary.** `ch-024` (benign
   password-reset notification) scores **0.4407** and `ch-027` (low-urgency
   credential request) scores **0.6303**. A small change of phrasing could flip
   either one. The 28-case set is too small to estimate that flip rate.
3. **No real-world estimate exists.** We have zero labelled real reports, so we
   report **no real-world precision, recall or calibration claim**. The correct
   statement is: "Performance on synthetic and hand-written data is recorded;
   real-world generalisation is unknown and must be measured in an authorised
   pilot."

The runtime risk engine is also not the ML classifier alone. The ML component is
25% of the score; URL, NLP and rule signals carry 75%. A single uncertain
classifier probability cannot by itself move a report into the high-risk band.

### 6.4 Closest-to-threshold cases (failure analysis)

With zero observed errors, the useful failure analysis is the margin to the
decision boundary.

| Case | Label | Probability | Margin | Language | Why it is close |
| --- | --- | --- | --- | --- | --- |
| `ch-024` | benign | 0.4407 | 0.0593 | en | Routine reset notification containing *password* |
| `ch-027` | phishing | 0.6303 | 0.1303 | en | Polite credential request with no threat or link |
| `ch-003` | phishing | 0.7186 | 0.2186 | en | Advance-fee lure with no URL |
| `ch-018` | benign | 0.2682 | 0.2318 | ha | Hausa public notice with no link |

Held-out closest cases are all above 0.93 or below 0.07, confirming that the
template test set contains no genuinely ambiguous examples. The challenge set
does, and that is the more credible signal.

### 6.5 Recorded failure modes

- **No-URL credential requests** rely on NLP and rules only. `ch-002` and
  `ch-027` are correctly classified but with lower confidence.
- **Benign messages with security vocabulary** are the main false-positive
  risk. `ch-024` is the closest benign case; the anti-fraud and security
  notification negatives are what keep it below 0.5.
- **Hausa** is learned from only 210 synthetic rows and 3 challenge cases. The
  observed result is perfect but the evidence base is thin.
- **Novel pretexts** (a new payment story, a new authority title) may miss all
  rules and rely on the classifier. The panel shows lower confidence and the
  component scores so an analyst can see this.
- **Attachments** are classified from text only; no file is opened or scanned.

---

## 7. Limitations and failure modes

| Limitation | Consequence | Mitigation |
| --- | --- | --- |
| Synthetic template data | May not generalise to real reports | Rules fallback, human review, documented limitation |
| Perfect benchmark scores | Can create false confidence | Challenge-set Brier score and closest-case table published |
| Small challenge set (28) | Wide uncertainty around the error rate | Expand with native speakers before any pilot |
| Hausa coverage is limited | Weaker Hausa performance likely | Native-speaker review, more examples, English fallback |
| Adversarial evasion | Attacker changes wording or domain | Four independent signals, rules, analyst override |
| Lookalike detection is heuristic | Homoglyphs and new TLDs may be missed | Character n-grams, URL rules, manual indicator review |
| No attachment analysis | Malware claims only from text | State the limit; scanning is post-hackathon |
| No live threat intelligence | Indicators are local to reports | Correlate within the deployment; feeds are future work |
| Short messages | Fewer NLP signals | Rely on URL and rules; lower confidence display |
| False positives on security advisories | Analyst workload | Hard negatives, visible reasons, easy override |

### Known ethical risks

- Over-flagging messages from a particular language or region.
- Treating a political actor's message as malicious without evidence.
- Creating a false sense of security if the tool is described as complete.
- Re-identifying a reporter through free text or small aggregates.

Mitigations: human review, non-attribution language, visible uncertainty, k-anonymity, privacy testing and clear limits.

---

## 8. Human oversight and feedback

- The analyst sees reasons, component scores, confidence, version and indicators before acting.
- Re-running an analysis appends a new row; earlier runs stay in the case record.
- Every run writes an `incident.analysed` entry to the SHA-256 audit chain.
- Model output never closes an incident automatically.
- Disagreements are reviewed in the weekly quality check.
- A missing model degrades gracefully: the score uses the other three components and the API reports `ai_status: degraded`.

---

## 9. Version record

| Version | Date | Change | Evaluation |
| --- | --- | --- | --- |
| `hybrid-v0.1.0` | Planned Phase 2 | Initial rules + TF-IDF + Logistic Regression design | Not run |
| `hybrid-v0.2.0` | 9 Nov 2026 | Trained model, four-component engine, persistence, UI, 28-case challenge set | Held-out F1 1.000, challenge 0/28 errors, Brier 0.0265 |

Each artefact records the dataset SHA-256, training date, split seed, library
versions and measured metrics.

### Environment

Python 3.12.5 · scikit-learn 1.6.0 · NumPy 2.2.1 · SciPy 1.15.0 · joblib 1.4.2.

---

## 10. Reproduction

```bash
# 1. Regenerate the synthetic dataset (optional; committed for convenience)
python ai-engine/training/generate_data.py

# 2. Train, evaluate and write the artefact + metrics
python ai-engine/training/train_model.py

# Expected output:
#   ai-engine/models/phishing_model.joblib
#   ai-engine/models/metrics.json
#   ai-engine/evaluation/challenge_results.json
```

The backend loads the artefact from `../ai-engine/models/phishing_model.joblib`
relative to `backend/`. Set `MODEL_PATH` to override. If the file is absent the
API still starts; health reports `model-unavailable` and analyses degrade.

---

## 11. Contact and review

Model questions and corrections should be raised as repository issues. Security issues must follow the responsible-disclosure process in [../safety/SAFETY_AND_LIMITATIONS.md](../safety/SAFETY_AND_LIMITATIONS.md).

| Review | Date | Reviewer |
| --- | --- | --- |
| Initial draft | 9 Nov 2026 | AI lead |
| Post-training review | 9 Nov 2026 | AI lead (self-review; independent review pending) |
