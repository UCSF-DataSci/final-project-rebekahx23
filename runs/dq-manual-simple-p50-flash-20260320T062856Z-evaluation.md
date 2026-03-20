# Evaluation Report: dq-manual-simple-p50-flash-20260320T062856Z

Generated at: 2026-03-20 06:29:20 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T062856Z.json`
Evaluation mode: `delta_vs_baseline`
Baseline DB: `sqlite:///./runs/db/healthcare_clean.sqlite`

## How To Read This Report
- `Query Result`: `issues_found` means SQL returned rows; `no_issues_found` means SQL returned zero rows.
- `Detection`: quality against ground-truth (`exact_hit`, `partial_recall`, `missed`, `false_alarm`, `mixed`).
- `micro_average`: TP/FP/FN summed across evaluable checks; then precision/recall/F1 from those sums.
- Precision = TP/(TP+FP), Recall = TP/(TP+FN), F1 = harmonic mean of precision and recall.
- `predicted_delta = current_query_rowids - baseline_query_rowids`.
- `TP = predicted_delta ∩ truth`, `FP = predicted_delta - truth`, `FN = truth - predicted_delta`.

## Micro Average (Selected Mode)
- TP: **2220**
- FP: **49**
- FN: **0**
- Precision: **0.9784**
- Recall: **1.0000**
- F1: **0.9891**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **49**
- FN: **0**
- Precision: **0.9784**
- Recall: **1.0000**
- F1: **0.9891**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **49**
- FN: **0**
- Precision: **0.9784**
- Recall: **1.0000**
- F1: **0.9891**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| detect_invalid_age_outliers | issues_found | hit_with_fp | code_drift,id_fragmentation,numeric_outlier | delta | yes | 1135 | 0 | 1135 | 1110 | 25 | 0 | 0.9780 | 1.0000 | 0.9889 |
| validate_admission_discharge_sequence | issues_found | hit_with_fp | future_date,id_fragmentation,temporal_inversion | delta | yes | 1134 | 0 | 1134 | 1110 | 24 | 0 | 0.9788 | 1.0000 | 0.9893 |
