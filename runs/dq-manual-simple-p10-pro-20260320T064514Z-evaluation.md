# Evaluation Report: dq-manual-simple-p10-pro-20260320T064514Z

Generated at: 2026-03-20 06:46:36 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T064340Z.json`
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
- FP: **196**
- FN: **2150**
- Precision: **0.8499**
- Recall: **0.3405**
- F1: **0.4862**

## Micro Average (Raw Current DB)
- TP: **1286**
- FP: **8943**
- FN: **1974**
- Precision: **0.1257**
- Recall: **0.3945**
- F1: **0.1907**

## Micro Average (Delta vs Baseline)
- TP: **1110**
- FP: **196**
- FN: **2150**
- Precision: **0.8499**
- Recall: **0.3405**
- F1: **0.4862**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discharge_before_admission | query_error | not_evaluable | future_date,id_fragmentation,temporal_inversion,truncate | raw | no | 0 | 0 | 0 | 0 | 0 | 2173 | 0.0000 | 0.0000 | 0.0000 |
| reason(discharge_before_admission) | - | - | - | - | - | - | - | - | - | - | - | - | - | `invalid_sql: Query must start with SELECT, WITH, or EXPLAIN.` |
| hospital_name_has_inconsistent_formatting | query_error | not_evaluable | id_fragmentation,truncate | raw | no | 0 | 0 | 0 | 0 | 0 | 1087 | 0.0000 | 0.0000 | 0.0000 |
| reason(hospital_name_has_inconsistent_formatting) | - | - | - | - | - | - | - | - | - | - | - | - | - | `invalid_sql: Query must start with SELECT, WITH, or EXPLAIN.` |
| discharge_before_admission | issues_found | mixed | future_date,id_fragmentation,temporal_inversion,truncate | delta | yes | 1136 | 0 | 1136 | 1110 | 26 | 1063 | 0.9771 | 0.5108 | 0.6709 |
| hospital_name_has_inconsistent_formatting | issues_found | mixed | id_fragmentation,truncate | delta | yes | 170 | 8923 | 170 | 0 | 170 | 1087 | 0.0000 | 0.0000 | 0.0000 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `discharge_before_admission`: `2, 65, 79, 103, 156, 187, 192, 195, 213, 217, 253, 305, 311, 325, 330, 339, 348, 360, 399, 401`
- `hospital_name_has_inconsistent_formatting`: `2, 79, 103, 156, 195, 213, 217, 348, 401, 411, 460, 494, 505, 514, 529, 566, 572, 587, 702, 713`
- `discharge_before_admission`: `2, 79, 103, 156, 195, 213, 217, 348, 411, 460, 494, 505, 514, 529, 566, 572, 587, 702, 713, 766`
- `hospital_name_has_inconsistent_formatting`: `2, 79, 103, 156, 195, 213, 217, 348, 401, 411, 460, 494, 505, 514, 529, 566, 572, 587, 702, 713`
