# Candidate Recall Audit: January 2026

This is a diagnostic-only audit generated after the baseline was frozen. It
uses future prices to locate missed opportunities. Its output must not be used
as a decision input for any Challenger.

## Key Findings

| Signal date | Frozen selected result | Best valid-return candidate | Was best in candidate audit? | Diagnosis |
|---|---:|---:|---|---|
| 2026-01-26 | empty | `003042.SZ` `+20.456906%` | no | possible low-position/theme recall miss, but environment was already classified as退潮 |
| 2026-01-27 | `601212.SH` `+20.843278%` | `601212.SH` `+20.843278%` | yes | no recall failure |
| 2026-01-28 | `601212.SH` `-10.006583%` | `002155.SZ` `+9.988109%` | yes | queue/candidate-role priority error; first Challenger addresses this |
| 2026-01-29 | `601212.SH` `-10.021946%` | `603103.SH` `+15.861214%` | no | candidate pool/theme or low-position fermentation miss |
| 2026-01-30 | empty | no valid return candidate | no | empty decision is not contradicted by this data chain |

The full machine-readable audit is
`evolution/candidate_recall_audit_2026-01.csv`.

## 2026-01-29 Missed Cluster

On the T-day raw facts, the following three independent first-board stocks
shared an entertainment/AI-media direction:

- `000607.SZ` 华媒控股: 数字人、AIGC、文化传媒
- `600959.SH` 江苏有线: 文化传媒、算力云网
- `603103.SH` 横店影视: 春节档、AI漫剧、院线龙头

The current baseline did not create a formal candidate audit entry for this
cluster. `603103.SH` later produced the best valid-return result in the audit,
but that fact is only being recorded now as a recall failure.

This is not evidence that the cluster should automatically become the main
line. It is evidence that the current process needs an explicit same-day
fermentation path: a coherent multi-stock cluster can enter low-position
observation or trial even before a multi-board ladder exists, provided the
environment gate, response count, and loss boundary all pass.

## Guardrails

- This audit does not change any baseline or Challenger decision.
- It does not rank every stock as tradable; it only identifies candidates with
  complete T+1-open and T+2-auction price evidence.
- A future return does not prove that a candidate was knowable or executable at
  T-day close. The next Challenger must use only T-day cluster facts and then
  re-run T+1 auction validation.
