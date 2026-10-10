#!/usr/bin/env python3
"""Validate the shared T+1 open-gap floor across January-March."""

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


def main() -> None:
    parent = load("replay_challenger_weak_repair_spike_2026-01.jsonl")
    challenger = load("replay_challenger_open_gap_floor_2026-01.jsonl")
    assert parent.keys() == challenger.keys()
    changes = {}
    for signal_date in parent:
        assert parent[signal_date]["original_queue"] == challenger[signal_date]["original_queue"]
        old = parent[signal_date].get("executed_candidate") or ""
        new = challenger[signal_date].get("executed_candidate") or ""
        if old != new:
            changes[signal_date] = (old, new)
    assert changes == {"2026-01-29": ("601212.SH", "600916.SH")}

    records = {
        row["candidate"]: row
        for row in challenger["2026-01-29"]["auction_records"]
    }
    assert records["601212.SH"]["open_gap_failure"] is True
    assert records["601212.SH"]["open_gap_pct"] < -10.0
    assert records["601212.SH"]["decision"] == "跳过并递补"
    assert records["600916.SH"]["open_gap_failure"] is False
    assert records["600916.SH"]["decision"] == "保留并执行"
    assert all(not any(row["leakage_check"].values()) for row in challenger.values())

    with (ROOT / "challenger_returns_open_gap_floor_2026-01.csv").open(
        encoding="utf-8", newline=""
    ) as handle:
        returns = list(csv.DictReader(handle))
    computed = [row for row in returns if row["status"] == "computed"]
    for row in computed:
        expected = (
            float(row["t2_auction_sell_price"]) / float(row["t1_open_buy_price"]) - 1.0
        ) * 100.0
        assert math.isclose(expected, float(row["return_pct"]), rel_tol=0, abs_tol=1e-10)

    for month in ("2026-02", "2026-03"):
        facts = pd.read_csv(
            ROOT / f"replay_inputs_{month}.csv",
            usecols=["date", "thscode", "close"],
        ).drop_duplicates(["date", "thscode"])
        close_lookup = {
            (str(row.date), str(row.thscode)): float(row.close)
            for row in facts.itertuples(index=False)
        }
        for item in load(f"replay_challenger_weak_repair_spike_{month}.jsonl").values():
            if not item.get("executed_candidate"):
                continue
            selected = next(
                record
                for record in item["auction_records"]
                if record["candidate"] == item["executed_candidate"]
            )
            previous_close = close_lookup[(item["signal_date"], item["executed_candidate"])]
            open_gap = (float(selected["t1_open"]) / previous_close - 1.0) * 100.0
            assert open_gap >= -2.0

    result = {
        "execution_changes": changes,
        "computed_returns_2026_01": len(computed),
        "queues_unchanged": True,
        "all_leakage_flags_false": True,
        "february_march_already_enforce_floor": True,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
