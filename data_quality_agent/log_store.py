"""Append-only run logs for traceability and reporting."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import settings

_CURRENT_RUN_ID: str | None = None


def make_run_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"dq-{timestamp}"


def current_run_id() -> str:
    global _CURRENT_RUN_ID

    env_run_id = os.getenv("DQ_RUN_ID")
    if env_run_id:
        _CURRENT_RUN_ID = env_run_id
        return _CURRENT_RUN_ID

    if _CURRENT_RUN_ID is None:
        _CURRENT_RUN_ID = make_run_id()
    return _CURRENT_RUN_ID


def set_run_id(run_id: str) -> None:
    global _CURRENT_RUN_ID

    _CURRENT_RUN_ID = run_id
    os.environ["DQ_RUN_ID"] = run_id


def run_log_path(run_id: str | None = None) -> Path:
    selected_run_id = run_id or current_run_id()
    return settings.log_dir / f"{selected_run_id}.jsonl"


def append_event(event: dict[str, Any], run_id: str | None = None) -> Path:
    selected_run_id = run_id or current_run_id()
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "run_id": selected_run_id,
        **event,
    }

    output_path = run_log_path(selected_run_id)
    with output_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=True) + "\n")

    return output_path


def load_events(run_id: str | None = None) -> list[dict[str, Any]]:
    output_path = run_log_path(run_id)
    if not output_path.exists():
        return []

    events: list[dict[str, Any]] = []
    with output_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            events.append(json.loads(line))
    return events


def save_text_report(content: str, run_id: str | None = None) -> Path:
    selected_run_id = run_id or current_run_id()
    report_path = settings.log_dir / f"{selected_run_id}.md"
    report_path.write_text(content, encoding="utf-8")
    return report_path
