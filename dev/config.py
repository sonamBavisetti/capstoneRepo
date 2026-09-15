from __future__ import annotations
"""Configuration loader for Vinayaka File Works.

Reads configuration from environment variables. For local development a .env file
may be used but MUST NOT be committed. In production, a managed secrets store
(e.g., AWS Secrets Manager) is required and should be documented in dev/docs.
"""
from dataclasses import dataclass
import os
from typing import Optional

try:
    # Optional for local dev convenience; respects .env only locally
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass


@dataclass
class Config:
    flask_env: str
    database_url: str
    redis_url: str
    secret_key: str
    storage_backend: str


def get_config() -> Config:
    flask_env = os.getenv("FLASK_ENV", "production")
    database_url = os.getenv("DATABASE_URL") or "sqlite:///dev.db"
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    secret_key = os.getenv("SECRET_KEY")
    storage_backend = os.getenv("STORAGE_BACKEND", "local")

    if not secret_key:
        # In CI and production this should be enforced by a secret manager
        raise RuntimeError("SECRET_KEY is not set. Use environment variables or a secret manager.")

    return Config(
        flask_env=flask_env,
        database_url=database_url,
        redis_url=redis_url,
        secret_key=secret_key,
        storage_backend=storage_backend,
    )
