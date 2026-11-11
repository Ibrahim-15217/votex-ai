"""Machine-learning classifier (component ``M``).

The saved artefact is a scikit-learn pipeline (TF-IDF word and character
n-grams plus logistic regression) trained by
``ai-engine/training/train_model.py``. Loading is lazy and thread-safe so the API
still starts if the model file has not been generated yet.
"""

from __future__ import annotations

from pathlib import Path
from threading import Lock

from app.ai.types import MlResult
from app.core.config import settings

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_bundle: dict | None = None
_load_lock = Lock()


def _model_path() -> Path:
    configured = Path(settings.model_path)
    if not configured.is_absolute():
        configured = (_BACKEND_DIR / configured).resolve()
    return configured


def load_model(force_reload: bool = False) -> dict | None:
    """Load and cache the joblib artefact, returning ``None`` if unavailable."""

    global _bundle
    with _load_lock:
        if _bundle is not None and not force_reload:
            return _bundle
        path = _model_path()
        if not path.exists():
            return None
        try:
            import joblib
        except ImportError:
            return None
        try:
            _bundle = joblib.load(path)
        except Exception:  # corrupt artefact or incompatible sklearn build
            return None
        return _bundle


def reset_model_cache() -> None:
    """Clear the cache; used by tests after retraining."""

    global _bundle
    with _load_lock:
        _bundle = None


def predict(text: str, url: str | None) -> MlResult:
    """Return the phishing probability as a 0–100 risk score."""

    bundle = load_model()
    if bundle is None:
        return MlResult(
            score=50.0,
            probability=0.5,
            model_version=settings.model_version,
            available=False,
            warning=(
                "The trained model artefact is not available; the ML component is "
                "neutral and the score relies on the rule, URL and NLP components."
            ),
        )

    pipeline = bundle.get("pipeline")
    model_version = str(bundle.get("model_version", settings.model_version))
    if pipeline is None:
        return MlResult(
            score=50.0,
            probability=0.5,
            model_version=model_version,
            available=False,
            warning="The model artefact has no pipeline; the ML component is neutral.",
        )

    combined = f"{text}\nURL: {url}" if url else text
    try:
        probability = float(pipeline.predict_proba([combined])[0][1])
    except Exception:
        return MlResult(
            score=50.0,
            probability=0.5,
            model_version=model_version,
            available=False,
            warning="The model could not score this report; the ML component is neutral.",
        )

    probability = max(0.0, min(1.0, probability))
    return MlResult(
        score=round(probability * 100.0, 1),
        probability=round(probability, 4),
        model_version=model_version,
        available=True,
    )
