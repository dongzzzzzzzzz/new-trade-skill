# Current Skill Replay: March 2026

## Scope

- Signal dates: `22`.
- Strategy-neutral stock facts: `1909` rows.
- Limit-up candidates: `1233`.
- T+1 auction coverage: `1230` full series, `3` explicit missing pairs.
- Frozen T-day queues: `12` non-empty dates, `10` waiting dates.
- The sealed September-October window was not read.

T-day queues were frozen before auction data was joined. T+2 prices were then
requested only for the `12` executed candidates.

## Parent result

| Metric | Result |
|---|---:|
| Computable trades | `12` |
| Simple return sum | `+49.172217%` |
| Average trade return | `+4.097685%` |
| Win rate | `75%` |
| Compounded return | `+56.369164%` |
| Maximum sequential equity drawdown | `-11.337209%` |

## Failure attribution

| Signal date | Executed | Return | Primary diagnosis |
|---|---|---:|---|
| 2026-03-09 | `000815.SZ` | `-4.418727%` | Node role / queue priority inside a broad compute-electric theme |
| 2026-03-12 | `000537.SZ` | `-11.337209%` | Same-board candidate role differentiation under weak breadth |
| 2026-03-30 | `603538.SH` | `-6.982033%` | Non-market-core 5-board continuation remained first during environment and sentiment divergence despite same-theme 2-board fronts |

All three selected stocks passed the T+1 auction gate, so none is primarily an
auction-data or execution failure.

Diagnostic-only counterfactual prices show that 2026-03-30 is the clearest
next Challenger target: same-theme 2-board fronts returned `+8.076358%`,
`+15.430862%`, and `+1.525054%`. Those prices are not decision inputs; they
only support testing a predeclared rule for non-market-core high-to-low
rotation during dual divergence.

## Next Challenger

When both environment and relay sentiment are `分歧`, a 4-to-6-board candidate
that is not the established market core cannot automatically remain first if
same-theme fronts at no more than 2 boards have independent T-day response.
The rule must regenerate the queue before T+1 auction facts and retain the
existing established-market-core exception.
