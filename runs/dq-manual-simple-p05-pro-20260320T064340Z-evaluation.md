# Evaluation Report: dq-manual-simple-p05-pro-20260320T064340Z

Generated at: 2026-03-20 06:45:04 UTC
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
- TP: **0**
- FP: **408**
- FN: **4358**
- Precision: **0.0000**
- Recall: **0.0000**
- F1: **0.0000**

## Micro Average (Raw Current DB)
- TP: **389**
- FP: **19724**
- FN: **3969**
- Precision: **0.0193**
- Recall: **0.0893**
- F1: **0.0318**

## Micro Average (Delta vs Baseline)
- TP: **0**
- FP: **408**
- FN: **4358**
- Precision: **0.0000**
- Recall: **0.0000**
- F1: **0.0000**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| hospital_name_formatting_issues | issues_found | mixed | id_fragmentation,truncate | delta | yes | 408 | 19705 | 408 | 0 | 408 | 1087 | 0.0000 | 0.0000 | 0.0000 |
| invalid_date_format | no_issues_found | missed | future_date,id_fragmentation,nullify,temporal_inversion,truncate | delta | yes | 0 | 0 | 0 | 0 | 0 | 3271 | 0.0000 | 0.0000 | 0.0000 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `hospital_name_formatting_issues`: `2, 79, 103, 156, 195, 213, 217, 348, 401, 411, 460, 494, 505, 514, 529, 566, 572, 587, 702, 713`
- `invalid_date_format`: `2, 38, 65, 79, 103, 151, 156, 187, 192, 195, 213, 217, 242, 253, 305, 311, 325, 330, 339, 340`
