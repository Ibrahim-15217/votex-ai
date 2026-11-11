# Votex AI — AI engine

This folder holds the reproducible data and model pipeline for the explainable
hybrid analyser.

## Phase 0 — synthetic dataset

```bash
python ai-engine/training/generate_data.py
```

Outputs:

- `datasets/electoral_phishing_synthetic.csv` — 1,400 balanced, labelled messages.
- `datasets/manifest.json` — seed, counts, SHA-256 and known limitations.

The generator uses only the Python standard library and a fixed seed (`20261109`). It is safe to run offline.

### Safety rules

- **Synthetic only.** No real message, person, voter record or private communication.
- **Reserved destinations.** Suspicious links use `.example` domains and RFC 5737 documentation IP ranges. Clicking one cannot reach a real host.
- **Benign links** reference public institutional home pages only as illustrative context. The generator never contacts them.
- **Shared vocabulary.** Both classes mention elections, states and deadlines so the classifier must learn security behaviour, not a keyword shortcut.
- **Template limits.** The set is intentionally small and documented; it tests triage logic, not real-world generalisation.

## Phase 2 — training and evaluation

Install the training dependencies (the backend virtualenv already has them):

```bash
python -m pip install -r ai-engine/requirements.txt
```

Train, evaluate and write the artefact:

```bash
python ai-engine/training/train_model.py
```

Outputs:

- `models/phishing_model.joblib` — the scikit-learn pipeline bundle.
- `models/metrics.json` — held-out metrics, cross-validation, per-language and per-category results, closest-to-threshold cases, environment versions.
- `evaluation/challenge_results.json` — the hand-written challenge-set evaluation.

### What the model is

1. Word TF-IDF (1–2 grams) and character TF-IDF (`char_wb`, 3–5 grams).
2. Logistic Regression (`C=4.0`, `liblinear`, balanced class weights, seed `20261109`).
3. Stratified 75/25 split plus 5-fold cross-validation.
4. A hand-written 28-case challenge set that is independent of the generator.
5. Weighted runtime score: URL 0.30, NLP 0.25, ML 0.25, rules 0.20.

### Measured results (9 November 2026)

| Set | Rows | F1 | Brier | Errors |
| --- | --- | --- | --- | --- |
| Held-out synthetic | 350 | 1.000 | 0.0006 | 0 / 350 |
| Hand-written challenge | 28 | 1.000 | 0.0265 | 0 / 28 |

The perfect held-out result is expected for template-generated data. The
challenge set is the stronger signal: labels are still perfect, but the Brier
score is 44× worse and the closest case is 0.059 from the 0.5 boundary. See
[../docs/model/EVALUATION.md](../docs/model/EVALUATION.md) and
[../docs/model/MODEL_CARD.md](../docs/model/MODEL_CARD.md).

**No real-world accuracy is claimed.** The datasets are synthetic and
hand-written; real-world generalisation must be measured in an authorised pilot.

### Challenge set

`evaluation/challenge_cases.jsonl` contains 28 cases (14 phishing, 14 benign;
25 English, 3 Hausa) with a `note` explaining the intent of each case. Add new
cases there and re-run training to refresh `challenge_results.json`.

No deep learning or large language model is used. The model is deterministic,
offline and explainable.
