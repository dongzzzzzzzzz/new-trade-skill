# Challenger: Isolated High-Core Lock in Divergence

## Failure addressed

On 2026-02-04 the parent queue selected `002830.SZ` 名雕股份. Its T+1
auction was executable and therefore did not fail at the auction layer, but
the required T+2 auction exit produced `-19.155111%`.

The T-day facts showed index divergence: the Shanghai and Shenzhen indices
rose while the growth index fell. The selected AI-media stock was the only
same-theme limit-up response in the replay input. Its prior-day identity was
being used as a substitute for T-day theme expansion.

## Rule change

When the environment is `分歧`, a high-board candidate that is the only T-day
response in its concrete theme cannot remain a formal candidate solely because
it was a prior-day mainline member or has a high board count. It becomes an
observation candidate unless T-day same-theme, adjacent-ladder, or common-
catalyst response is present.

This changes mainline confirmation, node role, and candidate generation. The
challenger regenerates the original queue before auction data is read; it does
not reorder a fixed queue and does not use the negative return as a decision
input.

## Paired February result

| Metric | Parent | Challenger |
|---|---:|---:|
| Signal dates | 14 | 14 |
| Computable trades | 8 | 7 |
| Simple return sum | `+44.677192%` | `+63.832304%` |
| Average trade return | `+5.584649%` | `+9.118901%` |
| Win rate | `87.5%` | `100%` |

The only changed date is 2026-02-04. The Challenger changes that date from an
executable `002830.SZ` trade to waiting, avoiding the `-19.155111%` loss. All
other 13 dates retain the parent's regenerated downstream decisions.

## Review status

The one-process paired review under the CPU cap prefers the Challenger because
it removes an explicitly diagnosed upstream failure without changing the
auction gate or adding a post-hoc sorter. Independent judge agents remain off
to avoid saturating the user's computer.

Status: `provisional_keep_for_development`.

This is not proof of global optimality. It must still be replayed across the
full January chain and later non-sealed development windows, then tested once
against the sealed 2026-09-01 to 2026-10-09 set after upstream optimization is
frozen.
