"""Runtime settings for the data quality agents."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:  # pragma: no cover - optional dependency for local quickstart
    def load_dotenv() -> None:
        return None

load_dotenv()


def _int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    try:
        return int(raw_value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    db_url: str = os.getenv("DQ_DB_URL", "sqlite:///./demo_data_quality.db")
    log_dir: Path = Path(os.getenv("DQ_LOG_DIR", "./runs"))
    model: str = os.getenv("DQ_MODEL", "gemini-2.5-flash")
    report_brand_name: str = os.getenv("DQ_REPORT_BRAND_NAME", "UCSF")
    report_logo_url: str = os.getenv(
        "DQ_REPORT_LOGO_URL",
        "../assets/ucsf_logo.svg",
    )
    default_sample_size: int = _int_env("DQ_SAMPLE_SIZE", 20)
    default_sample_batches: int = _int_env("DQ_SAMPLE_BATCHES", 3)
    profile_token_cap: int = _int_env("DQ_PROFILE_TOKEN_CAP", 0)
    query_row_limit: int = _int_env("DQ_QUERY_ROW_LIMIT", 200)
    max_planned_tests: int = _int_env("DQ_MAX_TESTS", 12)


settings = Settings()
settings.log_dir.mkdir(parents=True, exist_ok=True)
