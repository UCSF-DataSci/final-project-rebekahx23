# Evaluation Report: dq-manual-simple-p20-pro-20260320T061503Z

Generated at: 2026-03-20 06:16:27 UTC
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
- TP: **1387**
- FP: **19**
- FN: **5145**
- Precision: **0.9865**
- Recall: **0.2123**
- F1: **0.3495**

## Micro Average (Raw Current DB)
- TP: **2513**
- FP: **13418**
- FN: **4019**
- Precision: **0.1577**
- Recall: **0.3847**
- F1: **0.2237**

## Micro Average (Delta vs Baseline)
- TP: **1387**
- FP: **19**
- FN: **5145**
- Precision: **0.9865**
- Recall: **0.2123**
- F1: **0.3495**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| invalid_age_bounds | issues_found | hit_with_fp | id_fragmentation,numeric_outlier | delta | yes | 1129 | 0 | 1129 | 1110 | 19 | 0 | 0.9832 | 1.0000 | 0.9915 |
| malformed_hospital_names | issues_found | partial_recall | all_corruptions | delta | yes | 277 | 14525 | 277 | 277 | 0 | 5145 | 1.0000 | 0.0511 | 0.0972 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `malformed_hospital_names`: `1, 8, 12, 31, 41, 49, 58, 62, 66, 72, 79, 89, 95, 111, 115, 122, 126, 129, 147, 165`
