# Evaluation Report: dq-manual-complex-p10-flash-20260320T054014Z

Generated at: 2026-03-20 05:41:14 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T054014Z.json`
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
- TP: **555**
- FP: **0**
- FN: **555**
- Precision: **1.0000**
- Recall: **0.5000**
- F1: **0.6667**

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
| discharge_before_admission | issues_found | exact_hit | future_date,id_fragmentation,nullify,temporal_inversion | delta | yes | 555 | 0 | 555 | 555 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| invalid_admission_date_format | no_issues_found | missed | future_date,id_fragmentation,nullify,temporal_inversion,truncate | delta | yes | 0 | 0 | 0 | 0 | 0 | 555 | 0.0000 | 0.0000 | 0.0000 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `invalid_admission_date_format`: `8, 188, 273, 482, 615, 717, 721, 905, 926, 973, 1054, 1159, 1209, 1277, 1437, 1450, 1550, 1591, 1733, 1786`
