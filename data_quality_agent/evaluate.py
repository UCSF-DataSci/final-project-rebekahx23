"""Evaluation CLI for comparing dq-run findings against corruption ground truth."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.table import Table

from .config import settings
from .db import DatabaseClient
from .log_store import load_events

console = Console()

_KEYWORDS_BY_STRATEGY: dict[str, tuple[str, ...]] = {
    "nullify": ("null", "missing", "not null"),
    "truncate": ("truncate", "length", "short", "format", "regex"),
    "numeric_outlier": ("outlier", "range", "negative", "age", "amount", "zscore"),
    "future_date": ("date", "future", "admission", "discharge", "chronolog", "timestamp"),
    "duplicate_rows": ("duplicate", "unique", "distinct"),
    "temporal_inversion": ("admission", "discharge", "before", "after", "chronolog", "order"),
    "datetime_shift": ("timezone", "offset", "dst", "timestamp", "midnight"),
    "unit_mismatch": ("unit", "ucum", "mg", "kg", "mmol", "conversion"),
    "code_drift": ("code", "coding", "loinc", "icd", "rxnorm", "vocabulary", "system"),
    "id_fragmentation": ("member", "patient", "mrn", "npi", "identifier", "id"),
    "enum_encoding_drift": ("status", "flag", "encoding", "categor", "value set"),
}

_SQL_ALIAS_KEYWORDS = {
    "where",
    "group",
    "order",
    "limit",
    "join",
    "inner",
    "left",
    "right",
    "full",
    "cross",
    "union",
    "intersect",
    "except",
    "having",
}


@dataclass
class CheckEvaluation:
    test_name: str
    table: str
    status: str
    target_scope: str
    evaluation_mode: str
    tp: int
    fp: int
    fn: int
    precision: float
    recall: float
    f1: float
    raw_tp: int
    raw_fp: int
    raw_fn: int
    raw_precision: float
    raw_recall: float
    raw_f1: float
    delta_tp: int
    delta_fp: int
    delta_fn: int
    delta_precision: float
    delta_recall: float
    delta_f1: float
    evaluable: bool
    reason: str
    predicted_count: int
    raw_predicted_count: int
    baseline_predicted_count: int
    delta_predicted_count: int
    truth_count: int
    missed_issue_ids: list[int]


def _safe_div(num: float, den: float) -> float:
    if den == 0:
        return 0.0
    return num / den


def _f1_score(precision: float, recall: float) -> float:
    if precision + recall == 0.0:
        return 0.0
    return 2.0 * precision * recall / (precision + recall)


def _score_predictions(predicted_ids: set[int], truth_ids: set[int]) -> dict[str, Any]:
    tp_ids = predicted_ids & truth_ids
    fp_ids = predicted_ids - truth_ids
    fn_ids = truth_ids - predicted_ids

    tp = len(tp_ids)
    fp = len(fp_ids)
    fn = len(fn_ids)
    precision = _safe_div(tp, tp + fp)
    recall = _safe_div(tp, tp + fn)
    f1 = _f1_score(precision, recall)

    return {
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "fn_ids": fn_ids,
    }


def _micro_average(
    checks: list[CheckEvaluation],
    *,
    tp_attr: str,
    fp_attr: str,
    fn_attr: str,
) -> dict[str, Any]:
    evaluable_checks = [check for check in checks if check.evaluable]
    tp_sum = sum(int(getattr(check, tp_attr)) for check in evaluable_checks)
    fp_sum = sum(int(getattr(check, fp_attr)) for check in evaluable_checks)
    fn_sum = sum(int(getattr(check, fn_attr)) for check in evaluable_checks)
    precision = _safe_div(tp_sum, tp_sum + fp_sum)
    recall = _safe_div(tp_sum, tp_sum + fn_sum)
    f1 = _f1_score(precision, recall)
    return {
        "tp": tp_sum,
        "fp": fp_sum,
        "fn": fn_sum,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "evaluable_checks": len(evaluable_checks),
        "total_checks": len(checks),
    }


def _query_result_label(status: str) -> str:
    lowered = (status or "").lower().strip()
    if lowered == "fail":
        return "issues_found"
    if lowered == "pass":
        return "no_issues_found"
    if lowered == "error":
        return "query_error"
    return lowered or "unknown"


def _detection_outcome(check: CheckEvaluation) -> str:
    if not check.evaluable:
        return "not_evaluable"
    if check.tp > 0 and check.fp == 0 and check.fn == 0:
        return "exact_hit"
    if check.tp > 0 and check.fp == 0 and check.fn > 0:
        return "partial_recall"
    if check.tp == 0 and check.fp == 0 and check.fn > 0:
        return "missed"
    if check.tp == 0 and check.fp > 0 and check.fn == 0:
        return "false_alarm"
    if check.tp > 0 and check.fp > 0 and check.fn == 0:
        return "hit_with_fp"
    if check.tp > 0 and check.fp > 0 and check.fn > 0:
        return "mixed"
    if check.tp == 0 and check.fp == 0 and check.fn == 0:
        return "no_truth_or_no_findings"
    return "mixed"


def _load_ground_truth(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Ground truth file not found: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("artifact_type") != "lab_ground_truth":
        raise ValueError("Ground truth file does not appear to be a lab_ground_truth artifact.")
    return payload


def _truth_sets_by_strategy(ground_truth: dict[str, Any]) -> dict[str, set[int]]:
    grouped: dict[str, set[int]] = {}
    for operation in ground_truth.get("operations", []):
        strategy = str(operation.get("strategy", "")).strip()
        if not strategy:
            continue
        grouped.setdefault(strategy, set()).update(int(v) for v in operation.get("row_ids", []))
    return grouped


def _all_truth_ids(ground_truth: dict[str, Any]) -> set[int]:
    return {int(v) for v in ground_truth.get("unique_corrupted_row_ids", [])}


def _infer_target_strategies(test_name: str, rationale: str, sql: str) -> list[str]:
    blob = f"{test_name} {rationale} {sql}".lower()
    matched: list[str] = []
    for strategy, terms in _KEYWORDS_BY_STRATEGY.items():
        if any(term in blob for term in terms):
            matched.append(strategy)
    return matched


def _build_rowid_sql_for_sqlite(sql: str) -> str | None:
    simplified = " ".join(sql.strip().rstrip(";").split())
    if not simplified.lower().startswith("select "):
        return None

    if re.search(r"\b(join|group\s+by|having|union|intersect|except)\b", simplified, re.IGNORECASE):
        return None

    from_match = re.match(
        r"(?is)^\s*select\s+.+?\s+from\s+([^\s,()]+)(.*)$",
        simplified,
    )
    if not from_match:
        return None

    table_expr = from_match.group(1)
    tail = from_match.group(2) or ""
    alias = ""
    alias_match = re.match(r"(?is)^\s+(?:as\s+)?([A-Za-z_][A-Za-z0-9_]*)\b(.*)$", tail)
    if alias_match:
        candidate = alias_match.group(1).lower()
        if candidate not in _SQL_ALIAS_KEYWORDS:
            alias = alias_match.group(1)
            tail = alias_match.group(2) or ""

    rowid_expr = f"{alias}.rowid" if alias else "rowid"
    from_expr = f"{table_expr} {alias}".strip()
    return f"SELECT {rowid_expr} AS _dq_rowid FROM {from_expr}{tail}"


def _collect_predicted_rowids(
    db_client: DatabaseClient,
    sql: str,
) -> tuple[set[int], bool, str]:
    try:
        normalized = db_client._normalize_sql(sql)  # noqa: SLF001
        adapted = db_client._adapt_sql_for_dialect(normalized)  # noqa: SLF001
    except Exception as exc:
        return set(), False, f"invalid_sql: {exc}"

    dialect = db_client.engine.dialect.name.lower()
    if dialect != "sqlite":
        return set(), False, f"unsupported_dialect_for_rowid_eval: {dialect}"

    rowid_sql = _build_rowid_sql_for_sqlite(adapted)
    if not rowid_sql:
        return set(), False, "unsupported_query_shape_for_rowid_eval"

    try:
        from sqlalchemy import text

        with db_client.engine.connect() as conn:
            result = conn.execute(text(rowid_sql))
            row_ids = {int(row._mapping["_dq_rowid"]) for row in result if row._mapping["_dq_rowid"] is not None}
        return row_ids, True, ""
    except Exception as exc:
        return set(), False, f"rowid_query_failed: {exc}"


def _evaluate_check(
    *,
    event: dict[str, Any],
    db_client: DatabaseClient,
    baseline_db_client: DatabaseClient | None,
    truth_by_strategy: dict[str, set[int]],
    truth_all: set[int],
) -> CheckEvaluation:
    test_name = str(event.get("test_name", ""))
    table_name = str(event.get("table", ""))
    status = str(event.get("status", "unknown"))
    rationale = str(event.get("rationale", ""))
    sql = str(event.get("sql", ""))

    target_strategies = _infer_target_strategies(test_name, rationale, sql)
    if target_strategies:
        truth_ids = set()
        for strategy in target_strategies:
            truth_ids.update(truth_by_strategy.get(strategy, set()))
        target_scope = ",".join(sorted(target_strategies))
    else:
        truth_ids = set(truth_all)
        target_scope = "all_corruptions"

    predicted_ids, evaluable, reason = _collect_predicted_rowids(db_client, sql)
    if not evaluable:
        return CheckEvaluation(
            test_name=test_name,
            table=table_name,
            status=status,
            target_scope=target_scope,
            evaluation_mode="raw",
            tp=0,
            fp=0,
            fn=len(truth_ids),
            precision=0.0,
            recall=0.0,
            f1=0.0,
            raw_tp=0,
            raw_fp=0,
            raw_fn=len(truth_ids),
            raw_precision=0.0,
            raw_recall=0.0,
            raw_f1=0.0,
            delta_tp=0,
            delta_fp=0,
            delta_fn=len(truth_ids),
            delta_precision=0.0,
            delta_recall=0.0,
            delta_f1=0.0,
            evaluable=False,
            reason=reason,
            predicted_count=0,
            raw_predicted_count=0,
            baseline_predicted_count=0,
            delta_predicted_count=0,
            truth_count=len(truth_ids),
            missed_issue_ids=sorted(truth_ids)[:50],
        )

    baseline_ids: set[int] = set()
    if baseline_db_client is not None:
        baseline_ids, baseline_evaluable, baseline_reason = _collect_predicted_rowids(
            baseline_db_client, sql
        )
        if not baseline_evaluable:
            return CheckEvaluation(
                test_name=test_name,
                table=table_name,
                status=status,
                target_scope=target_scope,
                evaluation_mode="delta",
                tp=0,
                fp=0,
                fn=len(truth_ids),
                precision=0.0,
                recall=0.0,
                f1=0.0,
                raw_tp=0,
                raw_fp=0,
                raw_fn=len(truth_ids),
                raw_precision=0.0,
                raw_recall=0.0,
                raw_f1=0.0,
                delta_tp=0,
                delta_fp=0,
                delta_fn=len(truth_ids),
                delta_precision=0.0,
                delta_recall=0.0,
                delta_f1=0.0,
                evaluable=False,
                reason=f"baseline_{baseline_reason}",
                predicted_count=0,
                raw_predicted_count=len(predicted_ids),
                baseline_predicted_count=0,
                delta_predicted_count=0,
                truth_count=len(truth_ids),
                missed_issue_ids=sorted(truth_ids)[:50],
            )

    delta_ids = predicted_ids - baseline_ids
    raw_metrics = _score_predictions(predicted_ids, truth_ids)
    delta_metrics = _score_predictions(delta_ids, truth_ids)

    if baseline_db_client is not None:
        mode = "delta"
        selected_metrics = delta_metrics
        selected_predicted_count = len(delta_ids)
    else:
        mode = "raw"
        selected_metrics = raw_metrics
        selected_predicted_count = len(predicted_ids)

    return CheckEvaluation(
        test_name=test_name,
        table=table_name,
        status=status,
        target_scope=target_scope,
        evaluation_mode=mode,
        tp=int(selected_metrics["tp"]),
        fp=int(selected_metrics["fp"]),
        fn=int(selected_metrics["fn"]),
        precision=float(selected_metrics["precision"]),
        recall=float(selected_metrics["recall"]),
        f1=float(selected_metrics["f1"]),
        raw_tp=int(raw_metrics["tp"]),
        raw_fp=int(raw_metrics["fp"]),
        raw_fn=int(raw_metrics["fn"]),
        raw_precision=float(raw_metrics["precision"]),
        raw_recall=float(raw_metrics["recall"]),
        raw_f1=float(raw_metrics["f1"]),
        delta_tp=int(delta_metrics["tp"]),
        delta_fp=int(delta_metrics["fp"]),
        delta_fn=int(delta_metrics["fn"]),
        delta_precision=float(delta_metrics["precision"]),
        delta_recall=float(delta_metrics["recall"]),
        delta_f1=float(delta_metrics["f1"]),
        evaluable=True,
        reason="",
        predicted_count=selected_predicted_count,
        raw_predicted_count=len(predicted_ids),
        baseline_predicted_count=len(baseline_ids),
        delta_predicted_count=len(delta_ids),
        truth_count=len(truth_ids),
        missed_issue_ids=sorted(selected_metrics["fn_ids"])[:50],
    )


def _render_console_summary(run_id: str, checks: list[CheckEvaluation], evaluation_mode: str) -> None:
    table = Table(title=f"Evaluation Results: {run_id} ({evaluation_mode})")
    table.add_column("Query Result")
    table.add_column("Detection")
    table.add_column("Test")
    table.add_column("Scope")
    table.add_column("Mode")
    table.add_column("Pred", justify="right")
    table.add_column("TP", justify="right")
    table.add_column("FP", justify="right")
    table.add_column("FN", justify="right")
    table.add_column("Precision", justify="right")
    table.add_column("Recall", justify="right")
    table.add_column("F1", justify="right")
    table.add_column("Evaluable")

    for check in checks:
        table.add_row(
            _query_result_label(check.status),
            _detection_outcome(check),
            check.test_name,
            check.target_scope,
            check.evaluation_mode,
            str(check.predicted_count),
            str(check.tp),
            str(check.fp),
            str(check.fn),
            f"{check.precision:.3f}",
            f"{check.recall:.3f}",
            f"{check.f1:.3f}",
            "yes" if check.evaluable else "no",
        )

    console.print(table)


def _write_artifacts(
    *,
    run_id: str,
    ground_truth_path: Path,
    checks: list[CheckEvaluation],
    selected_mode: str,
    baseline_db_url: str | None,
) -> tuple[Path, Path]:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    micro_selected = _micro_average(checks, tp_attr="tp", fp_attr="fp", fn_attr="fn")
    micro_raw = _micro_average(checks, tp_attr="raw_tp", fp_attr="raw_fp", fn_attr="raw_fn")
    micro_delta = _micro_average(checks, tp_attr="delta_tp", fp_attr="delta_fp", fn_attr="delta_fn")

    payload = {
        "artifact_type": "dq_evaluation",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_id": run_id,
        "ground_truth_file": str(ground_truth_path),
        "evaluation_mode": selected_mode,
        "baseline_db_url": baseline_db_url or "",
        "checks": [
            {
                "test_name": check.test_name,
                "table": check.table,
                "status": check.status,
                "query_result_label": _query_result_label(check.status),
                "detection_outcome": _detection_outcome(check),
                "target_scope": check.target_scope,
                "evaluation_mode": check.evaluation_mode,
                "tp": check.tp,
                "fp": check.fp,
                "fn": check.fn,
                "precision": check.precision,
                "recall": check.recall,
                "f1": check.f1,
                "raw_tp": check.raw_tp,
                "raw_fp": check.raw_fp,
                "raw_fn": check.raw_fn,
                "raw_precision": check.raw_precision,
                "raw_recall": check.raw_recall,
                "raw_f1": check.raw_f1,
                "delta_tp": check.delta_tp,
                "delta_fp": check.delta_fp,
                "delta_fn": check.delta_fn,
                "delta_precision": check.delta_precision,
                "delta_recall": check.delta_recall,
                "delta_f1": check.delta_f1,
                "evaluable": check.evaluable,
                "reason": check.reason,
                "predicted_count": check.predicted_count,
                "raw_predicted_count": check.raw_predicted_count,
                "baseline_predicted_count": check.baseline_predicted_count,
                "delta_predicted_count": check.delta_predicted_count,
                "truth_count": check.truth_count,
                "missed_issue_ids": check.missed_issue_ids,
            }
            for check in checks
        ],
        "micro_average": micro_selected,
        "micro_average_raw": micro_raw,
        "micro_average_delta": micro_delta,
    }

    json_path = settings.log_dir / f"{run_id}-evaluation.json"
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        f"# Evaluation Report: {run_id}",
        "",
        f"Generated at: {timestamp}",
        f"Ground truth: `{ground_truth_path}`",
        f"Evaluation mode: `{selected_mode}`",
    ]
    if baseline_db_url:
        lines.append(f"Baseline DB: `{baseline_db_url}`")
    lines.extend(
        [
            "",
            "## How To Read This Report",
            "- `Query Result`: `issues_found` means SQL returned rows; `no_issues_found` means SQL returned zero rows.",
            "- `Detection`: quality against ground-truth (`exact_hit`, `partial_recall`, `missed`, `false_alarm`, `mixed`).",
            "- `micro_average`: TP/FP/FN summed across evaluable checks; then precision/recall/F1 from those sums.",
            "- Precision = TP/(TP+FP), Recall = TP/(TP+FN), F1 = harmonic mean of precision and recall.",
        ]
    )
    if selected_mode == "delta_vs_baseline":
        lines.extend(
            [
                "- `predicted_delta = current_query_rowids - baseline_query_rowids`.",
                "- `TP = predicted_delta ∩ truth`, `FP = predicted_delta - truth`, `FN = truth - predicted_delta`.",
            ]
        )

    lines.extend(
        [
            "",
            "## Micro Average (Selected Mode)",
            f"- TP: **{micro_selected['tp']}**",
            f"- FP: **{micro_selected['fp']}**",
            f"- FN: **{micro_selected['fn']}**",
            f"- Precision: **{micro_selected['precision']:.4f}**",
            f"- Recall: **{micro_selected['recall']:.4f}**",
            f"- F1: **{micro_selected['f1']:.4f}**",
            "",
            "## Micro Average (Raw Current DB)",
            f"- TP: **{micro_raw['tp']}**",
            f"- FP: **{micro_raw['fp']}**",
            f"- FN: **{micro_raw['fn']}**",
            f"- Precision: **{micro_raw['precision']:.4f}**",
            f"- Recall: **{micro_raw['recall']:.4f}**",
            f"- F1: **{micro_raw['f1']:.4f}**",
            "",
            "## Micro Average (Delta vs Baseline)",
            f"- TP: **{micro_delta['tp']}**",
            f"- FP: **{micro_delta['fp']}**",
            f"- FN: **{micro_delta['fn']}**",
            f"- Precision: **{micro_delta['precision']:.4f}**",
            f"- Recall: **{micro_delta['recall']:.4f}**",
            f"- F1: **{micro_delta['f1']:.4f}**",
            "",
            "## Per-Check Metrics",
            "| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |",
            "|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )

    for check in checks:
        lines.append(
            "| "
            f"{check.test_name} | "
            f"{_query_result_label(check.status)} | "
            f"{_detection_outcome(check)} | "
            f"{check.target_scope} | "
            f"{check.evaluation_mode} | "
            f"{'yes' if check.evaluable else 'no'} | "
            f"{check.predicted_count} | "
            f"{check.baseline_predicted_count} | "
            f"{check.delta_predicted_count} | "
            f"{check.tp} | {check.fp} | {check.fn} | "
            f"{check.precision:.4f} | {check.recall:.4f} | {check.f1:.4f} |"
        )
        if not check.evaluable and check.reason:
            lines.append(
                f"| reason({check.test_name}) | - | - | - | - | - | - | - | - | - | - | - | - | - | `{check.reason}` |"
            )

    missed_checks = [check for check in checks if check.missed_issue_ids]
    if missed_checks:
        lines.extend(
            [
                "",
                "## Missed Issue IDs (Sample, Up To 20 Per Check)",
            ]
        )
        for check in missed_checks:
            missed = ", ".join(str(v) for v in check.missed_issue_ids[:20])
            lines.append(f"- `{check.test_name}`: `{missed}`")

    md_path = settings.log_dir / f"{run_id}-evaluation.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return md_path, json_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate dq-run results against lab ground truth.")
    parser.add_argument("--run-id", required=True, help="Run ID from dq-run, e.g., dq-20260320T040000Z")
    parser.add_argument(
        "--ground-truth",
        required=True,
        help="Path to lab-ground-truth-*.json produced by dq-lab corrupt",
    )
    parser.add_argument(
        "--db-url",
        default=settings.db_url,
        help="Database URL used to replay row-id extraction queries (default: DQ_DB_URL)",
    )
    parser.add_argument(
        "--baseline-db-url",
        default="",
        help=(
            "Optional clean baseline DB URL. When set, evaluation uses "
            "delta rowids = current_query_results - baseline_query_results."
        ),
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    run_id = args.run_id.strip()
    ground_truth_path = Path(args.ground_truth).expanduser().resolve()

    ground_truth = _load_ground_truth(ground_truth_path)
    truth_by_strategy = _truth_sets_by_strategy(ground_truth)
    truth_all = _all_truth_ids(ground_truth)
    if not truth_all:
        raise ValueError("Ground truth contains no corrupted row IDs.")

    events = load_events(run_id)
    if not events:
        raise ValueError(f"No events found for run_id={run_id}")
    tests = [event for event in events if event.get("event") == "test_executed"]
    if not tests:
        raise ValueError(f"No test_executed events found for run_id={run_id}")

    db_client = DatabaseClient(args.db_url)
    baseline_db_client = DatabaseClient(args.baseline_db_url) if args.baseline_db_url else None
    selected_mode = "delta_vs_baseline" if baseline_db_client is not None else "raw_current_db"
    checks = [
        _evaluate_check(
            event=test,
            db_client=db_client,
            baseline_db_client=baseline_db_client,
            truth_by_strategy=truth_by_strategy,
            truth_all=truth_all,
        )
        for test in tests
    ]

    _render_console_summary(run_id, checks, selected_mode)
    md_path, json_path = _write_artifacts(
        run_id=run_id,
        ground_truth_path=ground_truth_path,
        checks=checks,
        selected_mode=selected_mode,
        baseline_db_url=args.baseline_db_url.strip() or None,
    )
    console.print(f"Saved evaluation report: {md_path}")
    console.print(f"Saved evaluation metrics JSON: {json_path}")


if __name__ == "__main__":
    main()
