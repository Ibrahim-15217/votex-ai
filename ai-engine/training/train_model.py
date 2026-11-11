"""Train and evaluate the Votex AI electoral phishing classifier.

The model is deliberately small, classical and explainable: TF-IDF word and
character n-grams feeding a logistic-regression classifier. It is trained on
the synthetic template dataset only and scored on both a held-out split and a
separate hand-written challenge set.

Run from the repository root:

    python ai-engine/training/train_model.py

Outputs:
    ai-engine/models/phishing_model.joblib
    ai-engine/models/metrics.json
    ai-engine/evaluation/challenge_results.json
"""

from __future__ import annotations

import csv
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import FeatureUnion, Pipeline

SEED = 20261109
TEST_SIZE = 0.25
THRESHOLD = 0.5

BASE_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = BASE_DIR / "datasets" / "electoral_phishing_synthetic.csv"
MANIFEST_PATH = BASE_DIR / "datasets" / "manifest.json"
CHALLENGE_PATH = BASE_DIR / "evaluation" / "challenge_cases.jsonl"
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "phishing_model.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"
CHALLENGE_RESULTS_PATH = BASE_DIR / "evaluation" / "challenge_results.json"


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_dataset() -> tuple[list[str], list[int], list[dict]]:
    """Load the synthetic dataset without a pandas dependency."""

    texts: list[str] = []
    labels: list[int] = []
    rows: list[dict] = []
    with DATASET_PATH.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            text = row["text"]
            url = row.get("url") or ""
            texts.append(f"{text}\nURL: {url}" if url else text)
            labels.append(int(row["label"]))
            rows.append(row)
    return texts, labels, rows


def build_pipeline() -> Pipeline:
    """Build the deterministic, explainable classifier pipeline."""

    features = FeatureUnion(
        [
            (
                "word",
                TfidfVectorizer(
                    analyzer="word",
                    ngram_range=(1, 2),
                    min_df=1,
                    max_features=20_000,
                    sublinear_tf=True,
                    lowercase=True,
                ),
            ),
            (
                "char",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    min_df=2,
                    max_features=30_000,
                    sublinear_tf=True,
                    lowercase=True,
                ),
            ),
        ]
    )
    classifier = LogisticRegression(
        C=4.0,
        class_weight="balanced",
        solver="liblinear",
        max_iter=2_000,
        random_state=SEED,
    )
    return Pipeline([("features", features), ("classifier", classifier)])


def _rates(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    return {
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "true_positives": int(tp),
        "false_positive_rate": round(fp / (fp + tn), 4) if (fp + tn) else 0.0,
        "false_negative_rate": round(fn / (fn + tp), 4) if (fn + tp) else 0.0,
    }


def _headline(y_true: np.ndarray, y_pred: np.ndarray, probabilities: np.ndarray) -> dict:
    rates = _rates(y_true, y_pred)
    unique_labels = set(np.unique(y_true).tolist())
    roc_auc = (
        round(float(roc_auc_score(y_true, probabilities)), 4)
        if len(unique_labels) == 2
        else None
    )
    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "roc_auc": roc_auc,
        "brier_score": round(float(brier_score_loss(y_true, probabilities)), 4),
        **rates,
    }


def _group_metrics(
    group_values: list[str], y_true: np.ndarray, y_pred: np.ndarray, probabilities: np.ndarray
) -> dict:
    grouped: dict[str, dict] = {}
    for value in sorted(set(group_values)):
        mask = np.array([item == value for item in group_values])
        if mask.sum() < 2:
            continue
        grouped[value] = {
            "count": int(mask.sum()),
            **_headline(y_true[mask], y_pred[mask], probabilities[mask]),
        }
    return grouped


def _category_metrics(
    category_values: list[str], y_true: np.ndarray, y_pred: np.ndarray
) -> dict:
    """Per-category detection accuracy.

    Each category belongs to a single label, so precision/recall would be
    misleading. Accuracy inside the category is the useful figure: for a
    phishing category it is recall, for a benign category it is specificity.
    """

    grouped: dict[str, dict] = {}
    for value in sorted(set(category_values)):
        mask = np.array([item == value for item in category_values])
        if mask.sum() == 0:
            continue
        expected = int(value.split(":", 1)[0])
        correct = int((y_pred[mask] == expected).sum())
        grouped[value] = {
            "count": int(mask.sum()),
            "accuracy": round(correct / int(mask.sum()), 4),
            "errors": int(mask.sum()) - correct,
        }
    return grouped


def _hardest_cases(
    rows: list[dict], probabilities: np.ndarray, predictions: np.ndarray, limit: int = 10
) -> list[dict]:
    """Return the cases closest to the decision boundary.

    With a clean synthetic benchmark there may be no errors at all, so the
    closest-to-threshold cases are the useful failure analysis: they show which
    reports the model is least certain about.
    """

    margins = np.abs(probabilities - THRESHOLD)
    order = np.argsort(margins)[:limit]
    cases = []
    for index in order:
        row = rows[int(index)]
        cases.append(
            {
                "id": row["id"],
                "label": "phishing" if int(row["label"]) == 1 else "benign",
                "predicted": "phishing" if int(predictions[index]) == 1 else "benign",
                "probability": round(float(probabilities[index]), 4),
                "margin_from_threshold": round(float(margins[index]), 4),
                "language": row["language"],
                "category": row["category"],
                "text": row["text"],
            }
        )
    return cases


def evaluate_challenge(pipeline: Pipeline) -> dict:
    """Score the hand-written challenge set and keep failure examples."""

    if not CHALLENGE_PATH.exists():
        return {"available": False}

    cases: list[dict] = []
    with CHALLENGE_PATH.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                cases.append(json.loads(line))

    texts = [
        f"{case['text']}\nURL: {case['url']}" if case.get("url") else case["text"]
        for case in cases
    ]
    y_true = np.array([int(case["label"]) for case in cases])
    probabilities = pipeline.predict_proba(texts)[:, 1]
    y_pred = (probabilities >= THRESHOLD).astype(int)
    languages = [str(case.get("language", "en")) for case in cases]

    failures = []
    for case, probability, prediction in zip(cases, probabilities, y_pred):
        if int(case["label"]) == int(prediction):
            continue
        failures.append(
            {
                "id": case["id"],
                "label": "phishing" if int(case["label"]) == 1 else "benign",
                "predicted": "phishing" if int(prediction) == 1 else "benign",
                "probability": round(float(probability), 4),
                "language": case.get("language", "en"),
                "note": case.get("note", ""),
                "text": case["text"],
            }
        )

    challenge_rows = [
        {
            "id": case["id"],
            "label": str(int(case["label"])),
            "language": str(case.get("language", "en")),
            "category": str(case.get("category", "uncategorised")),
            "text": case["text"],
        }
        for case in cases
    ]

    return {
        "available": True,
        "path": CHALLENGE_PATH.relative_to(BASE_DIR.parent).as_posix(),
        "threshold": THRESHOLD,
        "headline": _headline(y_true, y_pred, probabilities),
        "per_language": _group_metrics(languages, y_true, y_pred, probabilities),
        "hardest_cases": _hardest_cases(challenge_rows, probabilities, y_pred),
        "failures": failures,
    }


def main() -> int:
    if not DATASET_PATH.exists():
        print(f"Dataset not found: {DATASET_PATH}", file=sys.stderr)
        print("Run ai-engine/training/generate_data.py first.", file=sys.stderr)
        return 1

    texts, labels, rows = load_dataset()
    y = np.array(labels)

    train_texts, test_texts, train_y, test_y, _train_rows, test_rows = train_test_split(
        texts,
        y,
        rows,
        test_size=TEST_SIZE,
        random_state=SEED,
        stratify=y,
    )

    pipeline = build_pipeline()
    pipeline.fit(train_texts, train_y)

    probabilities = pipeline.predict_proba(test_texts)[:, 1]
    predictions = (probabilities >= THRESHOLD).astype(int)

    test_languages = [str(row["language"]) for row in test_rows]
    test_categories = [
        f"{row['label']}:{row['category']}" for row in test_rows
    ]

    cross_validation = cross_val_score(
        build_pipeline(),
        texts,
        y,
        cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED),
        scoring="f1",
    )

    failure_examples = []
    for row, probability, prediction in zip(test_rows, probabilities, predictions):
        if int(row["label"]) == int(prediction):
            continue
        failure_examples.append(
            {
                "id": row["id"],
                "label": "phishing" if int(row["label"]) == 1 else "benign",
                "predicted": "phishing" if int(prediction) == 1 else "benign",
                "probability": round(float(probability), 4),
                "language": row["language"],
                "category": row["category"],
                "text": row["text"],
            }
        )

    vectorizer: FeatureUnion = pipeline.named_steps["features"]
    word_features = len(vectorizer.transformer_list[0][1].vocabulary_)
    char_features = len(vectorizer.transformer_list[1][1].vocabulary_)

    manifest = {}
    if MANIFEST_PATH.exists():
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))

    model_version = "hybrid-v0.2.0"
    trained_at = datetime.now(timezone.utc).isoformat()
    challenge = evaluate_challenge(pipeline)

    metrics = {
        "model_name": "Votex Hybrid Electoral Phishing Analyser",
        "model_version": model_version,
        "trained_at": trained_at,
        "seed": SEED,
        "threshold": THRESHOLD,
        "dataset": {
            "path": DATASET_PATH.relative_to(BASE_DIR.parent).as_posix(),
            "sha256": sha256_of(DATASET_PATH),
            "rows": len(rows),
            "manifest_version": manifest.get("version"),
            "manifest_sha256": (
                manifest.get("files", [{}])[0].get("sha256") if manifest else None
            ),
        },
        "split": {
            "train_rows": len(train_texts),
            "test_rows": len(test_texts),
            "test_size": TEST_SIZE,
            "stratified": True,
        },
        "features": {
            "word_ngrams": "1-2",
            "char_ngrams": "3-5 (char_wb)",
            "word_vocabulary": word_features,
            "char_vocabulary": char_features,
            "total_features": word_features + char_features,
        },
        "headline": _headline(test_y, predictions, probabilities),
        "per_language": _group_metrics(test_languages, test_y, predictions, probabilities),
        "per_category": _category_metrics(test_categories, test_y, predictions),
        "hardest_cases": _hardest_cases(test_rows, probabilities, predictions),
        "cross_validation": {
            "folds": 5,
            "metric": "f1",
            "mean": round(float(cross_validation.mean()), 4),
            "std": round(float(cross_validation.std()), 4),
            "scores": [round(float(score), 4) for score in cross_validation],
        },
        "challenge": challenge,
        "failure_examples": failure_examples,
        "environment": {
            "python": platform.python_version(),
            "scikit_learn": sklearn.__version__,
            "numpy": np.__version__,
        },
    }

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": pipeline,
            "model_version": model_version,
            "threshold": THRESHOLD,
            "trained_at": trained_at,
            "dataset_sha256": metrics["dataset"]["sha256"],
        },
        MODEL_PATH,
    )
    METRICS_PATH.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")
    CHALLENGE_RESULTS_PATH.write_text(
        json.dumps(challenge, indent=2) + "\n", encoding="utf-8"
    )

    headline = metrics["headline"]
    print("Votex AI model trained")
    print(f"  model:      {MODEL_PATH}")
    print(f"  version:    {model_version}")
    print(f"  train/test: {len(train_texts)}/{len(test_texts)}")
    print(
        "  held-out:   "
        f"precision {headline['precision']:.3f} · recall {headline['recall']:.3f} · "
        f"F1 {headline['f1']:.3f} · FPR {headline['false_positive_rate']:.3f} · "
        f"FNR {headline['false_negative_rate']:.3f}"
    )
    if challenge.get("available"):
        ch = challenge["headline"]
        total = ch["true_positives"] + ch["true_negatives"] + ch["false_positives"] + ch["false_negatives"]
        print(
            "  challenge:  "
            f"precision {ch['precision']:.3f} · recall {ch['recall']:.3f} · "
            f"F1 {ch['f1']:.3f} · failures {len(challenge['failures'])}/{total}"
        )
    hardest = metrics["hardest_cases"]
    if hardest:
        closest = hardest[0]
        print(
            "  closest:    "
            f"{closest['id']} ({closest['label']}) p={closest['probability']:.3f} "
            f"margin={closest['margin_from_threshold']:.3f}"
        )
    print(f"  metrics:    {METRICS_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
