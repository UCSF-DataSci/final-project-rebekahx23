# Evaluation Report: dq-manual-simple-p20-flash-20260320T063523Z

Generated at: 2026-03-20 06:36:14 UTC
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
- FP: **33**
- FN: **1086**
- Precision: **0.9854**
- Recall: **0.6715**
- F1: **0.7987**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **33**
- FN: **1086**
- Precision: **0.9854**
- Recall: **0.6715**
- F1: **0.7987**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **33**
- FN: **1086**
- Precision: **0.9854**
- Recall: **0.6715**
- F1: **0.7987**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discharge_date_before_admission_date | issues_found | mixed | future_date,id_fragmentation,nullify,temporal_inversion | delta | yes | 1131 | 0 | 1131 | 1110 | 21 | 1086 | 0.9814 | 0.5055 | 0.6673 |
| patient_name_is_null | issues_found | hit_with_fp | id_fragmentation,nullify | delta | yes | 1122 | 0 | 1122 | 1110 | 12 | 0 | 0.9893 | 1.0000 | 0.9946 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `discharge_date_before_admission_date`: `58, 116, 163, 202, 309, 316, 339, 365, 395, 500, 781, 796, 817, 916, 1014, 1039, 1177, 1275, 1337, 1413`
