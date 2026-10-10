# January 2026 Baseline Diagnostic

This diagnostic is written after the current skill baseline was frozen. It is
not allowed to change the baseline decisions retroactively.

## Baseline

- Cases: 19 signal dates from 2026-01-06 through 2026-01-30
- Computable trades: 11
- Simple return sum: `70.640454%`
- Average single-trade return: `6.421859%`
- Win rate: `81.818182%`
- Empty/waiting cases: 6
- Selected but unverifiable cases: 2

Returns use only `T+1 open buy -> T+2 09:25 auction sell`.

## Failure Cases

### 2026-01-28 signal: high-core continuation was over-trusted

- Current chain: `environment=分歧`, `sentiment=强化但高位拥挤`,
  `mode=黄金白银主线接力`, queue head `601212.SH`.
- The T+1 auction for `601212.SH` was stable and executable: 09:20 `15.19`,
  09:24 `15.19`, open `15.19`.
- The realized T+2 auction return was `-10.006583%`.
- The failure therefore is not an unavailable-execution failure and not a
  missing-price failure.
- The strongest current hypothesis is an upstream candidate-generation error:
  the skill treated the highest market core as the default queue head even
  though breadth remained weak, the main board and growth board diverged, and
  high-core crowding was already extreme.
- Secondary hypothesis: the auction gate treats “stable and executable” as
  sufficient confirmation and has no explicit late-stage crowding downgrade.

### 2026-01-29 signal: the same error repeated after risk expanded

- Current chain: `environment=分歧`, `sentiment=强化与分歧并存`,
  `mode=高位核心接力与主线内部轮动`, queue head `601212.SH`.
- The T+1 auction for `601212.SH` was again stable and executable: 09:20
  `13.67`, 09:24 `13.67`, open `13.67`.
- The realized T+2 auction return was `-10.021946%`.
- On this date the independent risk evidence was stronger: 12 limit-down
  stocks, 34 limit breaks, and the prior limit-up close median was only
  `2.60%` despite a 75% positive-open ratio.
- The failure points to the environment/sentiment-to-candidate gate, not to a
  missing auction record. The skill did record the risk but still allowed the
  highest core to remain first without a crowding penalty or a defensive
  low-position alternative.

## What This Does Not Prove

- It does not prove that `601212.SH` should have been replaced by a particular
  stock at decision time. That would require a separate candidate-recall
  audit using only T-day facts and a predeclared counterfactual rule.
- It does not prove that the auction itself was “wrong”; the auction correctly
  reported that the stock was tradable and matched the pre-auction expectation.
- It does not justify changing the queue by using the observed T+2 returns.

## First Darwin Challenger Target

The first Challenger should change one upstream rule only: the environment /
sentiment gate for late-stage high cores when broad negative feedback and
crowding coexist. It must:

1. Re-run the complete chain for all 19 cases.
2. Preserve the original queue logic for cases outside that condition.
3. Either produce an explicit empty/low-position path or generate a new
   lower-position candidate from T-day facts; it must not merely reorder the
   old queue after seeing returns.
4. Keep the auction and return protocol unchanged.
5. Be rejected if it improves only the two failure cases by damaging the
   earlier winning core cases or if the improvement is not stable in the
   predeclared holdout window.

This is a diagnostic target, not yet an accepted skill change.
