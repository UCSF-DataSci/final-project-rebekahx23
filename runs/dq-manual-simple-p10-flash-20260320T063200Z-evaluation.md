# Evaluation Report: dq-manual-simple-p10-flash-20260320T063200Z

Generated at: 2026-03-20 06:32:46 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T063109Z.json`
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
- FP: **53**
- FN: **3231**
- Precision: **0.9767**
- Recall: **0.4073**
- F1: **0.5748**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **53**
- FN: **3231**
- Precision: **0.9767**
- Recall: **0.4073**
- F1: **0.5748**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **53**
- FN: **3231**
- Precision: **0.9767**
- Recall: **0.4073**
- F1: **0.5748**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| age_outlier | issues_found | mixed | id_fragmentation,nullify,numeric_outlier | delta | yes | 1140 | 0 | 1140 | 1110 | 30 | 1077 | 0.9737 | 0.5075 | 0.6673 |
| discharge_before_admission_date | issues_found | mixed | future_date,id_fragmentation,nullify,temporal_inversion,truncate | delta | yes | 1133 | 0 | 1133 | 1110 | 23 | 2154 | 0.9797 | 0.3401 | 0.5049 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `age_outlier`: `21, 69, 107, 204, 234, 274, 302, 452, 585, 602, 614, 698, 714, 746, 801, 938, 989, 1034, 1104, 1121`
- `discharge_before_admission_date`: `2, 12, 21, 39, 69, 103, 107, 152, 153, 162, 186, 196, 204, 234, 274, 276, 302, 390, 419, 452`
