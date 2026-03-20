# Evaluation Report: dq-manual-complex-p10-pro-20260320T051217Z

Generated at: 2026-03-20 05:13:52 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T050803Z.json`
Evaluation mode: `delta_vs_baseline`
Baseline DB: `sqlite:///./runs/db/healthcare_clean.sqlite`

## Micro Average (Selected Mode)
- TP: **555**
- FP: **0**
- FN: **555**
- Precision: **1.0000**
- Recall: **0.5000**
- F1: **0.6667**

## Micro Average (Raw Current DB)
- TP: **1108**
- FP: **54441**
- FN: **2**
- Precision: **0.0199**
- Recall: **0.9982**
- F1: **0.0391**

## Micro Average (Delta vs Baseline)
- TP: **555**
- FP: **0**
- FN: **555**
- Precision: **1.0000**
- Recall: **0.5000**
- F1: **0.6667**

## Per-Check Metrics
| Test | Status | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discharge_before_admission | FAIL | future_date,nullify,temporal_inversion,truncate,unit_mismatch | delta | yes | 555 | 0 | 555 | 555 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| inconsistent_name_capitalization | FAIL | duplicate_rows,enum_encoding_drift,id_fragmentation,nullify,truncate | delta | yes | 0 | 54994 | 0 | 0 | 0 | 555 | 0.0000 | 0.0000 | 0.0000 |
| missed_issue_ids(sample) | - | - | - | - | - | - | - | - | - | - | - | - | `57, 96, 225, 250, 262, 421, 456, 558, 561, 581, 878, 945, 950, 957, 1019, 1080, 1135, 1285, 1301, 1349` |
