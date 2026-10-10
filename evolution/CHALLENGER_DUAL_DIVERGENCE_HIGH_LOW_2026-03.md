# Challenger: Dual-Divergence High-to-Low Rotation

## Rule

When both environment and relay sentiment are `分歧`, a 4-to-6-board
candidate that is not the established market core is downgraded if the same
A-level theme contains independently active fronts at no more than 2 boards.
The low fronts regenerate the formal T-day queue. Established market cores and
themes without qualified low fronts remain under their existing rules.

This is an upstream node-role and candidate-generation change. It is not a
fixed-pool return sorter.

## Paired March replay

| Metric | Parent | Challenger |
|---|---:|---:|
| Signal dates | 22 | 22 |
| Computable trades | 12 | 12 |
| Simple return sum | `+49.172217%` | `+71.585112%` |
| Average trade return | `+4.097685%` | `+5.965426%` |
| Win rate | `75%` | `83.333333%` |
| Compounded return | `+56.369164%` | `+94.046677%` |
| Maximum sequential equity drawdown | `-11.337209%` | `-11.337209%` |

Only 2026-03-30 changes. The parent selected 5-board `603538.SH` and returned
`-6.982033%`. The Challenger regenerated the queue as
`002038.SZ -> 600488.SH`. The first low front failed its T+1 auction and was
skipped; the second passed and returned `+15.430862%`.

The result therefore preserves the frozen-queue auction workflow: it did not
select `600488.SH` directly from its future return.

## Cross-window trigger audit

The predeclared trigger scan reports:

- January: `0` triggers;
- February: `0` triggers;
- March: only `2026-03-30`.

All other March decisions and all January-February development decisions remain
unchanged. The rule is provisionally retained for development, but April and
later non-sealed windows are still required to show that it generalizes beyond
the motivating case.

## Remaining failure

Maximum drawdown does not improve because the 2026-03-12 `000537.SZ` trade
still loses `-11.337209%`. The next Darwin diagnosis should focus on same-board
front differentiation under weak breadth, not further expand this high-to-low
rule.
