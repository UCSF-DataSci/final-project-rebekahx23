"""Google ADK multi-agent graph for data quality scanning."""

from __future__ import annotations

from google.adk.agents import LlmAgent, SequentialAgent
from google.adk.apps import App

from .config import settings
from .db import db_client
from .tools import (
    describe_table_schema,
    finalize_quality_run,
    get_executed_tests,
    list_tables,
    run_data_quality_test,
    sample_table_data,
    start_quality_run,
)

_DIALECT_NAME = db_client.engine.dialect.name.lower()
_DIALECT_SQL_GUIDANCE = (
    """
SQL DIALECT REQUIREMENT:
- Target dialect is SQLite.
- Do NOT use TRY_CAST.
- Prefer SQLite-safe date logic such as `date(col)` and `julianday(col)`.
- For case-insensitive matching use `LOWER(col) LIKE LOWER('%pattern%')` (not ILIKE).
"""
    if _DIALECT_NAME == "sqlite"
    else f"\nSQL DIALECT REQUIREMENT:\n- Target dialect is {_DIALECT_NAME}.\n"
)

profiler_agent = LlmAgent(
    name="dq_profiler",
    description="Collect schema and realistic data shape context.",
    model=settings.model,
    tools=[start_quality_run, list_tables, describe_table_schema, sample_table_data],
    instruction="""
You are the profiling specialist for data quality.

Steps:
1. Call `start_quality_run` once at the beginning.
2. Call `list_tables` to understand candidate tables.
3. Pick high-value tables for checks (or honor the user-provided table list in the prompt).
4. For each selected table, call `describe_table_schema`.
5. For each selected table, call `sample_table_data` using multiple batches.
6. Return a concise profile summary with likely risk areas.

Be precise about column names and observed value patterns.
""",
    output_key="profile_summary",
)

planner_agent = LlmAgent(
    name="dq_planner",
    description="Convert profile observations into SQL test cases.",
    model=settings.model,
    instruction=f"""
You are the planner. Use `{{profile_summary}}` to design data-quality tests.
{_DIALECT_SQL_GUIDANCE}

Plan up to {settings.max_planned_tests} high-signal tests

For each test, output:
- test_name
- table_name
- severity (low/medium/high/critical)
- rationale
- sql (read-only query that returns violating rows)

Only output executable read-only SQL.
""",
    output_key="planned_tests",
)

executor_agent = LlmAgent(
    name="dq_executor",
    description="Execute planned SQL checks and collect evidence.",
    model=settings.model,
    tools=[run_data_quality_test, get_executed_tests],
    instruction="""
You are the execution specialist.

Input is `{planned_tests}`. For each test case:
1. Call `run_data_quality_test` with the exact SQL.
2. Keep SQL read-only.
3. Continue across all planned tests, even if some fail.
4. After execution, call `get_executed_tests` and summarize failures by severity.

Return a compact execution summary with counts and highest-risk findings.
""",
    output_key="execution_summary",
)

supervisor_agent = LlmAgent(
    name="dq_supervisor",
    description="Produce final report and recommended follow-ups.",
    model=settings.model,
    tools=[get_executed_tests, finalize_quality_run],
    instruction="""
You are the supervisor.

Use `{execution_summary}` and `get_executed_tests` to produce a final report with:
- Overall verdict (green/yellow/red)
- Top critical/high issues
- Test coverage notes
- Suggested production guardrails (SQL checks to schedule each load)

After generating the report text, call `finalize_quality_run` to persist the summary.
""",
    output_key="final_report",
)

root_agent = SequentialAgent(
    name="data_quality_root",
    description="End-to-end multi-agent data quality pipeline.",
    sub_agents=[profiler_agent, planner_agent, executor_agent, supervisor_agent],
)

app = App(
    name="data_quality_app",
    root_agent=root_agent,
)
