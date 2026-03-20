# Manual Benchmark Summary (20260320T051550Z)

## Demo Summary Table
| run_id | scenario | model | profile | delta_precision | delta_recall | delta_f1 | prompt_tokens | output_tokens | total_tokens | estimated_cost_usd |
|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| dq-manual-simple-p05-flash-20260320T045722Z | simple | gemini-2.5-flash | P05 | 0.9797 | 0.3370 | 0.5015 | 121042 | 2632 | 129054 | n/a |
| dq-manual-simple-p10-flash-20260320T045820Z | simple | gemini-2.5-flash | P10 | 0.9780 | 0.5043 | 0.6655 | 617580 | 2273 | 622702 | n/a |
| dq-manual-simple-p20-flash-20260320T045919Z | simple | gemini-2.5-flash | P20 | 0.9763 | 0.5066 | 0.6671 | 276785 | 2974 | 284476 | n/a |
| dq-manual-simple-p05-pro-20260320T050019Z | simple | gemini-2.5-pro | P05 | 0.9797 | 0.1696 | 0.2892 | 319389 | 2031 | 325740 | n/a |
| dq-manual-simple-p10-pro-20260320T050147Z | simple | gemini-2.5-pro | P10 | 0.9780 | 0.6705 | 0.7956 | 944703 | 1407 | 949869 | n/a |
| dq-manual-simple-p20-pro-20260320T050445Z | simple | gemini-2.5-pro | P20 | 0.9814 | 0.6705 | 0.7967 | 647008 | 1941 | 652893 | n/a |
| dq-manual-complex-p05-flash-20260320T050803Z | complex | gemini-2.5-flash | P05 | 1.0000 | 1.0000 | 1.0000 | 146887 | 3062 | 153746 | n/a |
| dq-manual-complex-p10-flash-20260320T050856Z | complex | gemini-2.5-flash | P10 | 0.0000 | 0.0000 | 0.0000 | 73674 | 2487 | 81122 | n/a |
| dq-manual-complex-p20-flash-20260320T050952Z | complex | gemini-2.5-flash | P20 | 1.0000 | 0.5000 | 0.6667 | 361029 | 2262 | 368650 | n/a |
| dq-manual-complex-p05-pro-20260320T051054Z | complex | gemini-2.5-pro | P05 | 0.0000 | 0.0000 | 0.0000 | 603329 | 1448 | 608189 | n/a |
| dq-manual-complex-p10-pro-20260320T051217Z | complex | gemini-2.5-pro | P10 | 1.0000 | 0.5000 | 0.6667 | 623046 | 2044 | 630142 | n/a |
| dq-manual-complex-p20-pro-20260320T051402Z | complex | gemini-2.5-pro | P20 | 1.0000 | 0.2517 | 0.4022 | 644268 | 1549 | 649955 | n/a |

## Aggregated (mean over successful runs)
| scenario | model | profile | runs | delta_precision | delta_recall | delta_f1 | total_tokens | cost_usd |
|---|---|---|---:|---:|---:|---:|---:|---:|
| complex | gemini-2.5-flash | P05 | 1 | 1.0000 | 1.0000 | 1.0000 | 153746.0 | n/a |
| complex | gemini-2.5-flash | P10 | 1 | 0.0000 | 0.0000 | 0.0000 | 81122.0 | n/a |
| complex | gemini-2.5-flash | P20 | 1 | 1.0000 | 0.5000 | 0.6667 | 368650.0 | n/a |
| complex | gemini-2.5-pro | P05 | 1 | 0.0000 | 0.0000 | 0.0000 | 608189.0 | n/a |
| complex | gemini-2.5-pro | P10 | 1 | 1.0000 | 0.5000 | 0.6667 | 630142.0 | n/a |
| complex | gemini-2.5-pro | P20 | 1 | 1.0000 | 0.2517 | 0.4022 | 649955.0 | n/a |
| simple | gemini-2.5-flash | P05 | 1 | 0.9797 | 0.3370 | 0.5015 | 129054.0 | n/a |
| simple | gemini-2.5-flash | P10 | 1 | 0.9780 | 0.5043 | 0.6655 | 622702.0 | n/a |
| simple | gemini-2.5-flash | P20 | 1 | 0.9763 | 0.5066 | 0.6671 | 284476.0 | n/a |
| simple | gemini-2.5-pro | P05 | 1 | 0.9797 | 0.1696 | 0.2892 | 325740.0 | n/a |
| simple | gemini-2.5-pro | P10 | 1 | 0.9780 | 0.6705 | 0.7956 | 949869.0 | n/a |
| simple | gemini-2.5-pro | P20 | 1 | 0.9814 | 0.6705 | 0.7967 | 652893.0 | n/a |

## Recommendations
| scenario | model | selected_profile | needs_p50_followup | reason |
|---|---|---|---|---|
| complex | gemini-2.5-flash | P05 | no | recall_plateau |
| complex | gemini-2.5-pro | P10 | no | recall_plateau |
| simple | gemini-2.5-flash | P10 | no | recall_plateau |
| simple | gemini-2.5-pro | P10 | no | recall_plateau |

Recommendation statement:
- For complex issues with gemini-2.5-flash: use P05.
- For complex issues with gemini-2.5-pro: use P10.
- For simple issues with gemini-2.5-flash: use P10.
- For simple issues with gemini-2.5-pro: use P10.
