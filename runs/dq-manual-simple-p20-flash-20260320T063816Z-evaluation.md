# Evaluation Report: dq-manual-simple-p20-flash-20260320T063816Z

Generated at: 2026-03-20 06:38:59 UTC
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
- FN: **3239**
- Precision: **0.9737**
- Recall: **0.4067**
- F1: **0.5737**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **60**
- FN: **3239**
- Precision: **0.9737**
- Recall: **0.4067**
- F1: **0.5737**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **60**
- FN: **3239**
- Precision: **0.9737**
- Recall: **0.4067**
- F1: **0.5737**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| future_date_of_admission | issues_found | mixed | future_date,id_fragmentation,nullify,numeric_outlier,temporal_inversion | delta | yes | 1140 | 0 | 1140 | 1110 | 30 | 2152 | 0.9737 | 0.3403 | 0.5043 |
| discharge_before_admission_date | issues_found | mixed | future_date,id_fragmentation,nullify,temporal_inversion | delta | yes | 1140 | 0 | 1140 | 1110 | 30 | 1087 | 0.9737 | 0.5052 | 0.6653 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `future_date_of_admission`: `8, 22, 106, 112, 113, 116, 117, 146, 165, 183, 228, 352, 363, 443, 470, 522, 608, 687, 695, 792`
- `discharge_before_admission_date`: `22, 106, 112, 183, 228, 363, 608, 687, 792, 825, 875, 913, 945, 960, 987, 1021, 1114, 1187, 1251, 1278`
