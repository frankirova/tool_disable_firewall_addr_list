"""Centralised configuration — loads everything from environment variables once.

Eliminates the scattered load_dotenv() calls throughout the original codebase.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv


load_dotenv()


def _required(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise RuntimeError(
            f"Missing required environment variable: {key}. "
            f"Set it in your .env file or environment."
        )
    return val


def _optional(key: str, default: str = "") -> str:
    return os.getenv(key, default)


@dataclass(frozen=True)
class AppConfig:
    # ── MikroTik ──────────────────────────────────────────────
    mikrotik_user: str = field(default_factory=lambda: _required("USER_MIKROTIK"))
    mikrotik_password: str = field(default_factory=lambda: _required("PASS_MIKROTIK"))

    # ── Google Sheets ─────────────────────────────────────────
    sheets_credentials_path: str = field(default_factory=lambda: _required("KEY"))
    spreadsheet_id: str = field(default_factory=lambda: _required("SPREADSHEET_ID"))

    # ── MongoDB ───────────────────────────────────────────────
    mongo_uri: str = field(default_factory=lambda: _required("MONGO_URI"))
    mongo_db_name: str = field(default_factory=lambda: _optional("MONGO_DB_NAME", "cortes-redmetro"))
    mongo_collection_options: str = field(default_factory=lambda: _optional("MONGO_OPTIONS_COLLECTION", "options"))

    # ── CORS ──────────────────────────────────────────────────
    cors_origins: list[str] = field(default_factory=lambda: [
        _optional("CORS_ORIGIN_1", "http://localhost:5173"),
        _optional("CORS_ORIGIN_2", "http://localhost:8000"),
    ])

    # ── Server ────────────────────────────────────────────────
    host: str = field(default_factory=lambda: _optional("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(_optional("PORT", "8000")))


# Single instance — import this everywhere instead of building your own.
config = AppConfig()
