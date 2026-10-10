# Challenger: Weak-Repair Last-Minute Spike

## Diagnosis

On 2026-01-21 the market and relay sentiment were both only `修复`, not an
attack state. The market-core head of the frozen queue was limit-locked and
unreachable. The next candidate, branch front `601616.SH`, moved from `6.19`
at 09:24 to `6.66` at the open, a `+7.593%` final-minute jump, and opened
`+9.36%` above the T-day close. The old record already called it
`超预期但高风险` but still retained it as fallback. The executable replay then
bought it and lost `-14.864865%`.

## Rule

When both environment and sentiment are exactly `修复`, a non-market-core
candidate is auction-invalidated if the 09:24-to-open jump is at least 5% and
the final opening gap is at least 8%. A last-minute spike is not independent
acceptance in a weak repair state.

This changes only T+1 auction validation. It does not alter the T-day queue or
use T+2 return data.

## Paired replay

| Metric | Executable parent | Challenger |
|---|---:|---:|
| January computed trades | `4` | `3` |
| Simple return sum | `-0.032594%` | `+14.832271%` |
| Win rate | `50%` | `66.666667%` |
| Compounded return | `-3.717593%` | `+13.093621%` |
| Maximum drawdown | `-10.021946%` | `-10.021946%` |

Only 2026-01-21 changes. February and March contain no trigger. The remaining
January loss is 2026-01-29 `601212.SH -10.021946%`.
