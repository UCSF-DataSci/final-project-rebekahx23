# Evaluation Report: dq-manual-simple-p10-flash-20260320T063436Z

Generated at: 2026-03-20 06:35:13 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T063344Z.json`
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
- FP: **41**
- FN: **1082**
- Precision: **0.9819**
- Recall: **0.6723**
- F1: **0.7981**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **41**
- FN: **1082**
- Precision: **0.9819**
- Recall: **0.6723**
- F1: **0.7981**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **41**
- FN: **1082**
- Precision: **0.9819**
- Recall: **0.6723**
- F1: **0.7981**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| age_outlier_check | issues_found | mixed | future_date,numeric_outlier,temporal_inversion | delta | yes | 1130 | 0 | 1130 | 1110 | 20 | 1082 | 0.9823 | 0.5064 | 0.6683 |
| discharge_before_admission_date | issues_found | hit_with_fp | future_date,id_fragmentation,temporal_inversion | delta | yes | 1131 | 0 | 1131 | 1110 | 21 | 0 | 0.9814 | 1.0000 | 0.9906 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `age_outlier_check`: `68, 89, 124, 138, 336, 424, 468, 505, 601, 618, 658, 664, 927, 1046, 1108, 1167, 1173, 1181, 1192, 1231`
