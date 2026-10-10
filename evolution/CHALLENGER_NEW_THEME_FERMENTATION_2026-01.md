# Challenger: Same-Day New-Theme Fermentation

## Scope

This Challenger changes only candidate-pool admission. In the high-core
crowding-lock regime, it permits a coherent same-day cluster of at least three
independent first-board stocks to enter a low-position trial queue. The
cluster remains “new-theme observation”, not a confirmed main line. Every
member must still pass the T+1 auction gate, and the queue is ordered only by
T-day observable activation and response evidence.

The environment lock, auction protocol, and return formula are unchanged from
the parent Challenger.

## Paired Replay

The full 19-case window was regenerated from
`replay_challenger_high_core_lock_2026-01.jsonl`.

| Metric | Parent Challenger | This Challenger | Difference |
|---|---:|---:|---:|
| Cases | 19 | 19 | 0 |
| Computable trades | 10 | 11 | +1 |
| Simple return sum | 100.657093% | 116.518307% | +15.861214 pp |
| Average return | 10.065709% | 10.592573% | +0.526864 pp |
| Win rate | 100.000000% | 100.000000% | 0 pp |
| Empty/waiting cases | 7 | 6 | -1 |

The added trade is 2026-01-29:

- T-day cluster: `000607.SZ`, `600959.SH`, `603103.SH`.
- T+1 auction rejects the first two for weakening expectations.
- `603103.SH` remains the first executable member after递补.
- T+1 open buy: `24.21`.
- T+2 09:25 auction sell: `28.05`.
- Return: `+15.861214%`.

This is a real queue-and-auction path, not a post-hoc replacement of the
parent's selected stock.

## Review Gate

The machine is kept at one local process, so no independent judge agents were
spawned. The paired review is explicitly resource-capped and not equivalent to
the full multi-agent Darwin vote.

- Full-chain regeneration: pass; all 19 dates are present.
- Upstream scope: pass; only new-theme candidate admission changed relative to
  the parent.
- Auction recursion: pass; two weak members are skipped before the third is
  executed.
- Leakage: pass; queue construction uses T-day cluster facts; returns are only
  used in this report.
- Generalization: unresolved; the rule has one clear development-window
  trigger and must be challenged on another non-sealed development period
  before final acceptance.

## Decision

`provisional_keep_for_development`.

This Challenger is stronger than the parent on the January development window,
but it is not evidence of final optimality. The next audit should search for
false positives from same-day three-stock clusters and determine whether the
new-theme path belongs in the mainline step or remains a strictly bounded
candidate-pool exception.
