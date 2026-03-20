# Evaluation Report: dq-manual-complex-p50-pro-20260320T062506Z

Generated at: 2026-03-20 06:27:13 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T062506Z.json`
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
- FN: **548**
- Precision: **1.0000**
- Recall: **0.5032**
- F1: **0.6695**

## Micro Average (Raw Current DB)
- TP: **555**
- FP: **14525**
- FN: **548**
- Precision: **0.0368**
- Recall: **0.5032**
- F1: **0.0686**

## Micro Average (Delta vs Baseline)
- TP: **555**
- FP: **0**
- FN: **548**
- Precision: **1.0000**
- Recall: **0.5032**
- F1: **0.6695**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discharge_before_admission | issues_found | partial_recall | enum_encoding_drift,future_date,id_fragmentation,nullify,temporal_inversion,truncate | delta | yes | 555 | 0 | 555 | 555 | 0 | 548 | 1.0000 | 0.5032 | 0.6695 |
| hospital_name_formatting_artifacts | issues_found | no_truth_or_no_findings | id_fragmentation,truncate | delta | yes | 0 | 14525 | 0 | 0 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 |

## Missed Issue IDs (Sample, Up To 20 Per Check)
- `discharge_before_admission`: `117, 177, 208, 242, 282, 334, 371, 384, 570, 729, 781, 1071, 1206, 1261, 1535, 1597, 1626, 1728, 1742, 1848`
