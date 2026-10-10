# Challenger: Candidate-Pool Completeness Check

## Hypothesis

The February auction audit shows that auction coverage is complete and that
many candidates remain executable even on weak days. The next likely failure
is upstream omission: a stock may be excluded before the queue is frozen
without a recorded, falsifiable reason.

## Rule change

Before freezing the original queue, the skill must perform a reverse audit of
all sufficiently described limit-up, limit-break, and key broken-board
candidates. A rejected candidate that has a high-confidence or explicitly
reinforced medium-confidence theme relation, a role compatible with the
current environment and mode, and T-day active response must force a return to
the earliest conflicting step. It cannot be silently re-ranked into the queue,
and it cannot be restored using future auction or return information.

## Why this is a real process change

This changes candidate generation and upstream backtracking. It does not add a
second ranking model, fix a candidate pool and sort it externally, or use
realized returns to choose a winner. The original queue still freezes only
after the upstream audit is clean.

## Paired review under the CPU cap

Independent judge agents remain disabled because the user previously observed
CPU saturation. The one-process review found the after-version better on:

- recall accountability: every exclusion has a named step and evidence;
- upstream integrity: a plausible omission causes regeneration rather than
  post-hoc ranking;
- compatibility with the existing four gates and T+1 auction boundary.

The change is provisionally retained for development. It is not yet an
economic keep: the full February replay must regenerate all downstream fields
for all 14 signal dates and compare executable returns against the kept parent.

## Required validation

For every February date, record whether a failure was:

1. no candidate allowed by environment/sentiment;
2. excluded by theme or node evidence;
3. caught by the completeness audit and regenerated upstream;
4. generated but invalidated by T+1 auction;
5. executable but assigned the wrong role or queue position;
6. missing raw evidence.

The current repair-day slice is a regression check: it must preserve the
2026-02-03 low-front handoff, the 2026-02-09 no-fallback branch, and the
2026-02-24 no-forced-handoff branch.
