"""Core configuration loaded from environment variables.

Every value has a safe local default so a fresh clone can start without a
``.env`` file. Production deployments must override secrets and URLs.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the Votex AI API."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Application
    environment: str = "development"
    app_version: str = "0.1.0"
    secret_key: str = "change-me-use-a-long-random-value"
    access_token_expire_minutes: int = 60

    # JWT
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "votex-ai"
    jwt_audience: str = "votex-ai-api"

    # Network
    cors_origins: str = (
        "http://localhost:5173,http://127.0.0.1:5173,"
        "http://localhost:5174,http://127.0.0.1:5174,http://localhost:8080"
    )

    # Persistence
    database_url: str = "sqlite:///./votex.db"
    redis_url: str = "redis://localhost:6379/0"

    # Evidence handling
    evidence_dir: str = "./storage/evidence"
    max_evidence_mb: int = 10

    # AI engine
    model_path: str = "../ai-engine/models/phishing_model.joblib"
    model_version: str = "hybrid-v0.2.0"

    # Privacy
    k_anonymity: int = 5

    # Demo behaviour
    auto_seed: bool = True
    demo_password: str = "VotexDemo!23"

    @property
    def cors_origin_list(self) -> list[str]:
        """Return CORS origins as a clean list."""

        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Return a cached settings instance."""

    return Settings()


settings = get_settings()
