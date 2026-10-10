# Challenger: Wait When Candidate Clusters Have No Shared Catalyst

## Diagnosis

The 2026-04-29 queue combined three unrelated T-day reasons into one formal
path: gold-supply-chain/turnaround, AI textile equipment, and liquid-cooling
storage. The resulting first candidate `002210.SZ` passed the auction gate but
returned `-10.416667%`. The problem was upstream mainline construction, not a
missing ranking coefficient.

## Rule

If the T-day candidates do not form a cluster with a concrete shared catalyst,
do not label the mixture as a formal mainline. Keep the individual stocks in
observation and generate an empty formal queue. This uses only T-day reasons,
梯队 and response facts; it does not inspect T+1 or T+2 outcomes.

## Paired April replay

| Metric | Parent after catalyst relation | Challenger |
|---|---:|---:|
| Computed trades | `11` | `10` |
| Simple return sum | `+12.828858%` | `+23.245524%` |
| Win rate | `54.545455%` | `60%` |
| Compounded return | `+10.315406%` | `+23.142778%` |
| Maximum drawdown | `-20.382649%` | `-11.124817%` |

Only `2026-04-29` changes: the mixed candidate pool becomes a wait decision and
the `-10.416667%` trade disappears. This is an upstream regeneration, not an
external post-selection filter, and remains provisional until later non-sealed
months confirm that the cluster test does not suppress valid new themes.
