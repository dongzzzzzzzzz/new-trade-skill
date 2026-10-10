# Challenger: Specific Mainline Relation Before Broad Concept Fallback

## Diagnosis

The May replay exposed three upstream candidate-generation errors:

- On `2026-05-07`, the queue placed `600673.SH` ahead of the more direct
  liquid-cooling/thermal-management candidate `603158.SH`.
- On `2026-05-08`, `002491.SZ` was moved behind broader compute candidates;
  it was untradeable that morning, so the queue change did not alter execution.
- On `2026-05-19`, `300657.SZ` had a broad compute label but no direct
  liquid-cooling relation. It should not have been a formal fallback after the
  direct candidates were locked.

This is candidate-pool and original-queue generation, not post-selection
sorting. The challenger regenerates the queue before T+1 auction facts are
read.

## Rule

Within a confirmed mainline, candidates with direct A-level catalyst,
industry, or funding-response evidence are formal before broad-concept
followers. A broad label cannot make a stock a formal recursive fallback. If
the direct candidates are all untradeable, the result can be no trade.

## May replay

| Metric | Current skill | Challenger |
|---|---:|---:|
| Computed trades | `6` | `5` |
| Simple return sum | `-4.510361%` | `+9.019487%` |
| Win rate | `33.333333%` | `60%` |
| Compounded return | `-5.257891%` | `+8.971269%` |
| Maximum drawdown | `-12.159634%` | `-3.363068%` |

The `2026-05-07` execution changes from `600673.SH` (`-6.233948%`) to
`603158.SH` (`+0.253646%`). The `2026-05-19` broad follower is removed, so
the locked direct candidates produce no trade instead of a `-7.042254%`
fallback loss. The `2026-05-08` queue changes but execution remains
`002929.SZ` because `002491.SZ` is limit-locked and untradeable.

The T+2 prices used for the Challenger are fetched only for its actual
executions. The separate all-queue diagnostic prices are kept outside the
strategy replay and did not influence any decision.

This is a provisional May generalization result. It must be checked on more
non-sealed months before the rule is treated as stable, and it does not use
the sealed September-October set.
