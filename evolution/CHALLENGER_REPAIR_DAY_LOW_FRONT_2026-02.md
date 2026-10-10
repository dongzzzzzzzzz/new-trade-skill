# Challenger: Repair-Day Low-Front Handoff

## Failure that motivated the challenger

On 2026-02-03 the market moved from the 2026-02-02 broad drawdown into a
strong index and breadth repair. The day still followed a severe negative-
feedback session: 2026-02-02 had 85.17% decliners, 98 limit-down stocks, and
the prior limit-up close-return median was negative.

The initial development replay treated `603103.SH` 横店影视, a 4-board high
core, as the continuation candidate because its 2026-02-04 auction was stable
and executable. The required independent price chain then produced:

| Candidate | Role at T-day close | T+1 open buy | T+2 09:25 sell | Return |
|---|---|---:|---:|---:|
| `603103.SH` | high core continuation | 33.90 | 28.78 | `-15.103245%` |
| `002830.SZ` | 3-board same-theme front | 28.19 | 31.01 | `+10.003547%` |

The auction was not the failure: `603103.SH` had a complete auction series and
was tradable. The failure is upstream, in treating a high-core continuation as
the default repair-day path while a lower-position same-theme front was
available.

## Rule change

When a repair day follows broad negative feedback, a high core cannot
automatically lead the formal queue if a qualified same-theme low front exists.
The low front must be no more than three boards, have A-level theme relation,
independent T-day response, at least one same-theme or adjacent-ladder
response, and explicit auction failure/loss boundaries. If no such handoff
exists, the rule does not manufacture one and the system may wait or retain the
high core under the ordinary gates.

This is a change to environment-to-mode-to-node-to-candidate generation. It is
not an external sorter and does not use the realized T+2 prices to form the
decision.

## Review status

- T-day decision boundary: pass; the trigger uses the prior drawdown facts and
  T-day ladder/response facts.
- Auction boundary: pass; only T+1 09:25-or-earlier facts decide whether the
  frozen candidate remains executable.
- Return protocol: pass; `T+1 open buy -> T+2 09:25 auction sell`.
- Economic result: positive on this development case, but this is one case and
  is not proof of general optimality.
- Generalization: pending. The February window must be replayed across all
  14 dates, with every upstream change regenerating the downstream fields.

Decision: `provisional_keep_for_development`.
