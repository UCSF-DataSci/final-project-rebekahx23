"""One-shot runner for scheduled data quality jobs."""

from __future__ import annotations

import argparse
import asyncio
import html
import io
import json
import random
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from .config import settings
from .log_store import append_event, current_run_id, load_events, save_text_report, set_run_id

console = Console(record=True)


def _severity_rank(severity: str) -> int:
    order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
    return order.get(severity.lower(), 0)


def _md_cell(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _risk_sorted_tests(tests: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        tests,
        key=lambda test: (
            -_severity_rank(str(test.get("severity", "medium"))),
            -int(test.get("issue_count", 0)),
            str(test.get("table", "")),
            str(test.get("test_name", "")),
        ),
    )


def _overall_verdict(tests: list[dict[str, Any]]) -> str:
    problem_tests = [test for test in tests if test.get("status") in {"fail", "error"}]
    if not problem_tests:
        return "green"

    if any(test.get("status") == "error" for test in problem_tests):
        return "red"

    if any(_severity_rank(str(test.get("severity", ""))) >= 3 for test in problem_tests):
        return "red"

    return "yellow"


def _build_prompt(user_prompt: str, tables: list[str]) -> str:
    if user_prompt:
        return user_prompt

    table_hint = ", ".join(tables) if tables else "all relevant tables"
    return (
        "Run a proactive data quality scan. "
        f"Target tables: {table_hint}. "
        "Profile schema and random samples, plan SQL checks, execute read-only tests, "
        "and produce a final risk summary with recommended recurring guardrails."
    )


def _extract_tests(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [event for event in events if event.get("event") == "test_executed"]


def _render_test_table(tests: list[dict[str, Any]]) -> None:
    table = Table(title="Data Quality Test Results")
    table.add_column("Severity", style="bold")
    table.add_column("Status")
    table.add_column("Table")
    table.add_column("Test")
    table.add_column("Issues", justify="right")
    table.add_column("Truncated")

    for test in tests:
        severity = str(test.get("severity", "medium")).lower()
        sev_style = {
            "critical": "bold red",
            "high": "red",
            "medium": "yellow",
            "low": "green",
        }.get(severity, "white")
        status = str(test.get("status", "unknown")).lower()
        status_style = {"fail": "bold red", "pass": "green", "error": "bold yellow"}.get(
            status, "white"
        )

        table.add_row(
            f"[{sev_style}]{severity.upper()}[/]",
            f"[{status_style}]{status.upper()}[/]",
            str(test.get("table", "")),
            str(test.get("test_name", "")),
            str(test.get("issue_count", 0)),
            "yes" if test.get("truncated") else "no",
        )

    console.print(table)


def _build_report_markdown(
    run_id: str,
    prompt: str,
    response_text: str,
    tests: list[dict[str, Any]],
) -> str:
    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    verdict = _overall_verdict(tests)
    failed_tests = [test for test in tests if test.get("status") == "fail"]
    passed_tests = [test for test in tests if test.get("status") == "pass"]
    errored_tests = [test for test in tests if test.get("status") == "error"]

    severity_counter = Counter(str(test.get("severity", "unknown")).lower() for test in tests)
    top_findings = _risk_sorted_tests(failed_tests + errored_tests)[:12]

    lines: list[str] = [
        f"# Data Quality Report - {run_id}",
        "",
        f"Generated at: {generated_at}",
        "",
        "## Executive Summary",
        f"- Overall verdict: **{verdict.upper()}**",
        f"- Total tests executed: **{len(tests)}**",
        f"- Passed: **{len(passed_tests)}**",
        f"- Failed: **{len(failed_tests)}**",
        f"- Errors: **{len(errored_tests)}**",
        "",
        "## Run Metadata",
        f"- Database: `{settings.db_url}`",
        f"- Prompt: `{_md_cell(prompt)}`",
        f"- Event log: `runs/{run_id}.jsonl`",
        "",
        "## Coverage Breakdown",
        "| Severity | Count |",
        "|---|---:|",
        f"| Critical | {severity_counter.get('critical', 0)} |",
        f"| High | {severity_counter.get('high', 0)} |",
        f"| Medium | {severity_counter.get('medium', 0)} |",
        f"| Low | {severity_counter.get('low', 0)} |",
        "",
    ]

    if top_findings:
        lines.extend(
            [
                "## Top Findings",
                "| Severity | Status | Table | Test | Issue Count |",
                "|---|---|---|---|---:|",
            ]
        )
        for finding in top_findings:
            lines.append(
                f"| {str(finding.get('severity', '')).upper()} | "
                f"{str(finding.get('status', '')).upper()} | "
                f"{_md_cell(finding.get('table', ''))} | "
                f"{_md_cell(finding.get('test_name', ''))} | "
                f"{int(finding.get('issue_count', 0))} |"
            )
        lines.append("")

        lines.append("## Detailed Findings")
        for idx, finding in enumerate(top_findings, start=1):
            severity = str(finding.get("severity", "medium")).upper()
            status = str(finding.get("status", "unknown")).upper()
            table_name = _md_cell(finding.get("table", ""))
            test_name = _md_cell(finding.get("test_name", ""))
            rationale = _md_cell(finding.get("rationale", "No rationale recorded."))
            issue_count = int(finding.get("issue_count", 0))
            truncated = "yes" if finding.get("truncated") else "no"

            lines.append(f"### {idx}. [{severity}/{status}] {test_name} ({table_name})")
            lines.append(f"- Why this matters: {rationale}")
            lines.append(f"- Issue count: **{issue_count}**")
            lines.append(f"- Output truncated: **{truncated}**")

            error_message = str(finding.get("error_message", "")).strip()
            if error_message:
                lines.append(f"- Execution error: `{_md_cell(error_message)}`")

            sql_text = str(finding.get("sql", "")).strip()
            if sql_text:
                lines.append("")
                lines.append("```sql")
                lines.append(sql_text)
                lines.append("```")

            sample_rows = finding.get("sample_rows", [])
            if isinstance(sample_rows, list) and sample_rows:
                preview_rows = sample_rows[:3]
                lines.append("")
                lines.append("Example rows:")
                lines.append("```json")
                lines.append(json.dumps(preview_rows, indent=2, default=str))
                lines.append("```")
            lines.append("")
    else:
        lines.append("## Findings")
        lines.append("No failing or errored tests were recorded in this run.")
        lines.append("")

    if response_text.strip():
        lines.append("## Supervisor Narrative")
        lines.append(response_text.strip())
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _extract_text_response(raw_response: Any) -> str:
    if isinstance(raw_response, str):
        return raw_response
    if raw_response is None:
        return ""

    for attribute in ("text", "output_text", "response"):
        value = getattr(raw_response, attribute, None)
        if isinstance(value, str) and value.strip():
            return value

    return str(raw_response)


def _iter_events(raw_response: Any) -> list[Any]:
    if raw_response is None:
        return []
    if isinstance(raw_response, (list, tuple)):
        return list(raw_response)
    return []


def _extract_usage_totals(raw_response: Any) -> dict[str, int]:
    totals = {
        "prompt_tokens": 0,
        "candidates_tokens": 0,
        "thoughts_tokens": 0,
        "total_tokens": 0,
        "events_with_usage": 0,
    }

    for event in _iter_events(raw_response):
        usage = getattr(event, "usage_metadata", None)
        if usage is None:
            continue

        totals["events_with_usage"] += 1
        totals["prompt_tokens"] += int(getattr(usage, "prompt_token_count", 0) or 0)
        totals["candidates_tokens"] += int(getattr(usage, "candidates_token_count", 0) or 0)
        totals["thoughts_tokens"] += int(getattr(usage, "thoughts_token_count", 0) or 0)
        totals["total_tokens"] += int(getattr(usage, "total_token_count", 0) or 0)

    return totals


def _extract_supervisor_summary(events: list[dict[str, Any]]) -> str:
    for event in reversed(events):
        if event.get("event") != "run_completed":
            continue
        summary = event.get("summary")
        if isinstance(summary, str) and summary.strip():
            return summary.strip()
    return ""


def _looks_like_debug_dump(text: str) -> bool:
    tokens = ["Event(model_version", "state_delta=", "invocation_id=", "FunctionCall("]
    return sum(token in text for token in tokens) >= 2


def _select_narrative_text(events: list[dict[str, Any]], response_text: str) -> str:
    summary = _extract_supervisor_summary(events)
    if summary:
        return summary

    cleaned = (response_text or "").strip()
    if not cleaned:
        return ""

    if _looks_like_debug_dump(cleaned):
        match = re.search(r"state_delta=\{.*?'final_report':\s*'(.+?)'.*?\}", cleaned, flags=re.S)
        if match:
            return match.group(1).replace("\\n", "\n").replace("\\'", "'").strip()
        return "Supervisor narrative was not available as plain text. See JSONL event logs for details."

    return cleaned


def _render_markdown_to_html(markdown_text: str) -> str:
    try:
        import markdown as markdown_lib
    except ModuleNotFoundError:
        html_console = Console(record=True, width=120, file=io.StringIO())
        html_console.print(Markdown(markdown_text))
        return html_console.export_html(inline_styles=True, clear=False)

    body = markdown_lib.markdown(
        markdown_text,
        extensions=["fenced_code", "tables", "sane_lists", "nl2br"],
        output_format="html5",
    )
    brand_name = html.escape(settings.report_brand_name.strip() or "Data Quality")
    logo_url = settings.report_logo_url.strip()
    logo_html = (
        f'<img class="brand-logo" src="{html.escape(logo_url)}" alt="{brand_name} logo" />'
        if logo_url
        else '<div class="brand-mark" aria-hidden="true"></div>'
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Data Quality Report</title>
  <style>
    body {{
      margin: 0;
      background: #f6f8fb;
      color: #122030;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    .wrap {{
      max-width: 1100px;
      margin: 32px auto;
      padding: 0 20px;
    }}
    .brand {{
      display: flex;
      align-items: center;
      gap: 14px;
      margin: 0 0 12px 0;
    }}
    .brand-logo {{
      width: 148px;
      height: auto;
      object-fit: contain;
    }}
    .brand-mark {{
      width: 18px;
      height: 48px;
      border-radius: 4px;
      background: linear-gradient(180deg, #052049 0%, #0d3b7a 100%);
    }}
    .brand-name {{
      margin: 0;
      font-size: 18px;
      letter-spacing: 0.02em;
      color: #052049;
      font-weight: 700;
    }}
    .brand-subtitle {{
      margin: 2px 0 0 0;
      font-size: 13px;
      color: #42566f;
    }}
    article {{
      background: #fff;
      border: 1px solid #d8e0ea;
      border-radius: 12px;
      padding: 24px;
      line-height: 1.6;
    }}
    pre {{
      background: #0f1724;
      color: #e5edf7;
      border-radius: 8px;
      padding: 12px;
      overflow-x: auto;
    }}
    code {{
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
      font-size: 0.92em;
    }}
    table {{
      border-collapse: collapse;
      width: 100%;
    }}
    th, td {{
      border: 1px solid #d8e0ea;
      padding: 8px;
      text-align: left;
    }}
    th {{
      background: #f0f4f9;
    }}
  </style>
</head>
<body>
  <div class="wrap">
    <div class="brand">
      {logo_html}
      <div>
        <p class="brand-name">{brand_name}</p>
        <p class="brand-subtitle">Data Quality Report</p>
      </div>
    </div>
    <article>
      {body}
    </article>
  </div>
</body>
</html>
"""


def _save_markdown_html_report(markdown_text: str, run_id: str) -> Path:
    html_content = _render_markdown_to_html(markdown_text)
    report_path = settings.log_dir / f"{run_id}.html"
    report_path.write_text(html_content, encoding="utf-8")
    return report_path


def _save_terminal_snapshot_html(run_id: str) -> Path:
    snapshot_path = settings.log_dir / f"{run_id}-terminal.html"
    snapshot_path.write_text(console.export_html(inline_styles=True, clear=False), encoding="utf-8")
    return snapshot_path


def _update_runs_index() -> Path:
    run_map: dict[str, dict[str, Path]] = {}

    for path in settings.log_dir.iterdir():
        if not path.is_file():
            continue
        name = path.name
        if name == "index.html":
            continue

        run_id = ""
        kind = ""
        if name.startswith("dq-") and name.endswith("-terminal.html"):
            run_id = name[: -len("-terminal.html")]
            kind = "terminal_html"
        elif name.startswith("dq-") and name.endswith(".html"):
            run_id = path.stem
            kind = "report_html"
        elif name.startswith("dq-") and name.endswith(".md"):
            run_id = path.stem
            kind = "report_md"
        elif name.startswith("dq-") and name.endswith(".jsonl"):
            run_id = path.stem
            kind = "events_jsonl"
        else:
            continue

        run_map.setdefault(run_id, {})[kind] = path

    for run_id, assets in run_map.items():
        if "report_html" in assets or "report_md" not in assets:
            continue
        md_text = assets["report_md"].read_text(encoding="utf-8")
        generated_html = _save_markdown_html_report(md_text, run_id)
        assets["report_html"] = generated_html

    rows: list[str] = []
    sorted_runs = sorted(
        run_map.items(),
        key=lambda item: max(path.stat().st_mtime for path in item[1].values()),
        reverse=True,
    )
    for run_id, assets in sorted_runs:
        mtime = datetime.fromtimestamp(
            max(path.stat().st_mtime for path in assets.values()), tz=timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S UTC")

        report_html = assets.get("report_html")
        report_md = assets.get("report_md")
        events_jsonl = assets.get("events_jsonl")
        terminal_html = assets.get("terminal_html")

        report_col = (
            f'<a href="{html.escape(report_html.name)}" target="_blank">report</a>'
            if report_html
            else (
                f'<a href="{html.escape(report_md.name)}" target="_blank">markdown</a>'
                if report_md
                else "-"
            )
        )
        terminal_col = (
            f'<a href="{html.escape(terminal_html.name)}" target="_blank">terminal view</a>'
            if terminal_html
            else "-"
        )
        events_col = (
            f'<a href="{html.escape(events_jsonl.name)}" target="_blank">jsonl</a>'
            if events_jsonl
            else "-"
        )

        rows.append(
            "<tr>"
            f"<td><code>{html.escape(run_id)}</code></td>"
            f"<td>{mtime}</td>"
            f"<td>{report_col}</td>"
            f"<td>{terminal_col}</td>"
            f"<td>{events_col}</td>"
            "</tr>"
        )

    rows_html = "\n".join(rows) if rows else "<tr><td colspan='5'>No reports yet.</td></tr>"
    brand_name = html.escape(settings.report_brand_name.strip() or "Data Quality")
    logo_url = settings.report_logo_url.strip()
    logo_html = (
        f'<img class="brand-logo" src="{html.escape(logo_url)}" alt="{brand_name} logo" />'
        if logo_url
        else '<div class="brand-mark" aria-hidden="true"></div>'
    )

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Data Quality Reports</title>
  <style>
    body {{
      margin: 0;
      padding: 24px;
      background: #f6f8fb;
      color: #122030;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }}
    h1 {{
      margin: 0 0 8px 0;
      font-size: 24px;
    }}
    .header {{
      display: flex;
      align-items: center;
      gap: 14px;
      margin: 0 0 10px 0;
    }}
    .brand-logo {{
      width: 148px;
      height: auto;
      object-fit: contain;
    }}
    .brand-mark {{
      width: 18px;
      height: 48px;
      border-radius: 4px;
      background: linear-gradient(180deg, #052049 0%, #0d3b7a 100%);
    }}
    .brand-title {{
      margin: 0;
      font-size: 22px;
      color: #052049;
      font-weight: 700;
    }}
    .brand-subtitle {{
      margin: 2px 0 0 0;
      font-size: 13px;
      color: #42566f;
    }}
    p {{
      margin: 0 0 18px 0;
      color: #3f5064;
    }}
    .card {{
      background: #ffffff;
      border: 1px solid #d8e0ea;
      border-radius: 12px;
      padding: 16px;
      overflow-x: auto;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      min-width: 680px;
    }}
    th, td {{
      text-align: left;
      padding: 10px 8px;
      border-bottom: 1px solid #ecf0f5;
    }}
    th {{
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: #60758f;
    }}
    a {{
      color: #005fcc;
      text-decoration: none;
    }}
    a:hover {{
      text-decoration: underline;
    }}
    code {{
      background: #f0f4f9;
      border-radius: 4px;
      padding: 2px 6px;
    }}
  </style>
</head>
<body>
  <div class="header">
    {logo_html}
    <div>
      <p class="brand-title">{brand_name}</p>
      <p class="brand-subtitle">Data Quality Reports</p>
    </div>
  </div>
  <p>Open structured report pages, terminal snapshots, and raw event logs from all detected runs.</p>
  <div class="card">
    <table>
      <thead>
        <tr>
          <th>Run ID</th>
          <th>Generated</th>
          <th>Report</th>
          <th>Terminal</th>
          <th>Events</th>
        </tr>
      </thead>
      <tbody>
        {rows_html}
      </tbody>
    </table>
  </div>
</body>
</html>
"""
    index_path = settings.log_dir / "index.html"
    index_path.write_text(page, encoding="utf-8")
    return index_path


def _is_quota_retryable_error(exc: Exception) -> bool:
    text = str(exc)
    return "RESOURCE_EXHAUSTED" in text or ("429" in text and "quota" in text.lower())


def _extract_retry_delay_seconds(exc: Exception) -> float | None:
    text = str(exc)
    patterns = [
        r"Please retry in ([0-9.]+)s",
        r"retryDelay['\"]?\s*:\s*['\"]([0-9.]+)s['\"]",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
    return None


async def run_job(
    prompt: str,
    run_id: str,
    retry_attempts: int,
    retry_base_seconds: float,
    retry_max_seconds: float,
) -> tuple[str, list[dict[str, Any]]]:
    from google.adk.runners import InMemoryRunner
    from .agent import app

    set_run_id(run_id)
    runner = InMemoryRunner(app=app)

    max_attempts = max(1, retry_attempts)
    base_delay = max(0.1, retry_base_seconds)
    cap_delay = max(base_delay, retry_max_seconds)

    raw_response = None
    for attempt in range(1, max_attempts + 1):
        try:
            raw_response = await runner.run_debug(prompt)
            break
        except Exception as exc:
            should_retry = _is_quota_retryable_error(exc) and attempt < max_attempts
            if not should_retry:
                raise

            hinted_delay = _extract_retry_delay_seconds(exc)
            backoff_delay = min(cap_delay, base_delay * (2 ** (attempt - 1)))
            delay = hinted_delay if hinted_delay is not None else backoff_delay
            jitter = random.uniform(0.0, 0.5)
            total_delay = delay + jitter

            console.print(
                f"[yellow]Quota limit hit (attempt {attempt}/{max_attempts}). "
                f"Retrying in {total_delay:.1f}s...[/]"
            )
            await asyncio.sleep(total_delay)

    if raw_response is None:
        raise RuntimeError("No response received from runner after retry attempts.")

    usage_totals = _extract_usage_totals(raw_response)
    if usage_totals["events_with_usage"] > 0:
        append_event(
            {
                "event": "run_usage",
                **usage_totals,
            },
            run_id,
        )

    response_text = _extract_text_response(raw_response)
    events = load_events(run_id)

    return response_text, events


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run a data-quality multi-agent scan.")
    parser.add_argument("--prompt", default="", help="Optional custom prompt for the run")
    parser.add_argument(
        "--tables",
        nargs="*",
        default=[],
        help="Optional list of preferred tables to focus on",
    )
    parser.add_argument("--run-id", default="", help="Optional explicit run ID")
    parser.add_argument(
        "--retry-attempts",
        type=int,
        default=5,
        help="Max attempts when quota/rate-limit errors occur",
    )
    parser.add_argument(
        "--retry-base-seconds",
        type=float,
        default=2.0,
        help="Base backoff delay in seconds for retries",
    )
    parser.add_argument(
        "--retry-max-seconds",
        type=float,
        default=60.0,
        help="Max retry delay in seconds",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    generated_run_id = (
        args.run_id
        if args.run_id
        else f"dq-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"
    )
    prompt = _build_prompt(args.prompt, args.tables)

    response_text, events = asyncio.run(
        run_job(
            prompt=prompt,
            run_id=generated_run_id,
            retry_attempts=args.retry_attempts,
            retry_base_seconds=args.retry_base_seconds,
            retry_max_seconds=args.retry_max_seconds,
        )
    )
    narrative_text = _select_narrative_text(events, response_text)
    tests = _extract_tests(events)
    sorted_tests = _risk_sorted_tests(tests)

    failed = sum(1 for test in tests if test.get("status") == "fail")
    passed = sum(1 for test in tests if test.get("status") == "pass")
    errored = sum(1 for test in tests if test.get("status") == "error")
    verdict = _overall_verdict(tests)

    console.print(
        Panel.fit(
            f"run_id: {current_run_id()}\n"
            f"db_url: {settings.db_url}\n"
            f"verdict: {verdict.upper()}\n"
            f"tests: {len(tests)} (pass={passed}, fail={failed}, error={errored})\n"
            f"log: {settings.log_dir / f'{current_run_id()}.jsonl'}",
            border_style={
                "green": "green",
                "yellow": "yellow",
                "red": "red",
            }.get(verdict, "white"),
        )
    )

    console.print(
        Markdown(
            "\n".join(
                [
                    "## Run Snapshot",
                    f"- Overall verdict: **{verdict.upper()}**",
                    f"- Total tests: **{len(tests)}**",
                    f"- Passed: **{passed}**",
                    f"- Failed: **{failed}**",
                    f"- Errors: **{errored}**",
                ]
            )
        )
    )

    if sorted_tests:
        _render_test_table(sorted_tests)
    else:
        console.print("No test execution events were captured.")

    if narrative_text.strip():
        console.print(Panel(Markdown(narrative_text.strip()), title="Supervisor Narrative"))

    final_report = _build_report_markdown(
        run_id=current_run_id(),
        prompt=prompt,
        response_text=narrative_text,
        tests=sorted_tests,
    )
    report_path_md = save_text_report(final_report, run_id=current_run_id())
    report_path_html = _save_markdown_html_report(final_report, run_id=current_run_id())
    terminal_snapshot_html = _save_terminal_snapshot_html(run_id=current_run_id())
    index_path = _update_runs_index()

    console.print(f"Saved report (markdown): {report_path_md}")
    console.print(f"Saved report (web): {report_path_html}")
    console.print(f"Saved terminal snapshot (web): {terminal_snapshot_html}")
    console.print(f"Reports index: {index_path}")


if __name__ == "__main__":
    main()
