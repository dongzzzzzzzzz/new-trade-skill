# Challenger: Reject an Unrelated Candidate Cluster on 2026-04-17

## Diagnosis

The `2026-04-17` queue labeled `605388.SH` (益生菌消费/扭亏) and
`600683.SH` (地产剥离/TOD/北京国资) as one `算力/消费/地产` path. Those
labels did not establish a shared concrete catalyst or a coherent industry
relationship. The defect was in mainline construction before node and queue
generation, not in the queue order or auction threshold.

## Rule

When the T-day candidates do not form a cluster with a concrete shared
catalyst, industry relationship, or coherent funding narrative, split them
back into observation and generate no formal queue. Broad labels such as
算力、消费、地产 or 国企 cannot be used to join unrelated candidates. The
decision uses only T-day facts; T+1 and T+2 outcomes are not used.

## Paired April replay

| Metric | Parent | Challenger |
|---|---:|---:|
| Computed trades | `10` | `9` |
| Simple return sum | `+23.245524%` | `+27.642007%` |
| Win rate | `60%` | `66.666667%` |
| Compounded return | `+23.142778%` | `+28.805699%` |
| Maximum drawdown | `-11.124817%` | `-7.037748%` |

Only `2026-04-17` changes: the mixed queue is replaced by a wait decision and
the `-4.396483%` trade disappears. The queue is regenerated upstream before
auction processing, and the return formula is recomputed from T+1 open to T+2
09:25 auction sell.

This is provisional until the same cluster-consistency rule is checked on
later non-sealed months and the sealed September-October set remains held out.
