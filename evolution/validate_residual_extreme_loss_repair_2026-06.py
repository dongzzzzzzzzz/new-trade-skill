#!/usr/bin/env python3
"""Validate the residual-extreme-loss repair Challenger."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pandas as pd


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
    parent = load("replay_challenger_first_day_single_tier_2026-06_auction.jsonl")
    challenger = load("replay_challenger_residual_extreme_loss_repair_2026-06_auction.jsonl")
    changes = {}
    for date in parent:
        old_queue = parent[date]["original_queue"]
        new_queue = challenger[date]["original_queue"]
        old = parent[date].get("executed_candidate") or ""
        new = challenger[date].get("executed_candidate") or ""
        if old_queue != new_queue or old != new:
            changes[date] = {"queue": (old_queue, new_queue), "execution": (old, new)}
    assert changes == {
        "2026-06-01": {
            "queue": (["000539.SZ", "002608.SZ", "000767.SZ"], ["002608.SZ", "000767.SZ"]),
            "execution": ("000539.SZ", "000767.SZ"),
        }
    }
    day = challenger["2026-06-01"]
    assert day["environment_state"] == "修复"
    assert day["environment_evidence"]["previous_trade_day_limit_down_count"] == 50
    assert day["environment_evidence"]["residual_limit_down_count"] == 21
    assert all(not any(item["leakage_check"].values()) for item in challenger.values())

    market = pd.concat(
        [pd.read_csv(path) for path in sorted(ROOT.glob("market_facts_2026-0[2-6].csv"))],
        ignore_index=True,
    ).sort_values("date").drop_duplicates("date")
    market["previous_down_ratio"] = market["down_ratio"].shift(1)
    market["previous_limit_down_count"] = market["limit_down_count"].shift(1)
    trigger_dates = set(
        market[
            market["previous_down_ratio"].ge(0.70)
            & market["previous_limit_down_count"].ge(20)
            & market["limit_down_count"].ge(10)
        ]["date"]
    )
    assert trigger_dates == {
        "2026-03-04",
        "2026-06-01",
        "2026-06-11",
        "2026-06-12",
        "2026-06-29",
    }
    state_by_date = {}
    for name in (
        "replay_current_skill_tday_queue_2026-03.jsonl",
        "replay_challenger_residual_extreme_loss_repair_2026-06.jsonl",
    ):
        state_by_date.update({date: row["environment_state"] for date, row in load(name).items()})
    assert all(state_by_date[date] != "进攻" for date in trigger_dates)

    with (ROOT / "challenger_returns_residual_extreme_loss_repair_2026-06.csv").open(
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
        "environment_reclassified_before_candidates": True,
        "upstream_queue_regenerated": True,
        "cross_window_trigger_dates": sorted(trigger_dates),
        "cross_window_attack_conflicts": 0,
        "all_leakage_flags_false": True,
        "return_formula_recomputed": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
