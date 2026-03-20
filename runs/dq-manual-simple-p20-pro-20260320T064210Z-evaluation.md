# Evaluation Report: dq-manual-simple-p20-pro-20260320T064210Z

Generated at: 2026-03-20 06:43:36 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T063903Z.json`
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
- FN: **1063**
- Precision: **0.9797**
- Recall: **0.6762**
- F1: **0.8001**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **46**
- FN: **1063**
- Precision: **0.9797**
- Recall: **0.6762**
- F1: **0.8001**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **46**
- FN: **1063**
- Precision: **0.9797**
- Recall: **0.6762**
- F1: **0.8001**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| unrealistic_age | issues_found | hit_with_fp | enum_encoding_drift,id_fragmentation,numeric_outlier | delta | yes | 1135 | 0 | 1135 | 1110 | 25 | 0 | 0.9780 | 1.0000 | 0.9889 |
| discharge_before_admission | issues_found | mixed | future_date,id_fragmentation,temporal_inversion,truncate | delta | yes | 1131 | 0 | 1131 | 1110 | 21 | 1063 | 0.9814 | 0.5108 | 0.6719 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `discharge_before_admission`: `35, 56, 80, 136, 145, 160, 234, 281, 292, 312, 339, 399, 455, 597, 606, 617, 772, 861, 881, 1203`
