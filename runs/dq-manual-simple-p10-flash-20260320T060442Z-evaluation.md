# Evaluation Report: dq-manual-simple-p10-flash-20260320T060442Z

Generated at: 2026-03-20 06:05:09 UTC
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
- FP: **553**
- FN: **2149**
- Precision: **0.6675**
- Recall: **0.3406**
- F1: **0.4510**

## Micro Average (Raw Current DB)
- TP: **1110**
- FP: **27531**
- FN: **2149**
- Precision: **0.0388**
- Recall: **0.3406**
- F1: **0.0696**

## Micro Average (Delta vs Baseline)
- TP: **1110**
- FP: **553**
- FN: **2149**
- Precision: **0.6675**
- Recall: **0.3406**
- F1: **0.4510**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| invalid_date_format_check | issues_found | mixed | future_date,id_fragmentation,nullify,temporal_inversion,truncate | delta | yes | 1135 | 0 | 1135 | 1110 | 25 | 2149 | 0.9780 | 0.3406 | 0.5052 |
| hospital_naming_clutter_check | issues_found | false_alarm | enum_encoding_drift | delta | yes | 528 | 26978 | 528 | 0 | 528 | 0 | 0.0000 | 0.0000 | 0.0000 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `invalid_date_format_check`: `43, 76, 135, 149, 177, 198, 202, 226, 315, 336, 365, 387, 444, 463, 469, 501, 535, 555, 584, 592`
