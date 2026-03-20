# Evaluation Report: dq-manual-simple-p05-flash-20260320T060203Z

Generated at: 2026-03-20 06:02:46 UTC
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
- FP: **54**
- FN: **1085**
- Precision: **0.9763**
- Recall: **0.6717**
- F1: **0.7958**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **54**
- FN: **1085**
- Precision: **0.9763**
- Recall: **0.6717**
- F1: **0.7958**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **54**
- FN: **1085**
- Precision: **0.9763**
- Recall: **0.6717**
- F1: **0.7958**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| test_age_physically_possible | issues_found | mixed | future_date,id_fragmentation,numeric_outlier | delta | yes | 1139 | 0 | 1139 | 1110 | 29 | 1085 | 0.9745 | 0.5057 | 0.6659 |
| test_admission_discharge_chronology | issues_found | hit_with_fp | code_drift,future_date,id_fragmentation,temporal_inversion | delta | yes | 1135 | 0 | 1135 | 1110 | 25 | 0 | 0.9780 | 1.0000 | 0.9889 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `test_age_physically_possible`: `109, 119, 131, 148, 289, 316, 499, 563, 633, 668, 778, 871, 894, 992, 1021, 1063, 1084, 1238, 1247, 1325`
