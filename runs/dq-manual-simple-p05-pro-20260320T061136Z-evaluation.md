# Evaluation Report: dq-manual-simple-p05-pro-20260320T061136Z

Generated at: 2026-03-20 06:13:11 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T061136Z.json`
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
- FP: **44**
- FN: **0**
- Precision: **0.9806**
- Recall: **1.0000**
- F1: **0.9902**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **44**
- FN: **0**
- Precision: **0.9806**
- Recall: **1.0000**
- F1: **0.9902**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **44**
- FN: **0**
- Precision: **0.9806**
- Recall: **1.0000**
- F1: **0.9902**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| age_out_of_bounds | issues_found | hit_with_fp | numeric_outlier | delta | yes | 1129 | 0 | 1129 | 1110 | 19 | 0 | 0.9832 | 1.0000 | 0.9915 |
| invalid_admission_chronology | issues_found | hit_with_fp | code_drift,datetime_shift,future_date,id_fragmentation,temporal_inversion | delta | yes | 1135 | 0 | 1135 | 1110 | 25 | 0 | 0.9780 | 1.0000 | 0.9889 |
