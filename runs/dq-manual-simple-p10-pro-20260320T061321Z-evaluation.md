# Evaluation Report: dq-manual-simple-p10-pro-20260320T061321Z

Generated at: 2026-03-20 06:14:53 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T061136Z.json`
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
- FP: **350**
- FN: **0**
- Precision: **0.7603**
- Recall: **1.0000**
- F1: **0.8638**

## Micro Average (Raw Current DB)
- TP: **1110**
- FP: **18043**
- FN: **0**
- Precision: **0.0580**
- Recall: **1.0000**
- F1: **0.1096**

## Micro Average (Delta vs Baseline)
- TP: **1110**
- FP: **350**
- FN: **0**
- Precision: **0.7603**
- Recall: **1.0000**
- F1: **0.8638**

## Per-Check Metrics
| Test | Query Result | Detection | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| missing_patient_name | issues_found | hit_with_fp | id_fragmentation,nullify | delta | yes | 1130 | 0 | 1130 | 1110 | 20 | 0 | 0.9823 | 1.0000 | 0.9911 |
| malformed_hospital_names | issues_found | false_alarm | enum_encoding_drift | delta | yes | 330 | 17693 | 330 | 0 | 330 | 0 | 0.0000 | 0.0000 | 0.0000 |
