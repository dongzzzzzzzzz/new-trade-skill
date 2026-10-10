# Challenger: Residual Extreme-Loss Effects Cap the Environment at Repair

## Diagnosis

The previous trading day before `2026-06-01` had a `71.171662%` down ratio
and `50` limit-down stocks. On `2026-06-01`, breadth and limit-ups rebounded,
but `21` stocks were still limit-down while the Shanghai Composite and ChiNext
both remained negative. The replay called this `进攻`; the facts only supported
an incomplete repair.

The wrong environment label kept the four-board electricity candidate
`000539.SZ` formal. Reclassifying the day as repair activates the existing
repair-day high-continuation downgrade and regenerates the low-front queue.

## Rule

If the previous trading day has at least a `70%` down ratio and at least `20`
limit-down stocks, while the current day still has at least `10` limit-down
stocks, the current environment cannot be `进攻`. Improved breadth can support
`修复`; weak breadth remains `分歧/退潮`. Attack requires residual losses to
contract and at least three of index, breadth, turnover, and short-line cores
to improve together.

## June replay

| Metric | Parent | Challenger |
|---|---:|---:|
| Computed trades | `8` | `8` |
| Simple return sum | `+23.310380%` | `+26.698641%` |
| Win rate | `75%` | `75%` |
| Compounded return | `+24.534804%` | `+29.078229%` |
| Maximum drawdown | `-7.128099%` | `-3.739837%` |

Only `2026-06-01` changes. The queue is regenerated from
`000539.SZ -> 002608.SZ -> 000767.SZ` to `002608.SZ -> 000767.SZ`.
The first low candidate fails auction and `000767.SZ` executes, replacing the
`-7.128099%` trade with `-3.739837%`.

Across February-June market facts, the same extreme-loss-residual condition
also appears on `2026-03-04`, `2026-06-11`, `2026-06-12`, and `2026-06-29`.
Those dates are already classified as retreat, divergence, or repair; no other
attack day is suppressed. September-October remains sealed.
