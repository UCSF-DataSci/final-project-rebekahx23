# Evaluation Report: dq-manual-simple-p10-flash-20260320T063721Z

Generated at: 2026-03-20 06:38:05 UTC
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
- FP: **53**
- FN: **4309**
- Precision: **0.9767**
- Recall: **0.3400**
- F1: **0.5044**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **53**
- FN: **4309**
- Precision: **0.9767**
- Recall: **0.3400**
- F1: **0.5044**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **53**
- FN: **4309**
- Precision: **0.9767**
- Recall: **0.3400**
- F1: **0.5044**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| age_unrealistic_values | issues_found | mixed | future_date,nullify,numeric_outlier,temporal_inversion | delta | yes | 1133 | 0 | 1133 | 1110 | 23 | 2152 | 0.9797 | 0.3403 | 0.5051 |
| discharge_date_before_admission | issues_found | mixed | future_date,id_fragmentation,nullify,temporal_inversion,truncate | delta | yes | 1140 | 0 | 1140 | 1110 | 30 | 2157 | 0.9737 | 0.3398 | 0.5037 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `age_unrealistic_values`: `22, 68, 106, 112, 183, 197, 228, 231, 363, 387, 416, 452, 489, 574, 590, 596, 599, 608, 626, 680`
- `discharge_date_before_admission`: `22, 41, 99, 106, 111, 112, 142, 183, 228, 239, 242, 280, 363, 382, 501, 566, 608, 687, 707, 792`
