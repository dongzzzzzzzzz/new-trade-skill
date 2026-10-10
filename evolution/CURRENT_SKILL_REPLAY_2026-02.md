# Current Skill Replay: February 2026

## Scope and ordering

This replay uses the current `SKILL.md` with the candidate-pool completeness
Challenger present. The process is deliberately split into:

1. T-day queue freeze from `replay_inputs_2026-02.csv` only;
2. T+1 auction confirmation from the `eltdx==3.1.1` cache;
3. T+1 open buy and T+2 09:25 auction sell prices.

The T-day queue artifact is
`evolution/replay_current_skill_tday_queue_2026-02.jsonl`.
The auction artifact is
`evolution/replay_current_skill_auction_2026-02.jsonl`.
The machine-readable decisions and returns are:

- `evolution/current_skill_decisions_2026-02.csv`
- `evolution/current_skill_returns_2026-02.csv`

The September-October sealed set was not read.

## Economic result

| Metric | Result |
|---|---:|
| Signal dates | 14 |
| Computable trades | 8 |
| Empty / not executed | 6 |
| Simple return sum | `+44.677192%` |
| Average trade return | `+5.584649%` |
| Win rate | `87.5%` |

Returns use only:

`T+1 open buy -> T+2 09:25 auction sell`

This is a February development-window result. It is not a proof of global
optimality and has no sealed validation-set claim.

## Failure attribution

### 2026-02-04: genuine upstream failure candidate

- Selected: `002830.SZ` 名雕股份.
- T+1 auction: stable and executable; the auction did not reject it.
- Return: `-19.155111%`.
- Diagnosis: the queue remains an upstream environment/mode/theme/node-to-
  candidate problem. The corrected T-day state is `分歧`, because the main
  indices and growth index diverged; the queue still treated a 4-board
  AI-media candidate as the formal continuation path without a sufficiently
  explicit defensive boundary.
- Diagnostic-only alternatives with complete prices included `301362.SZ`
  `+6.844995%`, `603618.SH` `+5.772496%`, and `603616.SH` `+9.946950%`.
  These future results are not fed back into the queue; they only show that
  candidate recall and role assignment need another predeclared Challenger.

### 2026-02-27: replay implementation correction, not a strategy loss

The first materialization incorrectly applied low-front priority even though
the prior limit-up closing feedback was positive. The current skill's repair
handoff rule was not triggered. After correcting the T-day queue to keep
`001896.SZ` first, the trade returned `+4.044944%`. The discarded first
materialization is retained only as an implementation audit and is not part
of the current result.

### 2026-02-09: correct no-fallback branch

The low-front candidate failed the T+1 auction. The high core had a strong
auction but remained downgraded by the upstream repair-day rule, so the skill
stayed flat. This is an intentional execution boundary, not a missing return.

## Next Darwin target

The next Challenger must address the 2026-02-04 failure at the upstream
environment/mode/node boundary. It must compare at least these two paths:

- stricter defensive interpretation: classify the mixed repair session as
  waiting and avoid the high-core continuation;
- qualified low-position trial: admit a lower-position candidate only when its
  T-day theme, node, response, and loss boundary are independently evidenced.

The Challenger must regenerate all 14 downstream rows and be rejected if it
only fixes 2026-02-04 by adding a hindsight-selected stock or damages the
positive cases.
