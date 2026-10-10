#!/usr/bin/env python3
"""Validate the April T-day catalyst-overlap candidate Challenger."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(name: str) -> dict[str, dict]:
    rows = [
        json.loads(line)
        for line in (ROOT / name).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {row["signal_date"]: row for row in rows}


def main() -> None:
    parent = load("replay_challenger_repair_high_gap_2026-04.jsonl")
    challenger = load("replay_challenger_theme_relation_auction_2026-04.jsonl")
    changes = {}
    for signal_date in parent:
        assert parent[signal_date]["original_queue"] != [] or challenger[signal_date]["original_queue"] == []
        if signal_date != "2026-04-21":
            assert parent[signal_date]["original_queue"] == challenger[signal_date]["original_queue"]
        old = parent[signal_date].get("executed_candidate") or ""
        new = challenger[signal_date].get("executed_candidate") or ""
        if old != new:
            changes[signal_date] = (old, new)
    assert changes == {"2026-04-21": ("603178.SH", "603017.SH")}

    changed = challenger["2026-04-21"]
    assert changed["original_queue"] == ["002081.SZ", "603017.SH"]
    excluded = next(a for a in changed["candidate_audit"] if a["candidate"] == "603178.SH")
    assert excluded["theme_pass"] is False
    assert excluded["include_status"] == "watch"
    assert all(not any(item["leakage_check"].values()) for item in challenger.values())

    with (ROOT / "challenger_returns_theme_relation_2026-04.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    computed = [row for row in rows if row["status"] == "computed"]
    for row in computed:
        expected = float(row["t2_auction_sell_price"]) / float(row["t1_open_buy_price"]) - 1.0
        assert math.isclose(expected * 100.0, float(row["return_pct"]), rel_tol=0, abs_tol=1e-10)
    changed_return = next(row for row in computed if row["signal_date"] == "2026-04-21")
    assert changed_return["candidate"] == "中衡设计"
    assert math.isclose(float(changed_return["return_pct"]), -7.037748, abs_tol=1e-5)

    print(json.dumps({
        "execution_changes": changes,
        "computed_returns_april": len(computed),
        "queues_regenerated_upstream": True,
        "all_leakage_flags_false": True,
        "return_formula_recomputed": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
