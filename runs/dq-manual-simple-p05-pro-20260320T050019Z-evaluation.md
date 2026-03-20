# Evaluation Report: dq-manual-simple-p05-pro-20260320T050019Z

Generated at: 2026-03-20 05:01:37 UTC
Ground truth: `/Users/rebekahxing/final-project-rebekahx23/runs/lab-ground-truth-20260320T045722Z.json`
Evaluation mode: `delta_vs_baseline`
Baseline DB: `sqlite:///./runs/db/healthcare_clean.sqlite`

## Micro Average (Selected Mode)
- TP: **1110**
- FP: **23**
- FN: **5434**
- Precision: **0.9797**
- Recall: **0.1696**
- F1: **0.2892**

## Micro Average (Raw Current DB)
- TP: **1110**
- FP: **23**
- FN: **5434**
- Precision: **0.9797**
- Recall: **0.1696**
- F1: **0.2892**

## Micro Average (Delta vs Baseline)
- TP: **1110**
- FP: **23**
- FN: **5434**
- Precision: **0.9797**
- Recall: **0.1696**
- F1: **0.2892**

## Per-Check Metrics
| Test | Status | Scope | Mode | Evaluable | Pred | Base Pred | Delta Pred | TP | FP | FN | Precision | Recall | F1 |
|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| invalid_date_format | PASS | future_date,id_fragmentation,nullify,temporal_inversion,truncate | delta | yes | 0 | 0 | 0 | 0 | 0 | 3272 | 0.0000 | 0.0000 | 0.0000 |
| missed_issue_ids(sample) | - | - | - | - | - | - | - | - | - | - | - | - | `18, 22, 35, 65, 87, 123, 145, 146, 171, 228, 248, 261, 275, 276, 299, 348, 355, 371, 400, 407` |
| discharge_before_admission | FAIL | future_date,id_fragmentation,nullify,temporal_inversion,truncate | delta | yes | 1133 | 0 | 1133 | 1110 | 23 | 2162 | 0.9797 | 0.3392 | 0.5040 |
| missed_issue_ids(sample) | - | - | - | - | - | - | - | - | - | - | - | - | `18, 22, 35, 65, 87, 145, 146, 228, 276, 348, 355, 371, 400, 407, 418, 424, 429, 455, 479, 497` |
