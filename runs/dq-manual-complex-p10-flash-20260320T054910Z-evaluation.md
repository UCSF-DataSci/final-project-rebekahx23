# Evaluation Report: dq-manual-complex-p10-flash-20260320T054910Z

Generated at: 2026-03-20 05:50:21 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T054910Z.json`
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
- TP: **0**
- FP: **0**
- FN: **0**
- Precision: **0.0000**
- Recall: **0.0000**
- F1: **0.0000**

## Micro Average (Raw Current DB)
- TP: **0**
- FP: **0**
- FN: **0**
- Precision: **0.0000**
- Recall: **0.0000**
- F1: **0.0000**

## Micro Average (Delta vs Baseline)
- TP: **0**
- FP: **0**
- FN: **0**
- Precision: **0.0000**
- Recall: **0.0000**
- F1: **0.0000**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| patient_name_standardization_issues | issues_found | not_evaluable | duplicate_rows,future_date,id_fragmentation,nullify,numeric_outlier,temporal_inversion | raw | no | 0 | 0 | 0 | 0 | 0 | 555 | 0.0000 | 0.0000 | 0.0000 |
| reason(patient_name_standardization_issues) | - | - | - | - | - | - | - | - | - | - | - | - | - | `rowid_query_failed: (sqlite3.OperationalError) incomplete input
[SQL: SELECT rowid AS _dq_rowid FROM healthcare_dataset WHERE name IS NOT NULL AND ( (LOWER(name) != name AND UPPER(name) != name) -- Detects mixed casing OR LOWER(name) LIKE '% md' -- Detects trailing ' MD' OR LOWER(name) LIKE '% dvm' -- Detects trailing ' DVM' OR LOWER(name) LIKE 'mrs.%' -- Detects leading 'Mrs.' OR LOWER(name) LIKE 'mr.%' -- Detects leading 'Mr.' )]
(Background on this error at: https://sqlalche.me/e/20/e3q8)` |
| admission_discharge_date_inconsistencies | query_error | not_evaluable | future_date,id_fragmentation,nullify,numeric_outlier,temporal_inversion,truncate | raw | no | 0 | 0 | 0 | 0 | 0 | 555 | 0.0000 | 0.0000 | 0.0000 |
| reason(admission_discharge_date_inconsistencies) | - | - | - | - | - | - | - | - | - | - | - | - | - | `invalid_sql: Only one SQL statement is allowed.` |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `patient_name_standardization_issues`: `78, 374, 510, 524, 627, 634, 652, 700, 764, 1062, 1072, 1202, 1329, 1525, 1783, 1792, 1799, 1824, 2000, 2200`
- `admission_discharge_date_inconsistencies`: `78, 374, 510, 524, 627, 634, 652, 700, 764, 1062, 1072, 1202, 1329, 1525, 1783, 1792, 1799, 1824, 2000, 2200`
