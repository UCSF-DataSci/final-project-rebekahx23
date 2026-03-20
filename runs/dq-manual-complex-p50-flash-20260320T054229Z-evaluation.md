# Evaluation Report: dq-manual-complex-p50-flash-20260320T054229Z

Generated at: 2026-03-20 05:43:17 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T054014Z.json`
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
- TP: **555**
- FP: **0**
- FN: **0**
- Precision: **1.0000**
- Recall: **1.0000**
- F1: **1.0000**

## Micro Average (Raw Current DB)
- TP: **555**
- FP: **108**
- FN: **0**
- Precision: **0.8371**
- Recall: **1.0000**
- F1: **0.9113**

## Micro Average (Delta vs Baseline)
- TP: **555**
- FP: **0**
- FN: **0**
- Precision: **1.0000**
- Recall: **1.0000**
- F1: **1.0000**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| admission_discharge_date_consistency | issues_found | exact_hit | future_date,id_fragmentation,temporal_inversion | delta | yes | 555 | 0 | 555 | 555 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| billing_amount_non_negative | issues_found | no_truth_or_no_findings | numeric_outlier | delta | yes | 0 | 108 | 0 | 0 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 |
