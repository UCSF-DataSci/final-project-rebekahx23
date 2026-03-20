"""Tool functions exposed to ADK agents."""

from __future__ import annotations

import json
from typing import Any

from .config import settings
from .db import db_client
from .log_store import append_event, current_run_id, load_events


def start_quality_run(target_tables: list[str] | None = None, notes: str = "") -> dict[str, Any]:
    """Initialize a quality run and persist basic metadata."""

    run_id = current_run_id()
    tables = target_tables or []
    append_event(
        {
            "event": "run_started",
            "target_tables": tables,
            "notes": notes,
            "db_url": settings.db_url,
        },
        run_id,
    )
    return {
        "run_id": run_id,
        "target_tables": tables,
        "sample_size": settings.default_sample_size,
        "sample_batches": settings.default_sample_batches,
    }


def list_tables(schema_name: str = "") -> dict[str, Any]:
    """List available tables for a schema (or default schema when omitted)."""

    schema = schema_name or None
    tables = db_client.list_tables(schema_name=schema)
    append_event(
        {
            "event": "tables_listed",
            "schema": schema_name,
            "table_count": len(tables),
        }
    )
    return {"tables": tables}


def describe_table_schema(table_name: str) -> dict[str, Any]:
    """Return table columns and types so the planner can design quality checks."""

    schema_info = db_client.describe_table(table_name)
    append_event(
        {
            "event": "schema_described",
            "table": table_name,
            "column_count": len(schema_info["columns"]),
        }
    )
    return schema_info


def sample_table_data(table_name: str, sample_size: int = 20, batches: int = 3) -> dict[str, Any]:
    """Collect multiple random batches from a table for profile-driven planning."""

    selected_size = max(1, sample_size)
    selected_batches = max(1, batches)
    samples = db_client.sample_rows(table_name, selected_size, selected_batches)

    token_cap = max(0, int(settings.profile_token_cap))
    if token_cap > 0:
        trimmed_samples = _trim_samples_by_token_cap(samples, token_cap)
    else:
        trimmed_samples = samples

    returned_rows = sum(len(batch) for batch in trimmed_samples)
    append_event(
        {
            "event": "data_sampled",
            "table": table_name,
            "sample_size": selected_size,
            "batches": selected_batches,
            "returned_rows": returned_rows,
            "profile_token_cap": token_cap,
        }
    )
    return {
        "table": table_name,
        "sample_size": selected_size,
        "batches": selected_batches,
        "samples": trimmed_samples,
        "profile_token_cap": token_cap,
        "returned_rows": returned_rows,
    }


def run_data_quality_test(
    table_name: str,
    test_name: str,
    rationale: str,
    sql: str,
    severity: str = "medium",
) -> dict[str, Any]:
    """Run one read-only SQL test case and flag rows that violate expected quality rules."""

    normalized_severity = severity.lower().strip() if severity else "medium"
    if normalized_severity not in {"low", "medium", "high", "critical"}:
        normalized_severity = "medium"

    try:
        result = db_client.execute_read_only_query(sql, row_limit=settings.query_row_limit)
        status = "fail" if result.issue_count > 0 else "pass"
        error_message = ""
        issue_count = result.issue_count
        truncated = result.truncated
        sample_rows = result.rows
    except Exception as exc:
        status = "error"
        issue_count = 0
        truncated = False
        sample_rows = []
        error_message = str(exc).strip()
        if len(error_message) > 1200:
            error_message = error_message[:1200] + "...(truncated)"

    event = {
        "event": "test_executed",
        "table": table_name,
        "test_name": test_name,
        "rationale": rationale,
        "sql": sql,
        "severity": normalized_severity,
        "status": status,
        "issue_count": issue_count,
        "truncated": truncated,
        "sample_rows": sample_rows,
    }
    if error_message:
        event["error_message"] = error_message
    append_event(event)

    response = {
        "table": table_name,
        "test_name": test_name,
        "status": status,
        "severity": normalized_severity,
        "issue_count": issue_count,
        "truncated": truncated,
        "sample_rows": sample_rows,
    }
    if error_message:
        response["error_message"] = error_message
    return response


def get_executed_tests(limit: int = 200) -> dict[str, Any]:
    """Fetch recently executed tests for supervisor reporting."""

    all_events = load_events()
    tests = [event for event in all_events if event.get("event") == "test_executed"]
    selected = tests[-max(1, limit) :]
    return {
        "run_id": current_run_id(),
        "total_tests": len(tests),
        "tests": selected,
    }


def finalize_quality_run(executive_summary: str) -> dict[str, Any]:
    """Persist final supervisor summary so each run has a durable narrative."""

    append_event(
        {
            "event": "run_completed",
            "summary": executive_summary,
        }
    )
    return {"run_id": current_run_id(), "summary_saved": True}


def _estimate_tokens_for_row(row: dict[str, Any]) -> int:
    try:
        row_text = json.dumps(row, ensure_ascii=True, default=str)
    except TypeError:
        row_text = str(row)
    return max(1, len(row_text) // 4)


def _trim_samples_by_token_cap(
    samples: list[list[dict[str, Any]]],
    token_cap: int,
) -> list[list[dict[str, Any]]]:
    remaining = max(0, token_cap)
    if remaining <= 0:
        return samples

    trimmed: list[list[dict[str, Any]]] = []
    stop = False
    for batch in samples:
        if stop:
            break
        trimmed_batch: list[dict[str, Any]] = []
        for row in batch:
            row_tokens = _estimate_tokens_for_row(row)
            if row_tokens > remaining:
                stop = True
                break
            trimmed_batch.append(row)
            remaining -= row_tokens
            if remaining <= 0:
                stop = True
                break
        trimmed.append(trimmed_batch)
    return trimmed
