# Challenger: Keep a First-Day Single-Tier Theme in Observation

## Diagnosis

On `2026-06-15`, three oil-shipping stocks shared a coherent catalyst, but all
three were T-day first boards. There was no prior leader, cross-day
continuation, or cross-tier ladder. The replay incorrectly promoted the
cluster from `新题材观察` to a formal mainline and bought `600026.SH`.

All three queue members later lost money under the same T+1-open to T+2-auction
protocol, but the rule is based only on the T-day structural defect: a
single-tier first-day cluster had no confirmed node for formal participation.

## Rule

A same-day cluster with at least three directly related first boards can be
kept as `新题材观察`. If every member is still a first board and there is no
previously confirmed leader, cross-day continuation, or cross-tier ladder, it
cannot generate a formal mainline queue. Re-evaluate only after later T-day
facts establish advancement, ladder expansion, or leader-driven response.

## June replay

| Metric | Parent | Challenger |
|---|---:|---:|
| Computed trades | `9` | `8` |
| Simple return sum | `+14.863237%` | `+23.310380%` |
| Win rate | `66.666667%` | `75%` |
| Compounded return | `+14.015172%` | `+24.534804%` |
| Maximum drawdown | `-8.447142%` | `-7.128099%` |

Only `2026-06-15` changes. The formal queue
`600026.SH -> 601872.SH -> 601975.SH` becomes observation-only and no trade is
executed. The upstream queue is regenerated before auction processing, all
leakage flags remain false, and returns are recomputed independently.

This remains provisional pending additional non-sealed cross-month evidence.
