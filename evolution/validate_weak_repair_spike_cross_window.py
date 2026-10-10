#!/usr/bin/env python3
"""Validate the weak-repair last-minute spike gate across January-March."""

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


def changes(parent: dict[str, dict], challenger: dict[str, dict]) -> dict[str, tuple[str, str]]:
    assert parent.keys() == challenger.keys()
    result = {}
    for signal_date in parent:
        assert parent[signal_date]["original_queue"] == challenger[signal_date]["original_queue"]
        old = parent[signal_date].get("executed_candidate") or ""
        new = challenger[signal_date].get("executed_candidate") or ""
        if old != new:
            result[signal_date] = (old, new)
    return result


def validate_returns(name: str) -> int:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    computed = [row for row in rows if row["status"] == "computed"]
    for row in computed:
        expected = (
            float(row["t2_auction_sell_price"]) / float(row["t1_open_buy_price"]) - 1.0
        ) * 100.0
        assert math.isclose(expected, float(row["return_pct"]), rel_tol=0, abs_tol=1e-10)
    return len(computed)


def main() -> None:
    parents = {
        "2026-01": load("replay_challenger_limit_open_execution_2026-01.jsonl"),
        "2026-02": load("replay_challenger_high_volatility_auction_decay_2026-02.jsonl"),
        "2026-03": load("replay_challenger_high_volatility_auction_decay_2026-03.jsonl"),
    }
    challengers = {
        "2026-01": load("replay_challenger_weak_repair_spike_2026-01.jsonl"),
        "2026-02": load("replay_challenger_weak_repair_spike_2026-02.jsonl"),
        "2026-03": load("replay_challenger_weak_repair_spike_2026-03.jsonl"),
    }
    execution_changes = {
        month: changes(parents[month], challengers[month]) for month in parents
    }
    assert execution_changes == {
        "2026-01": {"2026-01-21": ("601616.SH", "")},
        "2026-02": {},
        "2026-03": {},
    }
    for challenger in challengers.values():
        assert all(not any(row["leakage_check"].values()) for row in challenger.values())

    trigger = next(
        record
        for record in challengers["2026-01"]["2026-01-21"]["auction_records"]
        if record["candidate"] == "601616.SH"
    )
    assert trigger["weak_repair_last_minute_spike"] is True
    assert trigger["decision"] == "跳过并递补"

    result = {
        "execution_changes": execution_changes,
        "computed_returns": {
            month: validate_returns(f"challenger_returns_weak_repair_spike_{month}.csv")
            for month in parents
        },
        "queues_unchanged": True,
        "all_leakage_flags_false": True,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
