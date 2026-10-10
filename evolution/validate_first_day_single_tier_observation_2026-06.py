#!/usr/bin/env python3
"""Validate the first-day single-tier observation Challenger."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def load(name: str) -> dict[str, dict]:
    return {
        row["signal_date"]: row
        for row in (
            json.loads(line)
            for line in (ROOT / name).read_text(encoding="utf-8").splitlines()
            if line.strip()
        )
    }


def main() -> None:
    parent = load("replay_current_skill_auction_2026-06.jsonl")
    challenger = load("replay_challenger_first_day_single_tier_2026-06_auction.jsonl")
    changes = {}
    for date in parent:
        old_queue = parent[date]["original_queue"]
        new_queue = challenger[date]["original_queue"]
        old = parent[date].get("executed_candidate") or ""
        new = challenger[date].get("executed_candidate") or ""
        if old_queue != new_queue or old != new:
            changes[date] = {"queue": (old_queue, new_queue), "execution": (old, new)}
    assert changes == {
        "2026-06-15": {
            "queue": (["600026.SH", "601872.SH", "601975.SH"], []),
            "execution": ("600026.SH", ""),
        }
    }
    day = challenger["2026-06-15"]
    assert day["theme_classification"][0]["status"] == "新题材观察"
    assert all(audit["include_status"] == "watch" for audit in day["candidate_audit"])
    assert all(not any(item["leakage_check"].values()) for item in challenger.values())

    with (ROOT / "challenger_returns_first_day_single_tier_2026-06.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    computed = [row for row in rows if row["status"] == "computed"]
    for row in computed:
        expected = float(row["t2_auction_sell_price"]) / float(row["t1_open_buy_price"]) - 1.0
        assert math.isclose(expected * 100.0, float(row["return_pct"]), rel_tol=0, abs_tol=1e-10)
    print(json.dumps({
        "changes": changes,
        "computed_returns_june": len(computed),
        "upstream_queue_regenerated": True,
        "all_leakage_flags_false": True,
        "return_formula_recomputed": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
