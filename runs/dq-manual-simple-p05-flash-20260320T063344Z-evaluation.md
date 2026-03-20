# Evaluation Report: dq-manual-simple-p05-flash-20260320T063344Z

Generated at: 2026-03-20 06:34:25 UTC
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
- FN: **2151**
- Precision: **0.9819**
- Recall: **0.5079**
- F1: **0.6695**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **41**
- FN: **2151**
- Precision: **0.9819**
- Recall: **0.5079**
- F1: **0.6695**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **41**
- FN: **2151**
- Precision: **0.9819**
- Recall: **0.5079**
- F1: **0.6695**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| age_unrealistic_value | issues_found | hit_with_fp | id_fragmentation,numeric_outlier | delta | yes | 1130 | 0 | 1130 | 1110 | 20 | 0 | 0.9823 | 1.0000 | 0.9911 |
| discharge_before_admission_date | issues_found | mixed | future_date,id_fragmentation,nullify,temporal_inversion,truncate | delta | yes | 1131 | 0 | 1131 | 1110 | 21 | 2151 | 0.9814 | 0.3404 | 0.5055 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `discharge_before_admission_date`: `35, 58, 82, 116, 121, 163, 188, 194, 197, 202, 309, 316, 339, 365, 370, 395, 404, 442, 474, 500`
