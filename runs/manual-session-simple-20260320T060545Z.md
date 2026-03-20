# Manual Session Report: SIMPLE (20260320T060545Z)

- Ground truth: `runs/lab-ground-truth-20260320T060203Z.json`
- Total runs attempted: **6**

| run_id | test_id | model | profile | status | delta_precision | delta_recall | delta_f1 | tokens | cost_usd | error_excerpt | error_log |
|---|---|---|---|---|---:|---:|---:|---:|---:|---|---|
| dq-manual-simple-p05-flash-20260320T060203Z | SIMPLE-P05-FLASH | gemini-3-flash-preview | P05 | success | 0.9763 | 0.6717 | 0.7958 | 520612 | n/a |  |  |
| dq-manual-simple-p10-flash-20260320T060256Z | SIMPLE-P10-FLASH | gemini-3-flash-preview | P10 | success | 0.8525 | 0.5052 | 0.6345 | 534827 | n/a |  |  |
| dq-manual-simple-p20-flash-20260320T060349Z | SIMPLE-P20-FLASH | gemini-3-flash-preview | P20 | run_failed | 0.0000 | 0.0000 | 0.0000 | 0 | n/a | Warning: there are non-text parts in the response: ['function_call'], returning concatenated text result from text parts. Check the full candidates.content.parts accessor to get the full model response. Traceback (mos... | runs/dq-manual-simple-p20-flash-20260320T060349Z-run-error.log |
| dq-manual-simple-p05-flash-20260320T060403Z | SIMPLE-P05-FLASH | gemini-3.1-flash-lite-preview | P05 | success | 0.9814 | 0.5113 | 0.6723 | 583256 | n/a |  |  |
| dq-manual-simple-p10-flash-20260320T060442Z | SIMPLE-P10-FLASH | gemini-3.1-flash-lite-preview | P10 | success | 0.6675 | 0.3406 | 0.4510 | 616267 | n/a |  |  |
| dq-manual-simple-p20-flash-20260320T060519Z | SIMPLE-P20-FLASH | gemini-3.1-flash-lite-preview | P20 | success | 0.9797 | 0.6717 | 0.7970 | 626641 | n/a |  |  |
