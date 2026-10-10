# Cross-Window Validation: Isolated High-Core Lock

## January full-chain check

The refined rule was applied to all `19` January baseline signal dates. It
did not trigger on any date because:

- established market cores at or above the high-core boundary remain governed
  by the separate crowding protection;
- other disputed high cores had explicit multi-day theme or ladder response;
- no January queue head met the narrower definition of a non-core isolated
  high-board continuation.

The regenerated January result is identical to the parent:

| Metric | Parent | Challenger |
|---|---:|---:|
| Signal dates | 19 | 19 |
| Computable trades | 11 | 11 |
| Simple return sum | `+70.640454%` | `+70.640454%` |
| Average trade return | `+6.421859%` | `+6.421859%` |
| Win rate | `81.818182%` | `81.818182%` |

The one-process paired review therefore finds no January regression, but also
no additional January gain. The February gain remains a development-window
result and still requires later non-sealed windows and final sealed validation.

## False-positive correction

An earlier implementation of the rule incorrectly locked the 2026-01-20
15-board market core because it looked only for explicit response words in one
node field. That version reduced January returns and was rejected. The final
rule checks the candidate's role, height, and theme-level multi-ladder evidence
before it can trigger.
