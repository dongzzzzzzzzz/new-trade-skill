# Current Skill Cross-Window Replay: January-June 2026

This report concatenates the latest kept monthly replay output in signal-date
order. It does not sum monthly compounded returns and does not select a
different rule per trade. Each source window is the latest provisional Darwin
version for that month, with the same executable protocol:

`T+1 open buy -> T+2 09:25 auction sell`

The combined file is `current_skill_returns_2026-01_to_06.csv`; metrics are
recomputed from one continuous equity curve with starting capital `1.0`.

| Metric | Combined result |
|---|---:|
| Signal dates | `115` |
| Computed trades | `43` |
| Simple return sum | `+224.275501%` |
| Average trade return | `+5.215709%` |
| Win rate | `79.069767%` |
| Continuous compounded return | `+725.717871%` |
| Maximum drawdown | `-7.037748%` |

The window remains development evidence, not proof of a globally optimal
trading system. July-August are still needed for non-sealed generalization,
and September-October remains sealed for final validation.
