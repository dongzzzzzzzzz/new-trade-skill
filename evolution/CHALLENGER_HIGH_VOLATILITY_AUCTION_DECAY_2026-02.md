# Challenger: High-Volatility Auction Decay

## Diagnosis

On 2026-02-10 the first two frozen candidates were locked at limit-up and
therefore unreachable. The third candidate, `300182.SZ`, was a non-core 20cm
two-board stock. Its T+1 auction moved from the limit-up price at 09:20 to a
`-6.213%` price drift by 09:24, while the open still remained `+11.953%` above
the previous close. The old executor called this `超预期` solely because of the
high opening gap and bought it; the trade returned `-7.928118%`.

## Rule

In a divergence or retreat environment, a non-market-core 20cm/30cm candidate
is auction-invalidated when all of the following are known by T+1 open:

- its 09:20 price is at the theoretical limit-up price;
- its 09:24 price has declined at least 5% from 09:20;
- it still opens at least 10% above the T-day close.

This is a T+1 auction gate. It does not change the T-day theme, candidates, or
frozen queue, and it does not use T+2 return data.

## Paired replay

| Metric | Executable parent | Challenger |
|---|---:|---:|
| February computed trades | `7` | `6` |
| Simple return sum | `+45.900969%` | `+53.829087%` |
| Win rate | `85.714286%` | `100%` |
| Compounded return | `+53.459134%` | `+66.673181%` |
| Maximum drawdown | `-7.928118%` | `0%` |

Only 2026-02-10 changes, from executing `300182.SZ` to no trade. January and
March contain no matching candidate. The rule remains provisional until it is
tested on later non-sealed months.
