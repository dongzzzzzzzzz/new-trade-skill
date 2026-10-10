#!/usr/bin/env python3
"""Validate the repair high-gap gate against earlier windows and April."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parent


def load(name: str) -> dict[str, dict]:
    rows = [
        json.loads(line)
        for line in (ROOT / name).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    return {row["signal_date"]: row for row in rows}


def close_lookup(month: str) -> dict[tuple[str, str], float]:
    facts = pd.read_csv(ROOT / f"replay_inputs_{month}.csv", usecols=["date", "thscode", "close"])
    facts = facts.drop_duplicates(["date", "thscode"])
    return {(str(row.date), str(row.thscode)): float(row.close) for row in facts.itertuples(index=False)}


def trigger(item: dict, record: dict, rank: int, lookup: dict[tuple[str, str], float]) -> bool:
    node = next(node for node in item["node_role_records"] if node["candidate"] == record["candidate"])
    previous_close = lookup[(item["signal_date"], record["candidate"])]
    gap = (float(record["t1_open"]) / previous_close - 1.0) * 100.0
    return (
        item.get("environment_state") == "修复"
        and node.get("role") != "市场核心"
        and int(node.get("board_count", 0)) >= 3
        and rank <= 2
        and gap >= 5.0
    )


def return_count(name: str) -> int:
    with (ROOT / name).open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    computed = [row for row in rows if row["status"] == "computed"]
    for row in computed:
        expected = float(row["t2_auction_sell_price"]) / float(row["t1_open_buy_price"]) - 1.0
        assert math.isclose(expected * 100.0, float(row["return_pct"]), rel_tol=0, abs_tol=1e-10)
    return len(computed)


def main() -> None:
    windows = {
        "2026-01": "replay_challenger_weak_repair_spike_2026-01.jsonl",
        "2026-02": "replay_challenger_high_volatility_auction_decay_2026-02.jsonl",
        "2026-03": "replay_challenger_high_volatility_auction_decay_2026-03.jsonl",
        "2026-04": "replay_challenger_repair_high_gap_2026-04.jsonl",
    }
    trigger_sets = {}
    for month, filename in windows.items():
        records = load(filename)
        lookup = close_lookup(month)
        hits = []
        for item in records.values():
            for rank, record in enumerate(item.get("auction_records", []), 1):
                if record.get("t1_open") is not None and trigger(item, record, rank, lookup):
                    hits.append([item["signal_date"], record["candidate"]])
        trigger_sets[month] = hits

    assert trigger_sets["2026-01"] == [["2026-01-08", "002519.SZ"], ["2026-01-21", "601616.SH"]]
    assert trigger_sets["2026-02"] == [["2026-02-03", "603103.SH"]]
    assert trigger_sets["2026-03"] == []
    for expected in (
        ["2026-04-07", "000720.SZ"],
        ["2026-04-20", "002297.SZ"],
        ["2026-04-22", "003018.SZ"],
        ["2026-04-30", "603095.SH"],
    ):
        assert expected in trigger_sets["2026-04"]

    april_parent = load("replay_current_skill_auction_2026-04.jsonl")
    april_challenger = load("replay_challenger_repair_high_gap_2026-04.jsonl")
    changes = {}
    for signal_date in april_parent:
        assert april_parent[signal_date]["original_queue"] == april_challenger[signal_date]["original_queue"]
        old = april_parent[signal_date].get("executed_candidate") or ""
        new = april_challenger[signal_date].get("executed_candidate") or ""
        if old != new:
            changes[signal_date] = (old, new)
    assert changes == {
        "2026-04-07": ("000720.SZ", "002980.SZ"),
        "2026-04-20": ("002297.SZ", ""),
        "2026-04-22": ("003018.SZ", ""),
        "2026-04-30": ("603095.SH", "600379.SH"),
    }
    assert all(not any(item["leakage_check"].values()) for item in april_challenger.values())
    print(json.dumps({
        "trigger_sets": trigger_sets,
        "april_execution_changes": changes,
        "computed_returns_april": return_count("challenger_returns_repair_high_gap_2026-04.csv"),
        "queues_unchanged": True,
        "all_leakage_flags_false": True,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
