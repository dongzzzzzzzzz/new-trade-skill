# Challenger: Repair High-Gap Overextension

## Rule

During a plain `修复` environment, a non-market-core candidate with at least
three boards is invalidated at T+1 if it is in the first two positions of the
frozen queue and opens at least 5% above its T-day close. The rule protects the
repair phase from high-premium continuation; it does not change the T-day
queue, apply in an attack environment, or apply to the established market core.

## April paired replay

| Metric | Parent | Challenger |
|---|---:|---:|
| Computed trades | `13` | `11` |
| Simple return sum | `-37.574741%` | `+4.866606%` |
| Win rate | `38.461538%` | `54.545455%` |
| Compounded return | `-34.762360%` | `+0.866849%` |
| Maximum drawdown | `-45.858674%` | `-27.201905%` |

Changed execution dates:

- `2026-04-07`: `000720.SZ` -> `002980.SZ`, returning `-3.363636%` instead of `-6.474820%`;
- `2026-04-20`: `002297.SZ` -> no trade;
- `2026-04-22`: `003018.SZ` -> no trade;
- `2026-04-30`: `603095.SZ` -> `600379.SH`, returning `+11.287671%` instead of `-13.575801%`.

Earlier-window triggers were already skipped or non-executed by preceding rules,
and March has no trigger. This remains provisional until another non-sealed
month confirms it without suppressing valid repair trades.
