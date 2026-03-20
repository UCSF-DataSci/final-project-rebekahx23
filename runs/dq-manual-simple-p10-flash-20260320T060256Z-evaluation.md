# Evaluation Report: dq-manual-simple-p10-flash-20260320T060256Z

Generated at: 2026-03-20 06:03:39 UTC
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
- TP: **1110**
- FP: **192**
- FN: **1087**
- Precision: **0.8525**
- Recall: **0.5052**
- F1: **0.6345**

## Micro Average (Raw Current DB)
- TP: **1271**
- FP: **8954**
- FN: **926**
- Precision: **0.1243**
- Recall: **0.5785**
- F1: **0.2046**

## Micro Average (Delta vs Baseline)
- TP: **1110**
- FP: **192**
- FN: **1087**
- Precision: **0.8525**
- Recall: **0.5052**
- F1: **0.6345**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| test_admission_discharge_chronology | issues_found | hit_with_fp | future_date,id_fragmentation,temporal_inversion | delta | yes | 1135 | 0 | 1135 | 1110 | 25 | 0 | 0.9780 | 1.0000 | 0.9889 |
| test_hospital_name_formatting_artifacts | issues_found | mixed | truncate | delta | yes | 167 | 8923 | 167 | 0 | 167 | 1087 | 0.0000 | 0.0000 | 0.0000 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `test_hospital_name_formatting_artifacts`: `76, 177, 202, 336, 387, 444, 469, 501, 535, 555, 639, 657, 742, 904, 992, 1000, 1012, 1013, 1132, 1165`
