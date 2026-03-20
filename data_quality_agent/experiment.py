"""Budget-sweep runner for profiling experiments."""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import text

from .config import settings
from .db import DatabaseClient
from .log_store import load_events


@dataclass
class RunRecord:
    run_id: str
    model: str
    sample_pct: float
    sample_size: int
    batches: int
    token_cap: int
    seed: int
    run_seconds: float
    run_exit_code: int
    eval_exit_code: int
    status: str
    precision: float
    recall: float
    f1: float
    tp: int
    fp: int
    fn: int
    prompt_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float | None
    error_message: str


def _parse_float_list(raw_value: str) -> list[float]:
    values = [item.strip() for item in raw_value.split(",") if item.strip()]
    if not values:
        raise ValueError("Expected at least one float value.")
    return [float(value) for value in values]


def _parse_int_list(raw_value: str) -> list[int]:
    values = [item.strip() for item in raw_value.split(",") if item.strip()]
    if not values:
        raise ValueError("Expected at least one integer value.")
    return [int(value) for value in values]


def _parse_str_list(raw_value: str) -> list[str]:
    values = [item.strip() for item in raw_value.split(",") if item.strip()]
    if not values:
        raise ValueError("Expected at least one string value.")
    return values


def _table_row_count(db_url: str, table_name: str) -> int:
    db_client = DatabaseClient(db_url)
    schema_name, simple_table_name = db_client._split_table_name(table_name)  # noqa: SLF001
    if not db_client._has_table(schema_name, simple_table_name):  # noqa: SLF001
        raise ValueError(f"Table not found: {table_name}")
    qualified = db_client._quote_table(schema_name, simple_table_name)  # noqa: SLF001
    with db_client.engine.connect() as conn:
        row = conn.execute(text(f"SELECT COUNT(*) AS c FROM {qualified}")).first()
    return int(row._mapping["c"]) if row else 0


def _table_row_counts(db_url: str, tables: list[str]) -> dict[str, int]:
    return {table: _table_row_count(db_url, table) for table in tables}


def _run_subprocess(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
) -> tuple[int, float, str, str]:
    start = time.monotonic()
    proc = subprocess.run(
        command,
        cwd=str(cwd),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    elapsed = time.monotonic() - start
    return proc.returncode, elapsed, proc.stdout, proc.stderr


def _validate_runner_python(python_executable: str, cwd: Path) -> tuple[bool, str]:
    probe = subprocess.run(
        [python_executable, "-c", "import google.adk"],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
    )
    if probe.returncode == 0:
        return True, ""
    message = (probe.stderr or probe.stdout or "").strip()
    return False, message[:400]


def _read_eval_metrics(run_id: str) -> tuple[float, float, float, int, int, int]:
    eval_path = settings.log_dir / f"{run_id}-evaluation.json"
    payload = json.loads(eval_path.read_text(encoding="utf-8"))
    micro = payload.get("micro_average", {})
    return (
        float(micro.get("precision", 0.0)),
        float(micro.get("recall", 0.0)),
        float(micro.get("f1", 0.0)),
        int(micro.get("tp", 0)),
        int(micro.get("fp", 0)),
        int(micro.get("fn", 0)),
    )


def _read_usage_tokens(run_id: str) -> tuple[int, int, int]:
    events = load_events(run_id)
    usage_events = [event for event in events if event.get("event") == "run_usage"]
    if not usage_events:
        return 0, 0, 0
    usage = usage_events[-1]
    return (
        int(usage.get("prompt_tokens", 0)),
        int(usage.get("candidates_tokens", 0)),
        int(usage.get("total_tokens", 0)),
    )


def _estimated_cost(
    *,
    prompt_tokens: int,
    output_tokens: int,
    input_cost_per_1m: float,
    output_cost_per_1m: float,
) -> float | None:
    if input_cost_per_1m <= 0.0 and output_cost_per_1m <= 0.0:
        return None
    return (prompt_tokens / 1_000_000.0) * input_cost_per_1m + (
        output_tokens / 1_000_000.0
    ) * output_cost_per_1m


def _aggregate(records: list[RunRecord]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, float, int, int], list[RunRecord]] = defaultdict(list)
    for record in records:
        key = (record.model, record.sample_pct, record.batches, record.token_cap)
        grouped[key].append(record)

    rows: list[dict[str, Any]] = []
    for (model, sample_pct, batches, token_cap), runs in sorted(
        grouped.items(), key=lambda item: (item[0][0], item[0][1], item[0][2], item[0][3])
    ):
        successes = [run for run in runs if run.status == "success"]
        if successes:
            precision_values = [run.precision for run in successes]
            recall_values = [run.recall for run in successes]
            f1_values = [run.f1 for run in successes]
            tokens_values = [run.total_tokens for run in successes]
            seconds_values = [run.run_seconds for run in successes]
            costs_values = [run.estimated_cost_usd for run in successes if run.estimated_cost_usd is not None]
            row = {
                "model": model,
                "sample_pct": sample_pct,
                "batches": batches,
                "token_cap": token_cap,
                "runs_total": len(runs),
                "runs_success": len(successes),
                "precision_mean": statistics.mean(precision_values),
                "recall_mean": statistics.mean(recall_values),
                "f1_mean": statistics.mean(f1_values),
                "precision_std": statistics.pstdev(precision_values) if len(precision_values) > 1 else 0.0,
                "recall_std": statistics.pstdev(recall_values) if len(recall_values) > 1 else 0.0,
                "f1_std": statistics.pstdev(f1_values) if len(f1_values) > 1 else 0.0,
                "tokens_mean": statistics.mean(tokens_values),
                "seconds_mean": statistics.mean(seconds_values),
                "cost_mean_usd": statistics.mean(costs_values) if costs_values else None,
            }
        else:
            row = {
                "model": model,
                "sample_pct": sample_pct,
                "batches": batches,
                "token_cap": token_cap,
                "runs_total": len(runs),
                "runs_success": 0,
                "precision_mean": 0.0,
                "recall_mean": 0.0,
                "f1_mean": 0.0,
                "precision_std": 0.0,
                "recall_std": 0.0,
                "f1_std": 0.0,
                "tokens_mean": 0.0,
                "seconds_mean": 0.0,
                "cost_mean_usd": None,
            }
        rows.append(row)
    return rows


def _best_row(
    aggregated_rows: list[dict[str, Any]],
    *,
    sort_key: str,
) -> dict[str, Any] | None:
    candidates = [row for row in aggregated_rows if row.get("runs_success", 0) > 0]
    if not candidates:
        return None
    return max(candidates, key=lambda row: float(row.get(sort_key, 0.0)))


def _best_row_by_cost_efficiency(aggregated_rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    candidates = [
        row
        for row in aggregated_rows
        if row.get("runs_success", 0) > 0 and row.get("cost_mean_usd") not in (None, 0.0)
    ]
    if not candidates:
        return None
    return max(candidates, key=lambda row: float(row.get("f1_mean", 0.0)) / float(row["cost_mean_usd"]))


def _write_artifacts(
    *,
    records: list[RunRecord],
    aggregated_rows: list[dict[str, Any]],
    args: argparse.Namespace,
) -> tuple[Path, Path]:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    best_f1 = _best_row(aggregated_rows, sort_key="f1_mean")
    best_recall = _best_row(aggregated_rows, sort_key="recall_mean")
    best_efficiency = _best_row_by_cost_efficiency(aggregated_rows)

    payload = {
        "artifact_type": "dq_experiment",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "settings": {
            "tables": args.tables,
            "table_row_counts": args.table_row_counts,
            "reference_table_rows": args.reference_table_rows,
            "ground_truth": args.ground_truth,
            "baseline_db_url": args.baseline_db_url,
            "models": args.models,
            "sample_pcts": args.sample_pcts,
            "batches": args.batches,
            "token_caps": args.token_caps,
            "seeds": args.seeds,
            "max_sample_size": args.max_sample_size,
            "input_cost_per_1m": args.input_cost_per_1m,
            "output_cost_per_1m": args.output_cost_per_1m,
            "db_url": args.db_url,
        },
        "runs": [record.__dict__ for record in records],
        "aggregated": aggregated_rows,
        "best_configs": {
            "best_f1": best_f1,
            "best_recall": best_recall,
            "best_f1_per_cost": best_efficiency,
        },
    }

    json_path = settings.log_dir / f"experiment-{timestamp}.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        f"# Experiment Summary ({timestamp})",
        "",
        "## Best Configs",
    ]
    if best_f1:
        lines.append(
            f"- Best F1: model={best_f1['model']}, sample_pct={best_f1['sample_pct']:.3f}, "
            f"batches={best_f1['batches']}, token_cap={best_f1['token_cap']}, "
            f"f1={best_f1['f1_mean']:.4f}"
        )
    else:
        lines.append("- Best F1: n/a")
    if best_recall:
        lines.append(
            f"- Best recall: model={best_recall['model']}, sample_pct={best_recall['sample_pct']:.3f}, "
            f"batches={best_recall['batches']}, token_cap={best_recall['token_cap']}, "
            f"recall={best_recall['recall_mean']:.4f}"
        )
    else:
        lines.append("- Best recall: n/a")
    if best_efficiency:
        lines.append(
            f"- Best F1 per cost: model={best_efficiency['model']}, "
            f"sample_pct={best_efficiency['sample_pct']:.3f}, batches={best_efficiency['batches']}, "
            f"token_cap={best_efficiency['token_cap']}"
        )
    else:
        lines.append("- Best F1 per cost: n/a (provide non-zero token pricing to enable)")
    lines.extend(
        [
            "",
            "## Aggregated Results",
            "| Model | Sample % | Batches | Token Cap | Runs | Precision(mean) | Recall(mean) | F1(mean) | Tokens(mean) | Cost(mean USD) | Sec(mean) |",
            "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in aggregated_rows:
        cost_text = f"{row['cost_mean_usd']:.6f}" if row["cost_mean_usd"] is not None else "n/a"
        lines.append(
            f"| {row['model']} | {row['sample_pct']:.3f} | {row['batches']} | {row['token_cap']} | "
            f"{row['runs_success']}/{row['runs_total']} | "
            f"{row['precision_mean']:.4f} | {row['recall_mean']:.4f} | {row['f1_mean']:.4f} | "
            f"{row['tokens_mean']:.1f} | {cost_text} | {row['seconds_mean']:.1f} |"
        )

    lines.extend(
        [
            "",
            "## Per-Run Results",
            "| Run ID | Status | Model | Sample % | Sample Size | Batches | Token Cap | Seed | Precision | Recall | F1 | Total Tokens | Cost USD | Seconds | Error |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|",
        ]
    )
    for record in records:
        cost_text = f"{record.estimated_cost_usd:.6f}" if record.estimated_cost_usd is not None else "n/a"
        error_text = record.error_message.replace("\n", " ").replace("|", "\\|").strip()
        lines.append(
            f"| {record.run_id} | {record.status} | {record.model} | {record.sample_pct:.3f} | "
            f"{record.sample_size} | {record.batches} | {record.token_cap} | {record.seed} | "
            f"{record.precision:.4f} | {record.recall:.4f} | {record.f1:.4f} | "
            f"{record.total_tokens} | {cost_text} | {record.run_seconds:.1f} | {error_text} |"
        )

    md_path = settings.log_dir / f"experiment-{timestamp}.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path, json_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run profiling budget sweeps for dq-run + dq-eval.")
    parser.add_argument("--tables", nargs="+", required=True, help="Tables passed to dq-run")
    parser.add_argument("--ground-truth", required=True, help="Path to lab-ground-truth-*.json")
    parser.add_argument(
        "--baseline-db-url",
        default="",
        help="Optional clean baseline DB URL for delta-based dq-eval scoring",
    )
    parser.add_argument("--sample-pcts", default="0.5,1,2,5", help="Comma-separated sample percentages")
    parser.add_argument("--batches", default="1,2,3", help="Comma-separated sample batch counts")
    parser.add_argument("--token-caps", default="0", help="Comma-separated profiling token caps (0 = unlimited)")
    parser.add_argument("--models", default="gemini-2.5-flash", help="Comma-separated model names")
    parser.add_argument("--seeds", default="1,2,3", help="Comma-separated run seeds (repeat count)")
    parser.add_argument("--max-sample-size", type=int, default=2000, help="Cap computed sample size per run")
    parser.add_argument("--db-url", default=settings.db_url, help="Database URL for row-count and evaluation")
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python executable used to invoke data_quality_agent.run_job and evaluate",
    )
    parser.add_argument("--retry-attempts", type=int, default=5, help="dq-run retry attempts")
    parser.add_argument("--input-cost-per-1m", type=float, default=0.0, help="Estimated USD per 1M input tokens")
    parser.add_argument("--output-cost-per-1m", type=float, default=0.0, help="Estimated USD per 1M output tokens")
    parser.add_argument("--max-runs", type=int, default=0, help="Optional hard cap on number of launched runs")
    parser.add_argument("--dry-run", action="store_true", help="Print planned runs without executing")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    repo_root = Path.cwd()
    ground_truth_path = Path(args.ground_truth).expanduser().resolve()
    if not ground_truth_path.exists():
        raise FileNotFoundError(f"Ground truth file not found: {ground_truth_path}")

    sample_pcts = _parse_float_list(args.sample_pcts)
    batches_list = _parse_int_list(args.batches)
    token_caps = _parse_int_list(args.token_caps)
    models = _parse_str_list(args.models)
    seeds = _parse_int_list(args.seeds)

    if any(sample_pct <= 0 for sample_pct in sample_pcts):
        raise ValueError("All sample percentages must be > 0.")
    if any(batches < 1 for batches in batches_list):
        raise ValueError("All batches values must be >= 1.")
    if any(token_cap < 0 for token_cap in token_caps):
        raise ValueError("All token cap values must be >= 0.")

    table_row_counts = _table_row_counts(args.db_url, args.tables)
    if any(row_count <= 0 for row_count in table_row_counts.values()):
        empty_tables = [table for table, row_count in table_row_counts.items() if row_count <= 0]
        raise ValueError(f"Table(s) have no rows: {', '.join(empty_tables)}")
    reference_rows = max(table_row_counts.values())
    args.table_row_counts = table_row_counts
    args.reference_table_rows = reference_rows

    grid: list[tuple[str, float, int, int, int]] = []
    for model in models:
        for sample_pct in sample_pcts:
            for batches in batches_list:
                for token_cap in token_caps:
                    for seed in seeds:
                        grid.append((model, sample_pct, batches, token_cap, seed))

    if args.max_runs > 0:
        grid = grid[: args.max_runs]

    print(f"Planned runs: {len(grid)}")
    print(f"Reference row count (max across tables): {reference_rows}")
    print(f"Runner python: {args.python}")
    for idx, (model, sample_pct, batches, token_cap, seed) in enumerate(grid, start=1):
        sample_size = max(1, int(round(reference_rows * (sample_pct / 100.0))))
        if args.max_sample_size > 0:
            sample_size = min(sample_size, args.max_sample_size)
        print(
            f"{idx:03d}. model={model} sample_pct={sample_pct:.3f} sample_size={sample_size} "
            f"batches={batches} token_cap={token_cap} seed={seed}"
        )

    if args.dry_run:
        return

    python_ok, python_error = _validate_runner_python(args.python, repo_root)
    if not python_ok:
        details = f" ({python_error})" if python_error else ""
        raise RuntimeError(
            "Selected runner python cannot import google.adk. "
            f"Use --python with your working dq-run interpreter{details}"
        )

    records: list[RunRecord] = []
    timestamp_base = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    for run_index, (model, sample_pct, batches, token_cap, seed) in enumerate(grid, start=1):
        sample_size = max(1, int(round(reference_rows * (sample_pct / 100.0))))
        if args.max_sample_size > 0:
            sample_size = min(sample_size, args.max_sample_size)

        run_id = f"dq-exp-{timestamp_base}-{run_index:03d}"
        env = os.environ.copy()
        env["DQ_MODEL"] = model
        env["DQ_SAMPLE_SIZE"] = str(sample_size)
        env["DQ_SAMPLE_BATCHES"] = str(batches)
        env["DQ_PROFILE_TOKEN_CAP"] = str(max(0, token_cap))

        run_command = [
            args.python,
            "-m",
            "data_quality_agent.run_job",
            "--run-id",
            run_id,
            "--tables",
            *args.tables,
            "--retry-attempts",
            str(args.retry_attempts),
            "--prompt",
            (
                "Run a proactive data quality scan with concise planning. "
                f"Experiment seed marker: {seed}."
            ),
        ]

        run_exit, run_seconds, run_stdout, run_stderr = _run_subprocess(
            run_command,
            cwd=repo_root,
            env=env,
        )

        eval_exit = -1
        precision = recall = f1 = 0.0
        tp = fp = fn = 0
        prompt_tokens = output_tokens = total_tokens = 0
        estimated_cost = None
        status = "run_failed"
        error_message = ""

        if run_exit == 0:
            eval_command = [
                args.python,
                "-m",
                "data_quality_agent.evaluate",
                "--run-id",
                run_id,
                "--ground-truth",
                str(ground_truth_path),
                "--db-url",
                args.db_url,
            ]
            if args.baseline_db_url:
                eval_command.extend(["--baseline-db-url", args.baseline_db_url])
            eval_exit, _, eval_stdout, eval_stderr = _run_subprocess(
                eval_command,
                cwd=repo_root,
                env=env,
            )
            if eval_exit == 0:
                precision, recall, f1, tp, fp, fn = _read_eval_metrics(run_id)
                prompt_tokens, output_tokens, total_tokens = _read_usage_tokens(run_id)
                estimated_cost = _estimated_cost(
                    prompt_tokens=prompt_tokens,
                    output_tokens=output_tokens,
                    input_cost_per_1m=args.input_cost_per_1m,
                    output_cost_per_1m=args.output_cost_per_1m,
                )
                status = "success"
                error_message = ""
            else:
                status = "eval_failed"
                error_message = (eval_stderr or eval_stdout or "").strip()[:1200]
        else:
            status = "run_failed"
            error_message = (run_stderr or run_stdout or "").strip()[:1200]

        records.append(
            RunRecord(
                run_id=run_id,
                model=model,
                sample_pct=sample_pct,
                sample_size=sample_size,
                batches=batches,
                token_cap=max(0, token_cap),
                seed=seed,
                run_seconds=run_seconds,
                run_exit_code=run_exit,
                eval_exit_code=eval_exit,
                status=status,
                precision=precision,
                recall=recall,
                f1=f1,
                tp=tp,
                fp=fp,
                fn=fn,
                prompt_tokens=prompt_tokens,
                output_tokens=output_tokens,
                total_tokens=total_tokens,
                estimated_cost_usd=estimated_cost,
                error_message=error_message,
            )
        )
        print(
            f"[{run_index}/{len(grid)}] {run_id} status={status} "
            f"f1={f1:.4f} tokens={total_tokens}"
        )

    aggregated_rows = _aggregate(records)
    md_path, json_path = _write_artifacts(records=records, aggregated_rows=aggregated_rows, args=args)
    print(f"Saved experiment summary: {md_path}")
    print(f"Saved experiment JSON: {json_path}")


if __name__ == "__main__":
    main()
