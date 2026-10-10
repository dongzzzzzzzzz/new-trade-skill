# Challenger: Theme Relation Graph

## Scope

This round changes the upstream mainline and candidate-pool process only. It
requires a point-in-time relation graph before a stock can be promoted from an
isolated move to a theme, mainline, or new-theme observation cluster.

The graph distinguishes direct catalyst/industry relations (A), plausible but
incomplete relations (B), and generic concept overlap (C). Generic labels such
as AI, robotics, state-owned enterprise, price increase, or restructuring are
not sufficient on their own. A same-day new-theme cluster requires three
independent stocks, two response times or ladder positions, one A-level edge,
and no batch negative-feedback contradiction.

This is an upstream candidate-generation change. It does not reorder an
existing queue, alter auction rules, or alter the T+1-open to T+2-auction
return formula.

## January chain check

The kept January new-theme challenger already contains the 2026-01-29
entertainment/AI-media cluster:

- `000607.SZ` 华媒控股
- `600959.SH` 江苏有线
- `603103.SH` 横店影视

The three stocks have distinct response times and concrete media/AI-content/
cinema relationships. The relation graph therefore preserves this cluster as
new-theme observation rather than treating it as a post-hoc ranking change.
The existing full-chain output remains:

- 19 signal dates regenerated;
- 11 computable trades;
- simple return sum `116.518307%`;
- average trade return `10.592573%`;
- win rate `100%`.

The return figures are recalculated from the independent price chain in
`challenger_returns_new_theme_fermentation_2026-01.csv`; this document does
not feed those outcomes back into the relation graph.

## Review gate

- Point-in-time boundary: pass. Relation edges use T-day facts only.
- Upstream fidelity: pass. Theme classification precedes node, candidate,
  queue, auction, execution, and return fields.
- Leakage: pass for the rule definition; the 2026-01-29 outcome is recorded
  only as a diagnostic confirmation of the already-defined cluster.
- Generalization: unresolved. The January development window contains one
  explicit new-theme cluster. February upstream facts are available for audit,
  but February 3 onward lacks valid auction prices and cannot yet produce a
  profitability acceptance test.

## Decision

`provisional_keep_for_development`.

The next economic gate is not another queue-order adjustment. It is a valid
post-2026-02-02 auction source, followed by a blind replay of the complete
chain on February and later unlocked development months. The September 1 to
October 9 validation set remains sealed.
