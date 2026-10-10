#!/usr/bin/env python3
"""Validate the April 17 no-coherent-cluster Challenger."""

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
    parent = load("replay_challenger_unrelated_cluster_wait_auction_2026-04.jsonl")
    challenger = load("replay_challenger_unrelated_cluster_wait_april17_2026-04_auction.jsonl")
    changes = {}
    for signal_date in parent:
        old_queue = parent[signal_date]["original_queue"]
        new_queue = challenger[signal_date]["original_queue"]
        old = parent[signal_date].get("executed_candidate") or ""
        new = challenger[signal_date].get("executed_candidate") or ""
        if old != new or old_queue != new_queue:
            changes[signal_date] = {"execution": (old, new), "queue": (old_queue, new_queue)}
    assert changes == {
        "2026-04-17": {
            "execution": ("600683.SH", ""),
            "queue": (["605388.SH", "600683.SH"], []),
        }
    }
    day = challenger["2026-04-17"]
    assert day["market_mode"] == "等待，未确认可持续主线"
    assert day["theme_classification"][0]["status"] == "无正式主线"
    assert all(audit["theme_pass"] is False for audit in day["candidate_audit"])
    assert all(not any(item["leakage_check"].values()) for item in challenger.values())

    with (ROOT / "challenger_returns_unrelated_cluster_wait_april17_2026-04.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    computed = [row for row in rows if row["status"] == "computed"]
    for row in computed:
        expected = float(row["t2_auction_sell_price"]) / float(row["t1_open_buy_price"]) - 1.0
        assert math.isclose(expected * 100.0, float(row["return_pct"]), rel_tol=0, abs_tol=1e-10)

    print(json.dumps({
        "changes": changes,
        "computed_returns_april": len(computed),
        "upstream_queue_regenerated": True,
        "all_leakage_flags_false": True,
        "return_formula_recomputed": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
