"""Database helpers with strict read-only SQL guardrails."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

from .config import settings

_ALLOWED_TABLE_NAME = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*(\.[A-Za-z_][A-Za-z0-9_]*)?$")
_FORBIDDEN_SQL = re.compile(
    r"\b(insert|update|delete|drop|alter|create|truncate|merge|grant|revoke|call|copy|vacuum|replace)\b",
    re.IGNORECASE,
)


@dataclass
class QueryResult:
    rows: list[dict[str, Any]]
    issue_count: int
    truncated: bool


class DatabaseClient:
    def __init__(self, db_url: str):
        self.engine: Engine = create_engine(db_url, future=True)

    def _split_table_name(self, table_name: str) -> tuple[str | None, str]:
        if not _ALLOWED_TABLE_NAME.match(table_name):
            raise ValueError(f"Invalid table name: {table_name}")

        if "." not in table_name:
            return None, table_name

        schema_name, simple_table_name = table_name.split(".", 1)
        return schema_name, simple_table_name

    def _quote_table(self, schema_name: str | None, table_name: str) -> str:
        preparer = self.engine.dialect.identifier_preparer
        quoted_table = preparer.quote(table_name)
        normalized_schema = self._normalize_schema_name(schema_name)
        if normalized_schema:
            return f"{preparer.quote(normalized_schema)}.{quoted_table}"
        return quoted_table

    def _has_table(self, schema_name: str | None, table_name: str) -> bool:
        schema_name = self._normalize_schema_name(schema_name)
        inspector = inspect(self.engine)
        return inspector.has_table(table_name, schema=schema_name)

    def _normalize_schema_name(self, schema_name: str | None) -> str | None:
        if schema_name is None:
            return None
        normalized = schema_name.strip()
        if not normalized:
            return None

        lowered = normalized.lower()
        dialect = self.engine.dialect.name.lower()
        if dialect == "sqlite":
            if lowered in {"default", "public"}:
                return None
            return normalized

        return normalized

    def _normalize_sql(self, sql: str) -> str:
        normalized = sql.strip()
        if not normalized:
            raise ValueError("SQL cannot be empty.")

        if _FORBIDDEN_SQL.search(normalized):
            raise ValueError("Only read-only SQL is allowed.")

        if ";" in normalized.rstrip(";"):
            raise ValueError("Only one SQL statement is allowed.")

        first_token = normalized.split(maxsplit=1)[0].lower()
        if first_token not in {"select", "with", "explain"}:
            raise ValueError("Query must start with SELECT, WITH, or EXPLAIN.")

        return normalized.rstrip(";")

    def _adapt_sql_for_dialect(self, sql: str) -> str:
        dialect = self.engine.dialect.name.lower()
        adapted = sql

        # SQLite does not support TRY_CAST; use CAST equivalent.
        if dialect == "sqlite":
            adapted = re.sub(r"\bTRY_CAST\b", "CAST", adapted, flags=re.IGNORECASE)
            adapted = re.sub(r"\bILIKE\b", "LIKE", adapted, flags=re.IGNORECASE)

        return adapted

    def list_tables(self, schema_name: str | None = None) -> list[str]:
        schema_name = self._normalize_schema_name(schema_name)
        inspector = inspect(self.engine)
        raw_tables = inspector.get_table_names(schema=schema_name)
        if schema_name:
            return [f"{schema_name}.{table_name}" for table_name in raw_tables]
        return raw_tables

    def describe_table(self, table_name: str) -> dict[str, Any]:
        schema_name, simple_table_name = self._split_table_name(table_name)
        schema_name = self._normalize_schema_name(schema_name)
        if not self._has_table(schema_name, simple_table_name):
            raise ValueError(f"Table not found: {table_name}")

        inspector = inspect(self.engine)
        columns = inspector.get_columns(simple_table_name, schema=schema_name)
        primary_key = inspector.get_pk_constraint(simple_table_name, schema=schema_name)

        return {
            "table": table_name,
            "columns": [
                {
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": bool(column.get("nullable", True)),
                    "default": column.get("default"),
                }
                for column in columns
            ],
            "primary_key": primary_key.get("constrained_columns", []),
        }

    def sample_rows(self, table_name: str, sample_size: int, batches: int) -> list[list[dict[str, Any]]]:
        schema_name, simple_table_name = self._split_table_name(table_name)
        schema_name = self._normalize_schema_name(schema_name)
        if not self._has_table(schema_name, simple_table_name):
            raise ValueError(f"Table not found: {table_name}")

        if sample_size < 1 or batches < 1:
            raise ValueError("sample_size and batches must be >= 1")

        dialect_name = self.engine.dialect.name.lower()
        random_fn = "RANDOM()" if dialect_name != "mysql" else "RAND()"
        qualified_table = self._quote_table(schema_name, simple_table_name)

        sql = text(f"SELECT * FROM {qualified_table} ORDER BY {random_fn} LIMIT :limit")
        sampled_batches: list[list[dict[str, Any]]] = []

        with self.engine.connect() as conn:
            for _ in range(batches):
                result = conn.execute(sql, {"limit": sample_size})
                sampled_batches.append([dict(row._mapping) for row in result])

        return sampled_batches

    def execute_read_only_query(self, sql: str, row_limit: int) -> QueryResult:
        normalized = self._normalize_sql(sql)
        normalized = self._adapt_sql_for_dialect(normalized)
        selected_limit = max(1, row_limit)
        count_sql = text(
            f"SELECT COUNT(*) AS total_issue_count FROM ({normalized}) AS dq_count_subquery"
        )
        preview_sql = text(
            f"SELECT * FROM ({normalized}) AS dq_preview_subquery LIMIT :_limit"
        )

        with self.engine.connect() as conn:
            count_row = conn.execute(count_sql).first()
            issue_count = int(count_row._mapping["total_issue_count"]) if count_row else 0
            result = conn.execute(preview_sql, {"_limit": selected_limit})
            rows = [dict(row._mapping) for row in result]

        truncated = issue_count > selected_limit

        return QueryResult(rows=rows, issue_count=issue_count, truncated=truncated)


db_client = DatabaseClient(settings.db_url)
