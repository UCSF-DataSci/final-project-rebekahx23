# Evaluation Report: dq-manual-simple-p05-pro-20260320T063904Z

Generated at: 2026-03-20 06:40:41 UTC
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
- TP: **1110**
- FP: **49**
- FN: **2150**
- Precision: **0.9577**
- Recall: **0.3405**
- F1: **0.5024**

## Micro Average (Raw Current DB)
- TP: **1128**
- FP: **1096**
- FN: **2132**
- Precision: **0.5072**
- Recall: **0.3460**
- F1: **0.4114**

## Micro Average (Delta vs Baseline)
- TP: **1110**
- FP: **49**
- FN: **2150**
- Precision: **0.9577**
- Recall: **0.3405**
- F1: **0.5024**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discharge_date_before_admission_date | issues_found | mixed | future_date,id_fragmentation,temporal_inversion,truncate | delta | yes | 1131 | 0 | 1131 | 1110 | 21 | 1063 | 0.9814 | 0.5108 | 0.6719 |
| doctor_name_contains_titles | issues_found | mixed | id_fragmentation,truncate | delta | yes | 28 | 1065 | 28 | 0 | 28 | 1087 | 0.0000 | 0.0000 | 0.0000 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `discharge_date_before_admission_date`: `35, 56, 80, 136, 145, 160, 234, 281, 292, 312, 339, 399, 455, 597, 606, 617, 772, 861, 881, 1203`
- `doctor_name_contains_titles`: `35, 56, 80, 136, 145, 160, 234, 281, 292, 312, 339, 399, 455, 597, 606, 617, 772, 861, 881, 1203`
