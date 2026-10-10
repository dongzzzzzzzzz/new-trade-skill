# January 2026 Baseline Status

This is a provisional baseline generated from the current `SKILL.md`. It is not
an optimization result and must not be treated as proof of profitability.

## Covered Cases

| Signal dates | Cases | Executed and computable | Empty/wait | Selected but unverifiable |
|---|---:|---:|---:|---:|
| 2026-01-06 to 2026-01-23 | 14 | 8 | 4 | 2 |

The eight computable trades use the required timing:

`T+1 open buy -> T+2 09:25 auction sell`

Their simple return sum is `69.82571%`, average return is `8.72821%`, and all
eight are positive. This sample is still too small to support a performance
claim or an optimization claim.

The 2026-01-12 case selected the highest core after a valid T+1 auction, but the
T+1 daily open and T+2 auction price are missing from the independent raw price
chain. The 2026-01-22 case has a missing T+2 auction price. Both are excluded
from the return denominator and retained as execution/data-quality cases.

The 2026-01-13 through 2026-01-16 cases are recorded as empty/waiting days
because broad negative feedback, limit-down expansion, and weak core feedback
failed the environment and sentiment gates. They are not silently removed from
the replay.

## Replay manifest

The complete January baseline is the union of these files, read in signal-date
order:

- `replay_baseline_2026-01.jsonl`
- `replay_baseline_2026-01_addendum.jsonl`
- `replay_baseline_2026-01_addendum_2.jsonl`
- `replay_baseline_2026-01_addendum_3.jsonl`

The addendum files are part of the baseline, not optional notes. Any Challenger
must replay all 14 cases and regenerate every downstream field when an upstream
step changes.

## Integrity Checks

- T-day decisions are frozen before T+1 auction facts.
- Auction decisions use only 09:25-or-earlier auction fields.
- T+2 prices are never replaced with T+1 close or intraday highs.
- Missing prices are reported as execution/data-quality states, not zero return.
- The September-October sealed set is not used.
