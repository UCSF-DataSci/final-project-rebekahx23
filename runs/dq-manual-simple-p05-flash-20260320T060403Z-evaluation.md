# Evaluation Report: dq-manual-simple-p05-flash-20260320T060403Z

Generated at: 2026-03-20 06:04:31 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T060203Z.json`
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
- FP: **42**
- FN: **2122**
- Precision: **0.9814**
- Recall: **0.5113**
- F1: **0.6723**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **42**
- FN: **2122**
- Precision: **0.9814**
- Recall: **0.5113**
- F1: **0.6723**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **42**
- FN: **2122**
- Precision: **0.9814**
- Recall: **0.5113**
- F1: **0.6723**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| check_missing_names | issues_found | hit_with_fp | id_fragmentation,nullify | delta | yes | 1127 | 0 | 1127 | 1110 | 17 | 0 | 0.9849 | 1.0000 | 0.9924 |
| check_negative_or_zero_length_of_stay | issues_found | mixed | future_date,id_fragmentation,numeric_outlier,temporal_inversion,truncate | delta | yes | 1135 | 0 | 1135 | 1110 | 25 | 2122 | 0.9780 | 0.3434 | 0.5084 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `check_negative_or_zero_length_of_stay`: `12, 35, 37, 38, 76, 174, 177, 202, 313, 336, 345, 369, 376, 379, 387, 433, 444, 464, 469, 476`
