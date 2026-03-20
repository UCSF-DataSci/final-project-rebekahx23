# Evaluation Report: dq-manual-simple-p05-flash-20260320T063109Z

Generated at: 2026-03-20 06:31:50 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T063109Z.json`
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
- FN: **1089**
- Precision: **0.9767**
- Recall: **0.6709**
- F1: **0.7954**

## Micro Average (Raw Current DB)
- TP: **2220**
- FP: **53**
- FN: **1089**
- Precision: **0.9767**
- Recall: **0.6709**
- F1: **0.7954**

## Micro Average (Delta vs Baseline)
- TP: **2220**
- FP: **53**
- FN: **1089**
- Precision: **0.9767**
- Recall: **0.6709**
- F1: **0.7954**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| age_exceeds_plausible_human_lifespan | issues_found | mixed | future_date,numeric_outlier,temporal_inversion | delta | yes | 1140 | 0 | 1140 | 1110 | 30 | 1089 | 0.9737 | 0.5048 | 0.6649 |
| admission_or_discharge_date_invalid | issues_found | hit_with_fp | future_date,id_fragmentation,temporal_inversion | delta | yes | 1133 | 0 | 1133 | 1110 | 23 | 0 | 0.9797 | 1.0000 | 0.9897 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `age_exceeds_plausible_human_lifespan`: `22, 97, 129, 197, 205, 366, 407, 498, 598, 613, 615, 623, 657, 666, 702, 823, 929, 982, 986, 995`
