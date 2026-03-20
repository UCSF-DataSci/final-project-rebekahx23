# Evaluation Report: dq-manual-complex-p10-pro-20260320T061835Z

Generated at: 2026-03-20 06:20:18 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T061657Z.json`
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
- TP: **555**
- FP: **0**
- FN: **555**
- Precision: **1.0000**
- Recall: **0.5000**
- F1: **0.6667**

## Micro Average (Raw Current DB)
- TP: **1110**
- FP: **54945**
- FN: **0**
- Precision: **0.0198**
- Recall: **1.0000**
- F1: **0.0388**

## Micro Average (Delta vs Baseline)
- TP: **555**
- FP: **0**
- FN: **555**
- Precision: **1.0000**
- Recall: **0.5000**
- F1: **0.6667**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discharge_before_admission | issues_found | exact_hit | future_date,id_fragmentation,temporal_inversion | delta | yes | 555 | 0 | 555 | 555 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| unrounded_billing_amount | issues_found | missed | enum_encoding_drift,id_fragmentation,numeric_outlier | delta | yes | 0 | 55500 | 0 | 0 | 0 | 555 | 0.0000 | 0.0000 | 0.0000 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `unrounded_billing_amount`: `20, 194, 247, 347, 355, 495, 523, 661, 849, 895, 1378, 1429, 1477, 1643, 1669, 1778, 1953, 2155, 2265, 2402`
