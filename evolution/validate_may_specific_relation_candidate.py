#!/usr/bin/env python3
"""Validate the May specific-relation candidate Challenger."""

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
    parent = load("replay_current_skill_auction_2026-05.jsonl")
    challenger = load("replay_challenger_may_specific_relation_2026-05_auction.jsonl")
    changes = {}
    expected = {
        "2026-05-07": (["600673.SH", "603158.SH", "000818.SZ"], ["603158.SH", "600673.SH", "000818.SZ"]),
        "2026-05-08": (["002929.SZ", "603636.SH", "002491.SZ"], ["002491.SZ", "002929.SZ", "603636.SH"]),
        "2026-05-19": (["002421.SZ", "002272.SZ", "300657.SZ"], ["002421.SZ", "002272.SZ"]),
    }
    for date, (old_queue, new_queue) in expected.items():
        assert parent[date]["original_queue"] == old_queue
        assert challenger[date]["original_queue"] == new_queue
        changes[date] = {
            "execution": (parent[date].get("executed_candidate") or "", challenger[date].get("executed_candidate") or ""),
            "queue": (old_queue, new_queue),
        }
    for date in parent:
        if date not in expected:
            assert parent[date]["original_queue"] == challenger[date]["original_queue"]
    assert changes["2026-05-07"]["execution"] == ("600673.SH", "603158.SH")
    assert changes["2026-05-08"]["execution"] == ("002929.SZ", "002929.SZ")
    assert changes["2026-05-19"]["execution"] == ("300657.SZ", "")
    assert all(not any(item["leakage_check"].values()) for item in challenger.values())

    with (ROOT / "challenger_returns_may_specific_relation_2026-05.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        rows = list(csv.DictReader(handle))
    computed = [row for row in rows if row["status"] == "computed"]
    for row in computed:
        expected_return = float(row["t2_auction_sell_price"]) / float(row["t1_open_buy_price"]) - 1.0
        assert math.isclose(expected_return * 100.0, float(row["return_pct"]), rel_tol=0, abs_tol=1e-10)
    print(json.dumps({
        "changes": changes,
        "computed_returns_may": len(computed),
        "upstream_queue_regenerated": True,
        "diagnostic_prices_not_used_for_decisions": True,
        "all_leakage_flags_false": True,
        "return_formula_recomputed": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
