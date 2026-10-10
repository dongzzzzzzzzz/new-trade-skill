# Challenger: Shared T+1 Open-Gap Floor

## Diagnosis

On 2026-01-29 `601212.SH` closed the signal day at `15.19` and opened T+1 at
`13.67`, a `-10.0066%` gap. The old January manual label still called the
auction `符合预期`, so the replay bought a nearly limit-down open and lost
`-10.021946%`. February and March already used a mechanical `-2%` minimum
opening boundary; January did not.

## Rule

Unless the T-day plan predeclares a stricter candidate-specific boundary, a T+1
open below the T-day close by more than 2% is auction-invalidated. Fresh prices
override stale manual labels. The executor then continues through the frozen
queue.

## Paired replay

| Metric | Parent | Challenger |
|---|---:|---:|
| January computed trades | `3` | `3` |
| Simple return sum | `+14.832271%` | `+24.552330%` |
| Win rate | `66.666667%` | `66.666667%` |
| Compounded return | `+13.093621%` | `+25.310786%` |
| Maximum drawdown | `-10.021946%` | `-0.301887%` |

Only 2026-01-29 changes. `601212.SH` is rejected and the frozen queue falls
through to `600916.SH`, which returns `-0.301887%`. February and March already
enforce the same floor, so no additional execution changes are introduced.
