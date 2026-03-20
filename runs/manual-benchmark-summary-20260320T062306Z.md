# Manual Benchmark Summary (20260320T062306Z)

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
| dq-manual-complex-p10-flash-20260320T054014Z | complex | gemini-2.5-flash | P10 | 1.0000 | 0.5000 | 0.6667 | 291134 | 2190 | 301217 | n/a |
| dq-manual-complex-p20-flash-20260320T054124Z | complex | gemini-2.5-flash | P20 | 1.0000 | 1.0000 | 1.0000 | 486164 | 2368 | 494582 | n/a |
| dq-manual-complex-p50-flash-20260320T054229Z | complex | gemini-2.5-flash | P50 | 1.0000 | 1.0000 | 1.0000 | 497932 | 2194 | 504574 | n/a |
| dq-manual-complex-p10-pro-20260320T054327Z | complex | gemini-2.5-pro | P10 | 1.0000 | 1.0000 | 1.0000 | 151896 | 1870 | 158417 | n/a |
| dq-manual-complex-p20-pro-20260320T054458Z | complex | gemini-2.5-pro | P20 | 0.0000 | 0.0000 | 0.0000 | 363680 | 2413 | 370590 | n/a |
| dq-manual-complex-p50-pro-20260320T054633Z | complex | gemini-2.5-pro | P50 | 0.5000 | 1.0000 | 0.6667 | 657629 | 1993 | 664129 | n/a |
| dq-manual-simple-p05-flash-20260320T060203Z | simple | gemini-3-flash-preview | P05 | 0.9763 | 0.6717 | 0.7958 | 515805 | 2157 | 520612 | n/a |
| dq-manual-simple-p10-flash-20260320T060256Z | simple | gemini-3-flash-preview | P10 | 0.8525 | 0.5052 | 0.6345 | 530143 | 2329 | 534827 | n/a |
| dq-manual-simple-p20-flash-20260320T060349Z | simple | gemini-3-flash-preview | P20 | 0.0000 | 0.0000 | 0.0000 | 0 | 0 | 0 | n/a |
| dq-manual-simple-p05-flash-20260320T060403Z | simple | gemini-3.1-flash-lite-preview | P05 | 0.9814 | 0.5113 | 0.6723 | 581206 | 2050 | 583256 | n/a |
| dq-manual-simple-p10-flash-20260320T060442Z | simple | gemini-3.1-flash-lite-preview | P10 | 0.6675 | 0.3406 | 0.4510 | 613687 | 2580 | 616267 | n/a |
| dq-manual-simple-p20-flash-20260320T060519Z | simple | gemini-3.1-flash-lite-preview | P20 | 0.9797 | 0.6717 | 0.7970 | 624522 | 2119 | 626641 | n/a |
| dq-manual-simple-p05-pro-20260320T061136Z | simple | gemini-3.1-pro-preview | P05 | 0.9806 | 1.0000 | 0.9902 | 927662 | 2039 | 933580 | n/a |
| dq-manual-simple-p10-pro-20260320T061321Z | simple | gemini-3.1-pro-preview | P10 | 0.7603 | 1.0000 | 0.8638 | 603922 | 2526 | 610269 | n/a |
| dq-manual-simple-p20-pro-20260320T061503Z | simple | gemini-3.1-pro-preview | P20 | 0.9865 | 0.2123 | 0.3495 | 640769 | 2247 | 646241 | n/a |
| dq-manual-complex-p05-pro-20260320T061657Z | complex | gemini-3.1-pro-preview | P05 | 1.0000 | 0.2520 | 0.4026 | 598665 | 2569 | 604815 | n/a |
| dq-manual-complex-p10-pro-20260320T061835Z | complex | gemini-3.1-pro-preview | P10 | 1.0000 | 0.5000 | 0.6667 | 938590 | 2322 | 944725 | n/a |
| dq-manual-complex-p20-pro-20260320T062028Z | complex | gemini-3.1-pro-preview | P20 | 1.0000 | 1.0000 | 1.0000 | 635378 | 2187 | 641462 | n/a |

## Aggregated (mean over successful runs)
| scenario | model | profile | runs | delta_precision | delta_recall | delta_f1 | total_tokens | cost_usd |
|---|---|---|---:|---:|---:|---:|---:|---:|
| complex | gemini-2.5-flash | P05 | 1 | 1.0000 | 1.0000 | 1.0000 | 153746.0 | n/a |
| complex | gemini-2.5-flash | P10 | 2 | 0.5000 | 0.2500 | 0.3333 | 191169.5 | n/a |
| complex | gemini-2.5-flash | P20 | 2 | 1.0000 | 0.7500 | 0.8333 | 431616.0 | n/a |
| complex | gemini-2.5-flash | P50 | 1 | 1.0000 | 1.0000 | 1.0000 | 504574.0 | n/a |
| complex | gemini-2.5-pro | P05 | 1 | 0.0000 | 0.0000 | 0.0000 | 608189.0 | n/a |
| complex | gemini-2.5-pro | P10 | 2 | 1.0000 | 0.7500 | 0.8333 | 394279.5 | n/a |
| complex | gemini-2.5-pro | P20 | 2 | 0.5000 | 0.1259 | 0.2011 | 510272.5 | n/a |
| complex | gemini-2.5-pro | P50 | 1 | 0.5000 | 1.0000 | 0.6667 | 664129.0 | n/a |
| complex | gemini-3.1-pro-preview | P05 | 1 | 1.0000 | 0.2520 | 0.4026 | 604815.0 | n/a |
| complex | gemini-3.1-pro-preview | P10 | 1 | 1.0000 | 0.5000 | 0.6667 | 944725.0 | n/a |
| complex | gemini-3.1-pro-preview | P20 | 1 | 1.0000 | 1.0000 | 1.0000 | 641462.0 | n/a |
| simple | gemini-2.5-flash | P05 | 1 | 0.9797 | 0.3370 | 0.5015 | 129054.0 | n/a |
| simple | gemini-2.5-flash | P10 | 1 | 0.9780 | 0.5043 | 0.6655 | 622702.0 | n/a |
| simple | gemini-2.5-flash | P20 | 1 | 0.9763 | 0.5066 | 0.6671 | 284476.0 | n/a |
| simple | gemini-2.5-pro | P05 | 1 | 0.9797 | 0.1696 | 0.2892 | 325740.0 | n/a |
| simple | gemini-2.5-pro | P10 | 1 | 0.9780 | 0.6705 | 0.7956 | 949869.0 | n/a |
| simple | gemini-2.5-pro | P20 | 1 | 0.9814 | 0.6705 | 0.7967 | 652893.0 | n/a |
| simple | gemini-3-flash-preview | P05 | 1 | 0.9763 | 0.6717 | 0.7958 | 520612.0 | n/a |
| simple | gemini-3-flash-preview | P10 | 1 | 0.8525 | 0.5052 | 0.6345 | 534827.0 | n/a |
| simple | gemini-3.1-flash-lite-preview | P05 | 1 | 0.9814 | 0.5113 | 0.6723 | 583256.0 | n/a |
| simple | gemini-3.1-flash-lite-preview | P10 | 1 | 0.6675 | 0.3406 | 0.4510 | 616267.0 | n/a |
| simple | gemini-3.1-flash-lite-preview | P20 | 1 | 0.9797 | 0.6717 | 0.7970 | 626641.0 | n/a |
| simple | gemini-3.1-pro-preview | P05 | 1 | 0.9806 | 1.0000 | 0.9902 | 933580.0 | n/a |
| simple | gemini-3.1-pro-preview | P10 | 1 | 0.7603 | 1.0000 | 0.8638 | 610269.0 | n/a |
| simple | gemini-3.1-pro-preview | P20 | 1 | 0.9865 | 0.2123 | 0.3495 | 646241.0 | n/a |

## Recommendations
| scenario | model | selected_profile | needs_p50_followup | reason |
|---|---|---|---|---|
| complex | gemini-2.5-flash | P05 | no | recall_plateau |
| complex | gemini-2.5-pro | P50 | no | recall_plateau |
| complex | gemini-3.1-pro-preview | P20 | yes | recall_plateau |
| simple | gemini-2.5-flash | P10 | no | recall_plateau |
| simple | gemini-2.5-pro | P10 | no | recall_plateau |
| simple | gemini-3-flash-preview | P05 | no | recall_plateau |
| simple | gemini-3.1-flash-lite-preview | P20 | yes | recall_plateau |
| simple | gemini-3.1-pro-preview | P05 | no | recall_plateau |

Recommendation statement:
- For complex issues with gemini-2.5-flash: use P05.
- For complex issues with gemini-2.5-pro: use P50.
- For complex issues with gemini-3.1-pro-preview: use P20 (run P50 follow-up).
- For simple issues with gemini-2.5-flash: use P10.
- For simple issues with gemini-2.5-pro: use P10.
- For simple issues with gemini-3-flash-preview: use P05.
- For simple issues with gemini-3.1-flash-lite-preview: use P20 (run P50 follow-up).
- For simple issues with gemini-3.1-pro-preview: use P05.
