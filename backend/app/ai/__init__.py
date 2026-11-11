"""Explainable hybrid AI analysis for Votex AI.

Four independent, deterministic components feed a weighted risk score:

- ``U`` URL and domain intelligence
- ``N`` NLP social-engineering signals
- ``M`` machine-learning classifier
- ``I`` indicators and policy rules

The final score follows the published formula ``R = 0.30U + 0.25N + 0.25M + 0.20I``.
Every component returns human-readable reasons so an analyst can challenge it.
"""

from app.ai.engine import AnalysisResult, analyse_incident

__all__ = ["AnalysisResult", "analyse_incident"]
