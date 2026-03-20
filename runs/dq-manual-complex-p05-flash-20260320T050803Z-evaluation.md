# Evaluation Report: dq-manual-complex-p05-flash-20260320T050803Z

Generated at: 2026-03-20 05:08:46 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T050803Z.json`
Evaluation mode: `delta_vs_baseline`
Baseline DB: `sqlite:///./runs/db/healthcare_clean.sqlite`

## Micro Average (Selected Mode)
- TP: **555**
- FP: **0**
- FN: **0**
- Precision: **1.0000**
- Recall: **1.0000**
- F1: **1.0000**

## Micro Average (Raw Current DB)
- TP: **555**
- FP: **108**
- FN: **0**
- Precision: **0.8371**
- Recall: **1.0000**
- F1: **0.9113**

## Micro Average (Delta vs Baseline)
- TP: **555**
- FP: **0**
- FN: **0**
- Precision: **1.0000**
- Recall: **1.0000**
- F1: **1.0000**

## Per-Check Metrics
| Test | Status | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| discharge_before_admission | FAIL | future_date,id_fragmentation,nullify,temporal_inversion | delta | yes | 555 | 0 | 555 | 555 | 0 | 0 | 1.0000 | 1.0000 | 1.0000 |
| negative_billing_amount | FAIL | nullify,numeric_outlier | delta | yes | 0 | 108 | 0 | 0 | 0 | 0 | 0.0000 | 0.0000 | 0.0000 |
