# February Auction Survivorship Audit

## Purpose

This is a diagnostic window for the current skill. It joins only T-day
limit-up facts with the next trading day's auction snapshot. It does not use
T+1 close, T+2 prices, realized returns, or a hindsight ranking to create a
decision.

## Coverage

- Signal dates: `2026-02-02` through `2026-02-27`, `14` trading days.
- Limit-up candidates: `861`.
- T+1 auction pairs covered: `861 / 861`.
- Basic auction survivors: `753 / 861`.
- Basic gate: `T+1 09:25 open gap >= -2%` and positive opening volume.

The full machine-readable output is
`evolution/february_auction_survivorship_audit_2026-02.csv`.

## What This Says

1. **Auction data is not the current February bottleneck.** Coverage is
   complete, and most limit-up candidates remain tradable under the basic
   gate. A future negative result cannot be dismissed as “竞价数据没拿到”.
2. **The real decision burden is upstream.** On weak days there are still
   many auction survivors: `29` on 2026-02-02, `34` on 2026-02-05, `47` on
   2026-02-10, `38` on 2026-02-11, `51` on 2026-02-12, and `28` on 2026-02-13.
   The skill has to explain why a specific environment/mode/theme/node path
   admits one low-position trial or waits, rather than treating auction
   strength as sufficient evidence.
3. **High-board and low-board roles must stay separate.** On 2026-02-12,
   three of four high-board candidates survive the basic gate while the
   market breadth remains weak. A strong auction does not, by itself, undo a
   negative emotional regime.
4. **The repair-day Challenger is correctly aimed at the upstream boundary.**
   Its four cases do not change the auction gate. They change whether a
   same-theme low front is formally generated before the high core. This is
   consistent with the audit: the next meaningful comparison is candidate
   generation and role assignment, not another auction threshold.

## Next Darwin Target

Before changing the skill again, the full 14-day replay must freeze a T-day
original queue for every date. Each date then needs a failure label:

- no formal candidate generated because environment/sentiment blocked it;
- candidate generated but excluded by theme or node evidence;
- candidate generated but auction-invalidated;
- candidate executable but selected role was wrong;
- data or timing evidence missing.

Only after that labeling can Darwin choose between two competing directions:

- expand qualified low-position trials during weak breadth; or
- keep waiting and tighten the definition of a real low-position handoff.

The audit is therefore a gate for the next evolution, not proof that either
direction is profitable.
