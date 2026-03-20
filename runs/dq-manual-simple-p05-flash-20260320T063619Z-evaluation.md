# Evaluation Report: dq-manual-simple-p05-flash-20260320T063619Z

Generated at: 2026-03-20 06:37:10 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T063619Z.json`
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
- FP: **60**
- FN: **2174**
- Precision: **0.9737**
- Recall: **0.5052**
- F1: **0.6653**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **60**
- FN: **2174**
- Precision: **0.9737**
- Recall: **0.5052**
- F1: **0.6653**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **60**
- FN: **2174**
- Precision: **0.9737**
- Recall: **0.5052**
- F1: **0.6653**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| admission_discharge_date_order_validity | issues_found | mixed | future_date,id_fragmentation,nullify,temporal_inversion | delta | yes | 1140 | 0 | 1140 | 1110 | 30 | 1087 | 0.9737 | 0.5052 | 0.6653 |
| admission_date_not_in_future | issues_found | mixed | future_date,id_fragmentation,nullify,temporal_inversion | delta | yes | 1140 | 0 | 1140 | 1110 | 30 | 1087 | 0.9737 | 0.5052 | 0.6653 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `admission_discharge_date_order_validity`: `22, 106, 112, 183, 228, 363, 608, 687, 792, 825, 875, 913, 945, 960, 987, 1021, 1114, 1187, 1251, 1278`
- `admission_date_not_in_future`: `22, 106, 112, 183, 228, 363, 608, 687, 792, 825, 875, 913, 945, 960, 987, 1021, 1114, 1187, 1251, 1278`
