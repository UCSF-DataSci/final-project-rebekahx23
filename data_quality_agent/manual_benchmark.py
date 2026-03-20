"""Manual low-quota benchmark runner for simple/complex data-quality experiments."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .config import settings
from .log_store import load_events

_DEFAULT_TABLE = "healthcare_dataset"
_DEFAULT_MODELS = "gemini-2.5-flash,gemini-2.5-pro"
_DEFAULT_PROFILES = "P05,P10,P20"
_DEFAULT_TARGETED_STRATEGIES = ",".join(
    [
        "temporal_inversion",
        "datetime_shift",
        "code_drift",
        "id_fragmentation",
        "enum_encoding_drift",
        "unit_mismatch",
    ]
)

_PROFILE_CONFIG: dict[str, dict[str, int]] = {
    "P05": {"sample_size": 300, "batches": 1, "token_cap": 1500},
    "P10": {"sample_size": 600, "batches": 2, "token_cap": 3000},
    "P20": {"sample_size": 1200, "batches": 3, "token_cap": 5000},
    "P50": {"sample_size": 3000, "batches": 3, "token_cap": 8000},
}

_TARGETED_COLUMN_HINTS: dict[str, str] = {
    "code_drift": "medication",
    "id_fragmentation": "insurance_provider",
    "enum_encoding_drift": "gender",
    "unit_mismatch": "test_results",
}


@dataclass
class SessionRunRecord:
    run_id: str
    session: str
    scenario: str
    test_id: str
    model: str
    profile: str
    sample_size: int
    batches: int
    token_cap: int
    status: str
    run_exit_code: int
    eval_exit_code: int
    quota_error: bool
    selected_precision: float
    selected_recall: float
    selected_f1: float
    delta_precision: float
    delta_recall: float
    delta_f1: float
    raw_precision: float
    raw_recall: float
    raw_f1: float
    prompt_tokens: int
    output_tokens: int
    total_tokens: int
    estimated_cost_usd: float | None
    error_message: str
    error_log_path: str
    ground_truth_file: str
    baseline_db_url: str
    work_db_url: str


def _now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _parse_csv_list(raw_value: str) -> list[str]:
    values = [item.strip() for item in raw_value.split(",") if item.strip()]
    if not values:
        raise ValueError("Expected at least one value.")
    return values


def _parse_model_list(raw_value: str) -> list[str]:
    return _parse_csv_list(raw_value)


def _parse_profile_list(raw_value: str) -> list[str]:
    profiles = [profile.upper() for profile in _parse_csv_list(raw_value)]
    unknown = [profile for profile in profiles if profile not in _PROFILE_CONFIG]
    if unknown:
        allowed = ", ".join(sorted(_PROFILE_CONFIG))
        raise ValueError(f"Unknown profile(s): {', '.join(unknown)}. Allowed: {allowed}")
    return profiles


def _short_model_label(model: str) -> str:
    lower = model.lower()
    if "flash" in lower:
        return "FLASH"
    if "pro" in lower:
        return "PRO"
    compact = "".join(ch for ch in model.upper() if ch.isalnum())
    return compact[-10:] if len(compact) > 10 else compact


def _sqlite_url_to_path(db_url: str) -> Path:
    prefix = "sqlite:///"
    if not db_url.startswith(prefix):
        raise ValueError(f"Only sqlite URLs are supported for manual benchmark setup: {db_url}")
    raw_path = db_url[len(prefix) :]
    db_path = Path(raw_path)
    if not db_path.is_absolute():
        db_path = Path.cwd() / db_path
    return db_path.resolve()


def _run_subprocess(command: list[str], *, env: dict[str, str] | None = None) -> tuple[int, str, str]:
    proc = subprocess.run(
        command,
        cwd=str(Path.cwd()),
        env=env or os.environ.copy(),
        capture_output=True,
        text=True,
        check=False,
    )
    return proc.returncode, proc.stdout, proc.stderr


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


def _is_quota_error(text: str) -> bool:
    lowered = text.lower()
    return "resource_exhausted" in lowered or ("429" in lowered and "quota" in lowered)


def _latest_ground_truth_file() -> Path | None:
    candidates = sorted(
        settings.log_dir.glob("lab-ground-truth-*.json"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


def _estimate_cost_usd(
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


def _sanitize_markdown_cell(value: str) -> str:
    return value.replace("\n", " ").replace("\r", " ").replace("|", "\\|").strip()


def _error_excerpt(value: str, limit: int = 220) -> str:
    compact = _sanitize_markdown_cell(value)
    if len(compact) <= limit:
        return compact
    return compact[: max(0, limit - 3)] + "..."


def _persist_error_log(run_id: str, stage: str, stdout: str, stderr: str) -> str:
    log_path = settings.log_dir / f"{run_id}-{stage}-error.log"
    content = [
        f"run_id={run_id}",
        f"stage={stage}",
        "",
        "[stdout]",
        stdout.rstrip(),
        "",
        "[stderr]",
        stderr.rstrip(),
        "",
    ]
    log_path.write_text("\n".join(content), encoding="utf-8")
    return str(log_path)


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


def _read_eval_json(run_id: str) -> dict[str, Any]:
    path = settings.log_dir / f"{run_id}-evaluation.json"
    return json.loads(path.read_text(encoding="utf-8"))


def _copy_clean_to_work(base_db_url: str, work_db_url: str) -> None:
    base_path = _sqlite_url_to_path(base_db_url)
    work_path = _sqlite_url_to_path(work_db_url)
    if not base_path.exists():
        raise FileNotFoundError(f"Baseline DB file not found: {base_path}")
    work_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(base_path, work_path)


def _run_setup(args: argparse.Namespace) -> None:
    base_path = _sqlite_url_to_path(args.base_db_url)
    work_path = _sqlite_url_to_path(args.work_db_url)
    base_path.parent.mkdir(parents=True, exist_ok=True)
    work_path.parent.mkdir(parents=True, exist_ok=True)

    ingest_cmd = [
        args.python,
        "-m",
        "data_quality_agent.local_lab",
        "--db-url",
        args.base_db_url,
        "ingest",
        "--csv",
        args.csv,
    ]
    code, out, err = _run_subprocess(ingest_cmd)
    if code != 0:
        raise RuntimeError(f"Setup ingest failed:\n{out}\n{err}".strip())

    _copy_clean_to_work(args.base_db_url, args.work_db_url)

    list_cmd = [
        args.python,
        "-m",
        "data_quality_agent.local_lab",
        "--db-url",
        args.base_db_url,
        "list",
        "--verbose",
    ]
    list_code, list_out, list_err = _run_subprocess(list_cmd)
    if list_code != 0:
        raise RuntimeError(f"Setup validation failed:\n{list_out}\n{list_err}".strip())

    print(out.strip())
    print(f"\nCopied baseline DB -> work DB:\n- {base_path}\n- {work_path}")
    print("\nValidation:")
    print(list_out.strip())
    print("\nSuggested env:")
    print(f'export PYRUN="{args.python}"')
    print(f'export TABLE="{args.table}"')
    print(f'export BASE_DB_URL="{args.base_db_url}"')
    print(f'export WORK_DB_URL="{args.work_db_url}"')


def _create_ground_truth(
    *,
    python_exe: str,
    db_url: str,
    table: str,
    strategy: str,
    fraction: float,
    seed: int,
    column: str = "",
) -> Path:
    before = _latest_ground_truth_file()
    cmd = [
        python_exe,
        "-m",
        "data_quality_agent.local_lab",
        "--db-url",
        db_url,
        "corrupt",
        "--table",
        table,
        "--strategy",
        strategy,
        "--fraction",
        str(fraction),
        "--seed",
        str(seed),
    ]
    if column:
        cmd.extend(["--column", column])
    code, out, err = _run_subprocess(cmd)
    if code != 0:
        raise RuntimeError(f"Corruption step failed:\n{out}\n{err}".strip())

    after = _latest_ground_truth_file()
    if after is None or (before is not None and after == before):
        raise RuntimeError("Could not detect newly created lab-ground-truth artifact.")

    print(out.strip())
    print(f"Selected ground truth: {after}")
    return after


def _build_session_tests(
    *,
    session: str,
    models: list[str],
    profiles: list[str],
    max_runs: int,
) -> list[tuple[str, str, str]]:
    tests: list[tuple[str, str, str]] = []
    for model in models:
        model_tag = _short_model_label(model)
        for profile in profiles:
            test_id = f"{session.upper()}-{profile}-{model_tag}"
            tests.append((test_id, model, profile))
    return tests[: max(1, max_runs)]


def _render_test_command_preview(
    *,
    python_exe: str,
    run_id: str,
    table: str,
    model: str,
    work_db_url: str,
    profile: str,
    retry_attempts: int,
    session: str,
    test_id: str,
    ground_truth: Path,
    baseline_db_url: str,
) -> str:
    cfg = _PROFILE_CONFIG[profile]
    run_cmd = (
        f'DQ_DB_URL="{work_db_url}" DQ_MODEL="{model}" '
        f'DQ_SAMPLE_SIZE="{cfg["sample_size"]}" DQ_SAMPLE_BATCHES="{cfg["batches"]}" '
        f'DQ_PROFILE_TOKEN_CAP="{cfg["token_cap"]}" '
        f'{python_exe} -m data_quality_agent.run_job --run-id "{run_id}" --tables "{table}" '
        f'--retry-attempts {retry_attempts} --prompt "Manual benchmark {session} issues: {test_id}"'
    )
    eval_cmd = (
        f'{python_exe} -m data_quality_agent.evaluate --run-id "{run_id}" '
        f'--ground-truth "{ground_truth}" --db-url "{work_db_url}" '
        f'--baseline-db-url "{baseline_db_url}"'
    )
    return f"{run_cmd}\n{eval_cmd}"


def _run_single_benchmark_test(
    *,
    python_exe: str,
    table: str,
    work_db_url: str,
    baseline_db_url: str,
    ground_truth: Path,
    session: str,
    test_id: str,
    model: str,
    profile: str,
    retry_attempts: int,
    input_cost_per_1m: float,
    output_cost_per_1m: float,
) -> SessionRunRecord:
    timestamp = _now_utc()
    run_id = f"dq-manual-{test_id.lower()}-{timestamp}"
    cfg = _PROFILE_CONFIG[profile]

    env = os.environ.copy()
    env["DQ_DB_URL"] = work_db_url
    env["DQ_MODEL"] = model
    env["DQ_SAMPLE_SIZE"] = str(cfg["sample_size"])
    env["DQ_SAMPLE_BATCHES"] = str(cfg["batches"])
    env["DQ_PROFILE_TOKEN_CAP"] = str(cfg["token_cap"])

    run_cmd = [
        python_exe,
        "-m",
        "data_quality_agent.run_job",
        "--run-id",
        run_id,
        "--tables",
        table,
        "--retry-attempts",
        str(retry_attempts),
        "--prompt",
        f"Manual benchmark {session} issues: {test_id}",
    ]
    run_exit, run_out, run_err = _run_subprocess(run_cmd, env=env)
    merged_run_text = f"{run_out}\n{run_err}"
    quota_error = _is_quota_error(merged_run_text)

    eval_exit = -1
    selected_precision = selected_recall = selected_f1 = 0.0
    delta_precision = delta_recall = delta_f1 = 0.0
    raw_precision = raw_recall = raw_f1 = 0.0
    status = "run_failed"
    error_message = (run_err or run_out).strip()[:1200]
    error_log_path = ""

    if run_exit == 0:
        eval_cmd = [
            python_exe,
            "-m",
            "data_quality_agent.evaluate",
            "--run-id",
            run_id,
            "--ground-truth",
            str(ground_truth),
            "--db-url",
            work_db_url,
            "--baseline-db-url",
            baseline_db_url,
        ]
        eval_exit, eval_out, eval_err = _run_subprocess(eval_cmd, env=env)
        merged_eval_text = f"{eval_out}\n{eval_err}"
        quota_error = quota_error or _is_quota_error(merged_eval_text)
        if eval_exit == 0:
            payload = _read_eval_json(run_id)
            selected = payload.get("micro_average", {})
            raw = payload.get("micro_average_raw", {})
            delta = payload.get("micro_average_delta", {})
            selected_precision = float(selected.get("precision", 0.0))
            selected_recall = float(selected.get("recall", 0.0))
            selected_f1 = float(selected.get("f1", 0.0))
            raw_precision = float(raw.get("precision", 0.0))
            raw_recall = float(raw.get("recall", 0.0))
            raw_f1 = float(raw.get("f1", 0.0))
            delta_precision = float(delta.get("precision", 0.0))
            delta_recall = float(delta.get("recall", 0.0))
            delta_f1 = float(delta.get("f1", 0.0))
            status = "success"
            error_message = ""
            error_log_path = ""
        else:
            status = "eval_failed"
            error_message = (eval_err or eval_out).strip()[:1200]
            error_log_path = _persist_error_log(run_id, "eval", eval_out, eval_err)
    else:
        error_log_path = _persist_error_log(run_id, "run", run_out, run_err)

    prompt_tokens, output_tokens, total_tokens = _read_usage_tokens(run_id)
    estimated_cost = _estimate_cost_usd(
        prompt_tokens=prompt_tokens,
        output_tokens=output_tokens,
        input_cost_per_1m=input_cost_per_1m,
        output_cost_per_1m=output_cost_per_1m,
    )

    return SessionRunRecord(
        run_id=run_id,
        session=session,
        scenario=session,
        test_id=test_id,
        model=model,
        profile=profile,
        sample_size=cfg["sample_size"],
        batches=cfg["batches"],
        token_cap=cfg["token_cap"],
        status=status,
        run_exit_code=run_exit,
        eval_exit_code=eval_exit,
        quota_error=quota_error,
        selected_precision=selected_precision,
        selected_recall=selected_recall,
        selected_f1=selected_f1,
        delta_precision=delta_precision,
        delta_recall=delta_recall,
        delta_f1=delta_f1,
        raw_precision=raw_precision,
        raw_recall=raw_recall,
        raw_f1=raw_f1,
        prompt_tokens=prompt_tokens,
        output_tokens=output_tokens,
        total_tokens=total_tokens,
        estimated_cost_usd=estimated_cost,
        error_message=error_message,
        error_log_path=error_log_path,
        ground_truth_file=str(ground_truth),
        baseline_db_url=baseline_db_url,
        work_db_url=work_db_url,
    )


def _save_session_artifacts(
    *,
    session: str,
    ground_truth: Path,
    records: list[SessionRunRecord],
    args: argparse.Namespace,
) -> tuple[Path, Path]:
    timestamp = _now_utc()
    json_path = settings.log_dir / f"manual-session-{session}-{timestamp}.json"
    payload = {
        "artifact_type": "manual_benchmark_session",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "session": session,
        "ground_truth_file": str(ground_truth),
        "settings": {
            "table": args.table,
            "models": args.models,
            "profiles": args.profiles,
            "max_runs": args.max_runs,
            "sleep_seconds": args.sleep_seconds,
            "retry_attempts": args.retry_attempts,
            "base_db_url": args.base_db_url,
            "work_db_url": args.work_db_url,
            "python": args.python,
            "input_cost_per_1m": args.input_cost_per_1m,
            "output_cost_per_1m": args.output_cost_per_1m,
        },
        "runs": [record.__dict__ for record in records],
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        f"# Manual Session Report: {session.upper()} ({timestamp})",
        "",
        f"- Ground truth: `{ground_truth}`",
        f"- Total runs attempted: **{len(records)}**",
        "",
        "| run_id | test_id | model | profile | status | delta_precision | delta_recall | delta_f1 | tokens | cost_usd | error_excerpt | error_log |",
        "|---|---|---|---|---|---:|---:|---:|---:|---:|---|---|",
    ]
    for record in records:
        cost_text = (
            f"{record.estimated_cost_usd:.6f}" if record.estimated_cost_usd is not None else "n/a"
        )
        err_excerpt = _error_excerpt(record.error_message) if record.error_message else ""
        err_log = _sanitize_markdown_cell(record.error_log_path) if record.error_log_path else ""
        lines.append(
            f"| {record.run_id} | {record.test_id} | {record.model} | {record.profile} | {record.status} | "
            f"{record.delta_precision:.4f} | {record.delta_recall:.4f} | {record.delta_f1:.4f} | "
            f"{record.total_tokens} | {cost_text} | {err_excerpt} | {err_log} |"
        )

    md_path = settings.log_dir / f"manual-session-{session}-{timestamp}.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return md_path, json_path


def _run_session(args: argparse.Namespace) -> None:
    models = _parse_model_list(args.models)
    profiles = _parse_profile_list(args.profiles)
    tests = _build_session_tests(
        session=args.session,
        models=models,
        profiles=profiles,
        max_runs=args.max_runs,
    )

    print(f"Session: {args.session}")
    print(f"Planned tests ({len(tests)}):")
    for index, (test_id, model, profile) in enumerate(tests, start=1):
        cfg = _PROFILE_CONFIG[profile]
        print(
            f"{index:02d}. {test_id} model={model} sample={cfg['sample_size']} "
            f"batches={cfg['batches']} token_cap={cfg['token_cap']}"
        )

    if args.dry_run:
        mock_ground_truth = Path("runs/lab-ground-truth-<timestamp>.json")
        print("\nExact commands:")
        for test_id, model, profile in tests:
            run_id = f"dq-manual-{test_id.lower()}-<timestamp>"
            preview = _render_test_command_preview(
                python_exe=args.python,
                run_id=run_id,
                table=args.table,
                model=model,
                work_db_url=args.work_db_url,
                profile=profile,
                retry_attempts=args.retry_attempts,
                session=args.session,
                test_id=test_id,
                ground_truth=mock_ground_truth,
                baseline_db_url=args.base_db_url,
            )
            print("\n---")
            print(preview)
        return

    python_ok, python_error = _validate_runner_python(args.python, Path.cwd())
    if not python_ok:
        details = f" ({python_error})" if python_error else ""
        raise RuntimeError(
            "Selected runner python cannot import google.adk. "
            "Use --python with your working dq-run interpreter "
            f"(for example: /Library/Frameworks/Python.framework/Versions/3.11/bin/python3){details}"
        )

    _copy_clean_to_work(args.base_db_url, args.work_db_url)
    print(f"Reset work DB from baseline: {args.base_db_url} -> {args.work_db_url}")

    if args.session == "simple":
        ground_truth = _create_ground_truth(
            python_exe=args.python,
            db_url=args.work_db_url,
            table=args.table,
            strategy="auto",
            fraction=args.simple_fraction,
            seed=args.simple_seed,
        )
    else:
        ground_truth = _create_ground_truth(
            python_exe=args.python,
            db_url=args.work_db_url,
            table=args.table,
            strategy="complex_auto",
            fraction=args.complex_fraction,
            seed=args.complex_seed,
        )

    consecutive_quota_failures = 0
    records: list[SessionRunRecord] = []
    for index, (test_id, model, profile) in enumerate(tests, start=1):
        print(f"\n[{index}/{len(tests)}] Running {test_id} ...")
        record = _run_single_benchmark_test(
            python_exe=args.python,
            table=args.table,
            work_db_url=args.work_db_url,
            baseline_db_url=args.base_db_url,
            ground_truth=ground_truth,
            session=args.session,
            test_id=test_id,
            model=model,
            profile=profile,
            retry_attempts=args.retry_attempts,
            input_cost_per_1m=args.input_cost_per_1m,
            output_cost_per_1m=args.output_cost_per_1m,
        )
        records.append(record)
        print(
            f"status={record.status} delta_recall={record.delta_recall:.4f} "
            f"delta_f1={record.delta_f1:.4f} tokens={record.total_tokens}"
        )
        if record.error_message:
            print(f"error={_error_excerpt(record.error_message)}")
            if record.error_log_path:
                print(f"error_log={record.error_log_path}")

        if record.quota_error and record.status != "success":
            consecutive_quota_failures += 1
        else:
            consecutive_quota_failures = 0

        if consecutive_quota_failures >= 2:
            print("Stopping early due to 2 consecutive quota-related failures.")
            break

        if index < len(tests):
            time.sleep(max(0.0, args.sleep_seconds))

    md_path, json_path = _save_session_artifacts(
        session=args.session,
        ground_truth=ground_truth,
        records=records,
        args=args,
    )
    print(f"\nSaved session markdown: {md_path}")
    print(f"Saved session json: {json_path}")


def _run_targeted(args: argparse.Namespace) -> None:
    models = _parse_model_list(args.models)
    strategies = _parse_csv_list(args.strategies)
    profile = args.profile.upper()
    if profile not in _PROFILE_CONFIG:
        allowed = ", ".join(sorted(_PROFILE_CONFIG))
        raise ValueError(f"Unknown profile {profile}. Allowed: {allowed}")

    planned: list[tuple[str, str]] = []
    for strategy in strategies:
        for model in models:
            planned.append((strategy, model))
    planned = planned[: max(1, args.max_runs)]

    print(f"Targeted planned runs ({len(planned)}):")
    for index, (strategy, model) in enumerate(planned, start=1):
        print(f"{index:02d}. strategy={strategy} model={model} profile={profile}")

    if args.dry_run:
        return

    python_ok, python_error = _validate_runner_python(args.python, Path.cwd())
    if not python_ok:
        details = f" ({python_error})" if python_error else ""
        raise RuntimeError(
            "Selected runner python cannot import google.adk. "
            "Use --python with your working dq-run interpreter "
            f"(for example: /Library/Frameworks/Python.framework/Versions/3.11/bin/python3){details}"
        )

    records: list[SessionRunRecord] = []
    consecutive_quota_failures = 0
    for index, (strategy, model) in enumerate(planned, start=1):
        _copy_clean_to_work(args.base_db_url, args.work_db_url)
        seed = args.seed_base + index
        gt = _create_ground_truth(
            python_exe=args.python,
            db_url=args.work_db_url,
            table=args.table,
            strategy=strategy,
            fraction=args.fraction,
            seed=seed,
            column=_TARGETED_COLUMN_HINTS.get(strategy, ""),
        )
        test_id = f"TARGET-{strategy.upper()}-{_short_model_label(model)}"
        print(f"\n[{index}/{len(planned)}] Running {test_id} ...")
        record = _run_single_benchmark_test(
            python_exe=args.python,
            table=args.table,
            work_db_url=args.work_db_url,
            baseline_db_url=args.base_db_url,
            ground_truth=gt,
            session="targeted",
            test_id=test_id,
            model=model,
            profile=profile,
            retry_attempts=args.retry_attempts,
            input_cost_per_1m=args.input_cost_per_1m,
            output_cost_per_1m=args.output_cost_per_1m,
        )
        record.scenario = strategy
        records.append(record)
        print(
            f"status={record.status} delta_recall={record.delta_recall:.4f} "
            f"delta_f1={record.delta_f1:.4f}"
        )
        if record.error_message:
            print(f"error={_error_excerpt(record.error_message)}")
            if record.error_log_path:
                print(f"error_log={record.error_log_path}")

        if record.quota_error and record.status != "success":
            consecutive_quota_failures += 1
        else:
            consecutive_quota_failures = 0
        if consecutive_quota_failures >= 2:
            print("Stopping early due to 2 consecutive quota-related failures.")
            break

        if index < len(planned):
            time.sleep(max(0.0, args.sleep_seconds))

    md_path, json_path = _save_session_artifacts(
        session="targeted",
        ground_truth=Path(records[-1].ground_truth_file) if records else Path(""),
        records=records,
        args=args,
    )
    print(f"\nSaved targeted markdown: {md_path}")
    print(f"Saved targeted json: {json_path}")


def _profile_sort_key(profile: str) -> int:
    order = {"P05": 0, "P10": 1, "P20": 2, "P50": 3}
    return order.get(profile.upper(), 99)


def _mean(values: list[float]) -> float:
    if not values:
        return 0.0
    return sum(values) / len(values)


def _choose_plateau_profile(rows: list[dict[str, Any]]) -> dict[str, Any]:
    sorted_rows = sorted(rows, key=lambda row: _profile_sort_key(str(row.get("profile", ""))))
    if not sorted_rows:
        return {
            "selected_profile": "n/a",
            "reason": "no_data",
            "needs_p50_followup": False,
        }
    best_recall = max(float(row.get("delta_recall_mean", 0.0)) for row in sorted_rows)
    threshold = best_recall - 0.03
    candidates = [
        row for row in sorted_rows if float(row.get("delta_recall_mean", 0.0)) >= threshold
    ]
    if not candidates:
        return {
            "selected_profile": "P50",
            "reason": "no_plateau_candidate",
            "needs_p50_followup": True,
        }

    selected = candidates[0]
    selected_idx = sorted_rows.index(selected)
    needs_p50_followup = False

    if selected_idx + 1 < len(sorted_rows):
        next_row = sorted_rows[selected_idx + 1]
        selected_precision = float(selected.get("delta_precision_mean", 0.0))
        next_precision = float(next_row.get("delta_precision_mean", 0.0))
        if next_precision > 0.0 and selected_precision < (0.5 * next_precision):
            selected = next_row
            selected_idx += 1

    if selected_idx == len(sorted_rows) - 1 and str(selected.get("profile", "")) != "P50":
        lower_plateau_exists = any(
            row is not selected and float(row.get("delta_recall_mean", 0.0)) >= threshold
            for row in sorted_rows
        )
        if not lower_plateau_exists:
            needs_p50_followup = True

    return {
        "selected_profile": selected.get("profile", "n/a"),
        "reason": "recall_plateau",
        "needs_p50_followup": needs_p50_followup,
    }


def _summarize(args: argparse.Namespace) -> None:
    pattern = args.pattern
    files = sorted(
        settings.log_dir.glob(pattern),
        key=lambda path: path.stat().st_mtime,
    )
    if not files:
        print(f"No session files matched pattern: {pattern}")
        print("Run `dq-manual run-session --session simple` and/or `--session complex` first.")
        return

    records: list[dict[str, Any]] = []
    for path in files:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if payload.get("artifact_type") != "manual_benchmark_session":
            continue
        records.extend(payload.get("runs", []))
    if not records:
        print("No run records found in matched session files.")
        return

    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for record in records:
        if str(record.get("status", "")) != "success":
            continue
        key = (
            str(record.get("scenario", "")),
            str(record.get("model", "")),
            str(record.get("profile", "")),
        )
        grouped.setdefault(key, []).append(record)

    aggregated_rows: list[dict[str, Any]] = []
    for (scenario, model, profile), rows in sorted(
        grouped.items(),
        key=lambda item: (item[0][0], item[0][1], _profile_sort_key(item[0][2])),
    ):
        costs = [row.get("estimated_cost_usd") for row in rows if row.get("estimated_cost_usd") is not None]
        aggregated_rows.append(
            {
                "scenario": scenario,
                "model": model,
                "profile": profile,
                "run_count": len(rows),
                "delta_precision_mean": _mean([float(row.get("delta_precision", 0.0)) for row in rows]),
                "delta_recall_mean": _mean([float(row.get("delta_recall", 0.0)) for row in rows]),
                "delta_f1_mean": _mean([float(row.get("delta_f1", 0.0)) for row in rows]),
                "prompt_tokens_mean": _mean([float(row.get("prompt_tokens", 0.0)) for row in rows]),
                "output_tokens_mean": _mean([float(row.get("output_tokens", 0.0)) for row in rows]),
                "total_tokens_mean": _mean([float(row.get("total_tokens", 0.0)) for row in rows]),
                "cost_mean_usd": _mean([float(cost) for cost in costs]) if costs else None,
            }
        )

    recommendation_rows: list[dict[str, Any]] = []
    rec_groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in aggregated_rows:
        key = (str(row["scenario"]), str(row["model"]))
        rec_groups.setdefault(key, []).append(row)

    for (scenario, model), rows in sorted(rec_groups.items(), key=lambda item: item[0]):
        selected = _choose_plateau_profile(rows)
        recommendation_rows.append(
            {
                "scenario": scenario,
                "model": model,
                **selected,
            }
        )

    timestamp = _now_utc()
    json_path = settings.log_dir / f"manual-benchmark-summary-{timestamp}.json"
    payload = {
        "artifact_type": "manual_benchmark_summary",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_pattern": pattern,
        "source_files": [str(path) for path in files],
        "aggregated_rows": aggregated_rows,
        "recommendations": recommendation_rows,
    }
    json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    lines = [
        f"# Manual Benchmark Summary ({timestamp})",
        "",
        "## Demo Summary Table",
        "| run_id | scenario | model | profile | delta_precision | delta_recall | delta_f1 | prompt_tokens | output_tokens | total_tokens | estimated_cost_usd |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for record in records:
        cost_text = (
            f"{float(record['estimated_cost_usd']):.6f}"
            if record.get("estimated_cost_usd") is not None
            else "n/a"
        )
        lines.append(
            f"| {record.get('run_id','')} | {record.get('scenario','')} | {record.get('model','')} | "
            f"{record.get('profile','')} | {float(record.get('delta_precision', 0.0)):.4f} | "
            f"{float(record.get('delta_recall', 0.0)):.4f} | {float(record.get('delta_f1', 0.0)):.4f} | "
            f"{int(record.get('prompt_tokens', 0))} | {int(record.get('output_tokens', 0))} | "
            f"{int(record.get('total_tokens', 0))} | {cost_text} |"
        )

    lines.extend(
        [
            "",
            "## Aggregated (mean over successful runs)",
            "| scenario | model | profile | runs | delta_precision | delta_recall | delta_f1 | total_tokens | cost_usd |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in aggregated_rows:
        cost_text = f"{row['cost_mean_usd']:.6f}" if row["cost_mean_usd"] is not None else "n/a"
        lines.append(
            f"| {row['scenario']} | {row['model']} | {row['profile']} | {row['run_count']} | "
            f"{row['delta_precision_mean']:.4f} | {row['delta_recall_mean']:.4f} | {row['delta_f1_mean']:.4f} | "
            f"{row['total_tokens_mean']:.1f} | {cost_text} |"
        )

    lines.extend(
        [
            "",
            "## Recommendations",
            "| scenario | model | selected_profile | needs_p50_followup | reason |",
            "|---|---|---|---|---|",
        ]
    )
    for rec in recommendation_rows:
        lines.append(
            f"| {rec['scenario']} | {rec['model']} | {rec['selected_profile']} | "
            f"{'yes' if rec['needs_p50_followup'] else 'no'} | {rec['reason']} |"
        )

    lines.extend(
        [
            "",
            "Recommendation statement:",
        ]
    )
    for rec in recommendation_rows:
        lines.append(
            f"- For {rec['scenario']} issues with {rec['model']}: use {rec['selected_profile']}"
            + (" (run P50 follow-up)." if rec["needs_p50_followup"] else ".")
        )

    md_path = settings.log_dir / f"manual-benchmark-summary-{timestamp}.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Saved benchmark summary markdown: {md_path}")
    print(f"Saved benchmark summary json: {json_path}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Manual low-quota benchmark orchestration.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    setup = subparsers.add_parser("setup", help="Phase 0: ingest CSV into baseline DB and copy to work DB")
    setup.add_argument("--python", default=sys.executable, help="Python executable")
    setup.add_argument("--csv", default="./healthcare_dataset.csv", help="CSV input path")
    setup.add_argument("--table", default=_DEFAULT_TABLE, help="Target table name")
    setup.add_argument("--base-db-url", default="sqlite:///./runs/db/healthcare_clean.sqlite")
    setup.add_argument("--work-db-url", default="sqlite:///./runs/db/healthcare_work.sqlite")

    run_session = subparsers.add_parser(
        "run-session",
        help="Phase 1/2: run SIMPLE or COMPLEX session with 6-run low-quota pacing",
    )
    run_session.add_argument("--session", choices=["simple", "complex"], required=True)
    run_session.add_argument("--python", default=sys.executable, help="Python executable")
    run_session.add_argument("--table", default=_DEFAULT_TABLE, help="Target table name")
    run_session.add_argument("--base-db-url", default="sqlite:///./runs/db/healthcare_clean.sqlite")
    run_session.add_argument("--work-db-url", default="sqlite:///./runs/db/healthcare_work.sqlite")
    run_session.add_argument("--models", default=_DEFAULT_MODELS, help="Comma-separated models")
    run_session.add_argument("--profiles", default=_DEFAULT_PROFILES, help="Comma-separated profiles")
    run_session.add_argument("--max-runs", type=int, default=6, help="Hard cap per session")
    run_session.add_argument("--sleep-seconds", type=float, default=10.0)
    run_session.add_argument("--retry-attempts", type=int, default=5)
    run_session.add_argument("--simple-fraction", type=float, default=0.02)
    run_session.add_argument("--simple-seed", type=int, default=101)
    run_session.add_argument("--complex-fraction", type=float, default=0.01)
    run_session.add_argument("--complex-seed", type=int, default=202)
    run_session.add_argument("--input-cost-per-1m", type=float, default=0.0)
    run_session.add_argument("--output-cost-per-1m", type=float, default=0.0)
    run_session.add_argument("--dry-run", action="store_true", help="Print exact commands without execution")

    targeted = subparsers.add_parser(
        "run-targeted",
        help="Phase 4 optional: run targeted complex strategies with low-quota pacing",
    )
    targeted.add_argument("--python", default=sys.executable, help="Python executable")
    targeted.add_argument("--table", default=_DEFAULT_TABLE, help="Target table name")
    targeted.add_argument("--base-db-url", default="sqlite:///./runs/db/healthcare_clean.sqlite")
    targeted.add_argument("--work-db-url", default="sqlite:///./runs/db/healthcare_work.sqlite")
    targeted.add_argument("--models", default=_DEFAULT_MODELS, help="Comma-separated models")
    targeted.add_argument("--strategies", default=_DEFAULT_TARGETED_STRATEGIES)
    targeted.add_argument("--profile", default="P20", help="Profile label (P05/P10/P20/P50)")
    targeted.add_argument("--fraction", type=float, default=0.01)
    targeted.add_argument("--seed-base", type=int, default=500)
    targeted.add_argument("--max-runs", type=int, default=6)
    targeted.add_argument("--sleep-seconds", type=float, default=10.0)
    targeted.add_argument("--retry-attempts", type=int, default=5)
    targeted.add_argument("--input-cost-per-1m", type=float, default=0.0)
    targeted.add_argument("--output-cost-per-1m", type=float, default=0.0)
    targeted.add_argument("--dry-run", action="store_true")

    summarize = subparsers.add_parser(
        "summarize",
        help="Phase 3/5: aggregate manual sessions and emit plateau-based recommendations",
    )
    summarize.add_argument(
        "--pattern",
        default="manual-session-*.json",
        help="Glob pattern under runs/ to include session artifacts",
    )

    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if args.command == "setup":
        _run_setup(args)
    elif args.command == "run-session":
        _run_session(args)
    elif args.command == "run-targeted":
        _run_targeted(args)
    elif args.command == "summarize":
        _summarize(args)
    else:
        raise ValueError(f"Unsupported command: {args.command}")


if __name__ == "__main__":
    main()
