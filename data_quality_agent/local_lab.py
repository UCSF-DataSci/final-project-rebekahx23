"""Local data-quality lab utilities for CSV ingest and controlled corruption."""

from __future__ import annotations

import argparse
import csv
import json
import random
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from .config import settings

console = Console()
_ROWID_CHUNK_SIZE = 500


def _quote_ident(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def _sanitize_identifier(raw_name: str, fallback: str) -> str:
    cleaned = "".join(char if (char.isalnum() or char == "_") else "_" for char in raw_name.strip())
    cleaned = cleaned.strip("_").lower()
    if not cleaned:
        cleaned = fallback
    if cleaned[0].isdigit():
        cleaned = f"c_{cleaned}"
    return cleaned


def _resolve_sqlite_path(db_url: str) -> Path:
    prefix = "sqlite:///"
    if not db_url.startswith(prefix):
        raise ValueError(
            f"Local lab supports sqlite URLs only. Current DQ_DB_URL: {db_url}. "
            "Use e.g. sqlite:///./demo_data_quality.db"
        )

    raw_path = db_url[len(prefix) :]
    if raw_path == ":memory:":
        raise ValueError("Please use a file-backed SQLite path for the local lab.")

    db_path = Path(raw_path)
    if not db_path.is_absolute():
        db_path = Path.cwd() / db_path
    return db_path.resolve()


def _connect_sqlite(db_url: str) -> tuple[sqlite3.Connection, Path]:
    db_path = _resolve_sqlite_path(db_url)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn, db_path


def _is_int(value: str) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


def _is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def _normalize_cell(cell: Any) -> str:
    if cell is None:
        return ""
    return str(cell).strip()


def _infer_sqlite_type(values: list[str]) -> str:
    non_empty = [value for value in values if value != ""]
    if not non_empty:
        return "TEXT"

    if all(_is_int(value) for value in non_empty):
        return "INTEGER"

    if all(_is_float(value) for value in non_empty):
        return "REAL"

    return "TEXT"


def _read_csv_rows(csv_path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"CSV has no header row: {csv_path}")

        headers = [header.strip() for header in reader.fieldnames]
        rows: list[dict[str, str]] = []
        for raw_row in reader:
            normalized = {}
            for header in headers:
                normalized[header] = _normalize_cell(raw_row.get(header, ""))
            rows.append(normalized)

    return headers, rows


def _safe_table_name(raw_name: str) -> str:
    return _sanitize_identifier(raw_name, "table")


def _safe_columns(headers: list[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()

    for idx, header in enumerate(headers):
        name = _sanitize_identifier(header, f"col_{idx + 1}")
        if name in seen:
            suffix = 2
            while f"{name}_{suffix}" in seen:
                suffix += 1
            name = f"{name}_{suffix}"
        seen.add(name)
        normalized.append(name)

    return normalized


def _cast_value(raw_value: str, sqlite_type: str) -> Any:
    if raw_value == "":
        return None

    if sqlite_type == "INTEGER":
        try:
            return int(raw_value)
        except ValueError:
            return None

    if sqlite_type == "REAL":
        try:
            return float(raw_value)
        except ValueError:
            return None

    return raw_value


def _create_table(
    conn: sqlite3.Connection,
    table_name: str,
    columns: list[str],
    sqlite_types: list[str],
    if_exists: str,
) -> None:
    q_table = _quote_ident(table_name)
    if if_exists == "replace":
        conn.execute(f"DROP TABLE IF EXISTS {q_table}")

    col_defs = ", ".join(
        f"{_quote_ident(column)} {sqlite_type}"
        for column, sqlite_type in zip(columns, sqlite_types, strict=True)
    )
    conn.execute(f"CREATE TABLE IF NOT EXISTS {q_table} ({col_defs})")


def ingest_csv(
    conn: sqlite3.Connection,
    csv_path: Path,
    table_name: str,
    if_exists: str,
) -> dict[str, Any]:
    headers, raw_rows = _read_csv_rows(csv_path)
    safe_columns = _safe_columns(headers)

    column_values: list[list[str]] = [[] for _ in safe_columns]
    mapped_rows: list[list[Any]] = []

    for raw_row in raw_rows:
        row_values: list[str] = []
        for header, bucket in zip(headers, column_values, strict=True):
            cell = _normalize_cell(raw_row.get(header, ""))
            bucket.append(cell)
            row_values.append(cell)
        mapped_rows.append(row_values)

    inferred_types = [_infer_sqlite_type(values) for values in column_values]

    _create_table(conn, table_name, safe_columns, inferred_types, if_exists)

    q_table = _quote_ident(table_name)
    q_columns = ", ".join(_quote_ident(column) for column in safe_columns)
    placeholders = ", ".join("?" for _ in safe_columns)
    insert_sql = f"INSERT INTO {q_table} ({q_columns}) VALUES ({placeholders})"

    typed_rows = [
        tuple(_cast_value(value, col_type) for value, col_type in zip(row, inferred_types, strict=True))
        for row in mapped_rows
    ]

    if typed_rows:
        conn.executemany(insert_sql, typed_rows)
    conn.commit()

    return {
        "table": table_name,
        "rows": len(typed_rows),
        "columns": safe_columns,
        "types": inferred_types,
    }


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    q = "SELECT 1 FROM sqlite_master WHERE type='table' AND name = ?"
    return conn.execute(q, (table_name,)).fetchone() is not None


def _row_count(conn: sqlite3.Connection, table_name: str) -> int:
    q_table = _quote_ident(table_name)
    row = conn.execute(f"SELECT COUNT(*) AS c FROM {q_table}").fetchone()
    return int(row["c"]) if row else 0


def _table_columns(conn: sqlite3.Connection, table_name: str) -> list[dict[str, Any]]:
    q_table = _quote_ident(table_name)
    rows = conn.execute(f"PRAGMA table_info({q_table})").fetchall()
    return [
        {
            "name": str(row["name"]),
            "type": str(row["type"] or "").upper(),
            "notnull": bool(row["notnull"]),
            "pk": int(row["pk"]),
        }
        for row in rows
    ]


def _is_text_column(column: dict[str, Any]) -> bool:
    col_type = str(column.get("type", "")).upper()
    return ("CHAR" in col_type) or ("TEXT" in col_type) or (col_type == "")


def _is_numeric_column(column: dict[str, Any]) -> bool:
    col_type = str(column.get("type", "")).upper()
    return ("INT" in col_type) or ("REAL" in col_type) or ("NUM" in col_type) or ("DEC" in col_type)


def _is_temporal_column(column: dict[str, Any]) -> bool:
    name = str(column.get("name", "")).lower()
    col_type = str(column.get("type", "")).upper()
    name_hint = any(token in name for token in ("date", "time", "dt", "ts", "admission", "discharge"))
    type_hint = ("DATE" in col_type) or ("TIME" in col_type)
    return name_hint or type_hint


def _find_column_by_name_patterns(
    columns: list[dict[str, Any]],
    *,
    patterns: tuple[str, ...],
    require_text: bool = False,
    require_numeric: bool = False,
    exclude: set[str] | None = None,
) -> str | None:
    blocked = exclude or set()
    for col in columns:
        name = str(col["name"])
        lower = name.lower()
        padded = f"_{lower}_"
        if name in blocked:
            continue
        if not any(f"_{pattern}_" in padded for pattern in patterns):
            continue
        if require_text and not _is_text_column(col):
            continue
        if require_numeric and not _is_numeric_column(col):
            continue
        return name
    return None


def _find_temporal_pair(columns: list[dict[str, Any]]) -> tuple[str | None, str | None]:
    start_patterns = ("admission", "start", "from", "begin", "checkin")
    end_patterns = ("discharge", "end", "to", "stop", "checkout")
    start_col = _find_column_by_name_patterns(columns, patterns=start_patterns)
    end_col = _find_column_by_name_patterns(
        columns,
        patterns=end_patterns,
        exclude={start_col} if start_col else None,
    )
    if start_col and end_col:
        return start_col, end_col

    temporal_cols = [col["name"] for col in columns if _is_temporal_column(col)]
    if len(temporal_cols) >= 2:
        return temporal_cols[0], temporal_cols[1]
    return None, None


def _fetch_rows_by_rowid(
    conn: sqlite3.Connection,
    table_name: str,
    columns: list[str],
    row_ids: list[int],
) -> list[sqlite3.Row]:
    if not row_ids:
        return []
    q_table = _quote_ident(table_name)
    q_cols = ", ".join(_quote_ident(col) for col in columns)
    rows: list[sqlite3.Row] = []
    for chunk in _chunk_list(row_ids, _ROWID_CHUNK_SIZE):
        placeholders = ", ".join("?" for _ in chunk)
        query = f"""
            SELECT rowid, {q_cols}
            FROM {q_table}
            WHERE rowid IN ({placeholders})
        """
        rows.extend(conn.execute(query, tuple(chunk)).fetchall())
    return rows


def _update_column_values_by_rowid(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str,
    updates: list[tuple[Any, int]],
) -> None:
    if not updates:
        return
    q_table = _quote_ident(table_name)
    q_col = _quote_ident(column_name)
    query = f"UPDATE {q_table} SET {q_col} = ? WHERE rowid = ?"
    conn.executemany(query, updates)


def _update_two_columns_by_rowid(
    conn: sqlite3.Connection,
    table_name: str,
    column_a: str,
    column_b: str,
    updates: list[tuple[Any, Any, int]],
) -> None:
    if not updates:
        return
    q_table = _quote_ident(table_name)
    q_a = _quote_ident(column_a)
    q_b = _quote_ident(column_b)
    query = f"UPDATE {q_table} SET {q_a} = ?, {q_b} = ? WHERE rowid = ?"
    conn.executemany(query, updates)


def _mutate_identifier_value(value: Any) -> str:
    raw = str(value or "").strip()
    if len(raw) < 3:
        return raw
    if len(raw) < 6:
        drop_idx = 1
    else:
        drop_idx = random.randint(1, len(raw) - 2)
    mutated = raw[:drop_idx] + raw[drop_idx + 1 :]
    return mutated if mutated else raw


def _mutate_categorical_value(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return raw
    lowered = raw.lower()
    synonym_map = {
        "positive": "POS",
        "negative": "NEG",
        "yes": "Y",
        "no": "N",
        "true": "1",
        "false": "0",
        "male": "M",
        "female": "F",
    }
    if lowered in synonym_map:
        return synonym_map[lowered]
    return f" {raw.upper()} "


def _mutate_unit_value(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return raw
    unit_map = {
        "mg/dl": "mmol/L",
        "mmol/l": "mg/dL",
        "kg": "lb",
        "lb": "kg",
        "cm": "in",
        "in": "cm",
        "bpm": "/min",
        "%": "fraction",
    }
    return unit_map.get(raw.lower(), f"{raw}_ALT")


def _mutate_code_value(value: Any) -> str:
    raw = str(value or "").strip()
    if not raw:
        return raw
    if raw.startswith("LOCAL-"):
        return raw
    if "-" in raw:
        return raw.split("-", 1)[0] + "-OLD"
    return f"LOCAL-{raw}"


def _pick_count(total: int, fraction: float) -> int:
    if total <= 0:
        return 0
    return max(1, int(total * fraction))


def _chunk_list(values: list[int], chunk_size: int) -> list[list[int]]:
    if chunk_size <= 0:
        return [values]
    return [values[index : index + chunk_size] for index in range(0, len(values), chunk_size)]


def _select_random_rowids(
    conn: sqlite3.Connection,
    table_name: str,
    where_sql: str,
    params: tuple[Any, ...],
    limit: int,
) -> list[int]:
    if limit <= 0:
        return []

    q_table = _quote_ident(table_name)
    query = (
        f"SELECT rowid FROM {q_table} "
        f"WHERE {where_sql} "
        "ORDER BY RANDOM() "
        "LIMIT ?"
    )
    rows = conn.execute(query, (*params, limit)).fetchall()
    return [int(row["rowid"]) for row in rows]


def _update_rows_by_rowid(
    conn: sqlite3.Connection,
    table_name: str,
    set_sql: str,
    set_params: tuple[Any, ...],
    row_ids: list[int],
) -> None:
    if not row_ids:
        return

    q_table = _quote_ident(table_name)
    for chunk in _chunk_list(row_ids, _ROWID_CHUNK_SIZE):
        placeholders = ", ".join("?" for _ in chunk)
        query = f"UPDATE {q_table} SET {set_sql} WHERE rowid IN ({placeholders})"
        conn.execute(query, (*set_params, *chunk))


def _run_nullify(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str,
    fraction: float,
) -> dict[str, Any]:
    q_table = _quote_ident(table_name)
    q_col = _quote_ident(column_name)
    eligible = conn.execute(
        f"SELECT COUNT(*) AS c FROM {q_table} WHERE {q_col} IS NOT NULL"
    ).fetchone()["c"]
    affected = _pick_count(int(eligible), fraction)
    if affected <= 0:
        return {"rows": 0, "row_ids": []}

    row_ids = _select_random_rowids(
        conn=conn,
        table_name=table_name,
        where_sql=f"{q_col} IS NOT NULL",
        params=(),
        limit=affected,
    )
    _update_rows_by_rowid(
        conn=conn,
        table_name=table_name,
        set_sql=f"{q_col} = NULL",
        set_params=(),
        row_ids=row_ids,
    )
    conn.commit()
    return {"rows": len(row_ids), "row_ids": row_ids}


def _run_truncate(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str,
    fraction: float,
    truncate_to: int,
) -> dict[str, Any]:
    q_table = _quote_ident(table_name)
    q_col = _quote_ident(column_name)
    eligible = conn.execute(
        f"SELECT COUNT(*) AS c FROM {q_table} WHERE {q_col} IS NOT NULL AND LENGTH({q_col}) > ?",
        (truncate_to,),
    ).fetchone()["c"]
    affected = _pick_count(int(eligible), fraction)
    if affected <= 0:
        return {"rows": 0, "row_ids": []}

    row_ids = _select_random_rowids(
        conn=conn,
        table_name=table_name,
        where_sql=f"{q_col} IS NOT NULL AND LENGTH({q_col}) > ?",
        params=(truncate_to,),
        limit=affected,
    )
    _update_rows_by_rowid(
        conn=conn,
        table_name=table_name,
        set_sql=f"{q_col} = SUBSTR({q_col}, 1, ?)",
        set_params=(truncate_to,),
        row_ids=row_ids,
    )
    conn.commit()
    return {"rows": len(row_ids), "row_ids": row_ids}


def _run_numeric_outlier(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str,
    fraction: float,
) -> dict[str, Any]:
    q_table = _quote_ident(table_name)
    q_col = _quote_ident(column_name)
    eligible = conn.execute(
        f"SELECT COUNT(*) AS c FROM {q_table} WHERE {q_col} IS NOT NULL"
    ).fetchone()["c"]
    affected = _pick_count(int(eligible), fraction)
    if affected <= 0:
        return {"rows": 0, "row_ids": []}

    row_ids = _select_random_rowids(
        conn=conn,
        table_name=table_name,
        where_sql=f"{q_col} IS NOT NULL",
        params=(),
        limit=affected,
    )
    _update_rows_by_rowid(
        conn=conn,
        table_name=table_name,
        set_sql=f"{q_col} = (ABS(CAST({q_col} AS REAL)) * 500.0) + 10000.0",
        set_params=(),
        row_ids=row_ids,
    )
    conn.commit()
    return {"rows": len(row_ids), "row_ids": row_ids}


def _run_future_date(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str,
    fraction: float,
) -> dict[str, Any]:
    q_table = _quote_ident(table_name)
    q_col = _quote_ident(column_name)
    eligible = conn.execute(
        f"SELECT COUNT(*) AS c FROM {q_table} WHERE {q_col} LIKE '____-__-__%'"
    ).fetchone()["c"]
    affected = _pick_count(int(eligible), fraction)
    if affected <= 0:
        return {"rows": 0, "row_ids": []}

    row_ids = _select_random_rowids(
        conn=conn,
        table_name=table_name,
        where_sql=f"{q_col} LIKE '____-__-__%'",
        params=(),
        limit=affected,
    )
    _update_rows_by_rowid(
        conn=conn,
        table_name=table_name,
        set_sql=f"{q_col} = '2099-12-31'",
        set_params=(),
        row_ids=row_ids,
    )
    conn.commit()
    return {"rows": len(row_ids), "row_ids": row_ids}


def _run_duplicate_rows(conn: sqlite3.Connection, table_name: str, fraction: float) -> dict[str, Any]:
    cols = _table_columns(conn, table_name)
    non_autoincrement_pk = [
        col for col in cols if not (col["pk"] == 1 and "INT" in col["type"])
    ]
    target_columns = non_autoincrement_pk if non_autoincrement_pk else cols
    if not target_columns:
        return 0

    total = _row_count(conn, table_name)
    affected = _pick_count(total, fraction)
    if affected <= 0:
        return {"rows": 0, "row_ids": [], "source_row_ids": []}

    q_table = _quote_ident(table_name)
    q_cols = ", ".join(_quote_ident(col["name"]) for col in target_columns)
    source_row_ids = _select_random_rowids(
        conn=conn,
        table_name=table_name,
        where_sql="1=1",
        params=(),
        limit=affected,
    )
    if not source_row_ids:
        return {"rows": 0, "row_ids": [], "source_row_ids": []}

    max_before = int(
        conn.execute(f"SELECT COALESCE(MAX(rowid), 0) AS max_rowid FROM {q_table}").fetchone()[
            "max_rowid"
        ]
    )
    for chunk in _chunk_list(source_row_ids, _ROWID_CHUNK_SIZE):
        placeholders = ", ".join("?" for _ in chunk)
        conn.execute(
            f"""
            INSERT INTO {q_table} ({q_cols})
            SELECT {q_cols}
            FROM {q_table}
            WHERE rowid IN ({placeholders})
            """,
            tuple(chunk),
        )
    conn.commit()
    inserted_rows = conn.execute(
        f"SELECT rowid FROM {q_table} WHERE rowid > ? ORDER BY rowid ASC",
        (max_before,),
    ).fetchall()
    inserted_row_ids = [int(row["rowid"]) for row in inserted_rows[: len(source_row_ids)]]

    return {
        "rows": len(inserted_row_ids),
        "row_ids": inserted_row_ids,
        "source_row_ids": source_row_ids,
    }


def _run_temporal_inversion(
    conn: sqlite3.Connection,
    table_name: str,
    start_column: str,
    end_column: str,
    fraction: float,
) -> dict[str, Any]:
    q_table = _quote_ident(table_name)
    q_start = _quote_ident(start_column)
    q_end = _quote_ident(end_column)
    eligible = conn.execute(
        f"""
        SELECT COUNT(*) AS c
        FROM {q_table}
        WHERE {q_start} IS NOT NULL
          AND {q_end} IS NOT NULL
          AND julianday({q_start}) IS NOT NULL
          AND julianday({q_end}) IS NOT NULL
          AND julianday({q_end}) >= julianday({q_start})
        """
    ).fetchone()["c"]
    affected = _pick_count(int(eligible), fraction)
    if affected <= 0:
        return {"rows": 0, "row_ids": []}

    row_ids = _select_random_rowids(
        conn=conn,
        table_name=table_name,
        where_sql=(
            f"{q_start} IS NOT NULL AND {q_end} IS NOT NULL "
            f"AND julianday({q_start}) IS NOT NULL "
            f"AND julianday({q_end}) IS NOT NULL "
            f"AND julianday({q_end}) >= julianday({q_start})"
        ),
        params=(),
        limit=affected,
    )
    _update_rows_by_rowid(
        conn=conn,
        table_name=table_name,
        set_sql=(
            f"{q_end} = CASE "
            f"WHEN LENGTH({q_start}) >= 19 THEN datetime({q_start}, '-1 day') "
            f"ELSE date({q_start}, '-1 day') END"
        ),
        set_params=(),
        row_ids=row_ids,
    )
    conn.commit()
    return {"rows": len(row_ids), "row_ids": row_ids}


def _run_datetime_shift(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str,
    fraction: float,
    shift_hours: int = 8,
) -> dict[str, Any]:
    q_table = _quote_ident(table_name)
    q_col = _quote_ident(column_name)
    eligible = conn.execute(
        f"""
        SELECT COUNT(*) AS c
        FROM {q_table}
        WHERE {q_col} IS NOT NULL
          AND {q_col} LIKE '____-__-__%'
          AND julianday({q_col}) IS NOT NULL
        """
    ).fetchone()["c"]
    affected = _pick_count(int(eligible), fraction)
    if affected <= 0:
        return {"rows": 0, "row_ids": []}

    row_ids = _select_random_rowids(
        conn=conn,
        table_name=table_name,
        where_sql=f"{q_col} IS NOT NULL AND {q_col} LIKE '____-__-__%' AND julianday({q_col}) IS NOT NULL",
        params=(),
        limit=affected,
    )
    _update_rows_by_rowid(
        conn=conn,
        table_name=table_name,
        set_sql=(
            f"{q_col} = CASE "
            f"WHEN LENGTH({q_col}) >= 19 THEN datetime({q_col}, '{shift_hours:+d} hours') "
            f"ELSE date({q_col}, '+1 day') END"
        ),
        set_params=(),
        row_ids=row_ids,
    )
    conn.commit()
    return {"rows": len(row_ids), "row_ids": row_ids}


def _run_unit_mismatch(
    conn: sqlite3.Connection,
    table_name: str,
    unit_column: str,
    value_column: str,
    fraction: float,
) -> dict[str, Any]:
    q_table = _quote_ident(table_name)
    q_unit = _quote_ident(unit_column)
    q_val = _quote_ident(value_column)
    eligible = conn.execute(
        f"""
        SELECT COUNT(*) AS c
        FROM {q_table}
        WHERE {q_unit} IS NOT NULL
          AND TRIM(CAST({q_unit} AS TEXT)) <> ''
          AND {q_val} IS NOT NULL
        """
    ).fetchone()["c"]
    affected = _pick_count(int(eligible), fraction)
    if affected <= 0:
        return {"rows": 0, "row_ids": []}

    row_ids = _select_random_rowids(
        conn=conn,
        table_name=table_name,
        where_sql=f"{q_unit} IS NOT NULL AND TRIM(CAST({q_unit} AS TEXT)) <> '' AND {q_val} IS NOT NULL",
        params=(),
        limit=affected,
    )
    rows = _fetch_rows_by_rowid(conn, table_name, [unit_column], row_ids)
    updates: list[tuple[Any, int]] = []
    for row in rows:
        row_id = int(row["rowid"])
        updates.append((_mutate_unit_value(row[unit_column]), row_id))
    _update_column_values_by_rowid(conn, table_name, unit_column, updates)
    conn.commit()
    return {"rows": len(updates), "row_ids": [row_id for _, row_id in updates]}


def _run_code_drift(
    conn: sqlite3.Connection,
    table_name: str,
    code_column: str,
    fraction: float,
    system_column: str = "",
) -> dict[str, Any]:
    q_code = _quote_ident(code_column)
    where_sql = f"{q_code} IS NOT NULL AND TRIM(CAST({q_code} AS TEXT)) <> ''"
    affected = _pick_count(
        int(
            conn.execute(
                f"SELECT COUNT(*) AS c FROM {_quote_ident(table_name)} WHERE {where_sql}"
            ).fetchone()["c"]
        ),
        fraction,
    )
    if affected <= 0:
        return {"rows": 0, "row_ids": []}

    row_ids = _select_random_rowids(
        conn=conn,
        table_name=table_name,
        where_sql=where_sql,
        params=(),
        limit=affected,
    )
    fetch_cols = [code_column] + ([system_column] if system_column else [])
    rows = _fetch_rows_by_rowid(conn, table_name, fetch_cols, row_ids)
    if system_column:
        updates2: list[tuple[Any, Any, int]] = []
        for row in rows:
            row_id = int(row["rowid"])
            mutated_code = _mutate_code_value(row[code_column])
            mutated_system = "http://local.vendor.invalid/codesystem"
            updates2.append((mutated_code, mutated_system, row_id))
        _update_two_columns_by_rowid(conn, table_name, code_column, system_column, updates2)
        changed_row_ids = [row_id for _, _, row_id in updates2]
    else:
        updates1: list[tuple[Any, int]] = []
        for row in rows:
            row_id = int(row["rowid"])
            updates1.append((_mutate_code_value(row[code_column]), row_id))
        _update_column_values_by_rowid(conn, table_name, code_column, updates1)
        changed_row_ids = [row_id for _, row_id in updates1]
    conn.commit()
    return {"rows": len(changed_row_ids), "row_ids": changed_row_ids}


def _run_id_fragmentation(
    conn: sqlite3.Connection,
    table_name: str,
    id_column: str,
    fraction: float,
) -> dict[str, Any]:
    q_col = _quote_ident(id_column)
    where_sql = f"{q_col} IS NOT NULL AND LENGTH(TRIM(CAST({q_col} AS TEXT))) >= 6"
    affected = _pick_count(
        int(
            conn.execute(
                f"SELECT COUNT(*) AS c FROM {_quote_ident(table_name)} WHERE {where_sql}"
            ).fetchone()["c"]
        ),
        fraction,
    )
    if affected <= 0:
        return {"rows": 0, "row_ids": []}

    row_ids = _select_random_rowids(conn, table_name, where_sql, (), affected)
    rows = _fetch_rows_by_rowid(conn, table_name, [id_column], row_ids)
    updates: list[tuple[Any, int]] = []
    for row in rows:
        row_id = int(row["rowid"])
        updates.append((_mutate_identifier_value(row[id_column]), row_id))
    _update_column_values_by_rowid(conn, table_name, id_column, updates)
    conn.commit()
    return {"rows": len(updates), "row_ids": [row_id for _, row_id in updates]}


def _run_enum_encoding_drift(
    conn: sqlite3.Connection,
    table_name: str,
    column_name: str,
    fraction: float,
) -> dict[str, Any]:
    q_table = _quote_ident(table_name)
    q_col = _quote_ident(column_name)
    eligible = conn.execute(
        f"""
        SELECT COUNT(*) AS c
        FROM {q_table}
        WHERE {q_col} IS NOT NULL
          AND TRIM(CAST({q_col} AS TEXT)) <> ''
        """
    ).fetchone()["c"]
    affected = _pick_count(int(eligible), fraction)
    if affected <= 0:
        return {"rows": 0, "row_ids": []}

    row_ids = _select_random_rowids(
        conn=conn,
        table_name=table_name,
        where_sql=f"{q_col} IS NOT NULL AND TRIM(CAST({q_col} AS TEXT)) <> ''",
        params=(),
        limit=affected,
    )
    rows = _fetch_rows_by_rowid(conn, table_name, [column_name], row_ids)
    updates: list[tuple[Any, int]] = []
    for row in rows:
        row_id = int(row["rowid"])
        updates.append((_mutate_categorical_value(row[column_name]), row_id))
    _update_column_values_by_rowid(conn, table_name, column_name, updates)
    conn.commit()
    return {"rows": len(updates), "row_ids": [row_id for _, row_id in updates]}


def _pick_column(
    columns: list[dict[str, Any]],
    preferred: str,
    kind: str,
) -> str:
    if preferred:
        if not any(column["name"] == preferred for column in columns):
            raise ValueError(f"Column not found: {preferred}")
        return preferred

    if kind == "nullable":
        candidates = [col for col in columns if not col["notnull"] and col["pk"] == 0]
    elif kind == "text":
        candidates = [col for col in columns if "CHAR" in col["type"] or "TEXT" in col["type"]]
    elif kind == "numeric":
        candidates = [
            col
            for col in columns
            if "INT" in col["type"] or "REAL" in col["type"] or "NUM" in col["type"]
        ]
    elif kind == "date":
        candidates = [
            col
            for col in columns
            if any(token in col["name"].lower() for token in ("date", "time", "ts", "dt"))
        ]
    else:
        candidates = []

    if not candidates:
        raise ValueError(f"No candidate column found for kind={kind}")
    return candidates[0]["name"]


def _run_auto_corrupt(
    conn: sqlite3.Connection,
    table_name: str,
    fraction: float,
    truncate_to: int,
) -> list[dict[str, Any]]:
    columns = _table_columns(conn, table_name)
    operations: list[dict[str, Any]] = []

    try:
        nullable_col = _pick_column(columns, preferred="", kind="nullable")
        touched = _run_nullify(conn, table_name, nullable_col, fraction)
        operations.append({"strategy": "nullify", "column": nullable_col, **touched})
    except ValueError:
        pass

    try:
        text_col = _pick_column(columns, preferred="", kind="text")
        touched = _run_truncate(conn, table_name, text_col, fraction, truncate_to)
        operations.append({"strategy": "truncate", "column": text_col, **touched})
    except ValueError:
        pass

    try:
        numeric_col = _pick_column(columns, preferred="", kind="numeric")
        touched = _run_numeric_outlier(conn, table_name, numeric_col, fraction)
        operations.append({"strategy": "numeric_outlier", "column": numeric_col, **touched})
    except ValueError:
        pass

    try:
        date_col = _pick_column(columns, preferred="", kind="date")
        touched = _run_future_date(conn, table_name, date_col, fraction)
        operations.append({"strategy": "future_date", "column": date_col, **touched})
    except ValueError:
        pass

    touched = _run_duplicate_rows(conn, table_name, fraction)
    operations.append({"strategy": "duplicate_rows", "column": "(row)", **touched})

    return operations


def _run_complex_auto_corrupt(
    conn: sqlite3.Connection,
    table_name: str,
    fraction: float,
) -> list[dict[str, Any]]:
    columns = _table_columns(conn, table_name)
    operations: list[dict[str, Any]] = []

    start_col, end_col = _find_temporal_pair(columns)
    if start_col and end_col:
        touched = _run_temporal_inversion(conn, table_name, start_col, end_col, fraction)
        operations.append(
            {
                "strategy": "temporal_inversion",
                "column": f"{start_col}->{end_col}",
                "details": {"start_column": start_col, "end_column": end_col},
                **touched,
            }
        )

    time_col = _find_column_by_name_patterns(
        columns,
        patterns=("time", "timestamp", "datetime", "admission", "discharge"),
    )
    if time_col:
        touched = _run_datetime_shift(conn, table_name, time_col, fraction, shift_hours=8)
        operations.append(
            {
                "strategy": "datetime_shift",
                "column": time_col,
                "details": {"shift_hours": 8},
                **touched,
            }
        )

    id_col = _find_column_by_name_patterns(
        columns,
        patterns=("member", "patient", "person", "subscriber", "mrn", "npi", "id"),
        require_text=True,
    )
    if id_col:
        touched = _run_id_fragmentation(conn, table_name, id_col, fraction)
        operations.append({"strategy": "id_fragmentation", "column": id_col, **touched})

    code_col = _find_column_by_name_patterns(
        columns,
        patterns=("code", "loinc", "icd", "rxnorm", "cpt"),
        require_text=True,
    )
    system_col = _find_column_by_name_patterns(
        columns,
        patterns=("code_system", "system", "coding_system", "code_uri", "oid"),
        require_text=True,
        exclude={code_col} if code_col else None,
    )
    if code_col:
        touched = _run_code_drift(conn, table_name, code_col, fraction, system_col or "")
        operations.append(
            {
                "strategy": "code_drift",
                "column": code_col,
                "details": {"system_column": system_col or ""},
                **touched,
            }
        )

    unit_col = _find_column_by_name_patterns(
        columns,
        patterns=("unit", "uom", "ucum"),
        require_text=True,
    )
    value_col = _find_column_by_name_patterns(
        columns,
        patterns=("value", "result", "amount", "qty", "quantity"),
        require_numeric=True,
        exclude={unit_col} if unit_col else None,
    )
    if unit_col and value_col:
        touched = _run_unit_mismatch(conn, table_name, unit_col, value_col, fraction)
        operations.append(
            {
                "strategy": "unit_mismatch",
                "column": unit_col,
                "details": {"value_column": value_col},
                **touched,
            }
        )

    categorical_col = _find_column_by_name_patterns(
        columns,
        patterns=("status", "flag", "result", "gender", "sex", "outcome", "type"),
        require_text=True,
    )
    if categorical_col:
        touched = _run_enum_encoding_drift(conn, table_name, categorical_col, fraction)
        operations.append(
            {
                "strategy": "enum_encoding_drift",
                "column": categorical_col,
                **touched,
            }
        )

    return operations


def list_tables(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    output = []
    for row in rows:
        table_name = str(row["name"])
        output.append({"table": table_name, "rows": _row_count(conn, table_name)})
    return output


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local DB lab for data-quality experiments.")
    parser.add_argument("--db-url", default=settings.db_url, help="SQLite URL, e.g. sqlite:///./demo_data_quality.db")

    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest = subparsers.add_parser("ingest", help="Ingest one or more CSV files into SQLite tables")
    ingest.add_argument("--csv", action="append", default=[], help="CSV file path (repeatable)")
    ingest.add_argument("--csv-dir", default="", help="Directory containing *.csv files")
    ingest.add_argument("--if-exists", choices=["replace", "append"], default="replace")
    ingest.add_argument("--table", default="", help="Override table name when ingesting a single CSV")

    corrupt = subparsers.add_parser("corrupt", help="Inject controlled data-quality issues")
    corrupt.add_argument("--table", required=True, help="Target table name")
    corrupt.add_argument(
        "--strategy",
        choices=[
            "auto",
            "complex_auto",
            "nullify",
            "truncate",
            "numeric_outlier",
            "future_date",
            "duplicate_rows",
            "temporal_inversion",
            "datetime_shift",
            "unit_mismatch",
            "code_drift",
            "id_fragmentation",
            "enum_encoding_drift",
        ],
        default="auto",
    )
    corrupt.add_argument("--column", default="", help="Target column for non-auto strategies")
    corrupt.add_argument("--fraction", type=float, default=0.05, help="Fraction of rows to corrupt")
    corrupt.add_argument("--truncate-to", type=int, default=4, help="Length for truncate strategy")
    corrupt.add_argument("--seed", type=int, default=7, help="Random seed")

    ls_tables = subparsers.add_parser("list", help="List local tables and row counts")
    ls_tables.add_argument("--verbose", action="store_true", help="Show column details")

    probe = subparsers.add_parser("probe", help="Run deterministic quality probes on a table")
    probe.add_argument("--table", required=True, help="Target table name")
    probe.add_argument(
        "--short-len-threshold",
        type=int,
        default=4,
        help="Threshold for short text checks",
    )
    probe.add_argument(
        "--numeric-spike-factor",
        type=float,
        default=50.0,
        help="Flag numeric columns where max(abs(x)) > factor * avg(abs(x))",
    )

    return parser.parse_args()


def _render_tables(conn: sqlite3.Connection, verbose: bool) -> None:
    tables = list_tables(conn)
    if not tables:
        console.print("No tables found in local DB.")
        return

    table = Table(title="Local SQLite Tables")
    table.add_column("Table")
    table.add_column("Rows", justify="right")
    table.add_column("Columns")

    for item in tables:
        table_name = item["table"]
        cols = _table_columns(conn, table_name)
        if verbose:
            columns_text = ", ".join(f"{col['name']}:{col['type'] or 'TEXT'}" for col in cols)
        else:
            columns_text = str(len(cols))
        table.add_row(table_name, str(item["rows"]), columns_text)

    console.print(table)


def _ingest_command(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    paths: list[Path] = []
    for raw_path in args.csv:
        paths.append(Path(raw_path).expanduser().resolve())

    if args.csv_dir:
        csv_dir = Path(args.csv_dir).expanduser().resolve()
        if not csv_dir.exists():
            raise ValueError(f"CSV directory not found: {csv_dir}")
        paths.extend(sorted(csv_dir.glob("*.csv")))

    deduped: list[Path] = []
    seen: set[Path] = set()
    for path in paths:
        if path in seen:
            continue
        seen.add(path)
        deduped.append(path)

    if not deduped:
        raise ValueError("Provide at least one --csv or --csv-dir with CSV files.")

    if args.table and len(deduped) != 1:
        raise ValueError("--table can only be used when ingesting exactly one CSV file.")

    results: list[dict[str, Any]] = []
    for path in deduped:
        if not path.exists():
            raise ValueError(f"CSV file not found: {path}")
        if path.suffix.lower() != ".csv":
            raise ValueError(f"Not a CSV file: {path}")

        table_name = _safe_table_name(args.table if args.table else path.stem)
        result = ingest_csv(conn, path, table_name=table_name, if_exists=args.if_exists)
        result["source"] = str(path)
        results.append(result)

    table = Table(title="CSV Ingestion Summary")
    table.add_column("Source")
    table.add_column("Table")
    table.add_column("Rows", justify="right")
    table.add_column("Columns", justify="right")
    table.add_column("Types")

    for result in results:
        table.add_row(
            result["source"],
            result["table"],
            str(result["rows"]),
            str(len(result["columns"])),
            ", ".join(result["types"]),
        )

    console.print(table)


def _write_ground_truth_artifact(
    *,
    table_name: str,
    timestamp: str,
    strategy: str,
    fraction: float,
    seed: int,
    truncate_to: int,
    rows_before: int,
    rows_after: int,
    operations: list[dict[str, Any]],
) -> Path:
    unique_row_ids: set[int] = set()
    for op in operations:
        for row_id in op.get("row_ids", []):
            unique_row_ids.add(int(row_id))

    payload = {
        "artifact_type": "lab_ground_truth",
        "generated_at_utc": timestamp,
        "db_url": settings.db_url,
        "table": table_name,
        "row_id_field": "rowid",
        "strategy": strategy,
        "fraction": fraction,
        "seed": seed,
        "truncate_to": truncate_to,
        "rows_before": rows_before,
        "rows_after": rows_after,
        "total_operations": len(operations),
        "total_unique_corrupted_rows": len(unique_row_ids),
        "unique_corrupted_row_ids": sorted(unique_row_ids),
        "operations": [
            {
                "strategy": str(op.get("strategy", "")),
                "column": str(op.get("column", "")),
                "rows": int(op.get("rows", 0)),
                "row_ids": [int(row_id) for row_id in op.get("row_ids", [])],
                "source_row_ids": [int(row_id) for row_id in op.get("source_row_ids", [])],
                "details": op.get("details", {}),
            }
            for op in operations
        ],
    }

    ground_truth_path = settings.log_dir / f"lab-ground-truth-{timestamp}.json"
    ground_truth_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return ground_truth_path


def _corrupt_command(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    table_name = args.table
    if not _table_exists(conn, table_name):
        raise ValueError(f"Table not found: {table_name}")

    random.seed(args.seed)
    fraction = min(max(args.fraction, 0.0), 1.0)
    if fraction <= 0.0:
        raise ValueError("--fraction must be greater than 0.")

    cols = _table_columns(conn, table_name)
    rows_before = _row_count(conn, table_name)

    operations: list[dict[str, Any]] = []
    if args.strategy == "auto":
        operations = _run_auto_corrupt(conn, table_name, fraction, args.truncate_to)
    elif args.strategy == "complex_auto":
        operations = _run_complex_auto_corrupt(conn, table_name, fraction)
    elif args.strategy == "nullify":
        col = _pick_column(cols, args.column, "nullable")
        touched = _run_nullify(conn, table_name, col, fraction)
        operations = [{"strategy": "nullify", "column": col, **touched}]
    elif args.strategy == "truncate":
        col = _pick_column(cols, args.column, "text")
        touched = _run_truncate(conn, table_name, col, fraction, args.truncate_to)
        operations = [{"strategy": "truncate", "column": col, **touched}]
    elif args.strategy == "numeric_outlier":
        col = _pick_column(cols, args.column, "numeric")
        touched = _run_numeric_outlier(conn, table_name, col, fraction)
        operations = [{"strategy": "numeric_outlier", "column": col, **touched}]
    elif args.strategy == "future_date":
        col = _pick_column(cols, args.column, "date")
        touched = _run_future_date(conn, table_name, col, fraction)
        operations = [{"strategy": "future_date", "column": col, **touched}]
    elif args.strategy == "duplicate_rows":
        touched = _run_duplicate_rows(conn, table_name, fraction)
        operations = [{"strategy": "duplicate_rows", "column": "(row)", **touched}]
    elif args.strategy == "temporal_inversion":
        start_col, end_col = _find_temporal_pair(cols)
        if not (start_col and end_col):
            raise ValueError("No temporal start/end column pair found for temporal_inversion.")
        touched = _run_temporal_inversion(conn, table_name, start_col, end_col, fraction)
        operations = [
            {
                "strategy": "temporal_inversion",
                "column": f"{start_col}->{end_col}",
                "details": {"start_column": start_col, "end_column": end_col},
                **touched,
            }
        ]
    elif args.strategy == "datetime_shift":
        col = _pick_column(cols, args.column, "date")
        touched = _run_datetime_shift(conn, table_name, col, fraction, shift_hours=8)
        operations = [
            {
                "strategy": "datetime_shift",
                "column": col,
                "details": {"shift_hours": 8},
                **touched,
            }
        ]
    elif args.strategy == "unit_mismatch":
        unit_col = _pick_column(cols, args.column, "text") if args.column else _find_column_by_name_patterns(
            cols,
            patterns=("unit", "uom", "ucum"),
            require_text=True,
        )
        value_col = _find_column_by_name_patterns(
            cols,
            patterns=("value", "result", "amount", "qty", "quantity"),
            require_numeric=True,
            exclude={unit_col} if unit_col else None,
        )
        if not unit_col or not value_col:
            raise ValueError("Could not infer unit/value column pair for unit_mismatch.")
        touched = _run_unit_mismatch(conn, table_name, unit_col, value_col, fraction)
        operations = [
            {
                "strategy": "unit_mismatch",
                "column": unit_col,
                "details": {"value_column": value_col},
                **touched,
            }
        ]
    elif args.strategy == "code_drift":
        code_col = _pick_column(cols, args.column, "text") if args.column else _find_column_by_name_patterns(
            cols,
            patterns=("code", "loinc", "icd", "rxnorm", "cpt"),
            require_text=True,
        )
        if not code_col:
            raise ValueError("Could not infer a code column for code_drift.")
        system_col = _find_column_by_name_patterns(
            cols,
            patterns=("code_system", "system", "coding_system", "code_uri", "oid"),
            require_text=True,
            exclude={code_col},
        )
        touched = _run_code_drift(conn, table_name, code_col, fraction, system_col or "")
        operations = [
            {
                "strategy": "code_drift",
                "column": code_col,
                "details": {"system_column": system_col or ""},
                **touched,
            }
        ]
    elif args.strategy == "id_fragmentation":
        col = _pick_column(cols, args.column, "text") if args.column else _find_column_by_name_patterns(
            cols,
            patterns=("member", "patient", "person", "subscriber", "mrn", "npi", "id"),
            require_text=True,
        )
        if not col:
            raise ValueError("Could not infer identifier column for id_fragmentation.")
        touched = _run_id_fragmentation(conn, table_name, col, fraction)
        operations = [{"strategy": "id_fragmentation", "column": col, **touched}]
    elif args.strategy == "enum_encoding_drift":
        col = _pick_column(cols, args.column, "text") if args.column else _find_column_by_name_patterns(
            cols,
            patterns=("status", "flag", "result", "gender", "sex", "outcome", "type"),
            require_text=True,
        )
        if not col:
            raise ValueError("Could not infer categorical text column for enum_encoding_drift.")
        touched = _run_enum_encoding_drift(conn, table_name, col, fraction)
        operations = [{"strategy": "enum_encoding_drift", "column": col, **touched}]

    report_table = Table(title=f"Corruption Summary: {table_name}")
    report_table.add_column("Strategy")
    report_table.add_column("Column")
    report_table.add_column("Rows changed", justify="right")

    for op in operations:
        report_table.add_row(op["strategy"], op["column"], str(op["rows"]))

    console.print(report_table)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    rows_after = _row_count(conn, table_name)
    log_path = settings.log_dir / f"lab-corruption-{timestamp}.md"
    ground_truth_path = _write_ground_truth_artifact(
        table_name=table_name,
        timestamp=timestamp,
        strategy=args.strategy,
        fraction=fraction,
        seed=args.seed,
        truncate_to=args.truncate_to,
        rows_before=rows_before,
        rows_after=rows_after,
        operations=operations,
    )
    lines = [f"# Local Corruption Report ({timestamp})", "", f"Table: `{table_name}`", ""]
    for op in operations:
        details = op.get("details", {})
        details_suffix = f" details={json.dumps(details, ensure_ascii=True)}" if details else ""
        lines.append(
            f"- {op['strategy']} on `{op['column']}` -> {op['rows']} rows "
            f"(row_ids captured: {len(op.get('row_ids', []))}){details_suffix}"
        )
    lines.append("")
    lines.append(f"- Ground truth JSON: `{ground_truth_path}`")
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    console.print(f"Saved corruption log: {log_path}")
    console.print(f"Saved ground truth: {ground_truth_path}")


def _probe_command(conn: sqlite3.Connection, args: argparse.Namespace) -> None:
    table_name = args.table
    if not _table_exists(conn, table_name):
        raise ValueError(f"Table not found: {table_name}")

    q_table = _quote_ident(table_name)
    columns = _table_columns(conn, table_name)
    findings: list[dict[str, Any]] = []

    for col in columns:
        col_name = col["name"]
        q_col = _quote_ident(col_name)

        null_count = int(
            conn.execute(
                f"SELECT COUNT(*) AS c FROM {q_table} WHERE {q_col} IS NULL"
            ).fetchone()["c"]
        )
        if null_count > 0:
            findings.append(
                {
                    "check": "null_values",
                    "column": col_name,
                    "issues": null_count,
                }
            )

        if "CHAR" in col["type"] or "TEXT" in col["type"]:
            short_count = int(
                conn.execute(
                    f"""
                    SELECT COUNT(*) AS c
                    FROM {q_table}
                    WHERE {q_col} IS NOT NULL AND LENGTH(TRIM({q_col})) <= ?
                    """,
                    (args.short_len_threshold,),
                ).fetchone()["c"]
            )
            if short_count > 0:
                findings.append(
                    {
                        "check": f"short_text_len<={args.short_len_threshold}",
                        "column": col_name,
                        "issues": short_count,
                    }
                )

        if "INT" in col["type"] or "REAL" in col["type"] or "NUM" in col["type"]:
            stats = conn.execute(
                f"""
                SELECT
                    COALESCE(AVG(ABS(CAST({q_col} AS REAL))), 0.0) AS avg_abs,
                    COALESCE(MAX(ABS(CAST({q_col} AS REAL))), 0.0) AS max_abs
                FROM {q_table}
                WHERE {q_col} IS NOT NULL
                """
            ).fetchone()
            avg_abs = float(stats["avg_abs"])
            max_abs = float(stats["max_abs"])
            if avg_abs > 0.0 and max_abs > (args.numeric_spike_factor * avg_abs):
                findings.append(
                    {
                        "check": f"numeric_spike>{args.numeric_spike_factor}x_avg",
                        "column": col_name,
                        "issues": 1,
                    }
                )

        if any(token in col_name.lower() for token in ("date", "time", "dt", "ts")):
            future_count = int(
                conn.execute(
                    f"""
                    SELECT COUNT(*) AS c
                    FROM {q_table}
                    WHERE {q_col} LIKE '____-__-__%' AND {q_col} >= date('now', '+1 day')
                    """
                ).fetchone()["c"]
            )
            if future_count > 0:
                findings.append(
                    {
                        "check": "future_dates",
                        "column": col_name,
                        "issues": future_count,
                    }
                )

    all_cols = ", ".join(_quote_ident(col["name"]) for col in columns)
    duplicate_count = int(
        conn.execute(
            f"""
            SELECT COALESCE(SUM(c - 1), 0) AS duplicate_rows
            FROM (
                SELECT COUNT(*) AS c
                FROM {q_table}
                GROUP BY {all_cols}
                HAVING COUNT(*) > 1
            ) t
            """
        ).fetchone()["duplicate_rows"]
    )
    if duplicate_count > 0:
        findings.append({"check": "duplicate_rows", "column": "(row)", "issues": duplicate_count})

    report = Table(title=f"Probe Findings: {table_name}")
    report.add_column("Check")
    report.add_column("Column")
    report.add_column("Issue count", justify="right")

    if findings:
        for finding in findings:
            report.add_row(finding["check"], finding["column"], str(finding["issues"]))
        console.print(report)
        console.print(f"Total findings: {len(findings)}")
    else:
        report.add_row("no_issues_detected", "-", "0")
        console.print(report)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    log_path = settings.log_dir / f"lab-probe-{table_name}-{timestamp}.md"
    lines = [
        f"# Probe Report: {table_name}",
        "",
        f"Generated at: {timestamp}",
        "",
        "| Check | Column | Issue count |",
        "|---|---|---:|",
    ]
    if findings:
        for finding in findings:
            lines.append(
                f"| {finding['check']} | {finding['column']} | {int(finding['issues'])} |"
            )
    else:
        lines.append("| no_issues_detected | - | 0 |")

    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    console.print(f"Saved probe report: {log_path}")


def main() -> None:
    args = _parse_args()

    conn, db_path = _connect_sqlite(args.db_url)
    try:
        console.print(f"Using local DB: {db_path}")

        if args.command == "list":
            _render_tables(conn, verbose=args.verbose)
        elif args.command == "ingest":
            _ingest_command(conn, args)
        elif args.command == "corrupt":
            _corrupt_command(conn, args)
        elif args.command == "probe":
            _probe_command(conn, args)
        else:
            raise ValueError(f"Unsupported command: {args.command}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
