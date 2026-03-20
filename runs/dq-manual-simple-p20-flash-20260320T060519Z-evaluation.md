# Evaluation Report: dq-manual-simple-p20-flash-20260320T060519Z

Generated at: 2026-03-20 06:05:45 UTC
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
- FP: **46**
- FN: **1085**
- Precision: **0.9797**
- Recall: **0.6717**
- F1: **0.7970**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **46**
- FN: **1085**
- Precision: **0.9797**
- Recall: **0.6717**
- F1: **0.7970**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **46**
- FN: **1085**
- Precision: **0.9797**
- Recall: **0.6717**
- F1: **0.7970**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| invalid_age_outliers | issues_found | mixed | future_date,id_fragmentation,numeric_outlier | delta | yes | 1139 | 0 | 1139 | 1110 | 29 | 1085 | 0.9745 | 0.5057 | 0.6659 |
| missing_patient_names | issues_found | hit_with_fp | id_fragmentation,nullify | delta | yes | 1127 | 0 | 1127 | 1110 | 17 | 0 | 0.9849 | 1.0000 | 0.9924 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `invalid_age_outliers`: `109, 119, 131, 148, 289, 316, 499, 563, 633, 668, 778, 871, 894, 992, 1021, 1063, 1084, 1238, 1247, 1325`
