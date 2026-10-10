# Challenger: Limit-Open Execution Reachability

## Problem

The skill already required one-price or otherwise unreachable candidates to be
skipped in frozen-queue order. The replay executor nevertheless treated a
positive opening volume as proof that the user's order could buy a stock whose
09:20 price, 09:24 price, and T+1 open were all locked at the exchange limit-up
price. That created non-executable fills and overstated historical returns.

## Rule

Use only the T-day close, board-specific price-limit rule, and T+1 auction facts.
If the 09:20 price, 09:24 price, and open all match the theoretical limit-up
price, mark the candidate `不可交易` and continue through the frozen queue. The
rule changes only execution reachability; it never changes the T-day candidates
or their order.

## Cross-window replay

| Window | Parent | Challenger | Effect |
|---|---:|---:|---|
| February simple return | `+63.832304%` | `+45.900969%` | Removes a false `+10.003216%` fill; executable fallback loses `-7.928118%` |
| February win rate | `100%` | `85.714286%` | Exposes a real upstream candidate-generation failure on 2026-02-10 |
| March simple return | `+71.585112%` | `+82.533949%` | Frozen-queue fallbacks improve 2026-03-05 and 2026-03-12 |
| March win rate | `83.333333%` | `91.666667%` | Eleven of twelve executable trades win |
| March max drawdown | `-11.337209%` | `-4.418727%` | 2026-03-12 false fill is removed |

Changed executions:

- `2026-02-10`: `603533.SH` is locked at limit-up; skip `001330.SZ`, also locked,
  then execute `300182.SZ`.
- `2026-03-05`: skip limit-locked `000533.SZ`, execute `002498.SZ`.
- `2026-03-12`: skip limit-locked `000537.SZ`, execute `600726.SH`.

The February metric decline is not a reason to revert. A result that assumes an
unreachable fill is not eligible for Darwin profitability comparison. This is a
correctness gate, and the newly visible 2026-02-10 loss becomes the next upstream
diagnosis target.

## Remaining validation

January records contain the same false-fill risk but were built with an older,
manual auction materialization. January must be rematerialized from a queue-only
auction cache before its prior return metrics can be compared with this rule.
