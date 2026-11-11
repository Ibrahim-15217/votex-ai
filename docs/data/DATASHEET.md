# Votex AI — Datasheet: `electoral_phishing_synthetic`

| Field | Detail |
| --- | --- |
| **Dataset** | Electoral phishing and benign communications (synthetic) |
| **Version** | 0.1.0 |
| **Status** | Phase 0 — generated and reproducible |
| **Generator** | `ai-engine/training/generate_data.py` |
| **Seed** | `20261109` |
| **Rows** | 1,400 (700 phishing / 700 benign) |
| **Languages** | English and Hausa |
| **Licence** | CC BY 4.0 (proposed for the synthetic data) |
| **Contact** | Repository issue tracker |
| **Last updated** | 9 November 2026 |

---

## 1. Motivation

Electoral phishing is hard to study with real data: reports are sensitive, contain personal information and are rarely shareable. This dataset exists to:

1. Train and evaluate an explainable triage baseline.
2. Demonstrate a safe, reproducible workflow without real messages.
3. Teach the difference between genuine security signals and alarming but benign content.

### Creator and funding

Created by the Votex AI team for the **#AI4Elections Hackathon 2026–2027**, Track 4. No external funding was used. The dataset is generated on the team's own machines.

### Intended tasks

- Binary classification: phishing vs benign.
- Signal analysis: detect credential requests, payment demands, impersonation and malicious attachments.
- Explainability evaluation: check whether stated reasons match the message.
- Privacy testing: ensure no real personal data is processed.

### Non-intended tasks

- Real-world threat detection without further validation.
- Attribution to a person, group, party or region.
- Measuring real phishing prevalence.
- Surveillance or monitoring of private communications.
- Any operational decision without human review.

---

## 2. Composition

Each row describes one synthetic message.

| Field | Type | Description |
| --- | --- | --- |
| `id` | string | Stable synthetic identifier, e.g. `syn-00042` |
| `text` | string | Message body with salutation |
| `url` | string | One link from the message |
| `label` | integer | `1` = phishing, `0` = benign |
| `category` | string | Threat or benign category |
| `language` | string | `en` or `ha` |
| `channel` | string | `email`, `sms`, `whatsapp` or `web_form` |
| `state` | string | Nigerian state used as context |
| `created_at` | ISO 8601 UTC | Synthetic timestamp between June and November 2026 |

### Class distribution

| Label | Count | Share |
| --- | --- | --- |
| Phishing | 700 | 50% |
| Benign | 700 | 50% |

### Category distribution

**Phishing**

- Fake verification or accreditation portal
- Credential harvesting
- Payment fraud
- Impersonation of an institution or supervisor
- Early or altered results
- Malware or macro attachment
- Fake observer or media accreditation

**Benign**

- Official notice
- Training invitation
- Security advisory and hard negatives
- Public awareness
- Observer coordination
- Result-verification guidance
- Media release

### Languages

Approximately 85% English and 15% Hausa. Hausa rows are template-based and require native-speaker review before external claims are made.

### Channels

Messages are distributed across email, SMS, WhatsApp and web form. SMS rows are truncated to a realistic length.

### Example — phishing (synthetic)

> Dear Presiding Officer, Final notice: your PVC record could not be matched. Re-enter your voter identification number and date of birth at `http://pvc-confirm.example/`.
>
> Label: phishing · Category: fake portal · Language: English

### Example — benign hard negative (synthetic)

> Hello ICT Officer, Security reminder: the ICT team will never ask for your password or one-time code. Report suspicious messages to `https://cert.gov.ng/report/`.
>
> Label: benign · Category: security advisory · Language: English

---

## 3. Collection and generation process

This dataset was **not collected from people or systems**. It was generated from hand-written templates.

1. The team wrote phishing and benign templates grounded in common electoral workflows.
2. Placeholders cover states, roles, offices, deadlines, amounts and links.
3. A fixed seed selects templates, placeholders and channels.
4. Generated text is deduplicated.
5. Guard rails reject templates with unresolved placeholders or non-reserved suspicious links.
6. The CSV is hashed and the manifest records counts and provenance.

### Safe link policy

- Suspicious URLs use reserved `.example` domains or RFC 5737 documentation IP ranges (`192.0.2.0/24`, `198.51.100.0/24`, `203.0.113.0/24`).
- Benign URLs reference public institutional home pages as illustrative context.
- The generator never contacts any URL.

### Synthetic timestamps

Timestamps are randomly assigned within a fixed window to support trend demonstrations. They do not reflect real events.

---

## 4. Preprocessing and labelling

- **Preprocessing at generation:** deduplication, SMS truncation, placeholder validation.
- **Cleaning at training time:** whitespace normalisation, optional lowercasing, URL extraction. Text is otherwise preserved to keep evidence-like artefacts realistic.
- **Labelling rule:** a row is phishing when it attempts to obtain credentials, payment, malware execution or sensitive data, or impersonates an electoral authority to prompt a false action.
- **Labelling process:** rules applied by the generator author, then reviewed against the category templates.
- **Inter-annotator agreement:** not measured, because labels are generated from templates rather than independently annotated.
- **Label noise:** deliberately low. Real reports are noisier and may be ambiguous.

---

## 5. Uses

### Approved for the prototype

- Training and evaluating the Votex AI analyser.
- Demonstration and screenshots.
- Teaching, testing and documentation.
- Reproducibility checks.

### Requires caution

- Comparing against real-world phishing rates.
- Claiming generalisation to Nigerian languages or dialects not represented.
- Using the scores as the sole basis for an operational decision.

### Prohibited

- Combining with real voter data or personal records.
- Using the dataset to train systems that surveil or target individuals.
- Presenting synthetic examples as real incidents.
- Implying INEC or partner endorsement.

---

## 6. Distribution and maintenance

- **Location:** generated locally at `ai-engine/datasets/electoral_phishing_synthetic.csv`.
- **Version control:** generated files are excluded from Git; the generator, seed and manifest are the source of truth.
- **Manifest:** `ai-engine/datasets/manifest.json` records row counts, label balance, category counts, file size and SHA-256.
- **Updates:** template changes must increment the dataset version and regenerate the manifest.
- **Retention:** delete generated data after evaluation if no longer needed.
- **Errata:** template or label corrections should be recorded in the repository changelog.

---

## 7. Known biases and limitations

| Bias or limitation | Effect | Mitigation |
| --- | --- | --- |
| Template language is repetitive | Model may learn template phrasing | Expand templates; character n-grams; rules; human review |
| English dominates | Hausa performance may be weaker | Report per-language metrics; native review; add examples |
| Nigerian state names are evenly sampled | Does not reflect real incident geography | Do not use for geographic inference |
| Categories are balanced | Real reports are imbalanced | Use class weights and report per-class metrics |
| Hard negatives are curated | Real benign messages are more varied | Expand hard negatives; monitor false positives |
| No real attacker adaptation | Evasion is under-represented | Adversarial tests; analyst feedback |
| Institutional names are generic | Reduces realism slightly | Acceptable trade-off for safety and neutrality |

### Ethical review

- No personal data, voter records, biometrics or private communications are present.
- Names are replaced by roles.
- Suspicious links cannot reach real hosts.
- Content avoids partisan framing.
- The dataset is not intended to characterise any real actor.

---

## 8. Reproduction

```bash
python ai-engine/training/generate_data.py
```

Verify the output against the manifest's SHA-256. A mismatch means the generator, seed or Python environment changed.

### Manifest fields

- `dataset`, `version`, `seed`, `rows`
- `labels`, `languages`, `categories`, `channels`
- `files[].sha256`, `files[].bytes`
- `known_limitations`

---

## 9. Citation

> Votex AI contributors. (2026). *Electoral Phishing Synthetic Dataset v0.1.0* [Data set]. #AI4Elections Hackathon 2026–2027, Track 4. Generated with `ai-engine/training/generate_data.py`, seed 20261109.

## 10. Review log

| Date | Change | Reviewer |
| --- | --- | --- |
| 9 Nov 2026 | Initial datasheet and generator | AI lead |
| Phase 2 | Metrics and language review | AI lead + reviewer |
