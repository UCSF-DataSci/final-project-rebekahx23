# Evaluation Report: dq-manual-simple-p10-pro-20260320T064052Z

Generated at: 2026-03-20 06:41:59 UTC
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
- FP: **25**
- FN: **3267**
- Precision: **0.9780**
- Recall: **0.2536**
- F1: **0.4028**

## Micro Average (Raw Current DB)
- TP: **1110**
- FP: **25**
- FN: **3267**
- Precision: **0.9780**
- Recall: **0.2536**
- F1: **0.4028**

## Micro Average (Delta vs Baseline)
- TP: **1110**
- FP: **25**
- FN: **3267**
- Precision: **0.9780**
- Recall: **0.2536**
- F1: **0.4028**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| unrealistic_age | issues_found | hit_with_fp | enum_encoding_drift,numeric_outlier | delta | yes | 1135 | 0 | 1135 | 1110 | 25 | 0 | 0.9780 | 1.0000 | 0.9889 |
| invalid_date_format | no_issues_found | missed | future_date,id_fragmentation,nullify,temporal_inversion,truncate | delta | yes | 0 | 0 | 0 | 0 | 0 | 3267 | 0.0000 | 0.0000 | 0.0000 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `invalid_date_format`: `35, 56, 68, 80, 102, 105, 123, 136, 145, 158, 160, 164, 198, 202, 224, 234, 253, 281, 292, 309`
