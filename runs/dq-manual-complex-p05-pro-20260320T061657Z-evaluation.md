# Evaluation Report: dq-manual-complex-p05-pro-20260320T061657Z

Generated at: 2026-03-20 06:18:25 UTC
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
- FN: **1647**
- Precision: **1.0000**
- Recall: **0.2520**
- F1: **0.4026**

## Micro Average (Raw Current DB)
- TP: **1001**
- FP: **14079**
- FN: **1201**
- Precision: **0.0664**
- Recall: **0.4546**
- F1: **0.1158**

## Micro Average (Delta vs Baseline)
- TP: **555**
- FP: **0**
- FN: **1647**
- Precision: **1.0000**
- Recall: **0.2520**
- F1: **0.4026**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hospital_name_malformed_string_check | issues_found | missed | all_corruptions | delta | yes | 0 | 14525 | 0 | 0 | 0 | 1647 | 0.0000 | 0.0000 | 0.0000 |
| discharge_date_after_admission_check | issues_found | exact_hit | future_date,temporal_inversion | delta | yes | 555 | 0 | 555 | 555 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `hospital_name_malformed_string_check`: `13, 20, 60, 98, 106, 154, 171, 174, 180, 194, 247, 310, 345, 347, 353, 355, 371, 378, 495, 503`
